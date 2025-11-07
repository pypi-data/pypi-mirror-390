from dataclasses import dataclass
from typing import Callable, get_type_hints


@dataclass
class ValueRange:
    min: int | float
    max: int | float

    def validate_value(self, value: int | float, name: str):
        if not (self.min <= value <= self.max):
            raise ValueError(f"{name} ({value}) is not in range [{self.min}, {self.max}]")


def check_ranges(func: Callable):
    parameter_dict = get_type_hints(func, include_extras=True)['parameters']
    parameters = get_type_hints(parameter_dict, include_extras=True)

    def wrapper(*args, **kwargs):
        input_parameters = args[0] if len(args) > 0 else kwargs['parameters']
        for name, value_type in parameters.items():
            metadata = getattr(value_type, '__metadata__', None)
            if metadata:
                metadata[0].validate_value(input_parameters[name], name)
        return func(*args, **kwargs)
    return wrapper
