import math
from typing import TypedDict, Annotated

from acribis_scores.batch_processing import batch_process
from acribis_scores.value_range import ValueRange, check_ranges

# See: https://doi.org/10.1093/eurheartj/ehw054
# And: https://www.ahajournals.org/action/downloadSupplement?doi=10.1161%2FCIRCULATIONAHA.120.053100&file=Supplement_210420_final.pdf#subsection.2.1
# S0(365) = 0.9863 (according to document sent by Ziad Hijazi) instead of 0.9864

Parameters = TypedDict('Parameters', {
    'Prior Stroke/TIA': bool,
    'Age': Annotated[int, ValueRange(22, 95)],
    'Troponin T in ng/L': Annotated[float, ValueRange(3.0, 200.0)],
    'NT-proBNP in ng/L': Annotated[int, ValueRange(5, 21000)],
    'DOAC': bool,
    'Aspirin': bool
})

WEIGHTS: dict[str, float] = {
    'Prior Stroke/TIA': 0.8331,
    'Age': 0.007488,
    'log(Troponin T in ng/L)': 0.2139,
    'log(NT-proBNP in ng/L)': 0.2879
}


@batch_process
@check_ranges
def calc_abc_af_stroke_score(parameters: Parameters) -> float:
    if not any([parameters['DOAC'], parameters['Aspirin']]):
        raise ValueError("Either 'DOAC' or 'Aspirin' must be true!")
    if parameters['DOAC'] and parameters['Aspirin']:
        raise ValueError("'DOAC' and 'Aspirin' cannot both be true!")
    new_parameters = dict({key: value for key, value in parameters.items()})
    new_parameters['log(Troponin T in ng/L)'] = math.log(parameters['Troponin T in ng/L'])
    new_parameters['log(NT-proBNP in ng/L)'] = math.log(parameters['NT-proBNP in ng/L'])
    linear_predictor = sum([new_parameters[parameter] * weight for parameter, weight in WEIGHTS.items()]) - 3.286
    baseline_survival = 0.9863
    if parameters['Aspirin']:
        linear_predictor = 0.25627 + 1.0426 * linear_predictor
        baseline_survival = 0.9673
    one_year_risk = (1 - math.pow(baseline_survival, math.exp(linear_predictor)))
    return one_year_risk * 100
