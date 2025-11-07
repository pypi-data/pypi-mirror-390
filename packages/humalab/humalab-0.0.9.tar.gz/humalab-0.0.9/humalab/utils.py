import builtins

# Define what counts as "standard" types
STANDARD_TYPES = (
    int, float, complex, bool, str, bytes, bytearray,
    list, tuple, dict, set, frozenset, type(None)
)

def is_standard_type(obj, _seen=None):
    """Recursively check if an object only contains standard Python types."""
    if _seen is None:
        _seen = set()

    obj_id = id(obj)
    if obj_id in _seen:
        return True  # Prevent infinite recursion for self-referential structures
    _seen.add(obj_id)

    if isinstance(obj, STANDARD_TYPES):
        if isinstance(obj, (list, tuple, set, frozenset)):
            return all(is_standard_type(i, _seen) for i in obj)
        elif isinstance(obj, dict):
            return all(
                is_standard_type(k, _seen) and is_standard_type(v, _seen)
                for k, v in obj.items()
            )
        return True

    # If it's a builtin constant type (e.g., Ellipsis, NotImplemented)
    if obj in (Ellipsis, NotImplemented):
        return True

    # Check if it's a built-in type object (like int, str)
    if isinstance(obj, type) and obj.__module__ == 'builtins':
        return True

    return False