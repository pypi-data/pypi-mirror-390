import functools

import torch
import torch.nn as nn

import weakref

from typing import Mapping

class GenericModelHook:
    def init_hook(self, module):
        return module

    def pre_forward(self, module, *args, **kwargs):
        return args, kwargs
    
    def post_forward(self, module, output):
        return output
    
    def remove_hook(self, module):
        return module
    

class HookWrapper:
    def __init__(self, module: nn.Module, hook: GenericModelHook):
        self.module = module
        self.hook = hook
        self.original_forward = module.forward

    def forward_with_hook(self, *args, **kwargs):
        args, kwargs = self.hook.pre_forward(self.module, *args, **kwargs)
        output = self.original_forward(*args, **kwargs)
        return self.hook.post_forward(self.module, output)

    def restore_original_forward(self):
        self.module.forward = self.original_forward
        del self.module._hook_wrapper            


def attach_hook(module: nn.Module, hook: GenericModelHook):
    if hasattr(module, "_hook_wrapper"):
        raise RuntimeError("A hook is already attached to this module.")

    wrapper = HookWrapper(module, hook)
    module._hook_wrapper = wrapper

    def forward_with_hook(*args, **kwargs):
        return wrapper.forward_with_hook(*args, **kwargs)

    module.forward = functools.update_wrapper(
        forward_with_hook, module.forward.__func__
    )
    return wrapper

def detach_hook(module: nn.Module):
    if hasattr(module, "_hook_wrapper"):
        wrapper = module._hook_wrapper
        wrapper.restore_original_forward()
    else:
        print(f"No hook is attached to module {module}.")

def clear_hooks(module: nn.Module):
    if hasattr(module, "_local_hook"):
        module._local_hook.remove_hook(module)
        delattr(module, "_local_hook")

    if hasattr(module, "_original_forward"):
        # Overriding a GraphModuleImpl forward freezes the forward call and later modifications on the graph will fail.
        # Reference: https://pytorch.slack.com/archives/C3PDTEV8E/p1705929610405409
        if "GraphModuleImpl" in str(type(module)):
            module.__class__.forward = module._original_forward
        else:
            # print(module.forward)
            # print(id(module.forward))
            module.forward = module._original_forward
        delattr(module, "_original_forward")

    return module

def is_namedtuple(data):
    return isinstance(data, tuple) and hasattr(data, "_asdict") and hasattr(data, "_fields")

def honor_type(obj, generator):
    if is_namedtuple(obj):
        return type(obj)(*list(generator))
    else:
        return type(obj)(generator)

def to_device(input, device):
    if isinstance(input, torch.Tensor):
        return input.to(device)
    elif isinstance(input, (tuple, list)):
        return honor_type(input, (to_device(i, device) for i in input))
    elif isinstance(input, Mapping):
        return type(input)({k: to_device(i, device) for k, i in input.items()})
    else:
        return input

class InputsToHook(GenericModelHook):
    def __init__(self, device):
        self.device = device

    def pre_forward(self, module, *args, **kwargs):
        return to_device(args, self.device), to_device(kwargs, self.device)