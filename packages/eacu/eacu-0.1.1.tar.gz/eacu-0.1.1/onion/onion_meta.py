"""
OnionMeta: A Python metaclass for dynamic abstract method resolution
Implements the onion architecture pattern, decoupling core business logic from implementations
"""

import abc
import warnings
from typing import Dict, List, Type, Any, Optional


class OnionMeta(abc.ABCMeta):
    """
    Onion Architecture Metaclass
    
    This metaclass implements the "Construction & Binding" (C&B) process, dynamically
    collecting and integrating methods from all implementation submodules at first instantiation.
    """
    
    # Attribute section: all lowercase and private
    __onion_subs__ = []  # Registry of subclasses
    __onion_built__ = False  # Initialization flag
    
    # Internal methods: private methods starting with _
    # Note: impls loading is user responsibility, no auto-loading provided
    
    def __onion_get__onion_subs__(cls) -> List[Type]:
        """Retrieve all registered non-abstract subclasses"""
        subs = list(cls.__onion_subs__)
        # [DEBUG] found {len(subs)} subclasses
        return subs

    def __onion_get_all_subs(cls) -> List[Type]:
        """
        递归收集 cls 及其所有 OnionMeta 基类的 __onion_subs__
        返回一个 去重+保持顺序 的列表
        """
        seen = set()
        subs = []
        # 按 MRO 顺序，保证离 cls 越近的优先
        for base in cls.__mro__:
            if isinstance(base, OnionMeta) and hasattr(base, '__onion_subs__'):
                for sub in base.__onion_subs__:
                    if sub not in seen:
                        seen.add(sub)
                        subs.append(sub)
        return subs
    
    def __onion_get_meths(cls, subs: List[Type], warns: List[str]) -> Dict[str, Any]:
        """Collect method implementations from subclasses"""
        meths = {}
        srcs = {}  # Track source of each method
        attrs = {}  # Track class attributes that need to be copied

        for sub in subs:
            # Collect abstract method/property implementations
            for meth_name in cls.__abstractmethods__:
                if hasattr(sub, meth_name):
                    meth = getattr(sub, meth_name)
                    # Check if it's concretely implemented (not abstract)
                    if not getattr(meth, '__isabstractmethod__', False):
                        if meth_name in meths:
                            warns.append(
                                f"Method conflict: {meth_name} implemented in both {sub.__name__} "
                                f"and {srcs[meth_name]}, using {sub.__name__}'s implementation"
                            )
                        else:
                            srcs[meth_name] = sub.__name__
                        
                        meths[meth_name] = meth
            
            # Collect class attributes that are used by the implementation
            # Only collect attributes that are defined in the subclass (not inherited)
            for attr_name in sub.__dict__:
                attr_val = sub.__dict__[attr_name]
                # Skip special attributes and methods
                if attr_name.startswith('__') and attr_name.endswith('__'):
                    continue
                if callable(attr_val) or isinstance(attr_val, property):
                    continue
                # Skip ABC-related attributes
                if attr_name.startswith('_abc'):
                    continue

                if attr_name in attrs and attrs[attr_name] != attr_val:
                    warns.append(
                        f"Attribute conflict: {attr_name} defined differently in {sub.__name__} "
                        f"and previous implementation, using {sub.__name__}'s value"
                    )
                attrs[attr_name] = attr_val
        
        #DEBUG collected {len(meths)} methods and {len(attrs)} attributes from {len(subs)} subclasses
        return meths, attrs
    
    def __onion_merge_meths(cls, meths: Dict[str, Any], attrs: Dict[str, Any], warns: List[str]):
        """Merge method implementations and attributes into core class"""
        # Merge methods and properties
        for meth_name, meth in meths.items():
            setattr(cls, meth_name, meth)
            #DEBUG merged method: {meth_name}
        
        # Merge class attributes
        for attr_name, attr_val in attrs.items():
            setattr(cls, attr_name, attr_val)
            #DEBUG merged attribute: {attr_name} = {attr_val}
    
    def __onion_handle_warns(cls, warns: List[str]):
        """Handle warning messages"""
        for warn in warns:
            warnings.warn(warn, RuntimeWarning)
            # [DEBUG] warning: {warn}
    
    def __onion_raise_errs(cls, errs: List[str]):
        """Handle compilation errors"""
        err_msg = f"Failed to compile class '{cls.__name__}':\n" + "\n".join(f"- {err}" for err in errs)
        # [DEBUG] compile errors: {err_msg}
        raise TypeError(err_msg)

    def __onion_compile(cls):
        """
        Construction & Binding (C&B) 核心流程
        升级点：通过 __onion_get_all_subs 把兄弟核心类的实现也拉进来
        """
        errs, warns = [], []

        # 1. 收集所有相关实现子类（新增）
        subs = cls.__onion_get_all_subs()
        # [DEBUG] compiling {cls.__name__}, collected subs: {[s.__name__ for s in subs]}

        if not subs:
            errs.append(f"No implementation subclasses found for {cls.__name__}")
            cls.__onion_raise_errs(errs)
            return

        # 2. 收集方法与属性（复用原有逻辑）
        meths, attrs = cls.__onion_get_meths(subs, warns)

        # 3. 检查是否还有未实现的抽象方法
        miss_meths = cls.__abstractmethods__ - set(meths.keys())
        if miss_meths:
            errs.append(f"Missing implementations for abstract methods: {miss_meths}")
            cls.__onion_raise_errs(errs)
            return

        # 4. 合并到核心类（复用原有逻辑）
        cls.__onion_merge_meths(meths, attrs, warns)

        # 5. 发出警告（复用原有逻辑）
        if warns:
            cls.__onion_handle_warns(warns)
    
    # Public API: methods for external use
    def onionCompile(cls):
        """
        Manually trigger Construction & Binding (C&B) process
        
        Should be called after user loads impls modules, or rely on auto-trigger at first instantiation
        
        :param: None
        
        :raises: TypeError: If compilation fails (missing implementation subclasses or abstract methods)
        :warns: RuntimeWarning: For warning situations like method conflicts
        
        :usage:
            # User responsible for loading impls
            import impls
            # Manually trigger compilation
            MyCoreClass.onionCompile()
        """
        if not getattr(cls, '__onion_built__', False):
            cls.__onion_compile()
            cls.__onion_built__ = True
            
            # Recalculate abstract methods
            if hasattr(abc, 'update_abstractmethods'):
                abc.update_abstractmethods(cls)
                # [DEBUG] manually updated abstractmethods for {cls.__name__}
        else:
            # [DEBUG] {cls.__name__} already compiled, skipping
            pass
    
    # Magic methods section
    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)

        # Initialize subclass registry (only on core class)
        if not hasattr(cls, '__onion_subs__'):
            cls.__onion_subs__ = []

        # Register all subclasses that inherit from Onion classes
        # This allows partial implementations to be collected and merged
        for base in bases:
            if isinstance(base, OnionMeta) and hasattr(base, '__onion_subs__'):
                # Register all subclasses, including partial implementations
                if cls.__name__ != base.__name__:  # Avoid self-registration
                    base.__onion_subs__.append(cls)
                    #DEBUG registered subclass: {cls.__name__} to {base.__name__}
    
    def __call__(cls, *args, **kwargs):
        """
        Intercept first instantiation to trigger C&B process
        
        Uses __onion_built__ flag to ensure C&B runs only once
        """
        if not getattr(cls, '__onion_built__', False):
            cls.__onion_compile()
            cls.__onion_built__ = True
            
            # Recalculate abstract methods
            if hasattr(abc, 'update_abstractmethods'):
                abc.update_abstractmethods(cls)
                # [DEBUG] updated abstractmethods for {cls.__name__}
        
        return super().__call__(*args, **kwargs)
