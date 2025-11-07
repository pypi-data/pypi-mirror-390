"""
Tests for export functionality in aidge_export_tensorrt.
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, Mock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import aidge_export_tensorrt


class TestExportFunction(unittest.TestCase):
    """Tests for export() function"""
    
    def setUp(self):
        """Set up test environment with mocks"""
        self.test_dir = tempfile.mkdtemp(prefix="aidge_export_test_")
        self.export_folder = os.path.join(self.test_dir, "export_output")
        
        self.original_dirpath = aidge_export_tensorrt.dirpath
        
        class MockGraphView:
            pass
        
        self.mock_aidge_core = patch('aidge_export_tensorrt.aidge_core').start()
        self.mock_aidge_onnx = patch('aidge_export_tensorrt.aidge_onnx').start()
        self.mock_subprocess = patch('aidge_export_tensorrt.subprocess').start()
        
        self.mock_aidge_core.GraphView = MockGraphView
        
        self.test_static_dir = os.path.join(self.test_dir, "static")
        os.makedirs(os.path.join(self.test_static_dir, "tensorrt_10.10"), exist_ok=True)
        os.makedirs(os.path.join(self.test_static_dir, "tensorrt_8.6"), exist_ok=True)
        
        aidge_export_tensorrt.dirpath = self.test_static_dir
    
    def tearDown(self):
        """Clean up test environment"""
        patch.stopall()
        
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        aidge_export_tensorrt.dirpath = self.original_dirpath
    
    def test_export_directory_creation(self):
        """Test export directory creation with os.makedirs"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.path.split', return_value=('', 'dummy.onnx')) as mock_split, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree, \
             patch('aidge_export_tensorrt.os.makedirs', wraps=os.makedirs) as mock_makedirs:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="dummy.onnx"
            )
            
            mock_makedirs.assert_called_with(self.export_folder, exist_ok=True)
            
            self.assertTrue(os.path.exists(self.export_folder))
    
    def test_graphview_type_detection(self):
        """Test GraphView input type detection"""
        mock_graphview = self.mock_aidge_core.GraphView()
        
        with patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview=mock_graphview
            )
            
            self.mock_aidge_onnx.export_onnx.assert_called_once_with(
                mock_graphview, f"{self.export_folder}/model.onnx"
            )
    
    def test_string_type_detection(self):
        """Test string input type detection and routing"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.path.split', return_value=('', 'test.onnx')) as mock_split, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="test.onnx"
            )
            
            self.mock_aidge_onnx.export_onnx.assert_not_called()
            
            mock_copy.assert_called_once_with("test.onnx", self.export_folder)
    
    def test_invalid_input_type_handling(self):
        """Test invalid input type handling"""
        with patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree, \
             patch('builtins.print') as mock_print:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview=12345
            )
            
            mock_print.assert_any_call("The model should be a GraphView or an onnx file.")
            
            self.mock_aidge_onnx.export_onnx.assert_not_called()
    
    def test_onnx_file_extension_validation(self):
        """Test ONNX file extension validation with endswith check"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.path.split', return_value=('', 'model.onnx')) as mock_split, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="/path/to/model.onnx"
            )
            
            mock_copy.assert_called_once_with("/path/to/model.onnx", self.export_folder)
            mock_rename.assert_called_once()
    
    def test_onnx_file_copy_operation(self):
        """Test ONNX file copy operation using shutil.copy"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.path.split', return_value=('', 'test_model.onnx')) as mock_split, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            input_file = "/some/path/test_model.onnx"
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview=input_file
            )
            
            mock_copy.assert_called_once_with(input_file, self.export_folder)
    
    def test_onnx_file_path_splitting(self):
        """Test ONNX file path splitting using os.path.split"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            input_file = "/directory/path/my_model.onnx"
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview=input_file
            )
            
            mock_rename.assert_called_once()
            
            call_args = mock_rename.call_args[0]
            expected_source = f"{self.export_folder}/my_model.onnx"
            expected_dest = f"{self.export_folder}/model.onnx"
            self.assertEqual(call_args[0], expected_source)
            self.assertEqual(call_args[1], expected_dest)
    
    def test_onnx_file_renaming(self):
        """Test ONNX file renaming to model.onnx using os.rename"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
                
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="/some/path/original_name.onnx"
            )
            
            expected_source = f"{self.export_folder}/original_name.onnx"
            expected_dest = f"{self.export_folder}/model.onnx"
            mock_rename.assert_called_with(expected_source, expected_dest)
    
    def test_non_onnx_string_input(self):
        """Test non-ONNX string input handling"""
        with patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree, \
             patch('builtins.print') as mock_print:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="model.txt"
            )
            
            mock_print.assert_any_call("The file has to be an onnx file.")
            
            with patch('aidge_export_tensorrt.shutil.copy') as mock_copy:
                self.assertFalse(mock_copy.called)

    def test_trt_version_path_construction(self):
        """Test export builds correct static files path using trt_version parameter"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            custom_version = "8.6"
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="test.onnx", 
                trt_version=custom_version
            )
            
            expected_source_path = f"{aidge_export_tensorrt.dirpath}/static/tensorrt_{custom_version}/"
            mock_copytree.assert_called_once_with(
                expected_source_path,
                self.export_folder,
                dirs_exist_ok=True
            )

    def test_static_files_copytree(self):
        """Test export copies static files using shutil.copytree with dirs_exist_ok=True"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="model.onnx"
            )
            
            mock_copytree.assert_called_once()
            call_args = mock_copytree.call_args
            
            self.assertEqual(call_args[1]['dirs_exist_ok'], True)
            
            self.assertEqual(call_args[0][1], self.export_folder)

    def test_default_trt_version(self):
        """Test export uses default TRT version 10.10 when not specified"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="model.onnx"
            )
            
            expected_source_path = f"{aidge_export_tensorrt.dirpath}/static/tensorrt_10.10/"
            mock_copytree.assert_called_once_with(
                expected_source_path,
                self.export_folder,
                dirs_exist_ok=True
            )

    def test_custom_trt_version(self):
        """Test export uses custom TRT version parameter in static files path"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            custom_version = "9.2"
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="model.onnx",
                trt_version=custom_version
            )
            
            expected_source_path = f"{aidge_export_tensorrt.dirpath}/static/tensorrt_{custom_version}/"
            mock_copytree.assert_called_once_with(
                expected_source_path,
                self.export_folder,
                dirs_exist_ok=True
            )

    def test_pybind_cloning_enabled(self):
        """Test export clones PyBind11 when python_binding=True using subprocess.run"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="model.onnx",
                python_binding=True
            )
            
            self.mock_subprocess.run.assert_called_once()

    def test_pybind_cloning_disabled(self):
        """Test export skips PyBind11 cloning when python_binding=False"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="model.onnx",
                python_binding=False
            )
            
            self.mock_subprocess.run.assert_not_called()

    def test_pybind_subprocess_command(self):
        """Test export uses correct git clone command for PyBind11"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="model.onnx",
                python_binding=True
            )
            
            expected_command = [
                "git", "clone", "--depth=1", 
                "https://github.com/pybind/pybind11.git", 
                f"{self.export_folder}/python_binding/pybind11"
            ]
            self.mock_subprocess.run.assert_called_once_with(expected_command, check=True)

    def test_pybind_subprocess_error_handling(self):
        """Test export handles subprocess.CalledProcessError during PyBind11 cloning"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree, \
             patch('builtins.print') as mock_print:
            
            from subprocess import CalledProcessError
            self.mock_subprocess.CalledProcessError = CalledProcessError
            self.mock_subprocess.run.side_effect = CalledProcessError(1, "git")
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview="model.onnx",
                python_binding=True
            )
            
            mock_print.assert_any_call("Error cloning PyBind11: Command 'git' returned non-zero exit status 1.")

    def test_missing_static_files_error(self):
        """Test export handles missing static TRT files gracefully"""
        with patch('aidge_export_tensorrt.shutil.copy') as mock_copy, \
             patch('aidge_export_tensorrt.os.rename') as mock_rename, \
             patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree:
            
            mock_copytree.side_effect = FileNotFoundError("No such file or directory")
            
            with self.assertRaises(FileNotFoundError):
                aidge_export_tensorrt.export(
                    export_folder=self.export_folder,
                    graphview="model.onnx"
                )

    def test_missing_onnx_file_error(self):
        """Test export handles missing ONNX input file appropriately"""
        with patch('aidge_export_tensorrt.shutil.copytree') as mock_copytree, \
             patch('aidge_export_tensorrt.shutil.copy') as mock_copy:
            
            mock_copy.side_effect = FileNotFoundError("No such file or directory")
            
            with self.assertRaises(FileNotFoundError):
                aidge_export_tensorrt.export(
                    export_folder=self.export_folder,
                    graphview="nonexistent.onnx"
                )


if __name__ == '__main__':
    unittest.main(verbosity=2) 