"""Utility functions for working with Basecamp data and API responses.

This module provides helper functions for manipulating and transforming data
structures returned from the Basecamp API.
"""

def select(obj: dict, *properties: str) -> dict:
    """
    Select specific properties from a dictionary, preserving nested structure.
    
    Extracts values from a dictionary using dot notation to access nested properties.
    The original nesting structure is maintained in the output dictionary.

    Args:
        obj (dict): Source dictionary to extract properties from
        *properties (str): Property paths using dot notation (e.g. "id", "creator.name").
                          Each path represents a property to extract.

    Returns:
        dict: New dictionary containing only the selected properties with their 
              original nesting structure preserved. Only includes properties that
              exist in the source dictionary.

    Examples:
        >>> data = {"id": 1, "creator": {"name": "John", "company": "Acme"}}
        >>> select(data, "id", "creator.name")
        {"id": 1, "creator": {"name": "John"}}
    """
    result = {}

    for prop in properties:
        parts = prop.split(".")
        current = obj
        target = result

        for i, part in enumerate(parts[:-1]):
            if part not in current:
                break
            current = current[part]
            if i == 0:
                target[part] = {}
            target = target[part]

        last = parts[-1]
        if len(parts) == 1:
            if last in obj:
                result[last] = obj[last]
        elif last in current:
            target[last] = current[last]

    return result
