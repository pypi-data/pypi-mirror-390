import retracesoftware.functional as functional
import retracesoftware.utils as utils
from retracesoftware.proxy.thread import start_new_thread_wrapper
import threading
import importlib
from retracesoftware.install.typeutils import modify, WithFlags, WithoutFlags

from retracesoftware.install.typeutils import modify

class Phase:
    def __init__(self, name):
        self.name = name

    def patch(self, obj):
        return obj

    def patch_with_config(self, config, obj):
        return obj

    def __call__(self, config):
        if isinstance(config, str):
            return {config: self.patch}
        elif isinstance(config, list):
            return {key: self.patch for key in config}
        elif isinstance(config, dict):
            return {key: lambda obj: self.patch_with_config(value, obj) for key,value in config.items()}
        else:
            raise Exception(f'Unhandled config type: {config}')

class SimplePhase(Phase):
    def __init__(self, name, patch):
        super().__init__(name)
        self.patch = patch

class DisablePhase(Phase):
    def __init__(self, thread_state):
        super().__init__('disable')
        self.thread_state = thread_state

    def patch(self, obj):
        return self.thread_state.wrap('disabled', obj)

class TryPatchPhase(Phase):
    def __init__(self, patcher):
        super().__init__('try_patch')
        self.patcher = patcher

    def patch(self, obj):
        try:
            return self.patcher(obj)
        except:
            return obj

class PatchTypesPhase(Phase):
    def __init__(self, patcher):
        super().__init__('patch_types')
        self.patcher = patcher
    
    def patch(self, obj):
        if not isinstance(obj, type):
            raise Exception("TODO")

        self.patcher(obj)
        return obj

class ImmutableTypePhase(Phase):

    def __init__(self, types):
        super().__init__('immutable')
        self.types = types

    def patch(self, obj):
        if not isinstance(obj, type):
            raise Exception("TODO")

        self.types.add(obj)
        return obj

class PatchThreadPhase(Phase):
    def __init__(self, thread_state, on_exit):
        super().__init__('patch_start_new_thread')
        self.thread_state = thread_state
        self.on_exit = on_exit

    def patch(self, obj):
        return start_new_thread_wrapper(thread_state = self.thread_state, 
                                        on_exit = self.on_exit,
                                        start_new_thread = obj)

def resolve(path):
    module, sep, name = path.rpartition('.')
    if module == None: module = 'builtins'
    
    return getattr(importlib.import_module(module), name)

class WrapPhase(Phase):
    def __init__(self):
        super().__init__('wrap')

    def patch_with_config(self, wrapper, obj):
        return resolve(wrapper)(obj)

class PatchClassPhase(Phase):
    def __init__(self):
        super().__init__('patch_class')

    def patch_with_config(self, config, cls):

        patchers = utils.map_values(resolve, config)

        assert cls is not None

        with WithoutFlags(cls, "Py_TPFLAGS_IMMUTABLETYPE"):
            for name,func in patchers.items():                
                utils.update(cls, name, func)

        return cls

class ProxyWrapPhase(Phase):
    def __init__(self):
        super().__init__('wrap_proxy')

    def patch_with_config(self, config, cls):

        patchers = utils.map_values(resolve, config)
        
        def patch(proxytype):
            for name,func in patchers.items():
                utils.update(proxytype, name, func)

        cls.__retrace_patch_proxy__ = patch

        return cls
        # return resolve(wrapper)(obj)

class TypeAttributesPhase(Phase):

    def __init__(self, patcher):
        super().__init__('type_attributes')
        self.patcher = patcher

    def patch_with_config(self, config, cls):
        # print(f'TypeAttributesPhase: {config} {cls}')
        if not isinstance(cls, type):
            raise Exception("TODO")

        with modify(cls):
            for phase_name,values in config.items():
                for attribute_name,func in self.patcher.find_phase(phase_name)(values).items():
                    utils.update(cls, attribute_name, func)

        return cls

class PerThread(threading.local):
    def __init__(self):
        self.internal = utils.counter()
        self.external = utils.counter()

class PatchHashPhase(Phase):

    def __init__(self, thread_state):
        super().__init__('patch_hash')

        per_thread = PerThread()
        
        self.hashfunc = thread_state.dispatch(
            functional.constantly(None),
            internal = functional.repeatedly(functional.partial(getattr, per_thread, 'internal')),
            external = functional.repeatedly(functional.partial(getattr, per_thread, 'external')))

    def patch(self, obj):
        if not isinstance(obj, type):
            raise Exception("TODO")

        utils.patch_hash(cls = obj, hashfunc = self.hashfunc)
        return obj
