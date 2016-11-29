from cloudaux.orchestration import modify

def list_modify(lst, output):
    if isinstance(lst, list):
        return [modify(x, format=output) for x in lst]
    else:
        return None
