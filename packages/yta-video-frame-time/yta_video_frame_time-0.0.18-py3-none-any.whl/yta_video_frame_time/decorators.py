"""
TODO: I think this module should not be here, or maybe
yes, but I need this decorator.
"""
from functools import wraps


def parameter_to_time_interval(
    param_name: str
):
    """
    Force the parameter with the given `param_name` to
    be a `TimeInterval` instance.

    Values accepted:
    - `TimeInterval` instance
    - `tuple[float, float]` that will be `(start, end)`
    """
    def decorator(
        func
    ):
        @wraps(func)
        def wrapper(
            *args,
            **kwargs
        ):
            from inspect import signature
            from yta_validation import PythonValidator
            from yta_video_frame_time.interval import TimeInterval

            sig = signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            value = bound.arguments[param_name]

            if PythonValidator.is_instance_of(value, TimeInterval):
                pass
            elif (
                PythonValidator.is_tuple(value) and
                len(value) == 2
            ):
                value = TimeInterval(*value)
                bound.arguments[param_name] = value
            else:
                raise Exception(f'The "{param_name}" parameter must be a TimeInterval or a tuple[float, float].')

            return func(*bound.args, **bound.kwargs)
        
        return wrapper
    
    return decorator