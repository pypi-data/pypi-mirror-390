import math
from typing import TypedDict, Annotated

from acribis_scores.batch_processing import batch_process
from acribis_scores.value_range import ValueRange, check_ranges

# See: https://doi.org/10.1093/eurheartj/ehx584
# Also: https://academic.oup.com/eurheartj/article/39/6/477/4554831#supplementary-data

Parameters = TypedDict('Parameters', {
    'Heart Failure': bool,
    'Age': Annotated[int, ValueRange(22, 95)],
    'NT-proBNP in ng/L': Annotated[float, ValueRange(5, 21000)],
    'GDF-15 in ng/L': Annotated[float, ValueRange(400.0, 20000.0)],
    'Troponin T in ng/L': Annotated[float, ValueRange(3.0, 200.0)]
})

# Model A: All-cause mortality model
MODEL_A_WEIGHTS: dict[str, float] = {
    'Heart Failure': 0.3416,
    'Age': -0.01305,
    '(Age - 66) ^ 3': 0.0001723,
    '(Age - 74) ^ 3': -0.0003446,
    '(Age - 82) ^ 3': 0.0001723,
    'NT-proBNP in ng/L': 0.04248,
    '(NT-proBNP in ng/L - 5.303) ^ 3': 0.04728,
    '(NT-proBNP in ng/L - 6.708) ^ 3': -0.1139,
    '(NT-proBNP in ng/L - 7.705) ^ 3': 0.0666,
    'GDF-15 in ng/L': 0.7963,
    '(GDF-15 in ng/L - 6.608) ^ 3': -0.1923,
    '(GDF-15 in ng/L - 7.231) ^ 3': 0.341,
    '(GDF-15 in ng/L - 8.037) ^ 3': -0.1487,
    'Troponin T in ng/L': 0.6875,
    '(Troponin T in ng/L - 1.705) ^ 3': -0.07336,
    '(Troponin T in ng/L - 2.389) ^ 3': 0.1344,
    '(Troponin T in ng/L - 3.211) ^ 3': -0.06104
}

MODEL_A_SPLINE_TERMS = {
    'Age': (66, 74, 82),
    'NT-proBNP in ng/L': (5.303, 6.708, 7.705),
    'GDF-15 in ng/L': (6.608, 7.231, 8.037),
    'Troponin T in ng/L': (1.705, 2.389, 3.211)
}

# Model B: Cardiovascular mortality model
MODEL_B_WEIGHTS: dict[str, float] = {
    'Heart Failure': 0.4635,
    'Age': -0.01244,
    '(Age - 71) ^ 3': 0.0003442,
    '(Age - 77) ^ 3': -0.0006393,
    '(Age - 84) ^ 3': 0.0002951,
    'NT-proBNP in ng/L': 0.05166,
    '(NT-proBNP in ng/L - 5.303) ^ 3': 0.05677,
    '(NT-proBNP in ng/L - 6.708) ^ 3': -0.1367,
    '(NT-proBNP in ng/L - 7.705) ^ 3': 0.07998,
    'GDF-15 in ng/L': 0.4796,
    '(GDF-15 in ng/L - 6.608) ^ 3': -0.1769,
    '(GDF-15 in ng/L - 7.231) ^ 3': 0.3137,
    '(GDF-15 in ng/L - 8.037) ^ 3': -0.1368,
    'Troponin T in ng/L': 1.026,
    '(Troponin T in ng/L - 1.705) ^ 3': -0.1508,
    '(Troponin T in ng/L - 2.389) ^ 3': 0.2763,
    '(Troponin T in ng/L - 3.211) ^ 3': -0.1255
}

MODEL_B_SPLINE_TERMS = {
    'Age': (71, 77, 84),
    'NT-proBNP in ng/L': (5.303, 6.708, 7.705),
    'GDF-15 in ng/L': (6.608, 7.231, 8.037),
    'Troponin T in ng/L': (1.705, 2.389, 3.211)
}


def __calc_score__(parameters: dict[str, bool | float | int],
                   weights: dict[str, float],
                   spline_terms: dict[str, tuple[float, float, float] | tuple[int, int, int]],
                   base: float,
                   exponent: float) -> float:

    for parameter, terms in spline_terms.items():
        parameters |= {f"({parameter} - {x}) ^ 3": max(0.0, parameters[parameter] - x) ** 3 for x in terms}

    x = sum([parameters[parameter] * weight for parameter, weight in weights.items()])
    one_year_risk = (1 - math.pow(base, math.exp(x - exponent)))
    return one_year_risk * 100


@batch_process
@check_ranges
def calc_abc_af_death_score(parameters: Parameters) -> tuple[float, float]:
    model_a_new_parameters = {'Heart Failure': parameters['Heart Failure'],
                              'NT-proBNP in ng/L': math.log(max(200.0, parameters['NT-proBNP in ng/L'])),
                              'GDF-15 in ng/L': math.log(parameters['GDF-15 in ng/L']),
                              'Troponin T in ng/L': math.log(parameters['Troponin T in ng/L'])}
    model_b_new_parameters = model_a_new_parameters.copy()
    model_a_new_parameters['Age'] = max(65, parameters['Age'])
    model_b_new_parameters['Age'] = max(70, parameters['Age'])

    model_a = __calc_score__(model_a_new_parameters, MODEL_A_WEIGHTS, MODEL_A_SPLINE_TERMS, 0.9763, 7.218)
    model_b = __calc_score__(model_b_new_parameters, MODEL_B_WEIGHTS, MODEL_B_SPLINE_TERMS, 0.9876, 5.952)
    return model_a, model_b
