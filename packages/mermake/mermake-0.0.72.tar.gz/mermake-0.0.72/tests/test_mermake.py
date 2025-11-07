import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import toml
import shutil
import filecmp
import toml
import re

import numpy as np
import cupy as cp
from mermake.__main__ import main as mermake_main
from mermake.io import namespace_to_array

def array_to_dict(array):
	out = {'paths':{}, 'hybs':{}, 'dapi':{}}
	for block, key, val in array:
		out[block][key] = val
	return out

def sort_Xh(xh):
    """
    Sort a 2D array by the first three columns.
    """
    # Use lexsort, which sorts by last key first, so reverse the order
    sort_idx = np.lexsort((xh[:,2], xh[:,1], xh[:,0]))
    return xh[sort_idx]



@pytest.fixture
def dummy_toml(tmp_path):
	settings_path = tmp_path / "settings.toml"
	settings = {
		"paths": {
			"codebook": "none",
			"psf_file": str(tmp_path / "psf.npy"),
			"flat_field_tag": "flat_field",
			"hyb_range": "H1_test:H2_test",
			"hyb_folders": [str(tmp_path / "hyb")],
			"output_folder": str(tmp_path / "output"),
			"redo": False,
			"fov_range": "0:1",
			"hyb_save": "{fov}--{tag}--col{icol}__Xhfits.npz",
			"dapi_save": "{fov}--{tag}--dapiFeatures.npz",
			"drift_save": "drift_{fov}--_set{iset}.pkl",
			"regex": r"([A-z]+)(\d+)_(.+)_set(\d+)(.*)"
		},
		"hybs": {
			"tile_size": 10,
			"overlap": 2,
			"beta": 0.01,
			"threshold": 10,
			"blur_radius": 1,
			"delta": 1,
			"delta_fit": 1,
			"sigmaZ": 1,
			"sigmaXY": 1.0
		},
		"dapi": {
			"tile_size": 10,
			"overlap": 2,
			"beta": 0.01,
			"threshold": 3.0,
			"blur_radius": 1,
			"delta": 1,
			"delta_fit": 1,
			"sigmaZ": 1,
			"sigmaXY": 1.0
		}
	}
	settings_path.write_text(toml.dumps(settings))
	np.save(tmp_path / "psf.npy", np.ones((3,3,3)))  # dummy PSF
	(tmp_path / "hyb" / "H1_test_set1").mkdir(parents=True)
	(tmp_path / "hyb" / "H2_test_set1").mkdir(parents=True)
	return settings_path

def test_mermake_main(dummy_toml):
	with patch("mermake.io.ImageQueue") as mock_queue_class, \
		 patch("mermake.io.load_flats") as mock_load_flats, \
		 patch("mermake.deconvolver.Deconvolver") as mock_deconvolver_class, \
		 patch("mermake.maxima.find_local_maxima") as mock_find_max, \
		 patch("concurrent.futures.ThreadPoolExecutor") as mock_executor, \
		 patch("mermake.align.drift") as mock_drift, \
		 patch("mermake.align.drift_save") as mock_drift_save:

		# Fake ImageQueue
		mock_queue = MagicMock()
		mock_queue.__enter__.return_value = mock_queue
		mock_queue.shape = (1, 3, 5, 5)
		mock_queue.summary = "dummy_summary"
		mock_image = MagicMock()
		mock_image.path = "dummy_path"
		mock_image.__getitem__.return_value.data = np.ones((3,5,5), dtype=np.uint16)
		#mock_queue.__iter__.return_value = [[mock_image]]
		mock_queue.__iter__.return_value = [mock_image]
		mock_queue_class.return_value = mock_queue

		# Fake load_flats returns numpy array (not cupy)
		mock_load_flats.return_value = [np.ones((3,5,5), dtype=np.uint16)]

		# Fake deconvolver
		mock_deconvolver = MagicMock()
		mock_deconvolver.apply.side_effect = lambda *a, **kw: None
		mock_deconvolver_class.return_value = mock_deconvolver

		# Fake maxima
		mock_find_max.return_value = np.array([[0,0,0]])

		# Fake executor
		mock_executor.return_value.submit.side_effect = lambda fn, *a, **kw: None

		# Fake drift
		mock_drift.return_value = None

		# Run main with dummy toml
		sys.argv = ["mermake", str(dummy_toml)]
		mermake_main()

		# Assertions
		mock_queue_class.assert_called()
		mock_load_flats.assert_called()
		mock_deconvolver_class.assert_called()
		mock_find_max.assert_called()
		mock_executor.return_value.submit.assert_called()


@pytest.fixture
def single_fov_toml(tmp_path):
	"""
	Copy example TOML and xfits files into a temp folder.
	Returns path to TOML.
	"""
	example_folder = Path("tests/examples/single")
	tmp_example = tmp_path / "single"
	tmp_example.mkdir()

	# Copy toml
	toml_src = example_folder / "single.toml"
	toml_dst = tmp_example / "single.toml"
	shutil.copy(toml_src, toml_dst)

	# Copy xfits folder
	xfits_src = example_folder / "out"
	xfits_dst = tmp_example / "out"
	shutil.copytree(xfits_src, xfits_dst)

	return toml_dst, xfits_dst

def test_mermake_single_fov(single_fov_toml, tmp_path):
	toml_path, xfits_folder = single_fov_toml

	# Prepare temp output folder
	temp_output = tmp_path / "output"
	temp_output.mkdir()

	# Update TOML to point output to temp folder
	settings = toml.load(toml_path)
	settings["paths"]["output_folder"] = str(temp_output)
	toml_path.write_text(toml.dumps(settings))

	# Run MERMAKE
	sys.argv = ["mermake", str(toml_path)]
	mermake_main()

	# Compare outputs to reference files
	ref_folder = Path("tests/examples/single/out")
	for ref_file in ref_folder.glob("Conv*.npz"):
		temp_file = temp_output / ref_file.name
		assert temp_file.exists(), f"Output file missing: {temp_file}"

		# Load and compare arrays
		ref_data = np.load(ref_file)
		temp_data = np.load(temp_file)
		#np.testing.assert_allclose(temp_data, ref_data, rtol=1e-5, atol=1e-8)

		# version is a number
		version = temp_data['version'].item()
		assert isinstance(version, str)
		assert re.match(r'^\d+\.\d+\.\d+$', version), f"Version format invalid: {ver}"

		# args matches toml
		ref_args = array_to_dict(ref_data['args'])
		temp_args = array_to_dict(temp_data['args'])
		# ignore the output_folder path cause it aint gonna match
		temp_args['paths']['output_folder'] = ref_args['paths']['output_folder']
		# now compare
		assert temp_args == ref_args

		key = 'Xh' if 'Xh' in ref_data else 'Xh_plus'
		# sort the Xh arrays since the rows are unordered from non deterministic gpu
		ref_sorted = sort_Xh(ref_data[key])
		temp_sorted = sort_Xh(temp_data[key])
		# now compare
		np.testing.assert_allclose(temp_sorted, ref_sorted, rtol=1e-5, atol=1e-8)
		if key == 'Xh_plus':
			key = 'Xh_minus'
			ref_sorted = sort_Xh(ref_data[key])
			temp_sorted = sort_Xh(temp_data[key])
			# now compare
			np.testing.assert_allclose(temp_sorted, ref_sorted, rtol=1e-5, atol=1e-8)
		
