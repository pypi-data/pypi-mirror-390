"""
Tests for file generation functionality in aidge_export_tensorrt.
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import aidge_export_tensorrt
from aidge_export_tensorrt.generate_plugin import generate_plugin


class TestFileGeneration(unittest.TestCase):
    """Base test class for file generation"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="aidge_test_")
        self.template_dir = os.path.join(self.test_dir, "templates")
        self.output_dir = os.path.join(self.test_dir, "output")
        
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.original_dirpath = aidge_export_tensorrt.dirpath
        
        self._create_test_template()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        aidge_export_tensorrt.dirpath = self.original_dirpath
    
    def _create_test_template(self):
        template_content = "Test: {{ test_var }}"
        
        template_path = os.path.join(self.template_dir, "test_template.jinja")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        self.test_template = template_path


class TestGenerateFileFunction(TestFileGeneration):
    """Tests for generate_file() function"""
    
    def test_directory_creation(self):
        """Test directory creation with nested paths"""
        nested_dir = os.path.join(self.output_dir, 'level1', 'level2', 'level3')
        output_file = os.path.join(nested_dir, 'test_output.txt')
        
        self.assertFalse(os.path.exists(nested_dir))
        
        aidge_export_tensorrt.generate_file(
            filename=output_file,
            templatename=self.test_template,
            test_var="test"
        )
        
        self.assertTrue(os.path.exists(nested_dir))
        
        level1_dir = os.path.join(self.output_dir, 'level1')
        level2_dir = os.path.join(self.output_dir, 'level1', 'level2')
        
        self.assertTrue(os.path.exists(level1_dir))
        self.assertTrue(os.path.exists(level2_dir))
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.exists(output_file))
    
    def test_basic_integration(self):
        """Test basic template rendering and file writing"""
        output_file = os.path.join(self.output_dir, 'integration_test.txt')
        
        aidge_export_tensorrt.generate_file(
            filename=output_file,
            templatename=self.test_template,
            test_var="integration"
        )
        
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertTrue(len(content) > 0)
        self.assertIn("integration", content)
    
    def test_template_path_parsing(self):
        """Test template path parsing with nested directories"""
        nested_template_dir = os.path.join(self.template_dir, "subdir")
        os.makedirs(nested_template_dir, exist_ok=True)
        
        nested_template_path = os.path.join(nested_template_dir, "nested_template.jinja")
        with open(nested_template_path, 'w', encoding='utf-8') as f:
            f.write("Nested: {{ value }}")
        
        output_file = os.path.join(self.output_dir, 'path_test.txt')
        
        aidge_export_tensorrt.generate_file(
            filename=output_file,
            templatename=nested_template_path,
            value="parsed"
        )
        
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("parsed", content)
    
    def test_generate_file_error_cases(self):
        """Test error handling for invalid templates"""
        output_file = os.path.join(self.output_dir, 'error_test.txt')
        
        with self.assertRaises(Exception):
            aidge_export_tensorrt.generate_file(
                filename=output_file,
                templatename="/non/existent/template.jinja",
                test_var="test"
            )
        
        self.assertFalse(os.path.exists(output_file))


class TestGeneratePluginFunction(TestFileGeneration):
    """Tests for generate_plugin() function"""
    
    def setUp(self):
        super().setUp()
        aidge_export_tensorrt.dirpath = self.template_dir
        self._create_plugin_templates()
    
    def _create_plugin_templates(self):
        header_template = """// Header for {{ name_plugin }}
class {{ name_plugin }}Plugin {};"""
        
        header_path = os.path.join(self.template_dir, "plugin_header.jinja")
        with open(header_path, 'w', encoding='utf-8') as f:
            f.write(header_template)
        
        source_template = """// Source for {{ name_plugin }}
void {{ name_plugin }}Plugin::execute() {};"""
        
        source_path = os.path.join(self.template_dir, "plugin_src.jinja")
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(source_template)
    
    def test_generate_plugin_file_paths(self):
        """Test file path generation for plugin files"""
        plugin_name = "TestPlugin"
        
        generate_plugin(plugin_name, self.output_dir)
        
        expected_hpp = os.path.join(self.output_dir, "plugins", "testplugin", "testplugin_plugin.hpp")
        expected_cu = os.path.join(self.output_dir, "plugins", "testplugin", "testplugin_plugin.cu")
        
        self.assertTrue(os.path.exists(expected_hpp))
        self.assertTrue(os.path.exists(expected_cu))
    
    def test_generate_plugin_directory_structure(self):
        """Test plugin directory structure creation"""
        plugin_name = "DirectoryTest"
        
        generate_plugin(plugin_name, self.output_dir)
        
        expected_plugin_dir = os.path.join(self.output_dir, "plugins", "directorytest")
        self.assertTrue(os.path.exists(expected_plugin_dir))
        
        plugins_dir = os.path.join(self.output_dir, "plugins")
        self.assertTrue(os.path.exists(plugins_dir))
    
    def test_plugin_name_lowercasing(self):
        """Test plugin name gets converted to lowercase"""
        plugin_name = "MixedCasePlugin"
        
        generate_plugin(plugin_name, self.output_dir)
        
        expected_dir = os.path.join(self.output_dir, "plugins", "mixedcaseplugin")
        self.assertTrue(os.path.exists(expected_dir))
        
        expected_hpp = os.path.join(expected_dir, "mixedcaseplugin_plugin.hpp")
        expected_cu = os.path.join(expected_dir, "mixedcaseplugin_plugin.cu")
        
        self.assertTrue(os.path.exists(expected_hpp))
        self.assertTrue(os.path.exists(expected_cu))
    
    def test_plugin_template_path_construction(self):
        """Test template path construction"""
        plugin_name = "PathTest"
        
        expected_header_template = os.path.join(self.template_dir, "plugin_header.jinja")
        expected_source_template = os.path.join(self.template_dir, "plugin_src.jinja")
        
        self.assertTrue(os.path.exists(expected_header_template))
        self.assertTrue(os.path.exists(expected_source_template))
        
        try:
            generate_plugin(plugin_name, self.output_dir)
            template_paths_correct = True
        except Exception:
            template_paths_correct = False
        
        self.assertTrue(template_paths_correct)
        
        expected_hpp = os.path.join(self.output_dir, "plugins", "pathtest", "pathtest_plugin.hpp")
        expected_cu = os.path.join(self.output_dir, "plugins", "pathtest", "pathtest_plugin.cu")
        
        self.assertTrue(os.path.exists(expected_hpp))
        self.assertTrue(os.path.exists(expected_cu))
    
    def test_plugin_dual_file_creation(self):
        """Test creation of both .hpp and .cu files"""
        plugin_name = "DualFileTest"
        
        generate_plugin(plugin_name, self.output_dir)
        
        plugin_dir = os.path.join(self.output_dir, "plugins", "dualfiletest")
        hpp_file = os.path.join(plugin_dir, "dualfiletest_plugin.hpp")
        cu_file = os.path.join(plugin_dir, "dualfiletest_plugin.cu")
        
        self.assertTrue(os.path.exists(hpp_file))
        self.assertTrue(os.path.exists(cu_file))
        
        with open(hpp_file, 'r', encoding='utf-8') as f:
            hpp_content = f.read()
        with open(cu_file, 'r', encoding='utf-8') as f:
            cu_content = f.read()
        
        self.assertTrue(len(hpp_content) > 0)
        self.assertTrue(len(cu_content) > 0)
        
        self.assertIn("DualFileTest", hpp_content)
        self.assertIn("DualFileTest", cu_content)


if __name__ == '__main__':
    unittest.main(verbosity=2) 