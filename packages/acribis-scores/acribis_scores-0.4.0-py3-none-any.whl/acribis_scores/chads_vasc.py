from typing import TypedDict
from acribis_scores.batch_processing import batch_process

# See: https://doi.org/10.1378/chest.09-1584

Parameters = TypedDict('Parameters', {
    'Congestive heart failure/LV dysfunction': bool,
    'Hypertension': bool,
    'Age ≥75y': bool,
    'Diabetes mellitus': bool,
    'Stroke/TIA/TE': bool,
    'Vascular diseases': bool,
    'Age 65-74y': bool,
    'Sex category': bool
})

POINTS: dict[str, float] = {
    'Congestive heart failure/LV dysfunction': 1,
    'Hypertension': 1,
    'Age ≥75y': 2,
    'Diabetes mellitus': 1,
    'Stroke/TIA/TE': 2,
    'Vascular diseases': 1,
    'Age 65-74y': 1,
    'Sex category': 1
}


@batch_process
def calc_chads_vasc_score(parameters: Parameters) -> int:
    if parameters['Age ≥75y'] and parameters['Age 65-74y']:
        raise ValueError('Not both age parameters can be true!')
    return sum([value * POINTS[parameter] for parameter, value in parameters.items()])
