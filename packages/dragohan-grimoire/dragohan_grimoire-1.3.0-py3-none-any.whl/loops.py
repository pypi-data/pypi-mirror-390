# loops.py - Universal Loop Library
"""
DragoHan's Loop Mastery Library
Extract values from ANY data structure - no bullshit loops needed.

Usage:
    from loops import *
    
    urls = loopon(data, "url")
    fire = loopon(data, "type", where="fire")
    sorted_weights = loopon.sorta(data, "weight")
    full_items = loopon_and_get(data, "type", where="fire")
"""

from typing import Any, List, Union
import re


class LoopOn:
    """
    Universal loop extractor - handles ANY data structure
    """
    
    def __call__(self, data: Any, key: str, where: str = None, limit: int = None) -> List:
        """
        Extract values from data
        
        Args:
            data: List of dicts or MageJSON object
            key: Key to extract
            where: Optional filter (e.g., "fire", ">100", "!=water")
            limit: Optional limit on results
        
        Returns:
            List of extracted values
        """
        # Handle MageJSON objects
        if hasattr(data, 'raw'):
            data = data.raw
        
        if not isinstance(data, list):
            return []
        
        # Extract all values for the key
        values = []
        for item in data:
            if not isinstance(item, dict) or item.get('error'):
                continue
            
            extracted = self._extract_value(item, key)
            
            if extracted is not None:
                # Handle multiple values per item (e.g., dual-types)
                if isinstance(extracted, list):
                    values.extend(extracted)
                else:
                    values.append(extracted)
        
        # Apply filter if specified
        if where:
            values = self._filter_values(values, where)
        
        # Apply limit if specified
        if limit:
            values = values[:limit]
        
        return values
    
    def sorta(self, data: Any, key: str, where: str = None, limit: int = None) -> List:
        """
        Extract and sort ASCENDING
        
        Usage:
            loopon.sorta(data, "weight")
            loopon.sorta(data, "weight", where=">100")
            loopon.sorta(data, "weight", limit=5)
        """
        values = self(data, key, where=where, limit=None)  # Get all first
        
        try:
            values = sorted(values)  # Sort ascending
        except TypeError:
            pass  # Can't sort mixed types
        
        # Apply limit after sorting
        if limit:
            values = values[:limit]
        
        return values
    
    def sortd(self, data: Any, key: str, where: str = None, limit: int = None) -> List:
        """
        Extract and sort DESCENDING
        
        Usage:
            loopon.sortd(data, "weight")
            loopon.sortd(data, "weight", where=">100")
            loopon.sortd(data, "weight", limit=5)
        """
        values = self(data, key, where=where, limit=None)  # Get all first
        
        try:
            values = sorted(values, reverse=True)  # Sort descending
        except TypeError:
            pass  # Can't sort mixed types
        
        # Apply limit after sorting
        if limit:
            values = values[:limit]
        
        return values
    
    def _extract_value(self, obj: dict, search_key: str, depth: int = 0) -> Any:
        """
        Extract value from nested structure
        
        Handles:
        - Direct: obj[key]
        - Nested: obj[key].name
        - Plural: obj[keys][].key.name
        """
        if depth > 50 or not isinstance(obj, dict):
            return None
        
        # PATTERN 1: Direct access
        if search_key in obj:
            val = obj[search_key]
            if not isinstance(val, (dict, list)):
                return val
            if isinstance(val, dict):
                if 'name' in val:
                    return val['name']
                if 'value' in val:
                    return val['value']
            return val
        
        # PATTERN 2: Plural array
        plural_key = search_key + 's'
        if plural_key in obj and isinstance(obj[plural_key], list):
            values = []
            for item in obj[plural_key]:
                if isinstance(item, dict) and search_key in item:
                    nested = item[search_key]
                    if isinstance(nested, dict):
                        if 'name' in nested:
                            values.append(nested['name'])
                        elif 'value' in nested:
                            values.append(nested['value'])
                    else:
                        values.append(nested)
            
            if len(values) > 1:
                return values
            elif len(values) == 1:
                return values[0]
        
        # PATTERN 3: Recursive search
        for key, val in obj.items():
            if isinstance(val, dict):
                result = self._extract_value(val, search_key, depth + 1)
                if result is not None:
                    return result
            elif isinstance(val, list):
                for list_item in val:
                    if isinstance(list_item, dict):
                        result = self._extract_value(list_item, search_key, depth + 1)
                        if result is not None:
                            return result
        
        return None
    
    def _filter_values(self, values: List, condition: str) -> List:
        """
        Filter values based on condition
        
        Supports:
        - "fire" (equals)
        - ">100" (greater than)
        - ">=100" (greater or equal)
        - "<50" (less than)
        - "<=50" (less or equal)
        - "!=water" (not equal)
        """
        # Parse operator and value
        operator, compare_value = self._parse_condition(condition)
        
        filtered = []
        for value in values:
            if self._compare(value, operator, compare_value):
                filtered.append(value)
        
        return filtered
    
    def _parse_condition(self, condition: str) -> tuple:
        """Parse condition into operator and value"""
        condition = str(condition).strip()
        
        # Check for operators
        if condition.startswith('>='):
            return '>=', self._convert_value(condition[2:].strip())
        elif condition.startswith('<='):
            return '<=', self._convert_value(condition[2:].strip())
        elif condition.startswith('!='):
            return '!=', self._convert_value(condition[2:].strip())
        elif condition.startswith('>'):
            return '>', self._convert_value(condition[1:].strip())
        elif condition.startswith('<'):
            return '<', self._convert_value(condition[1:].strip())
        else:
            # No operator = equals
            return '==', self._convert_value(condition)
    
    def _convert_value(self, value_str: str) -> Any:
        """Convert string to appropriate type"""
        value_str = value_str.strip()
        
        # Try to convert to number
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            return value_str
    
    def _compare(self, value: Any, operator: str, compare_value: Any) -> bool:
        """Compare value with condition"""
        try:
            if operator == '==':
                return value == compare_value
            elif operator == '!=':
                return value != compare_value
            elif operator == '>':
                return value > compare_value
            elif operator == '<':
                return value < compare_value
            elif operator == '>=':
                return value >= compare_value
            elif operator == '<=':
                return value <= compare_value
            else:
                return value == compare_value
        except (TypeError, ValueError):
            return False


def loopon_and_get(data: Any, key: str, where: str = None, limit: int = None) -> List:
    """
    Get FULL ITEMS where key matches condition
    
    Usage:
        fire_pokemon = loopon_and_get(data, "type", where="fire")
        heavy = loopon_and_get(data, "weight", where=">100")
    
    Args:
        data: List of dicts or MageJSON object
        key: Key to filter by
        where: Condition (e.g., "fire", ">100")
        limit: Optional limit
    
    Returns:
        List of full items (dicts)
    """
    # Handle MageJSON objects
    if hasattr(data, 'raw'):
        data = data.raw
    
    if not isinstance(data, list):
        return []
    
    results = []
    
    for item in data:
        if not isinstance(item, dict) or item.get('error'):
            continue
        
        # Extract value for this item
        extracted = loopon._extract_value(item, key)
        
        if extracted is None:
            continue
        
        # If where condition specified, check it
        if where:
            # Handle multiple values (e.g., dual-types)
            if isinstance(extracted, list):
                # Check if ANY value matches
                matches = False
                for val in extracted:
                    if loopon._compare(val, *loopon._parse_condition(where)):
                        matches = True
                        break
                if not matches:
                    continue
            else:
                # Single value - check directly
                if not loopon._compare(extracted, *loopon._parse_condition(where)):
                    continue
        
        results.append(item)
    
    # Apply limit
    if limit:
        results = results[:limit]
    
    return results


# Create singleton instance
loopon = LoopOn()

# Export everything
__all__ = ['loopon', 'loopon_and_get']
