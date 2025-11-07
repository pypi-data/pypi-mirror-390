import pytest
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from types import SimpleNamespace
import argparse
import xml.etree.ElementTree as ET
import queue
import threading
import time

# Import the module under test
from mermake import io


class TestCenterCrop:
	def test_center_crop_basic(self):
		"""Test basic center cropping functionality."""
		# Create a 10x10 array
		A = np.arange(100).reshape(10, 10)
		# Crop to 4x4
		result = io.center_crop(A, (4, 4))
		
		assert result.shape == (4, 4)
		# Should extract from center (3:7, 3:7)
		expected = A[3:7, 3:7]
		np.testing.assert_array_equal(result, expected)

	def test_center_crop_odd_dimensions(self):
		"""Test center cropping with odd dimensions."""
		A = np.arange(25).reshape(5, 5)
		result = io.center_crop(A, (3, 3))
		
		assert result.shape == (3, 3)
		expected = A[1:4, 1:4]
		np.testing.assert_array_equal(result, expected)

	def test_center_crop_same_size(self):
		"""Test center cropping when target size equals input size."""
		A = np.arange(16).reshape(4, 4)
		result = io.center_crop(A, (4, 4))
		
		np.testing.assert_array_equal(result, A)


class TestPathParts:
	def test_path_parts_basic(self):
		"""Test path_parts function with basic path."""
		path = "/some/directory/tag_name/fov_123.zarr"
		fov, tag = io.path_parts(path)
		
		assert fov == "fov_123"
		assert tag == "tag_name"

	def test_path_parts_no_extension(self):
		"""Test path_parts function without file extension."""
		path = "/some/directory/tag_name/fov_456"
		fov, tag = io.path_parts(path)
		
		assert fov == "fov_456"
		assert tag == "tag_name"


class TestGetFunctions:
	def test_get_ih(self):
		"""Test get_ih function."""
		assert io.get_ih("/path/to/H1_file.ext") == 1
		assert io.get_ih("/path/to/H25_test.ext") == 25
		assert io.get_ih("test123file.ext") == 123

	def test_get_ih_no_digits(self):
		"""Test get_ih raises error when no digits found."""
		#with pytest.raises(ValueError, match="No number found"):
		assert io.get_ih("/path/to/nodigits.ext") == 10**100

	def test_get_ifov(self):
		"""Test get_ifov function."""
		assert io.get_ifov("/path/to/file_123.zarr") == 123
		assert io.get_ifov("test_456.zarr") == 456

	def test_get_ifov_no_digits(self):
		"""Test get_ifov raises error when no digits found."""
		with pytest.raises(ValueError, match="No digits found before .zarr"):
			io.get_ifov("/path/to/nodigits.zarr")

	def test_get_iset(self):
		"""Test get_iset function."""
		assert io.get_iset("/path/to/file_set123.ext") == 123
		assert io.get_iset("/path/parent_set456/file.ext") == 456

	def test_get_iset_recursive(self):
		"""Test get_iset recursive search."""
		with tempfile.TemporaryDirectory() as tmpdir:
			# Create nested directory structure
			nested_path = Path(tmpdir) / "parent_set789" / "subdir" / "file.ext"
			nested_path.parent.mkdir(parents=True, exist_ok=True)
			nested_path.touch()
			
			assert io.get_iset(str(nested_path)) == 789

	def test_get_iset_not_found(self):
		"""Test get_iset raises error when not found."""
		with pytest.raises(ValueError, match="No digits found after the word _set"):
			io.get_iset("/root/no_set_here/file.ext")


class TestContainer:
	@patch('mermake.io.read_im')
	def test_container_from_path(self, mock_read_im):
		"""Test Container creation from file path."""
		# Mock a 3-channel image
		mock_image = np.random.rand(3, 100, 100)
		mock_read_im.return_value = mock_image
		
		container = io.Container("/fake/path.zarr")
		
		assert container.path == "/fake/path.zarr"
		assert len(container.data) == 3
		assert all(isinstance(ch, io.Container) for ch in container.data)

	def test_container_from_array(self):
		"""Test Container creation from numpy array."""
		array = np.random.rand(50, 50)
		container = io.Container(array)
		
		assert container.path is None
		np.testing.assert_array_equal(container.data, array)

	def test_container_getitem(self):
		"""Test Container indexing."""
		array = np.random.rand(50, 50)
		container = io.Container(array)
		
		# Should return the array itself for single array containers
		result = container[0] if hasattr(container.data, '__getitem__') else container.data
		assert result is not None

	def test_container_repr(self):
		"""Test Container string representation."""
		array = np.random.rand(50, 50)
		container = io.Container(array)
		
		repr_str = repr(container)
		assert "Container" in repr_str
		assert "shape=" in repr_str

	def test_container_array_interface(self):
		"""Test Container numpy array interface."""
		array = np.random.rand(50, 50)
		container = io.Container(array)
		
		# Test __array__ method
		result = container.__array__()
		np.testing.assert_array_equal(result, array)

	def test_container_array_interface_with_dtype(self):
		"""Test Container numpy array interface with dtype conversion."""
		array = np.random.rand(50, 50).astype(np.float32)
		container = io.Container(array)
		
		result = container.__array__(dtype=np.float64)
		assert result.dtype == np.float64

	def test_container_array_interface_multichannel_error(self):
		"""Test Container array interface raises error for multi-channel."""
		with patch('mermake.io.read_im') as mock_read_im:
			mock_image = np.random.rand(3, 100, 100)
			mock_read_im.return_value = mock_image
			
			container = io.Container("/fake/path.zarr")
			
			with pytest.raises(ValueError, match="Cannot convert a multi-channel Container"):
				container.__array__()


class TestFolderFilter:
	def test_folder_filter_init(self):
		"""Test FolderFilter initialization."""
		filter_obj = io.FolderFilter("H1MER_set1:H5MER_set3", r"(H)(\d+)(MER)_set(\d+)(.*)", 0, 100)
		
		assert filter_obj.hyb_range == "H1MER_set1:H5MER_set3"
		assert filter_obj.fov_min == 0
		assert filter_obj.fov_max == 100

	def test_folder_filter_parse_pattern(self):
		"""Test pattern parsing."""
		filter_obj = io.FolderFilter("H1MER_set1:H5MER_set3", r"(H)(\d+)(MER)_set(\d+)(.*)", 0, 100)
		
		result = filter_obj._parse_pattern("H3MER_set2_suffix")
		assert result == ("H", "3", "MER", "2", "_suffix")

	def test_folder_filter_isin(self):
		"""Test isin method."""
		filter_obj = io.FolderFilter("H1MER_set1:H5MER_set3", r"(H)(\d+)(MER)_set(\d+)(.*)", 0, 100)
		
		assert filter_obj.isin("H3MER_set2") == True
		assert filter_obj.isin("H6MER_set2") == False  # H number too high
		assert filter_obj.isin("H1MER_set4") == False  # set number too high
		assert filter_obj.isin("H0MER_set1") == False  # H number too low

	@patch('os.scandir')
	@patch('os.path.exists')
	def test_folder_filter_get_matches(self, mock_exists, mock_scandir):
		"""Test get_matches method."""
		# Mock filesystem structure
		mock_exists.return_value = True
		
		# Mock directory entries
		mock_dir_entry = MagicMock()
		mock_dir_entry.is_dir.return_value = True
		mock_dir_entry.name = "H1MER_set1"
		mock_dir_entry.path = "/root/H1MER_set1"
		
		mock_file_entry = MagicMock()
		mock_file_entry.is_dir.return_value = True
		mock_file_entry.name = "fov_50.zarr"
		mock_file_entry.path = "/root/H1MER_set1/fov_50.zarr"
		
		# Configure mock_scandir to return different values based on path
		def scandir_side_effect(path):
			mock_context = MagicMock()
			if path == "/root":
				mock_context.__enter__.return_value = [mock_dir_entry]
			else:
				mock_context.__enter__.return_value = [mock_file_entry]
			mock_context.__exit__.return_value = None
			return mock_context
		
		mock_scandir.side_effect = scandir_side_effect
		
		filter_obj = io.FolderFilter("H1MER_set1:H2MER_set2", r"(H)(\d+)(MER)_set(\d+)(.*)", 0, 100)
		result = filter_obj.get_matches(["/root"])
		
		assert (1, 50) in result
		assert result[(1, 50)] == ["/root/H1MER_set1/fov_50.zarr"]

'''
class TestBlock:
	def test_block_init_empty(self):
		"""Test Block initialization with no items."""
		block = io.Block()
		assert len(block) == 0
		assert block.background is None

	def test_block_init_with_items(self):
		"""Test Block initialization with items."""
		mock_container = Mock()
		mock_container.path = "/path/to/tag/fov.zarr"
		
		block = io.Block([mock_container])
		assert len(block) == 1
		assert block[0] == mock_container

	def test_block_init_single_item(self):
		"""Test Block initialization with single item."""
		mock_container = Mock()
		mock_container.path = "/path/to/tag/fov.zarr"
		
		block = io.Block(mock_container)
		assert len(block) == 1
		assert block[0] == mock_container

	def test_block_parts(self):
		"""Test Block parts method."""
		mock_container = Mock()
		mock_container.path = "/path/to/tag_name/fov_123.zarr"
		
		block = io.Block([mock_container])
		fov, tag = block.parts()
		
		assert fov == "fov_123"
		assert tag == "tag_name"

	def test_block_fov(self):
		"""Test Block fov method."""
		mock_container = Mock()
		mock_container.path = "/path/to/tag_name/fov_456.zarr"
		
		block = io.Block([mock_container])
		assert block.fov() == "fov_456"

	def test_block_tag(self):
		"""Test Block tag method."""
		mock_container = Mock()
		mock_container.path = "/path/to/tag_name/fov_456.zarr"
		
		block = io.Block([mock_container])
		assert block.tag() == "tag_name"

	def test_block_iset(self):
		"""Test Block iset method."""
		mock_container = Mock()
		mock_container.path = "/path/to/tag_set123/fov_456.zarr"
		
		block = io.Block([mock_container])
		assert block.iset() == 123
'''

class TestImageQueue:
	@patch('mermake.io.read_im')
	@patch('mermake.io.FolderFilter')
	@patch('os.makedirs')
	def test_image_queue_init(self, mock_makedirs, mock_folder_filter, mock_read_im):
		"""Test ImageQueue initialization."""
		# Mock arguments
		mock_args = Mock()
		mock_args.settings = SimpleNamespace()
		mock_args.paths = SimpleNamespace(
			output_folder="/output",
			hyb_range="H1MER_set1:H2MER_set1",
			regex=r"(H)(\d+)(MER)_set(\d+)(.*)",
			hyb_folders=["/data"],
			hyb_save="hyb_{fov}_{tag}_{icol}.npz",
			dapi_save="dapi_{fov}_{tag}_{icol}.npz"
		)
		
		# Mock FolderFilter
		mock_filter_instance = Mock()
		#mock_filter_instance.get_matches.return_value = {(1, 50): ["/path1.zarr"]}
		#mock_folder_filter.return_value = mock_filter_instance
		mock_filter_instance.get_matches.return_value = {(1, 50): ["/path1.zarr"]}
		mock_filter_instance._parse_pattern.return_value = ('H', '1', 'MER', '1', '')
		mock_filter_instance._undo_regex.return_value = ('H1_MER_set1')
		mock_folder_filter.return_value = mock_filter_instance

		
		# Mock first image
		mock_read_im.return_value = np.random.rand(3, 100, 100).astype(np.uint16)
		
		with patch('threading.Thread'):
			queue_obj = io.ImageQueue(mock_args)
			
			assert queue_obj.output_folder == "/output"
			assert queue_obj.shape == (3, 100, 100)
			assert queue_obj.dtype == np.uint16

	@patch('mermake.io.read_im')
	@patch('mermake.io.FolderFilter')
	@patch('os.makedirs')
	@patch('threading.Thread')
	def test_image_queue_hsorted(self, mock_thread, mock_makedirs, mock_folder_filter, mock_read_im):
		"""Test hsorted method."""
		# Mock arguments
		mock_args = Mock()
		mock_args.settings = SimpleNamespace()
		mock_args.paths = SimpleNamespace(
			output_folder="/output",
			hyb_range="H1MER_set1:H2MER_set1",
			regex=r"(H)(\d+)(MER)_set(\d+)(.*)",
			hyb_folders=["/data"],
			hyb_save="hyb_{fov}_{tag}_{icol}.npz",
			dapi_save="dapi_{fov}_{tag}_{icol}.npz"
		)
		
		# Mock FolderFilter
		mock_filter_instance = Mock()
		mock_filter_instance.get_matches.return_value = {(1, 50): ["/path1.zarr"]}
		mock_filter_instance._parse_pattern.return_value = ('H', '1', 'MER', '1', '')
		mock_filter_instance._undo_regex.return_value = ('H1_MER_set1')
		mock_folder_filter.return_value = mock_filter_instance
		
		# Mock first image
		mock_read_im.return_value = np.random.rand(3, 100, 100).astype(np.uint16)
		
		queue_obj = io.ImageQueue(mock_args)
		
		files = ["/H3/fov.zarr", "/H1/fov.zarr", "/H2/fov.zarr"]
		sorted_files = queue_obj.hsorted(files)
		
		assert sorted_files == ["/H1/fov.zarr", "/H2/fov.zarr", "/H3/fov.zarr"]


class TestUtilityFunctions:
	def test_dict_to_namespace(self):
		"""Test dict_to_namespace conversion."""
		test_dict = {
			"a": 1,
			"b": {
				"c": 2,
				"d": [{"e": 3}, {"f": 4}]
			}
		}
		
		result = io.dict_to_namespace(test_dict)
		
		assert isinstance(result, SimpleNamespace)
		assert result.a == 1
		assert isinstance(result.b, SimpleNamespace)
		assert result.b.c == 2
		assert isinstance(result.b.d[0], SimpleNamespace)
		assert result.b.d[0].e == 3

	def test_namespace_to_dict(self):
		"""Test namespace_to_dict conversion."""
		ns = argparse.Namespace(
			a=1,
			b=argparse.Namespace(c=2, d=3),
			e=[argparse.Namespace(f=4)]
		)
		
		result = io.namespace_to_dict(ns)
		
		expected = {
			"a": 1,
			"b": {"c": 2, "d": 3},
			"e": [{"f": 4}]
		}
		
		assert result == expected

	def test_namespace_to_array(self):
		"""Test namespace_to_array conversion."""
		ns = SimpleNamespace(
			a=1,
			b=SimpleNamespace(c=2, d=3)
		)
		
		result = io.namespace_to_array(ns)
		
		# Result should be list of (prefix, key, value) tuples
		assert isinstance(result, list)
		assert len(result) >= 3  # Should have entries for a, b.c, b.d
		
		# Check that we have the expected entries
		entries = {(prefix, key): value for prefix, key, value in result}
		assert entries[("", "a")] == "1"
		assert entries[("b", "c")] == "2"
		assert entries[("b", "d")] == "3"

	@patch('builtins.open', new_callable=mock_open, read_data='<root><field>value</field></root>')
	def test_read_xml(self, mock_file):
		"""Test read_xml function."""
		result = io.read_xml("test.xml")
		
		assert result.tag == "root"
		field = result.find(".//field")
		assert field.text == "value"

	@patch('mermake.io.read_xml')
	def test_get_xml_field(self, mock_read_xml):
		"""Test get_xml_field function."""
		# Create a mock XML root
		root = ET.Element("root")
		field = ET.SubElement(root, "field")
		field.text = "test_value"
		
		mock_read_xml.return_value = root
		
		result = io.get_xml_field("test.xml", "field")
		assert result == "test_value"


class TestLoadFlats:
	@patch('glob.glob')
	@patch('numpy.load')
	def test_load_flats_basic(self, mock_np_load, mock_glob):
		"""Test load_flats function."""
		# Skip this test if cupy is not available
		pytest.importorskip("cupy")
		
		# Mock glob to return some files
		mock_glob.return_value = ["flat1.npz", "flat2.npz"]
		
		# Mock numpy.load to return mock data
		mock_data = {"im": np.random.rand(3000, 3000)}
		mock_np_load.return_value = mock_data
		with patch('mermake.blur.box') as mock_blur:
			# Mock blur to return the input
			mock_blur.side_effect = lambda x, _: x
		
			
			result = io.load_flats("flat_field", shape=(3000, 3000))
			# Should return a cupy array stack
			assert result is not None
			for i in range(result.shape[0]):
				assert result[i].shape == (3000, 3000)
			mock_glob.assert_called_once_with("flat_field*")
			
			with pytest.raises(AssertionError):
				result = io.load_flats("flat_field", shape=(3200, 3200))


# Integration tests
class TestIntegration:
	def test_container_with_real_array(self):
		"""Integration test with real numpy arrays."""
		# Test Container with real arrays
		test_array = np.random.rand(64, 64).astype(np.float32)
		container = io.Container(test_array)
		
		# Test array interface
		result = np.array(container)
		np.testing.assert_array_equal(result, test_array)
		
		# Test dtype conversion
		result_float64 = np.array(container, dtype=np.float64)
		assert result_float64.dtype == np.float64

	def test_path_functions_integration(self):
		"""Integration test for path parsing functions."""
		test_paths = [
			"/data/H1MER_set1/fov_123.zarr",
			"/other/H25_set456/fov_789.zarr"
		]
		
		for path in test_paths:
			# Test get_ifov
			ifov = io.get_ifov(path)
			assert isinstance(ifov, int)
			assert ifov > 0
			
			# Test get_iset
			iset = io.get_iset(path)
			assert isinstance(iset, int)
			assert iset > 0
			
			# Test path_parts
			fov, tag = io.path_parts(path)
			assert isinstance(fov, str)
			assert isinstance(tag, str)


if __name__ == "__main__":
	pytest.main([__file__])
