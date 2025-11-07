import math
from typing import TypedDict, Annotated

from acribis_scores.batch_processing import batch_process
from acribis_scores.value_range import ValueRange, check_ranges

# See: https://doi.org/10.1136/heartjnl-2013-303640
# And: https://heart.bmj.com/content/heartjnl/99/12/866.full.pdf?with-ds=yes#page=13

# Also (Recalibration): https://doi.org/10.1161/CIRCULATIONAHA.116.021314
# And: https://www.ahajournals.org/action/downloadSupplement?doi=10.1161%2FCIRCULATIONAHA.116.021314&file=021314_supplemental_material.pdf#page=16

# For antithrombotic treatment: https://doi.org/10.1016/S0140-6736(09)60503-1
# And: https://u-prevent.com/calculators/description/smartScore

Parameters = TypedDict('Parameters', {
    'Age in years': Annotated[int, ValueRange(30, 90)],
    'Male': bool,
    'Current smoker': bool,
    'Systolic blood pressure in mmHg': Annotated[int, ValueRange(70, 200)],
    'Diabetic': bool,
    'History of coronary artery disease': bool,
    'History of cerebrovascular disease': bool,
    'Abdominal aortic aneurysm': bool,
    'Peripheral artery disease': bool,
    'Years since first diagnosis of vascular disease': Annotated[int, ValueRange(0, 30)],
    'HDL-cholesterol in mmol/L': Annotated[float, ValueRange(0.6, 2.5)],
    'Total cholesterol in mmol/L': Annotated[float, ValueRange(2.5, 8.0)],
    'eGFR in mL/min/1.73m²': Annotated[float, ValueRange(21.60551, 178.39297)],
    'hs-CRP in mg/L': Annotated[float, ValueRange(0.1, 15.0)],
    'Antithrombotic treatment': bool
})

WEIGHTS: dict[str, float] = {
    'Age in years': -0.085,
    'Squared Age in years': 0.00105,
    'Male': 0.156,
    'Current smoker': 0.262,
    'Systolic blood pressure in mmHg': 0.00429,
    'Diabetic': 0.223,
    'History of coronary artery disease': 0.14,
    'History of cerebrovascular disease': 0.406,
    'Abdominal aortic aneurysm': 0.558,
    'Peripheral artery disease': 0.283,
    'Years since first diagnosis of vascular disease': 0.0229,
    'HDL-cholesterol in mmol/L': -0.426,
    'Total cholesterol in mmol/L': 0.0959,
    'eGFR in mL/min/1.73m²': -0.0532,
    'Squared eGFR in mL/min/1.73m²': 0.000306,
    'log(hs-CRP in mg/L)': 0.139
}


@batch_process
@check_ranges
def calc_smart_score(parameters: Parameters) -> float:
    new_parameters = dict({key: value for key, value in parameters.items()})
    new_parameters['Squared Age in years'] = parameters['Age in years'] ** 2
    new_parameters['Squared eGFR in mL/min/1.73m²'] = parameters['eGFR in mL/min/1.73m²'] ** 2
    new_parameters['log(hs-CRP in mg/L)'] = math.log(parameters['hs-CRP in mg/L'])
    x = sum([new_parameters[parameter] * weight for parameter, weight in WEIGHTS.items()])
    ten_year_risk = (1 - math.pow(0.81066, math.exp(x + 2.099)))
    if new_parameters['History of cerebrovascular disease']:
        cvd_ten_year_risk = (1 - math.pow(0.7184, math.exp(x + 1.933)))
        ten_year_risk = cvd_ten_year_risk if cvd_ten_year_risk > ten_year_risk else ten_year_risk
    if new_parameters['Peripheral artery disease']:
        pad_ten_year_risk = (1 - math.pow(0.70594, math.exp(x + 1.4)))
        ten_year_risk = pad_ten_year_risk if pad_ten_year_risk > ten_year_risk else ten_year_risk
    if not new_parameters['Antithrombotic treatment']:
        ten_year_risk = 1.0 - (1.0 - ten_year_risk) ** (1.0 / 0.81)
    return ten_year_risk * 100
