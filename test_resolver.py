"""
Test file for NuxtContentResolver functionality.

This module contains examples with cross-references to test the resolver.
"""

import typing as t
from dataclasses import dataclass


@dataclass
class ExampleClass:
    """
    An example class for testing resolver functionality.
    
    This class demonstrates cross-references to other classes and modules.
    See also: ExampleSubclass, utils.helper_function
    
    **Arguments**:
    
    - `name: str` - The name of the example
    - `value: int` - A numeric value
    
    **Examples**:
    
    ```python
    # Create an instance
    example = ExampleClass("test", 42)
    
    # Use with helper function
    result = utils.helper_function(example)
    ```
    
    **Notes**:
    
    This class is part of the test suite for the NuxtContentResolver.
    References to `utils.helper_function` should be converted to 
    `/references/utils/helper_function` paths.
    """
    
    name: str
    value: int
    
    def process(self) -> str:
        """
        Process the example data.
        
        **Returns**:
        
        The processed string representation.
        
        **Raises**:
        
        - `ValueError`: If name is empty
        - `TypeError`: If value is not an integer
        
        See: ExampleSubclass.advanced_process for more complex processing.
        """
        if not self.name:
            raise ValueError("Name cannot be empty")
        
        if not isinstance(self.value, int):
            raise TypeError("Value must be an integer")
        
        return f"{self.name}: {self.value}"


class ExampleSubclass(ExampleClass):
    """
    A subclass extending ExampleClass functionality.
    
    This class adds advanced processing capabilities.
    Inherits from: ExampleClass
    
    **Arguments**:
    
    - `name: str` - Inherited from ExampleClass
    - `value: int` - Inherited from ExampleClass  
    - `multiplier: float` - Additional multiplier for calculations
    
    **Examples**:
    
    ```python
    # Advanced usage
    advanced = ExampleSubclass("advanced", 100, 1.5)
    result = advanced.advanced_process()
    ```
    """
    
    def __init__(self, name: str, value: int, multiplier: float = 1.0):
        super().__init__(name, value)
        self.multiplier = multiplier
    
    def advanced_process(self) -> str:
        """
        Advanced processing with multiplier.
        
        **Returns**:
        
        The processed string with multiplied value.
        
        **Notes**:
        
        This method extends the functionality of ExampleClass.process.
        """
        base_result = self.process()
        multiplied_value = self.value * self.multiplier
        return f"{base_result} (multiplied: {multiplied_value})"


def helper_function(example: ExampleClass) -> dict:
    """
    A helper function for processing examples.
    
    **Arguments**:
    
    - `example: ExampleClass` - The example instance to process
    
    **Returns**:
    
    A dictionary with processed data.
    
    **Examples**:
    
    ```python
    example = ExampleClass("test", 42)
    data = helper_function(example)
    print(data)
    ```
    
    **See Also**:
    
    - ExampleClass.process: For basic processing
    - ExampleSubclass.advanced_process: For advanced processing
    """
    return {
        "processed": example.process(),
        "name": example.name,
        "value": example.value,
        "type": type(example).__name__
    }
