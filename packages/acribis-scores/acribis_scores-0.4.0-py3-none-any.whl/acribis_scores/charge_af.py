import math
from typing import TypedDict, Annotated

from acribis_scores.batch_processing import batch_process
from acribis_scores.value_range import ValueRange, check_ranges

# See https://doi.org/10.1161/JAHA.112.000102

Parameters = TypedDict('Parameters', {
    'Age': Annotated[int, ValueRange(46, 94)],
    'Race (white)': bool,
    'Height': Annotated[int, ValueRange(122, 239)],
    'Weight': Annotated[float, ValueRange(32, 185)],
    'Systolic Blood Pressure': Annotated[int, ValueRange(71, 248)],
    'Diastolic Blood Pressure': Annotated[int, ValueRange(23, 136)],
    'Smoking (current)': bool,
    'Antihypertensive Medication Use (Yes)': bool,
    'Diabetes (Yes)': bool,
    'Heart failure (Yes)': bool,
    'Myocardial infarction (Yes)': bool
})

WEIGHTS: dict[str, float] = {
    'Age': 0.508,
    'Race (white)': 0.465,
    'Height': 0.248,
    'Weight': 0.115,
    'Systolic Blood Pressure': 0.197,
    'Diastolic Blood Pressure': -0.101,
    'Smoking (current)': 0.359,
    'Antihypertensive Medication Use (Yes)': 0.349,
    'Diabetes (Yes)': 0.237,
    'Heart failure (Yes)': 0.701,
    'Myocardial infarction (Yes)': 0.496
}

SCALES: dict[str, int] = {
    'Age': 5,
    'Race (white)': 1,
    'Height': 10,
    'Weight': 15,
    'Systolic Blood Pressure': 20,
    'Diastolic Blood Pressure': 10,
    'Smoking (current)': 1,
    'Antihypertensive Medication Use (Yes)': 1,
    'Diabetes (Yes)': 1,
    'Heart failure (Yes)': 1,
    'Myocardial infarction (Yes)': 1
}


@batch_process
@check_ranges
def calc_charge_af_score(parameters: Parameters) -> float:
    x = sum([(value / SCALES[parameter]) * WEIGHTS[parameter] for parameter, value in parameters.items()])
    return (1 - math.pow(0.9718412736, math.exp(x + -12.58156))) * 100
