import json
from collections import Counter
from typing import Any, Union, List, Dict


class DuplicateChecker:
    """Enhanced wrapper for duplicate detection and removal in complex data structures"""
    
    def __init__(self, data: Any):
        self._data = data
        self._raw = data
    
    @property
    def raw(self):
        """Return the raw data"""
        return self._raw
    
    def _flatten_values(self, data: Any, parent_key: str = '') -> List[tuple]:
        """Recursively flatten nested structures to extract all key-value pairs"""
        items = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, (dict, list)):
                    items.extend(self._flatten_values(value, new_key))
                else:
                    items.append((new_key, value))
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                new_key = f"{parent_key}[{idx}]" if parent_key else f"[{idx}]"
                if isinstance(item, (dict, list)):
                    items.extend(self._flatten_values(item, new_key))
                else:
                    items.append((parent_key, item))
        
        return items
    
    def _serialize_item(self, item: Any) -> str:
        """Convert item to a hashable string for comparison"""
        if isinstance(item, (dict, list)):
            return json.dumps(item, sort_keys=True)
        return str(item)
    
    def duplicate_check(self, key: str = None) -> Dict[str, Any]:
        """
        Check for duplicates in the data structure
        
        Args:
            key: Optional key to check duplicates for (works with nested keys using dot notation)
        
        Returns:
            Dictionary with duplicate information in JSON format
        """
        result = {
            "duplicates_found": False,
            "total_items": 0,
            "unique_items": 0,
            "duplicate_count": 0,
            "details": []
        }
        
        if not self._data:
            print("no duplicates found ✅")
            return result
        
        # Handle list of items
        if isinstance(self._data, list):
            result["total_items"] = len(self._data)
            
            if key:
                # Check duplicates for a specific key
                values = []
                for item in self._data:
                    if isinstance(item, dict):
                        # Handle nested keys
                        keys = key.split('.')
                        value = item
                        try:
                            for k in keys:
                                value = value[k]
                            values.append(self._serialize_item(value))
                        except (KeyError, TypeError):
                            continue
                    else:
                        values.append(self._serialize_item(item))
                
                counter = Counter(values)
                duplicates = {k: v for k, v in counter.items() if v > 1}
                
                if duplicates:
                    result["duplicates_found"] = True
                    result["unique_items"] = len(counter)
                    result["duplicate_count"] = sum(v - 1 for v in duplicates.values())
                    
                    for value, count in duplicates.items():
                        result["details"].append({
                            "key": key,
                            "value": value,
                            "occurrences": count,
                            "excess_copies": count - 1
                        })
            else:
                # Check entire items for duplicates
                serialized = [self._serialize_item(item) for item in self._data]
                counter = Counter(serialized)
                duplicates = {k: v for k, v in counter.items() if v > 1}
                
                if duplicates:
                    result["duplicates_found"] = True
                    result["unique_items"] = len(counter)
                    result["duplicate_count"] = sum(v - 1 for v in duplicates.values())
                    
                    for value, count in duplicates.items():
                        try:
                            parsed = json.loads(value)
                        except:
                            parsed = value
                        
                        result["details"].append({
                            "item": parsed,
                            "occurrences": count,
                            "excess_copies": count - 1
                        })
        
        elif isinstance(self._data, dict):
            # For dictionaries, check duplicate values
            values = list(self._data.values())
            serialized = [self._serialize_item(v) for v in values]
            counter = Counter(serialized)
            duplicates = {k: v for k, v in counter.items() if v > 1}
            
            result["total_items"] = len(values)
            
            if duplicates:
                result["duplicates_found"] = True
                result["unique_items"] = len(counter)
                result["duplicate_count"] = sum(v - 1 for v in duplicates.values())
                
                for value, count in duplicates.items():
                    keys_with_value = [k for k, v in self._data.items() 
                                      if self._serialize_item(v) == value]
                    
                    try:
                        parsed = json.loads(value)
                    except:
                        parsed = value
                    
                    result["details"].append({
                        "value": parsed,
                        "keys": keys_with_value,
                        "occurrences": count,
                        "excess_copies": count - 1
                    })
        
        # Print result
        if result["duplicates_found"]:
            print(json.dumps(result, indent=2))
        else:
            print("no duplicates found ✅")
        
        return result
    
    def del_duplicate(self, key: str = None) -> Any:
        """
        Remove duplicates from the data structure
        
        Args:
            key: Optional key to deduplicate by (works with nested keys using dot notation)
        
        Returns:
            Data with duplicates removed
        """
        if not self._data:
            print("no duplicates found ✅")
            return self._data
        
        # Handle list of items
        if isinstance(self._data, list):
            if key:
                # Remove duplicates based on specific key
                seen = set()
                unique_items = []
                
                for item in self._data:
                    if isinstance(item, dict):
                        # Handle nested keys
                        keys = key.split('.')
                        value = item
                        try:
                            for k in keys:
                                value = value[k]
                            serialized = self._serialize_item(value)
                            
                            if serialized not in seen:
                                seen.add(serialized)
                                unique_items.append(item)
                        except (KeyError, TypeError):
                            unique_items.append(item)
                    else:
                        serialized = self._serialize_item(item)
                        if serialized not in seen:
                            seen.add(serialized)
                            unique_items.append(item)
                
                removed = len(self._data) - len(unique_items)
                self._data = unique_items
                self._raw = unique_items
                
                if removed > 0:
                    print(f"✅ Removed {removed} duplicate(s). {len(unique_items)} unique items remaining.")
                else:
                    print("no duplicates found ✅")
            else:
                # Remove complete duplicate items
                seen = set()
                unique_items = []
                
                for item in self._data:
                    serialized = self._serialize_item(item)
                    if serialized not in seen:
                        seen.add(serialized)
                        unique_items.append(item)
                
                removed = len(self._data) - len(unique_items)
                self._data = unique_items
                self._raw = unique_items
                
                if removed > 0:
                    print(f"✅ Removed {removed} duplicate(s). {len(unique_items)} unique items remaining.")
                else:
                    print("no duplicates found ✅")
        
        elif isinstance(self._data, dict):
            # For dictionaries, remove keys with duplicate values
            seen = set()
            unique_dict = {}
            removed = 0
            
            for k, v in self._data.items():
                serialized = self._serialize_item(v)
                if serialized not in seen:
                    seen.add(serialized)
                    unique_dict[k] = v
                else:
                    removed += 1
            
            self._data = unique_dict
            self._raw = unique_dict
            
            if removed > 0:
                print(f"✅ Removed {removed} duplicate value(s). {len(unique_dict)} unique entries remaining.")
            else:
                print("no duplicates found ✅")
        
        return self._data
    
    def show(self):
        """Display the current data in pretty JSON format"""
        print(json.dumps(self._data, indent=2))
        return self._data


def modify(data: Any) -> DuplicateChecker:
    """
    Create a DuplicateChecker instance for the given data
    
    Usage:
        from duplicates import *
        
        data = [{"id": 1}, {"id": 1}, {"id": 2}]
        checker = modify(data)
        checker.duplicate_check("id")
        checker.del_duplicate("id")
    """
    return DuplicateChecker(data)


__all__ = ['modify', 'DuplicateChecker']

