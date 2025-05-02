import re

def legal_method_name(name):
    return isinstance(name, str) and re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name) is not None
