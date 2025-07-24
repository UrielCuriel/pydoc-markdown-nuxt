"""
Example module to test comprehensive MDC processing
"""

def comprehensive_example_function(data, format_type="json", validate=True):
    """
    A comprehensive example function with multiple docstring sections.
    
    **Arguments**:
    
    - `data` - Input data to process
    - `format_type: str` - Output format (json, xml, yaml)
    - `validate: bool` - Whether to validate input
    
    **Returns**:
    
    Processed data in the specified format as a string.
    
    **Examples**:
    
    ```python
    # Basic usage
    result = comprehensive_example_function({"key": "value"})
    print(result)
    ```
    
    ```bash
    # Command line usage
    python example.py --data input.json --format json
    ```
    
    **Notes**:
    
    This function is optimized for performance. Consider caching results 
    for repeated calls with the same parameters.
    
    **Warnings**:
    
    Large datasets may consume significant memory. Monitor memory usage
    for datasets larger than 1GB.
    
    **Raises**:
    
    - `ValueError`: When format_type is not supported
    - `TypeError`: When data cannot be serialized
    - `MemoryError`: When data is too large to process
    """
    pass
