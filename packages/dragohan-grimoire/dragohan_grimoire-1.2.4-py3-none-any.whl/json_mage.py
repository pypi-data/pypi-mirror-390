# json_mage.py - Your Personal JSON Grimoire (ULTIMATE EDITION v6)
"""
DragoHan's JSON Mastery Library
The simplest way to work with JSON - no bullshit, just results.

Powers: 31+ methods for reading, counting, filtering, sorting, math, occurrence analysis, and modifying JSON
"""

import jmespath
from typing import Any, Union, List, Dict
import json
from collections import Counter


class MageJSON:
    """
    The simplest JSON sorcery - read, write, count, filter, sort ANY JSON structure.
    """
    
    def __init__(self, data: Union[str, dict, list]):
        """Auto-converts anything to workable JSON"""
        if isinstance(data, str):
            try:
                self._raw = json.loads(data)
            except:
                self._raw = data
        else:
            self._raw = data
    
    # ===================================================================
    # READING POWERS (11 methods)
    # ===================================================================
    
    @property
    def first(self) -> Any:
        """Get first item - data.first"""
        if isinstance(self._raw, list):
            return self._raw[0] if self._raw else None
        elif isinstance(self._raw, dict):
            return list(self._raw.values())[0] if self._raw else None
        return self._raw
    
    @property
    def last(self) -> Any:
        """Get last item - data.last"""
        if isinstance(self._raw, list):
            return self._raw[-1] if self._raw else None
        elif isinstance(self._raw, dict):
            return list(self._raw.values())[-1] if self._raw else None
        return self._raw
    
    @property
    def keys(self) -> List[str]:
        """All unique keys - data.keys"""
        keys = set()
        self._collect_keys(self._raw, keys)
        return sorted(list(keys))
    
    @property
    def raw(self) -> Any:
        """Get original data - data.raw"""
        return self._raw
    
    def get(self, key: str) -> Any:
        """
        Get value for a key (searches anywhere)
        Works with dot notation: data.get('user.email')
        """
        result = jmespath.search(key, self._raw)
        if result is not None:
            return result
        return self._deep_search(self._raw, key)
    
    def all(self, key: str) -> List:
        """
        Get ALL values for a key
        Example: data.all('email') → all emails
        """
        return self._collect_all_values(self._raw, key)
    
    def find(self, value: Any) -> List:
        """
        Find items containing a value
        Example: data.find('john@email.com')
        """
        return self._find_value(self._raw, value)
    
    def unique(self, key: str) -> List:
        """
        Get unique values (no duplicates)
        Example: data.unique('status') → ['success', 'error']
        """
        return list(set(self.all(key)))
    
    def has(self, key: str, value: Any) -> bool:
        """
        Check if value exists
        Example: data.has('status', 'error') → True/False
        """
        return value in self.all(key)
    
    @property
    def show(self) -> str:
        """Pretty print - print(data.show)"""
        return json.dumps(self._raw, indent=2)
    
    def __getitem__(self, key):
        """Direct access - data['key'] or data[0]"""
        if isinstance(self._raw, (dict, list)):
            return self._raw[key]
        return None
    
    # ===================================================================
    # COUNTING & FILTERING POWERS (4 methods)
    # ===================================================================
    
    def count(self, key: str, value: Any = None) -> Union[int, dict]:
        """
        Count occurrences
        
        Examples:
            data.count('status', 'success')  → 3
            data.count('status')             → {'success': 3, 'error': 2}
        """
        all_values = self.all(key)
        
        if value is None:
            return dict(Counter(all_values))
        else:
            return all_values.count(value)
    
    def filter(self, key: str, value: Any) -> List:
        """
        Get items where key=value (direct match only)
        
        Example: data.filter('status', 'error') → all errors
        Note: For nested filtering, use smart_filter()
        """
        result = []
        if isinstance(self._raw, list):
            for item in self._raw:
                if isinstance(item, dict) and item.get(key) == value:
                    result.append(item)
        return result
    
    def smart_filter(self, key: str, operator_or_value: Any, value: Any = None) -> 'MageJSON':
        """
        UNIVERSAL smart filter with operator support - CHAINABLE
        
        Usage patterns:
            # Simple equality (backward compatible)
            logs.smart_filter("type", "water")
            
            # With operators
            logs.smart_filter("weight", ">", 50)
            logs.smart_filter("height", "<=", 10)
            logs.smart_filter("name", "contains", "char")
            logs.smart_filter("id", "in", [1, 5, 10])
            
            # Chained filters
            heavy_water = (logs
                .smart_filter("type", "water")
                .smart_filter("weight", ">", 50)
            )
        
        Operators:
            ==, !=, >, <, >=, <=, contains, in
        
        Returns:
            MageJSON object (chainable)
        """
        # Determine if we have 2 or 3 arguments
        if value is None:
            # 2 args: smart_filter(key, value) - simple equality
            operator = "=="
            compare_value = operator_or_value
        else:
            # 3 args: smart_filter(key, operator, value)
            operator = operator_or_value
            compare_value = value
        
        results = []
        
        if not isinstance(self._raw, list):
            return MageJSON(results)
        
        for item in self._raw:
            if item.get('error'):  # Skip error items
                continue
            
            # Get the actual value from the item
            item_value = self._get_nested_value(item, key)
            
            if item_value is None:
                continue
            
            # Apply operator comparison
            if self._compare(item_value, operator, compare_value):
                results.append(item)
        
        return MageJSON(results)
    
    def summary(self) -> dict:
        """
        Complete data summary
        
        Returns: type, total_items, all_keys, key_counts
        """
        result = {
            'type': 'list' if isinstance(self._raw, list) else 'dict',
            'total_items': len(self._raw) if isinstance(self._raw, list) else 1,
            'all_keys': self.keys,
            'key_counts': {}
        }
        
        for key in self.keys:
            values = self.all(key)
            if values:
                result['key_counts'][key] = dict(Counter(values))
        
        return result
    
    # ===================================================================
    # MATH POWERS (4 methods)
    # ===================================================================
    
    def sum(self, key: str) -> Union[int, float]:
        """
        Sum numeric values
        
        Example: data.sum('tokens_used') → 1543
        """
        all_values = self.all(key)
        try:
            return sum(all_values) if all_values else 0
        except TypeError:
            return 0
    
    def avg(self, key: str) -> float:
        """
        Average of numeric values
        
        Example: data.avg('score') → 85.3
        """
        all_values = self.all(key)
        try:
            return sum(all_values) / len(all_values) if all_values else 0
        except (TypeError, ZeroDivisionError):
            return 0
    
    def max(self, key: str) -> Any:
        """
        Maximum value
        
        Example: data.max('score') → 98
        """
        all_values = self.all(key)
        try:
            return max(all_values) if all_values else None
        except (TypeError, ValueError):
            return None
    
    def min(self, key: str) -> Any:
        """
        Minimum value
        
        Example: data.min('age') → 18
        """
        all_values = self.all(key)
        try:
            return min(all_values) if all_values else None
        except (TypeError, ValueError):
            return None
    
    # ===================================================================
    # OCCURRENCE ANALYSIS POWERS (4 methods) - BULLETPROOF!
    # ===================================================================
    
    def occurs_most(self, key: str, value_only: bool = False) -> Union[tuple, Any]:
        """
        BULLETPROOF - Find the most frequent value for ANY key (direct OR nested)
        
        Automatically handles:
        - Direct values: weight, height, id
        - Nested values: type (finds types[].type.name)
        - Multiple values per item: dual-types counted separately
        - Any data type: strings, numbers, booleans
        
        Usage:
            # Get both value and count
            value, count = logs.occurs_most('type')
            # → ('water', 15)
            
            # Get only the value
            most_common = logs.occurs_most('weight', value_only=True)
            # → 905
        
        Parameters:
            key: Field to analyze (direct or nested)
            value_only: If True, returns only the value; if False, returns (value, count)
        
        Returns:
            (value, count) tuple by default, or just value if value_only=True
            Returns (None, 0) or None if no data
        """
        all_values = []
        
        if not isinstance(self._raw, list):
            return None if value_only else (None, 0)
        
        # Extract ALL values for this key (handles nested automatically)
        for item in self._raw:
            if item.get('error'):
                continue
            
            # Get value(s) using smart extraction
            extracted = self._extract_all_values_for_key(item, key)
            
            if extracted is not None:
                # If multiple values (like dual-types), add all
                if isinstance(extracted, list):
                    all_values.extend(extracted)
                else:
                    all_values.append(extracted)
        
        # Count occurrences
        if not all_values:
            return None if value_only else (None, 0)
        
        counts = Counter(all_values)
        value, count = counts.most_common(1)[0]
        
        return value if value_only else (value, count)
    
    def occurs_min(self, key: str, value_only: bool = False) -> Union[tuple, Any]:
        """
        BULLETPROOF - Find the least frequent (rarest) value for ANY key
        
        Usage:
            value, count = logs.occurs_min('type')
            # → ('dragon', 1)
        """
        all_values = []
        
        if not isinstance(self._raw, list):
            return None if value_only else (None, 0)
        
        # Extract ALL values
        for item in self._raw:
            if item.get('error'):
                continue
            
            extracted = self._extract_all_values_for_key(item, key)
            
            if extracted is not None:
                if isinstance(extracted, list):
                    all_values.extend(extracted)
                else:
                    all_values.append(extracted)
        
        if not all_values:
            return None if value_only else (None, 0)
        
        counts = Counter(all_values)
        value, count = counts.most_common()[-1]  # Last = least common
        
        return value if value_only else (value, count)
    
    def occurs_rare(self, key: str, value_only: bool = False) -> Union[tuple, Any]:
        """
        Alias for occurs_min - finds the rarest value
        """
        return self.occurs_min(key, value_only)
    
    def occurs_mid(self, key: str, value_only: bool = False) -> Union[tuple, Any]:
        """
        BULLETPROOF - Find the median frequency value for ANY key
        
        Usage:
            value, count = logs.occurs_mid('type')
            # → ('grass', 8)
        """
        all_values = []
        
        if not isinstance(self._raw, list):
            return None if value_only else (None, 0)
        
        # Extract ALL values
        for item in self._raw:
            if item.get('error'):
                continue
            
            extracted = self._extract_all_values_for_key(item, key)
            
            if extracted is not None:
                if isinstance(extracted, list):
                    all_values.extend(extracted)
                else:
                    all_values.append(extracted)
        
        if not all_values:
            return None if value_only else (None, 0)
        
        counts = Counter(all_values)
        sorted_items = counts.most_common()
        
        # Get middle item
        mid_idx = len(sorted_items) // 2
        value, count = sorted_items[mid_idx]
        
        return value if value_only else (value, count)
    
    # ===================================================================
    # SORTING POWER (1 method)
    # ===================================================================
    
    def sort(self, key: str, ascending: bool = True) -> List:
        """
        Sort items by a key
        
        Parameters:
            key: Field to sort by
            ascending: True = low→high, False = high→low
        
        Examples:
            data.sort('weight', False)  # Heaviest first
        """
        if isinstance(self._raw, list):
            try:
                return sorted(self._raw, key=lambda x: x.get(key, ''), reverse=not ascending)
            except Exception:
                return self._raw
        return self._raw
    
    # ===================================================================
    # MODIFICATION POWERS (5 methods)
    # ===================================================================
    
    def change(self, key: str, new_value: Any) -> 'MageJSON':
        """Change a key's value - returns self for chaining"""
        self._change_key(self._raw, key, new_value)
        return self
    
    def change_at(self, path: str, new_value: Any) -> 'MageJSON':
        """Change value at specific path - returns self for chaining"""
        parts = path.split('.')
        current = self._raw
        
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return self
        
        if isinstance(current, dict) and parts[-1] in current:
            current[parts[-1]] = new_value
        
        return self
    
    def add_key(self, key: str, value: Any) -> 'MageJSON':
        """Add new key - returns self for chaining"""
        if isinstance(self._raw, dict):
            self._raw[key] = value
        return self
    
    def remove_key(self, key: str) -> 'MageJSON':
        """Remove key everywhere - returns self for chaining"""
        self._remove_key(self._raw, key)
        return self
    
    def save_to(self, filename: str) -> str:
        """Save modified JSON"""
        try:
            import simple_file
            return simple_file.save(filename, self._raw)
        except:
            from pathlib import Path
            Path(filename if '.' in filename else f"{filename}.json").write_text(json.dumps(self._raw, indent=2))
            return f"✅ Saved: {filename}"
    
    # ===================================================================
    # ADVANCED
    # ===================================================================
    
    def where(self, jmes_query: str) -> Any:
        """Advanced JMESPath queries"""
        return jmespath.search(jmes_query, self._raw)
    
    def __repr__(self):
        """When you print(data)"""
        return self.show
    
    # ===================================================================
    # INTERNAL MAGIC - BULLETPROOF VALUE EXTRACTION
    # ===================================================================
    
    def _extract_all_values_for_key(self, obj: dict, search_key: str, depth: int = 0) -> Any:
        """
        BULLETPROOF extractor - gets ALL values for a key at ANY depth
        
        Returns:
        - Single value: 905
        - List of values: ["fire", "flying"] (for dual-types)
        - None: key not found
        """
        if depth > 50 or not isinstance(obj, dict):
            return None
        
        # PATTERN 1: Direct access
        if search_key in obj:
            val = obj[search_key]
            # Simple value - return it
            if not isinstance(val, (dict, list)):
                return val
            # Dict with 'name' or 'value' - return that
            if isinstance(val, dict):
                if 'name' in val:
                    return val['name']
                if 'value' in val:
                    return val['value']
            return val
        
        # PATTERN 2: Plural array (types[], abilities[], etc.)
        plural_key = search_key + 's'
        if plural_key in obj and isinstance(obj[plural_key], list):
            values = []
            for item in obj[plural_key]:
                if isinstance(item, dict) and search_key in item:
                    nested = item[search_key]
                    # Extract name/value if nested dict
                    if isinstance(nested, dict):
                        if 'name' in nested:
                            values.append(nested['name'])
                        elif 'value' in nested:
                            values.append(nested['value'])
                    else:
                        values.append(nested)
            
            # Return list if multiple, single if one, None if empty
            if len(values) > 1:
                return values
            elif len(values) == 1:
                return values[0]
        
        # PATTERN 3: Recursive deep search
        for key, val in obj.items():
            if isinstance(val, dict):
                result = self._extract_all_values_for_key(val, search_key, depth + 1)
                if result is not None:
                    return result
            elif isinstance(val, list):
                for list_item in val:
                    if isinstance(list_item, dict):
                        result = self._extract_all_values_for_key(list_item, search_key, depth + 1)
                        if result is not None:
                            return result
        
        return None
    
    def _deep_search(self, data: Any, key: str) -> Any:
        if isinstance(data, dict):
            if key in data:
                return data[key]
            for v in data.values():
                result = self._deep_search(v, key)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._deep_search(item, key)
                if result is not None:
                    return result
        return None
    
    def _find_value(self, data: Any, target_value: Any) -> List:
        matches = []
        if isinstance(data, dict):
            if target_value in data.values():
                matches.append(data)
            for v in data.values():
                matches.extend(self._find_value(v, target_value))
        elif isinstance(data, list):
            for item in data:
                if item == target_value:
                    matches.append(item)
                else:
                    matches.extend(self._find_value(item, target_value))
        return matches
    
    def _collect_keys(self, data: Any, keys: set):
        if isinstance(data, dict):
            keys.update(data.keys())
            for v in data.values():
                self._collect_keys(v, keys)
        elif isinstance(data, list):
            for item in data:
                self._collect_keys(item, keys)
    
    def _collect_all_values(self, data: Any, key: str) -> List:
        values = []
        if isinstance(data, dict):
            if key in data:
                values.append(data[key])
            for v in data.values():
                values.extend(self._collect_all_values(v, key))
        elif isinstance(data, list):
            for item in data:
                values.extend(self._collect_all_values(item, key))
        return values
    
    def _change_key(self, data: Any, key: str, new_value: Any) -> bool:
        if isinstance(data, dict):
            if key in data:
                data[key] = new_value
                return True
            for v in data.values():
                if self._change_key(v, key, new_value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._change_key(item, key, new_value):
                    return True
        return False
    
    def _remove_key(self, data: Any, key: str):
        if isinstance(data, dict):
            if key in data:
                del data[key]
            for v in list(data.values()):
                self._remove_key(v, key)
        elif isinstance(data, list):
            for item in data:
                self._remove_key(item, key)
    
    def _get_nested_value(self, obj: Any, search_key: str, depth: int = 0) -> Any:
        """Get SINGLE value for smart_filter (returns first match)"""
        if depth > 50 or not isinstance(obj, dict):
            return None
        
        # Direct match
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
        
        # Plural array - return FIRST match
        plural_key = search_key + 's'
        if plural_key in obj and isinstance(obj[plural_key], list):
            for item in obj[plural_key]:
                if isinstance(item, dict) and search_key in item:
                    nested = item[search_key]
                    if isinstance(nested, dict):
                        if 'name' in nested:
                            return nested['name']
                        if 'value' in nested:
                            return nested['value']
                    else:
                        return nested
        
        # Recursive
        for key, val in obj.items():
            if isinstance(val, dict):
                result = self._get_nested_value(val, search_key, depth + 1)
                if result is not None:
                    return result
            elif isinstance(val, list):
                for list_item in val:
                    if isinstance(list_item, dict):
                        result = self._get_nested_value(list_item, search_key, depth + 1)
                        if result is not None:
                            return result
        
        return None
    
    def _compare(self, item_value: Any, operator: str, compare_value: Any) -> bool:
        """Compare values using operator"""
        try:
            if operator == "==" or operator == "=":
                return item_value == compare_value
            elif operator == "!=":
                return item_value != compare_value
            elif operator == ">":
                return item_value > compare_value
            elif operator == "<":
                return item_value < compare_value
            elif operator == ">=":
                return item_value >= compare_value
            elif operator == "<=":
                return item_value <= compare_value
            elif operator == "contains":
                return str(compare_value).lower() in str(item_value).lower()
            elif operator == "in":
                return item_value in compare_value
            else:
                return item_value == compare_value
        except (TypeError, ValueError):
            return False


# ===================================================================
# THE MAGIC SPELL
# ===================================================================

def modify(data: Union[str, dict, list]) -> MageJSON:
    """Convert ANY JSON to mage object"""
    return MageJSON(data)


def myjson(data: Union[str, dict, list]) -> MageJSON:
    """Alternative name"""
    return MageJSON(data)


__all__ = ['modify', 'myjson', 'MageJSON']
