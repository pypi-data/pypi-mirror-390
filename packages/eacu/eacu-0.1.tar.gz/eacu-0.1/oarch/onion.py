"""
Onion - Base class for onion architecture

Provides usage similar to abc.ABC, users only need to inherit Onion to use the onion architecture pattern.
"""
from oarch.onion_meta import OnionMeta


class Onion(metaclass=OnionMeta):
    """
    Base class for onion architecture, providing dynamic abstract method resolution.
    
    Usage is similar to abc.ABC, users only need to inherit this class:
    
    class MyCore(Onion):
        @abc.abstractmethod
        def abstract_method(self):
            pass
    
    class MyImpl(MyCore):
        def abstract_method(self):
            return "implemented"
    
    # User is responsible for loading impls modules
    import impls
    
    # Manual compilation or automatic compilation
    MyCore.onionCompile()  # Manual compilation
    # or
    instance = MyCore()  # Automatically compiled at first instantiation
    """
    pass