from typing import TypeVar
from collections.abc import Callable

ScoreParameters = TypeVar('ScoreParameters', bound=dict)
RetType = TypeVar("RetType")


def batch_process(func: Callable[[ScoreParameters], RetType]) -> Callable[
        [ScoreParameters | dict[str, ScoreParameters]], RetType | dict[str, RetType]]:
    def wrapper(parameters: ScoreParameters | dict[str, ScoreParameters]) -> RetType | dict[str, RetType]:
        if all(isinstance(v, dict) for v in parameters.values()):
            results: dict[str, RetType] = {}
            for k, v in parameters.items():
                results[k] = func(v)
            return results
        else:
            return func(parameters)

    return wrapper
