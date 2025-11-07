import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from operators import plugin_trt_register, supported_plugins, PLUGIN_TRT_REGISTRY


class TestPluginRegistry(unittest.TestCase):
    
    def setUp(self):
        self.original_registry = PLUGIN_TRT_REGISTRY.copy()
        PLUGIN_TRT_REGISTRY.clear()
    
    def tearDown(self):
        PLUGIN_TRT_REGISTRY.clear()
        PLUGIN_TRT_REGISTRY.update(self.original_registry)
    
    def test_empty_registry(self):
        self.assertEqual(supported_plugins(), [])
    
    def test_single_plugin_registration(self):
        @plugin_trt_register("TestOp")
        def dummy_operator():
            return "test_result"
        
        self.assertIn("TestOp", PLUGIN_TRT_REGISTRY)
        self.assertTrue(callable(PLUGIN_TRT_REGISTRY["TestOp"]))
        self.assertEqual(PLUGIN_TRT_REGISTRY["TestOp"](), "test_result")
        self.assertEqual(supported_plugins(), ["TestOp"])
    
    def test_multiple_keys_registration(self):
        @plugin_trt_register("Add", "Addition", "Plus") 
        def add_operator():
            return "add_result"
        
        add_func = PLUGIN_TRT_REGISTRY["Add"]
        for key in ["Addition", "Plus"]:
            self.assertEqual(PLUGIN_TRT_REGISTRY[key], add_func)
            self.assertEqual(PLUGIN_TRT_REGISTRY[key](), "add_result")
            self.assertIn(key, supported_plugins())
        
        self.assertEqual(len(supported_plugins()), 3)
    
    def test_multiple_plugins(self):
        @plugin_trt_register("Conv2D")
        def conv_operator():
            return "conv_result"
        
        @plugin_trt_register("ReLU")  
        def relu_operator():
            return "relu_result"
        
        self.assertEqual(len(PLUGIN_TRT_REGISTRY), 2)
        
        for op, result in [("Conv2D", "conv_result"), ("ReLU", "relu_result")]:
            self.assertIn(op, PLUGIN_TRT_REGISTRY)
            self.assertEqual(PLUGIN_TRT_REGISTRY[op](), result)
            self.assertIn(op, supported_plugins())
    
    def test_decorated_function_callable(self):
        @plugin_trt_register("Multiply")
        def multiply_operator(a, b):
            return a * b
        
        self.assertEqual(multiply_operator(3, 4), 12)
        
        self.assertEqual(PLUGIN_TRT_REGISTRY["Multiply"](5, 6), 30)


if __name__ == '__main__':
    unittest.main()
