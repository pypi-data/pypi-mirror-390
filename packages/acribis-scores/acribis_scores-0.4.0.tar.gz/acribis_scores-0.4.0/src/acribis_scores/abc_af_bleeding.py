import math
from typing import TypedDict, Annotated

from acribis_scores.batch_processing import batch_process
from acribis_scores.value_range import ValueRange, check_ranges

# See: https://doi.org/10.1016/S0140-6736(16)00741-8
# And: https://www.ahajournals.org/action/downloadSupplement?doi=10.1161%2FCIRCULATIONAHA.120.053100&file=Supplement_210420_final.pdf#subsection.2.1

Parameters = TypedDict('Parameters', {
    'Prior Bleeding': bool,
    'Age': Annotated[int, ValueRange(22, 95)],
    'Troponin T in ng/L': Annotated[float, ValueRange(3.0, 200.0)],
    'GDF-15 in ng/L': Annotated[float, ValueRange(400.0, 20000.0)],
    'Hemoglobin in g/dL': Annotated[float, ValueRange(9.0, 20.0)],
    'DOAC': bool,
    'Aspirin': bool
})

WEIGHTS: dict[str, float] = {
    'Prior Bleeding': 0.2611,
    'Age': 0.02168,
    'log(Troponin T in ng/L)': 0.4095,
    'log(GDF-15 in ng/L)': 0.4134,
    'Hemoglobin in g/dL': -0.08541
}


@batch_process
@check_ranges
def calc_abc_af_bleeding_score(parameters: Parameters) -> float:
    if not any([parameters['DOAC'], parameters['Aspirin']]):
        raise ValueError("Either 'DOAC' or 'Aspirin' must be true!")
    if parameters['DOAC'] and parameters['Aspirin']:
        raise ValueError("'DOAC' and 'Aspirin' cannot both be true!")
    new_parameters = dict({key: value for key, value in parameters.items()})
    new_parameters['log(Troponin T in ng/L)'] = math.log(parameters['Troponin T in ng/L'])
    new_parameters['log(GDF-15 in ng/L)'] = math.log(parameters['GDF-15 in ng/L'])
    linear_predictor = sum([new_parameters[parameter] * weight for parameter, weight in WEIGHTS.items()]) - 4.667
    baseline_survival = 0.9766
    if parameters['Aspirin']:
        linear_predictor = 0.19965 + 1.2579 * linear_predictor
        baseline_survival = 0.9914
    one_year_risk = (1 - math.pow(baseline_survival, math.exp(linear_predictor)))
    return one_year_risk * 100
