"""
Copyright (c) 2023 CEA-List

This program and the accompanying materials are made available under the
terms of the Eclipse Public License 2.0 which is available at
http://www.eclipse.org/legal/epl-2.0.

SPDX-License-Identifier: EPL-2.0
"""

PLUGIN_TRT_REGISTRY = {}


def plugin_trt_register(*args):
   
    key_list = [arg for arg in args]

    def decorator(operator):
        def wrapper(*args, **kwargs):
            return operator(*args, **kwargs)
        
        for key in key_list:
            PLUGIN_TRT_REGISTRY[key] = operator

        return wrapper
    return decorator

def supported_plugins():
    return list(PLUGIN_TRT_REGISTRY.keys())
