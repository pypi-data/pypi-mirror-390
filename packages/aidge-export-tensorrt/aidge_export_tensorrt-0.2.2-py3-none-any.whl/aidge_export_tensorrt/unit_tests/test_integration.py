"""
Integration tests for aidge_export_tensorrt.

These tests provide end-to-end validation of the export functionality,
combining the fast unit test approach with real-world integration testing.
"""

import unittest
import sys
import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import aidge_export_tensorrt


class TestExportIntegration(unittest.TestCase):
    """Integration tests for end-to-end export functionality"""
    
    def setUp(self):
        """Set up test environment for integration tests"""
        self.test_dir = tempfile.mkdtemp(prefix="aidge_integration_test_")
        self.export_folder = os.path.join(self.test_dir, "export_output")
        self.original_dirpath = aidge_export_tensorrt.dirpath
        
        self.test_static_dir = os.path.join(self.test_dir, "static")
        os.makedirs(os.path.join(self.test_static_dir, "tensorrt_10.10"), exist_ok=True)
        os.makedirs(os.path.join(self.test_static_dir, "tensorrt_8.6"), exist_ok=True)
        
        self._create_dummy_static_files()
        aidge_export_tensorrt.dirpath = self.test_dir
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        aidge_export_tensorrt.dirpath = self.original_dirpath
    
    def _create_dummy_static_files(self):
        """Create dummy static files to simulate TensorRT static content"""
        trt_10_dir = os.path.join(self.test_static_dir, "tensorrt_10.10")
        with open(os.path.join(trt_10_dir, "dummy_lib.so"), 'w') as f:
            f.write("dummy library content")
        
        trt_8_dir = os.path.join(self.test_static_dir, "tensorrt_8.6")
        with open(os.path.join(trt_8_dir, "dummy_lib.so"), 'w') as f:
            f.write("dummy library content")
    
    def _create_dummy_onnx_file(self, filename="test_model.onnx"):
        """Create a dummy ONNX file for testing"""
        dummy_onnx_content = b"""dummy onnx content for testing"""
        onnx_path = os.path.join(self.test_dir, filename)
        with open(onnx_path, 'wb') as f:
            f.write(dummy_onnx_content)
        return onnx_path
    
    def test_end_to_end_export_with_onnx_file(self):
        """Test complete export workflow with ONNX file input"""
        onnx_file = self._create_dummy_onnx_file("integration_test.onnx")
        
        aidge_export_tensorrt.export(
            export_folder=self.export_folder,
            graphview=onnx_file,
            trt_version="10.10",
            python_binding=False
        )
        
        expected_model_path = os.path.join(self.export_folder, "model.onnx")
        expected_static_file = os.path.join(self.export_folder, "dummy_lib.so")
        
        self.assertTrue(os.path.exists(self.export_folder))
        self.assertTrue(os.path.exists(expected_model_path))
        self.assertTrue(os.path.exists(expected_static_file))
        self.assertTrue(os.path.isdir(self.export_folder))
    
    def test_end_to_end_export_with_graphview(self):
        """Test complete export workflow with GraphView input"""
        with mock.patch('aidge_export_tensorrt.aidge_core') as mock_core, \
             mock.patch('aidge_export_tensorrt.aidge_onnx') as mock_onnx:
            
            class MockGraphView:
                pass
            
            mock_graphview = MockGraphView()
            mock_core.GraphView = MockGraphView
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview=mock_graphview,
                trt_version="8.6",
                python_binding=False
            )
            
            mock_onnx.export_onnx.assert_called_once_with(
                mock_graphview, f"{self.export_folder}/model.onnx"
            )
            
            expected_static_file = os.path.join(self.export_folder, "dummy_lib.so")
            self.assertTrue(os.path.exists(self.export_folder))
            self.assertTrue(os.path.exists(expected_static_file))
    
    def test_pybind11_integration(self):
        """Test PyBind11 cloning integration"""
        onnx_file = self._create_dummy_onnx_file("pybind_test.onnx")
        
        with mock.patch('aidge_export_tensorrt.subprocess') as mock_subprocess:
            mock_subprocess.run.return_value = mock.MagicMock(returncode=0)
            
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview=onnx_file,
                python_binding=True
            )
            
            mock_subprocess.run.assert_called_once()
            
            call_args = mock_subprocess.run.call_args[0][0]
            self.assertIn("git", call_args)
            self.assertIn("clone", call_args)
            self.assertIn("pybind11", call_args[4])
            
            self.assertTrue(os.path.exists(self.export_folder))
    
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios"""
        non_existent_file = os.path.join(self.test_dir, "nonexistent.onnx")
        
        with self.assertRaises(FileNotFoundError):
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview=non_existent_file
            )
        
        with mock.patch('builtins.print') as mock_print:
            aidge_export_tensorrt.export(
                export_folder=self.export_folder,
                graphview=12345
            )
            
            mock_print.assert_any_call("The model should be a GraphView or an onnx file.")
    
    def test_tensorrt_version_integration(self):
        """Test TensorRT version handling in integration"""
        onnx_file = self._create_dummy_onnx_file("version_test.onnx")
        
        aidge_export_tensorrt.export(
            export_folder=self.export_folder,
            graphview=onnx_file,
            python_binding=False
        )
        
        expected_static_file = os.path.join(self.export_folder, "dummy_lib.so")
        self.assertTrue(os.path.exists(expected_static_file))
        
        shutil.rmtree(self.export_folder)
        
        aidge_export_tensorrt.export(
            export_folder=self.export_folder,
            graphview=onnx_file,
            trt_version="8.6",
            python_binding=False
        )
        
        expected_static_file = os.path.join(self.export_folder, "dummy_lib.so")
        self.assertTrue(os.path.exists(expected_static_file))
    
    def test_file_generation_integration(self):
        """Test file generation functionality in integration"""
        template_content = "Test template: {{ test_var }}"
        template_path = os.path.join(self.test_dir, "test_template.jinja")
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        output_file = os.path.join(self.export_folder, "generated_file.txt")
        
        aidge_export_tensorrt.generate_file(
            filename=output_file,
            templatename=template_path,
            test_var="integration_test"
        )
        
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("integration_test", content)


class TestExportRealWorldScenarios(unittest.TestCase):
    """Real-world scenario tests for export functionality"""
    
    def setUp(self):
        """Set up test environment for real-world scenarios"""
        self.test_dir = tempfile.mkdtemp(prefix="aidge_realworld_test_")
        self.export_folder = os.path.join(self.test_dir, "export_output")
        self.original_dirpath = aidge_export_tensorrt.dirpath
        
        self.test_static_dir = os.path.join(self.test_dir, "static")
        os.makedirs(os.path.join(self.test_static_dir, "tensorrt_10.10"), exist_ok=True)
        
        with open(os.path.join(self.test_static_dir, "tensorrt_10.10", "dummy_lib.so"), 'w') as f:
            f.write("dummy library content")
        
        aidge_export_tensorrt.dirpath = self.test_dir
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        aidge_export_tensorrt.dirpath = self.original_dirpath
    
    def test_concurrent_export_operations(self):
        """Test multiple concurrent export operations"""
        import threading
        import time
        
        results = []
        errors = []
        
        def export_operation(thread_id):
            try:
                onnx_file = os.path.join(self.test_dir, f"concurrent_test_{thread_id}.onnx")
                with open(onnx_file, 'wb') as f:
                    f.write(f"dummy onnx content for thread {thread_id}".encode())
                
                export_folder = os.path.join(self.export_folder, f"thread_{thread_id}")
                
                aidge_export_tensorrt.export(
                    export_folder=export_folder,
                    graphview=onnx_file,
                    python_binding=False
                )
                
                results.append(thread_id)
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=export_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(results), 3, f"Expected 3 successful operations, got {len(results)}")
        self.assertEqual(len(errors), 0, f"Expected 0 errors, got {len(errors)}: {errors}")
        
        for thread_id in range(3):
            thread_export_folder = os.path.join(self.export_folder, f"thread_{thread_id}")
            self.assertTrue(os.path.exists(thread_export_folder))
    
    def test_large_file_handling(self):
        """Test handling of large ONNX files"""
        large_onnx_file = os.path.join(self.test_dir, "large_model.onnx")
        
        large_content = b"dummy content " * 65536
        with open(large_onnx_file, 'wb') as f:
            f.write(large_content)
        
        aidge_export_tensorrt.export(
            export_folder=self.export_folder,
            graphview=large_onnx_file,
            python_binding=False
        )
        
        expected_model_path = os.path.join(self.export_folder, "model.onnx")
        
        self.assertTrue(os.path.exists(self.export_folder))
        self.assertTrue(os.path.exists(expected_model_path))
        
        original_size = os.path.getsize(large_onnx_file)
        copied_size = os.path.getsize(expected_model_path)
        self.assertEqual(original_size, copied_size)


if __name__ == '__main__':
    unittest.main(verbosity=2) 