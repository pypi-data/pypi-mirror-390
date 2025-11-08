from oarch.onion import Onion
from oarch.onion_meta import OnionMeta
from abc import abstractmethod

__all__ = ['Onion', 'OnionMeta', 'abstractmethod']


if __name__ == '__main__':
    """
    Quick demo of oarch onion architecture framework.
    
    This example shows how to define an abstract core class and 
    implement it through separate implementation classes.
    """
    from abc import abstractmethod
    
    # Define abstract core class with onion metaclass
    class Calculator(Onion):
        @abstractmethod
        def add(self, a, b):
            """Abstract method for addition operation"""
            pass
        
        @abstractmethod
        def sub(self, a, b):
            """Abstract method for subtraction operation"""
            pass
    
    # Implementation class providing concrete methods
    class BasicCalculator(Calculator):
        def add(self, a, b):
            print(f"[DEBUG] BasicCalculator.add({a}, {b})")  # Debug output: method call trace
            return a + b
        
        def sub(self, a, b):
            print(f"[DEBUG] BasicCalculator.sub({a}, {b})")  # Debug output: method call trace
            return a - b
    
    # Advanced implementation with additional functionality
    class ScientificCalculator(Calculator):
        def add(self, a, b):
            print(f"[DEBUG] ScientificCalculator.add({a}, {b})")  # Debug output: method call trace
            return a + b
        
        def sub(self, a, b):
            print(f"[DEBUG] ScientificCalculator.sub({a}, {b})")  # Debug output: method call trace  
            return a - b
    
    '''
    You can import BasicCalculator or ScientificCalculator to use different implementations.
    In here, we define both BasicCalculator and ScientificCalculator. This will cause a warning, and shouldn't be imported together in production.
    
    ** Note:
    This is an engineering-level dynamic feature selection mechanism; therefore, it does not support runtime switching of implementation classes. If you need such behavior, consider using the 'pluggy'.
    '''


    # Create instance and test functionality
    print("=== oarch Onion Architecture Demo ===")
    calc = Calculator()
    
    print("\nTesting basic operations:")
    result1 = calc.add(10, 5)
    print(f"10 + 5 = {result1}")
    
    result2 = calc.sub(10, 5)
    print(f"10 - 5 = {result2}")
    
    print("\n=== Demo completed successfully ===")
    