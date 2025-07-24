#!/usr/bin/env python3
"""
Demonstration of pydoc-markdown-nuxt with custom components

This script shows how to use the new variables and arguments components,
as well as the configurable MDC component system.
"""

from pydoc_markdown_nuxt import (
    create_mdc_variables,
    create_mdc_arguments, 
    create_variable_or_argument_component,
    NuxtContentHelper
)

def demo_variables_component():
    """Demonstrate the variables component."""
    variables = [
        {
            "name": "`starting_after`",
            "type": "`string`", 
            "content": "The last ID on the page you're currently on when you want to fetch the next page."
        },
        {
            "name": "`ending_before`",
            "type": "`string`",
            "content": "The first ID on the page you're currently on when you want to fetch the previous page."
        },
        {
            "name": "`limit`",
            "type": "`integer`",
            "content": "Limit the number of items returned."
        }
    ]
    
    # Using default Nuxt UI component
    variables_content = create_mdc_variables(variables)
    print("Variables component (default UVariables):")
    print(variables_content)
    print("\n" + "="*50 + "\n")
    
    # Using custom component
    variables_content_custom = create_mdc_variables(variables, component="CustomVariables")
    print("Variables component (custom component):")
    print(variables_content_custom)
    print("\n" + "="*50 + "\n")


def demo_arguments_component():
    """Demonstrate the arguments component."""
    arguments = [
        {
            "name": "`data`",
            "type": "`dict`",
            "content": "The data to be processed by the function."
        },
        {
            "name": "`options`",
            "type": "`dict, optional`",
            "content": "Additional options for processing. Defaults to an empty dict."
        },
        {
            "name": "`validate`",
            "type": "`bool`",
            "content": "Whether to validate the input data. Defaults to True."
        }
    ]
    
    # Using default component
    arguments_content = create_mdc_arguments(arguments)
    print("Arguments component (default UArguments):")
    print(arguments_content)
    print("\n" + "="*50 + "\n")


def demo_generic_component():
    """Demonstrate the generic variable_or_argument_component function."""
    items = [
        {
            "name": "`api_key`",
            "type": "`string`",
            "content": "Your API key for authentication."
        },
        {
            "name": "`timeout`",
            "type": "`integer`",
            "content": "Request timeout in seconds. Defaults to 30."
        }
    ]
    
    # Create variables component
    variables_content = create_variable_or_argument_component(items, "variables")
    print("Generic function - Variables:")
    print(variables_content)
    print("\n" + "="*50 + "\n")
    
    # Create arguments component
    arguments_content = create_variable_or_argument_component(items, "arguments")
    print("Generic function - Arguments:")
    print(arguments_content)
    print("\n" + "="*50 + "\n")


def demo_nuxt_content_helper():
    """Demonstrate the NuxtContentHelper with custom components."""
    # Custom component configuration
    custom_components = {
        "alert": "MyAlert",
        "variables": "MyVariables", 
        "arguments": "MyArguments",
        "button": "MyButton"
    }
    
    helper = NuxtContentHelper(
        base_url="/docs",
        use_mdc=True,
        mdc_components=custom_components
    )
    
    # Test variables section
    variables = [
        {
            "name": "`user_id`",
            "type": "`string`",
            "content": "The unique identifier for the user."
        }
    ]
    
    variables_section = helper.create_variables_section(variables)
    print("NuxtContentHelper with custom components - Variables:")
    print(variables_section)
    print("\n" + "="*50 + "\n")
    
    # Test arguments section
    arguments = [
        {
            "name": "`query`",
            "type": "`string`",
            "content": "The search query to execute."
        }
    ]
    
    arguments_section = helper.create_arguments_section(arguments)
    print("NuxtContentHelper with custom components - Arguments:")
    print(arguments_section)
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    print("🚀 pydoc-markdown-nuxt - New Components Demo\n")
    
    demo_variables_component()
    demo_arguments_component() 
    demo_generic_component()
    demo_nuxt_content_helper()
    
    print("✅ Demo completed! Check the output above to see the generated MDC syntax.")
