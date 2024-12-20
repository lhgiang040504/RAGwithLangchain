def individual_serial(obj) -> dict:
    return {
        "id": str(obj['_id']),
        "name": obj['name'],
    }

def list_serial(objs) -> list:
    return [individual_serial(obj) for obj in objs]