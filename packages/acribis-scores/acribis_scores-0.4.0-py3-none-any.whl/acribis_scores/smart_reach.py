import math
from enum import Enum
from typing import TypedDict, Annotated

from acribis_scores.batch_processing import batch_process
from acribis_scores.value_range import ValueRange, check_ranges


# See: https://doi.org/10.1161/JAHA.118.009217
# And: https://www.ahajournals.org/action/downloadSupplement?doi=10.1161%2FJAHA.118.009217&file=jah33408-sup-0001-supinfo.pdf#page=11


class Model(Enum):
    CARDIOVASCULAR = 'Cardiovascular model (A)'
    NON_CARDIOVASCULAR = 'Non-cardiovascular mortality model (B)'


Parameters = TypedDict('Parameters', {
    'Age in years': Annotated[int, ValueRange(45, 80)],
    'Male': bool,
    'Current smoker': bool,
    'Diabetes mellitus': bool,
    'Systolic blood pressure in mmHg': Annotated[int, ValueRange(100, 200)],
    'Total cholesterol in mmol/L': Annotated[float, ValueRange(3, 10)],
    'Creatinine in µmol/L': Annotated[float, ValueRange(30, 500)],
    'History of coronary artery disease': bool,
    'History of cerebrovascular disease': bool,
    'Peripheral artery disease': bool,
    'History of atrial fibrillation': bool,
    'History of congestive heart failure': bool,
    'Similar to the Dutch SMART population': bool,
    'Similar to the North American REACH population': bool
})

CV_DISEASES = ['History of coronary artery disease',
               'History of cerebrovascular disease',
               'Peripheral artery disease']

# Model A: Cardiovascular model
MODEL_A_WEIGHTS: dict[str, float] = {
    'Male': 0.072,
    'Current smoker': 0.4309,
    'Diabetes mellitus': 0.4357,
    'Systolic blood pressure in mmHg': -0.02814,
    'Squared systolic blood pressure in mmHg': 0.0001,
    'Total cholesterol in mmol/L': -0.3671,
    'Squared Total cholesterol in mmol/L': 0.0356,
    'Creatinine in µmol/L': 0.00612,
    'Two locations of cardiovascular disease': 0.3176,
    'Three locations of cardiovascular disease': 0.2896,
    'History of atrial fibrillation': 0.2143,
    'History of congestive heart failure': 0.4447,
    'Similar to the Dutch SMART population': -0.4246,
    'Similar to the North American REACH population': 0.1552
}

MODEL_A_BASELINE_SURVIVALS: dict[int, float] = {
    45: 1.0000,
    46: 0.8539,
    47: 0.8420,
    48: 0.9088,
    49: 0.9172,
    50: 0.8464,
    51: 0.7297,
    52: 0.8081,
    53: 0.8980,
    54: 0.8155,
    55: 0.7609,
    56: 0.8113,
    57: 0.8173,
    58: 0.7939,
    59: 0.8382,
    60: 0.8333,
    61: 0.8257,
    62: 0.8000,
    63: 0.7930,
    64: 0.7962,
    65: 0.7807,
    66: 0.7731,
    67: 0.8118,
    68: 0.7325,
    69: 0.7671,
    70: 0.7236,
    71: 0.6690,
    72: 0.7173,
    73: 0.6978,
    74: 0.6074,
    75: 0.6880,
    76: 0.6473,
    77: 0.7034,
    78: 0.6904,
    79: 0.6507,
    80: 0.5946,
    81: 0.5328,
    82: 0.4954,
    83: 0.5376,
    84: 0.4403,
    85: 0.5043,
    86: 0.5509,
    87: 0.5480,
    88: 0.3889,
    89: 0.3048
}

# Model B: Non-cardiovascular mortality model
MODEL_B_WEIGHTS: dict[str, float] = {
    'Male': 0.5986,
    'Current smoker': 4.2538,
    'Age in years': -0.0486,
    'Diabetes mellitus': 0.4065,
    'Systolic blood pressure in mmHg': -0.00741,
    'Total cholesterol in mmol/L': -0.003,
    'Creatinine in µmol/L': -0.01886,
    'Squared Creatinine in µmol/L': 0.00008,
    'Two locations of cardiovascular disease': 0.1442,
    'Three locations of cardiovascular disease': 0.5694,
    'History of atrial fibrillation': 0.3212,
    'History of congestive heart failure': 0.2061,
    'Similar to the Dutch SMART population': 0.1232,
    'Similar to the North American REACH population': 0.4134
}

MODEL_B_BASELINE_SURVIVALS: dict[int, float] = {
    45: 1.0000,
    46: 0.9855,
    47: 1.0000,
    48: 0.9950,
    49: 1.0000,
    50: 1.0000,
    51: 0.9949,
    52: 0.9958,
    53: 1.0000,
    54: 0.9896,
    55: 0.9966,
    56: 0.9935,
    57: 0.9842,
    58: 0.9869,
    59: 0.9935,
    60: 0.9938,
    61: 0.9934,
    62: 0.9734,
    63: 0.9683,
    64: 0.9768,
    65: 0.9725,
    66: 0.9724,
    67: 0.9586,
    68: 0.9683,
    69: 0.9720,
    70: 0.9539,
    71: 0.9439,
    72: 0.9469,
    73: 0.9299,
    74: 0.9369,
    75: 0.9537,
    76: 0.9172,
    77: 0.9018,
    78: 0.9280,
    79: 0.8622,
    80: 0.8688,
    81: 0.8381,
    82: 0.8647,
    83: 0.8478,
    84: 0.8125,
    85: 0.7855,
    86: 0.7284,
    87: 0.7685,
    88: 0.7197,
    89: 0.6469
}


def calc_one_year_survival(parameters: dict[str, int | float | bool], model: Model) -> float:
    if model == Model.CARDIOVASCULAR:
        model_weights = MODEL_A_WEIGHTS
        model_baseline_survivals = MODEL_A_BASELINE_SURVIVALS
    else:
        model_weights = dict(MODEL_B_WEIGHTS)
        model_baseline_survivals = MODEL_B_BASELINE_SURVIVALS
        if not parameters['Current smoker']:
            model_weights['Age in years'] = 0
    x = sum([parameters[parameter] * value for parameter, value in model_weights.items()])
    return math.pow(model_baseline_survivals[parameters['Age in years']], math.exp(x))


@batch_process
@check_ranges
def calc_smart_reach_score(parameters: Parameters) -> tuple[float, float, float] | None:
    n_cardiovascular_diseases = sum([value for parameter, value in parameters.items() if parameter in CV_DISEASES])
    new_parameters = dict({key: value for key, value in parameters.items() if key not in CV_DISEASES})
    new_parameters['Two locations of cardiovascular disease'] = n_cardiovascular_diseases == 2
    new_parameters['Three locations of cardiovascular disease'] = n_cardiovascular_diseases == 3
    new_parameters['Squared systolic blood pressure in mmHg'] = parameters['Systolic blood pressure in mmHg'] ** 2
    new_parameters['Squared Total cholesterol in mmol/L'] = parameters['Total cholesterol in mmol/L'] ** 2
    new_parameters['Squared Creatinine in µmol/L'] = parameters['Creatinine in µmol/L'] ** 2
    cvd_free_survival = 1.0
    no_cv_event = 1.0
    cvd_free_life_expectancy = new_parameters['Age in years']
    ten_year_risk = 0.0
    ten_years_later = new_parameters['Age in years'] + 10
    while new_parameters['Age in years'] < 90:
        cv_risk = 1.0 - calc_one_year_survival(new_parameters, Model.CARDIOVASCULAR)
        non_cv_risk = 1.0 - calc_one_year_survival(new_parameters, Model.NON_CARDIOVASCULAR)
        total_risk = cv_risk + non_cv_risk if cv_risk + non_cv_risk <= 1.0 else 1.0
        cvd_free_survival = cvd_free_survival * (1.0 - total_risk)
        cvd_free_life_expectancy += cvd_free_survival
        no_cv_event = no_cv_event * (1.0 - cv_risk)
        new_parameters['Age in years'] += 1
        if new_parameters['Age in years'] == ten_years_later:
            ten_year_risk = 1.0 - no_cv_event
        print(f"CVD Free Survival: {new_parameters['Age in years']}: {cvd_free_survival}")
    lifetime_risk = 1.0 - no_cv_event
    print(f"Ten year risk of CV event: {ten_year_risk}")
    print(f"Lifetime risk of CV event: {lifetime_risk}")
    print(f"CVD-free life-expectancy: {cvd_free_life_expectancy}")
    return ten_year_risk, lifetime_risk, cvd_free_life_expectancy
