def ast(json_data: dict, key: str, value):
    if key in json_data:
        if json_data[key] == value:
            return True
    return False