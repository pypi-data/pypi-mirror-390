from typing import Dict, Any
from pytsterrors.exception import TSTError
import json
import functools


def json_to_tst_error(json_string: str | bytes) -> TSTError:
    data = json.loads(json_string)
    if not isinstance(data, dict):
        raise TSTError("not-instance-of-dict", "JSON must have specific variables to serialize to TSTError exception")

    tag = data.get("tag")
    message = data.get("message")
    func_trace = data.get("func_trace")
    if not tag or not message or not func_trace :
        raise TSTError("not-correct-json", "JSON is not from TSTError")

    tst = TSTError(tag, message=message, can_inspect=False)
    tst.set_func_trace(func_trace)

    return tst


def tst_decorator(func):
    @functools.wraps(func)
    def tst_decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, TSTError):
                raise e
            
            tag = type(e).__name__
            message = e.__str__()
            
            err = TSTError(tag, message, other_exception=e)
            for _ in range(err._func_trace.count('tst_decorated')):
                err._func_trace.remove('tst_decorated')

            raise err

    return tst_decorated
