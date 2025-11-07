# Refactored ImageQueue with better separation of concerns

import os
import queue
import threading
from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, Dict, Tuple, Any
from pathlib import Path
from itertools import chain

from .io import *

# Properly refactored ImageQueue that actually works

import os
import queue
import threading
from itertools import chain
from typing import List, Iterator, Optional, Dict, Tuple

class FileManager:
	"""Handles all file discovery and ordering logic."""

	def __init__(self, hyb_folders, hyb_range, regex, fov_range=None, background_range=None):
		self.hyb_folders = hyb_folders
		self.hyb_range = hyb_range
		self.regex = regex
		self.background_range = background_range

		# Parse FOV range
		if fov_range:
			self.fov_min, self.fov_max = map(float, fov_range.split(':'))
		else:
			self.fov_min, self.fov_max = -float('inf'), float('inf')

	def discover_files(self):
		"""Discover and order all files."""
		# Find matching files
		matches = FolderFilter(self.hyb_range, self.regex, self.fov_min, self.fov_max).get_matches(self.hyb_folders)

		background = None
		if self.background_range:
			background = FolderFilter(self.background_range, self.regex, self.fov_min, self.fov_max).get_matches(self.hyb_folders)

		# Create ordered file list
		return self._create_ordered_list(matches, background)

	def _create_ordered_list(self, matches, background):
		"""Create ordered file list with background interlacing."""
		shared = set(matches.keys()).intersection(background.keys()) if background else matches.keys()

		ordered_files = []
		for key in shared:
			if background and key in background:
				ordered_files.extend(background[key])

			# Sort by hybridization number
			hsorted = sorted(matches[key], key=lambda f: get_ih(os.path.dirname(f)))
			ordered_files.extend(hsorted)

		return ordered_files, bool(background)


class ContainerProcessor:
	"""Handles container creation and file checking."""

	def __init__(self, output_folder, hyb_save, dapi_save, shape):
		self.output_folder = output_folder
		self.hyb_save = hyb_save
		self.dapi_save = dapi_save
		self.shape = shape

	def process_file(self, path):
		"""Process a single file into a container."""
		container = Container(path)

		# Check existing files and load/compute as needed
		fov, tag = path_parts(path)

		# Handle hybridization channels
		for icol in range(self.shape[0] - 1):
			filepath = os.path.join(self.output_folder,
								  self.hyb_save.format(fov=fov, tag=tag, icol=icol))
			if os.path.exists(filepath):
				container[icol].fits = cp.load(filepath) if 'cp' in globals() else np.load(filepath)
			else:
				container[icol].compute()

		# Handle DAPI channel
		icol = self.shape[0] - 1
		filepath = os.path.join(self.output_folder,
							  self.dapi_save.format(fov=fov, tag=tag, icol=icol))
		if os.path.exists(filepath):
			data = cp.load(filepath) if 'cp' in globals() else np.load(filepath)
			container.Xh_plus = data['Xh_plus']
			container.Xh_minus = data['Xh_minus']
		else:
			container[icol].compute()

		return container


class BlockBuilder:
	"""Handles grouping containers into blocks."""

	def __init__(self, has_background=False):
		self.has_background = has_background
		self.current_block = Block()
		self.current_fov = None
		self.current_set = None

	def should_start_new_block(self, container):
		"""Check if we should start a new block."""
		if not container or container is False:
			return False

		try:
			ifov = get_ifov(container.path)
			iset = get_iset(container.path)

			if self.current_fov is None:
				# First container
				self.current_fov = ifov
				self.current_set = iset
				return True

			return ifov != self.current_fov or iset != self.current_set
		except:
			return False

	def add_to_block(self, container):
		"""Add container to current block."""
		if self.has_background and not hasattr(self.current_block, 'background'):
			self.current_block.background = container
		else:
			self.current_block.append(container)

	def get_current_block(self):
		"""Get current block and start a new one."""
		block = self.current_block
		self.current_block = Block()
		return block

	def update_current_fov_set(self, container):
		"""Update current FOV and set from container."""
		try:
			self.current_fov = get_ifov(container.path)
			self.current_set = get_iset(container.path)
		except:
			pass


class ImageQueue:
	"""Main ImageQueue class with cleaner separation of concerns."""

	def __init__(self, args, prefetch_count=6):
		self.args = args
		self.args_array = namespace_to_array(self.args.settings)

		# Extract paths
		paths = vars(args.paths)
		self.__dict__.update(paths)

		# Create output directory
		os.makedirs(self.output_folder, exist_ok=True)

		# Set up file management
		self.file_manager = FileManager(
			self.hyb_folders,
			self.hyb_range,
			self.regex,
			getattr(self, 'fov_range', None),
			getattr(self, 'background_range', None)
		)

		# Discover files
		file_list, has_background = self.file_manager.discover_files()

		if not file_list:
			raise RuntimeError("No files found to process")

		# Get image metadata from first file
		self.shape, self.dtype = self._get_metadata(file_list)

		# Set up container processor
		self.processor = ContainerProcessor(
			self.output_folder,
			self.hyb_save,
			self.dapi_save,
			self.shape
		)

		# Set up block builder
		self.block_builder = BlockBuilder(has_background)

		# Set up threading
		self.file_iterator = iter(file_list)
		self.queue = queue.Queue(maxsize=prefetch_count)
		self.stop_event = threading.Event()
		self.worker_thread = threading.Thread(target=self._worker, daemon=True)
		self.worker_thread.start()

	def _get_metadata(self, file_list):
		"""Get shape and dtype from first valid file."""
		for path in file_list:
			try:
				first_image = read_im(path)
				return first_image.shape, first_image.dtype
			except:
				continue
		raise RuntimeError("No valid images found")

	def _worker(self):
		"""Background worker thread."""
		try:
			for path in self.file_iterator:
				if self.stop_event.is_set():
					break

				try:
					container = self.processor.process_file(path)
					self.queue.put(container)
				except Exception as e:
					print(f"Warning: failed to process {path}: {e}")
					self.queue.put(False)
		except Exception as e:
			print(f"Worker error: {e}")
		finally:
			self.queue.put(None)  # Signal end

	def __iter__(self):
		return self

	def __next__(self):
		"""Get next block of images."""
		while True:
			try:
				# Get next container with timeout to avoid infinite hangs
				container = self.queue.get(timeout=30)

				if container is None:
					# End of queue - return any remaining block
					if len(self.block_builder.current_block) > 0:
						return self.block_builder.get_current_block()
					raise StopIteration

				if container is False:
					# Skip failed containers
					continue

				# Check if we should start a new block
				if self.block_builder.should_start_new_block(container):
					# Return current block if it has items
					if len(self.block_builder.current_block) > 0:
						current_block = self.block_builder.get_current_block()
						self.block_builder.add_to_block(container)
						self.block_builder.update_current_fov_set(container)
						return current_block
					else:
						# First container or empty block
						self.block_builder.add_to_block(container)
						self.block_builder.update_current_fov_set(container)
				else:
					# Add to current block
					self.block_builder.add_to_block(container)

			except queue.Empty:
				print("Queue timeout - no more images")
				if len(self.block_builder.current_block) > 0:
					return self.block_builder.get_current_block()
				raise StopIteration

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

	def close(self):
		"""Clean shutdown."""
		self.stop_event.set()
		if self.worker_thread.is_alive():
			self.worker_thread.join(timeout=5)

	# Keep your existing save methods unchanged
	def save_hyb(self, path, icol, Xhf, attempt=1, max_attempts=3):
		fov, tag = path_parts(path)
		filename = self.hyb_save.format(fov=fov, tag=tag, icol=icol)
		filepath = os.path.join(self.output_folder, filename)

		Xhf = [x for x in Xhf if x.shape[0] > 0]
		if Xhf:
			xp = cp.get_array_module(Xhf[0]) if 'cp' in globals() else np
			Xhf = xp.vstack(Xhf)
		else:
			xp = np
			Xhf = np.array([])

		if not os.path.exists(filepath) or (hasattr(self, "redo") and self.redo):
			xp.savez_compressed(filepath, Xh=Xhf, version=__version__, args=self.args_array)
		del Xhf
		if 'cp' in globals() and xp == cp:
			xp._default_memory_pool.free_all_blocks()

	def save_dapi(self, path, icol, Xh_plus, Xh_minus, attempt=1, max_attempts=3):
		fov, tag = path_parts(path)
		filename = self.dapi_save.format(fov=fov, tag=tag, icol=icol)
		filepath = os.path.join(self.output_folder, filename)

		xp = cp.get_array_module(Xh_plus) if 'cp' in globals() else np
		if not os.path.exists(filepath) or (hasattr(self, "redo") and self.redo):
			xp.savez_compressed(filepath, Xh_plus=Xh_plus, Xh_minus=Xh_minus,
							  version=__version__, args=self.args_array)
		del Xh_plus, Xh_minus
		if 'cp' in globals() and xp == cp:
			xp._default_memory_pool.free_all_blocks()
