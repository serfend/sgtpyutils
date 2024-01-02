def all_key_to_lower(data: dict, recursive: int = 1e3):
    if data is None:
        return None
    if not isinstance(data, dict):
        return data
    result = {}
    for x in data:
        val = data[x]
        if recursive > 0:
            if isinstance(val, dict):
                val = all_key_to_lower(val, recursive-1)
                
        result[x.lower()] = val

    return result
