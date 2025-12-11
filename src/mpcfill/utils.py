from types import SimpleNamespace
from typing import Any, Dict, Callable
import threading
import re
import string

def dict_to_namespace(data: Dict[str, Any]) -> SimpleNamespace:
    """
    Recursively convert a dictionary to a SimpleNamespace.
    Nested dictionaries and lists of dictionaries are converted recursively.
    """
    ns_data = {}    
    for k, v in data.items():
        if isinstance(v, dict):
            ns_data[k] = dict_to_namespace(v)
        elif isinstance(v, list):
            ns_data[k] = [dict_to_namespace(i) if isinstance(i, dict) else i for i in v]
        else:
            ns_data[k] = v
    return SimpleNamespace(**ns_data)


def namespace_to_dict(ns: SimpleNamespace) -> Dict[str, Any]:
    """
    Recursively convert a SimpleNamespace back to a dictionary.
    """
    result = {}
    for k, v in ns.__dict__.items():
        if isinstance(v, SimpleNamespace):
            result[k] = namespace_to_dict(v)
        elif isinstance(v, list):
            result[k] = [namespace_to_dict(i) if isinstance(i, SimpleNamespace) else i for i in v]
        else:
            result[k] = v
    return result

def make_safe_path(s: str) -> str:
    """
    Convert any string into a filesystem-safe name:
    - Replaces invalid characters with '_'
    - Strips leading/trailing whitespace
    """
    # Replace anything that is not a-z, A-Z, 0-9, dash, or underscore with _
    safe = re.sub(r'[^a-zA-Z0-9\-_.]', '_', s)
    # Collapse multiple underscores
    safe = re.sub(r'_+', '_', safe)
    return safe.strip('_')

def normalize_query(query_str: str) -> str:
    s = query_str.lower()
    s = re.sub(r"[\(\[].*?[\)\]]", "", s)
    s = re.sub(r"-+", " ", s)              
    s = re.sub(r"\bthe\b", " ", s)           
    s = s.replace("’", "'")                  
    s = re.sub(r"^the\s+", "", s)
    s = re.sub(rf"[{re.escape(string.punctuation)}]", "", s)
    s = re.sub(r"\d+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
