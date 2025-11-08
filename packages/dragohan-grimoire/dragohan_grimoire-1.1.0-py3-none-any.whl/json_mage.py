# json_mage.py - Your Personal JSON Grimoire (ULTIMATE EDITION v3)
"""
DragoHan's JSON Mastery Library
The simplest way to work with JSON - no bullshit, just results.

Powers: 25+ methods for reading, counting, filtering, sorting, math, and modifying JSON
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
    # COUNTING & FILTERING POWERS (3 methods)
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
        Get items where key=value
        
        Example: data.filter('status', 'error') → all errors
        """
        result = []
        if isinstance(self._raw, list):
            for item in self._raw:
                if isinstance(item, dict) and item.get(key) == value:
                    result.append(item)
        return result
    
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
    # MATH POWERS (4 methods) - NEW!
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
    # SORTING POWER (1 method) - NEW! Your requested feature!
    # ===================================================================
    
    def sort(self, key: str, ascending: bool = True) -> List:
        """
        Sort items by a key
        
        Parameters:
            key: Field to sort by
            ascending: True = low→high (oldest first), False = high→low (newest first)
        
        Examples:
            data.sort('timestamp')          # Oldest first
            data.sort('timestamp', False)   # Newest first
            data.sort('score', False)       # Highest score first
            data.sort('name')               # A-Z
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
        """
        Change a key's value
        
        Example: data.change('status', 'success')
        Returns self for chaining
        """
        self._change_key(self._raw, key, new_value)
        return self
    
    def change_at(self, path: str, new_value: Any) -> 'MageJSON':
        """
        Change value at specific path
        
        Example: data.change_at('user.name', 'Farhan')
        Returns self for chaining
        """
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
        """
        Add new key
        
        Example: data.add_key('timestamp', '2025-11-06')
        Returns self for chaining
        """
        if isinstance(self._raw, dict):
            self._raw[key] = value
        return self
    
    def remove_key(self, key: str) -> 'MageJSON':
        """
        Remove key everywhere
        
        Example: data.remove_key('password')
        Returns self for chaining
        """
        self._remove_key(self._raw, key)
        return self
    
    def save_to(self, filename: str) -> str:
        """
        Save modified JSON
        
        Example: data.change('status', 'done').save_to('updated')
        """
        try:
            import simple_file
            return simple_file.save(filename, self._raw)
        except:
            from pathlib import Path
            Path(filename if '.' in filename else f"{filename}.json").write_text(json.dumps(self._raw, indent=2))
            return f"✅ Saved: {filename}"
    
    # ===================================================================
    # ADVANCED (Optional - for power users)
    # ===================================================================
    
    def where(self, jmes_query: str) -> Any:
        """
        Advanced JMESPath queries (optional, for complex filtering)
        
        Example: data.where("users[?age > `25`].name")
        Note: Usually .filter() is simpler!
        """
        return jmespath.search(jmes_query, self._raw)
    
    def __repr__(self):
        """When you print(data)"""
        return self.show
    
    # ===================================================================
    # INTERNAL MAGIC (Don't touch)
    # ===================================================================
    
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


# ===================================================================
# THE MAGIC SPELL
# ===================================================================

def modify(data: Union[str, dict, list]) -> MageJSON:
    """Convert ANY JSON to mage object"""
    return MageJSON(data)


def myjson(data: Union[str, dict, list]) -> MageJSON:
    """Alternative name"""
    return MageJSON(data)


__all__ = ['modify', 'myjson']
