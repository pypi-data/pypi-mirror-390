import inspect
import re
import typing
from functools import wraps


def silent_type_cast(fn):
    """
    Decorator that attempts to silently type cast args and kwargs (if supported)
    """
    fn_annotations = inspect.signature(fn)
    parameter_conversion = {}
    for param_name, annotation in fn_annotations.parameters.items():
        base_type = typing.get_args(annotation.annotation)
        if base_type:  # continue only if method has parameters
            while True:
                if isinstance(base_type, tuple):
                    # if iterable, take the first one
                    base_type = base_type[0]
                elif typing.get_origin(base_type) in (list, typing.Union):
                    # if iterable type, take the first one
                    base_type = typing.get_args(base_type)
                    if not base_type:
                        break
                    base_type = base_type[0]
                elif base_type is typing.Any:
                    # no need of polymorphism if any type
                    break
                elif base_type.__module__ == "builtins":
                    # if one of the base python object, polymorphism is not supported
                    break
                else:
                    class_name = base_type.__name__
                    function_name = f"convert_to_{re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()}"
                    parameter_conversion[param_name] = function_name
                    break

    @wraps(fn)
    def decorator(*args, **kwargs):
        new_args = []
        for arg, _param_name in zip(args, fn_annotations.parameters.keys()):
            if (
                arg is None
                or _param_name not in parameter_conversion
                or not hasattr(arg, parameter_conversion[_param_name])
            ):
                new_args.append(arg)
            else:
                new_args.append(getattr(arg, parameter_conversion[_param_name])())
        new_args_tuple = tuple(new_args)
        kwargs = {
            k: (
                getattr(v, parameter_conversion[k])()
                if v  # not null
                and k in parameter_conversion  # parameter allows conversion
                and hasattr(v, parameter_conversion[k])  # conversion fn exists
                else v
            )
            for k, v in kwargs.items()
        }
        return fn(*new_args_tuple, **kwargs)

    return decorator
