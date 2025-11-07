import math
import typing
import pandas as pd
from enum import Enum
from importlib import resources as ir
from typing import TypedDict, Any, Annotated

import acribis_scores.resources as bcn_resources
from acribis_scores.batch_processing import batch_process
from acribis_scores.value_range import ValueRange, check_ranges


class Model(Enum):
    MODEL_1 = "Basic Clinical Model"
    MODEL_2 = "Basic model with NT-proBNP"
    MODEL_3 = "Basic model with hs-cTnT"
    MODEL_4 = "Basic model with ST2"
    MODEL_5 = "Basic model with NT-proBNP and ST2"
    MODEL_6 = "Basic model with NT-proBNP and hs-cTnT"
    MODEL_7 = "Basic model with hs-cTNT and ST2"
    MODEL_8 = "Basic model with NT-proBNP + hs-cTNT + ST2"


Parameters = TypedDict('Parameters', {
    'Age (years)': int,
    'Female': bool,
    'NYHA Class': Annotated[int, ValueRange(1, 4)],
    'Ejection fraction (%)': typing.NotRequired[int],
    'Sodium (mmol/L)': typing.NotRequired[int],
    'eGFR in mL/min/1.73m²': typing.NotRequired[int],
    'Hemoglobin (g/dL)': typing.NotRequired[float],
    'Loop Diuretic Furosemide Dose': int,
    'Loop Diuretic Torasemide Dose': int,
    'Statin': bool,
    'ACEi/ARB': bool,
    'Betablockers': bool,
    'HF Duration in months': typing.NotRequired[Annotated[int, ValueRange(1, 1000)]],
    'Diabetes Mellitus': bool,
    'Hospitalisation Prev. Year': int,
    'MRA': bool,
    'ICD': bool,
    'CRT': bool,
    'ARNI': bool,
    'NT-proBNP in pg/mL': typing.NotRequired[int],
    'hs-cTnT in ng/L': typing.NotRequired[float],
    'ST2 (ng/mL)': typing.NotRequired[float],
    'SGLT2i': bool,
})

#   The values in the min-max-median below is taken from the v3 disclaimer (terms of use).
#   Edit: 02.01.2025: Replaced with values from the Excel sheets provided by the author
MIN_MAX_MEDIAN = pd.DataFrame(
    {
        'lower_limit': [31.31446954141, 13, 128, 7.63881506570324, 8.9, 37.45, 4.8245, 6.29, 0, 0],
        'upper_limit': [90.9212046543464, 78.71, 145, 119.283356873844, 16.771, 34800, 242.84, 171.1, 257.040000000001,
                        5.71000000000004],
        'median_impute': [70.3, 35, 138, 60.613452863849, 12.9, 1361.5, 22.6, 38.1, 6, 0]
    },
    index=['Age (years)', 'Ejection fraction (%)', 'Sodium (mmol/L)', 'eGFR in mL/min/1.73m²',
           'Hemoglobin (g/dL)', 'NT-proBNP in pg/mL', 'hs-cTnT in ng/L', 'ST2 (ng/mL)',
           'HF Duration in months', 'Hospitalisation Prev. Year']
)

IMPUTABLE_PARAMETERS = ['Ejection fraction (%)',
                        'Sodium (mmol/L)',
                        'eGFR in mL/min/1.73m²',
                        'Hemoglobin (g/dL)',
                        'HF Duration in months']


def check_values(parameter_value, parameter_name, min_max_median):
    lower_limit = min_max_median["lower_limit"][parameter_name]
    upper_limit = min_max_median["upper_limit"][parameter_name]
    median_impute = min_max_median["median_impute"][parameter_name]
    if parameter_value is None:
        parameter_value = median_impute if not math.isnan(median_impute) else None
    elif parameter_value < lower_limit:
        parameter_value = lower_limit
    elif parameter_value > upper_limit:
        parameter_value = upper_limit
    return parameter_value


def get_model(parameters):
    if ('NT-proBNP in pg/mL' in parameters and
            ('hs-cTnT in ng/L' not in parameters and 'ST2 (ng/mL)' not in parameters)):
        model = Model.MODEL_2
    elif ('hs-cTnT in ng/L' in parameters and
          ('NT-proBNP in pg/mL' not in parameters and 'ST2 (ng/mL)' not in parameters)):
        model = Model.MODEL_3
    elif ('ST2 (ng/mL)' in parameters and
          ('NT-proBNP in pg/mL' not in parameters and 'hs-cTnT in ng/L' not in parameters)):
        model = Model.MODEL_4
    elif (('NT-proBNP in pg/mL' in parameters and 'ST2 (ng/mL)' in parameters) and
          'hs-cTnT in ng/L' not in parameters):
        model = Model.MODEL_5
    elif (('NT-proBNP in pg/mL' in parameters and 'hs-cTnT in ng/L' in parameters) and
          'ST2 (ng/mL)' not in parameters):
        model = Model.MODEL_6
    elif (('hs-cTnT in ng/L' in parameters and 'ST2 (ng/mL)' in parameters) and
          'NT-proBNP in pg/mL' not in parameters):
        model = Model.MODEL_7
    elif 'NT-proBNP in pg/mL' in parameters and 'hs-cTnT in ng/L' in parameters and 'ST2 (ng/mL)' in parameters:
        model = Model.MODEL_8
    else:
        model = Model.MODEL_1
    return model


def get_coefficients(model, model_coefficients):
    coefficients = model_coefficients[model.name][:-6]
    sum_product = model_coefficients[model.name]['Sum_Product']
    return coefficients, sum_product


def get_survival_estimate(model, survival_year, model_coefficients) -> float:
    if survival_year == 1:
        survival_estimate = model_coefficients[model.name]['One_year_survival']
    elif survival_year == 2:
        survival_estimate = model_coefficients[model.name]['Two_year_survival']
    elif survival_year == 3:
        survival_estimate = model_coefficients[model.name]['Three_year_survival']
    elif survival_year == 4:
        survival_estimate = model_coefficients[model.name]['Four_year_survival']
    elif survival_year == 5:
        survival_estimate = model_coefficients[model.name]['Five_year_survival']
    else:
        raise ValueError(f"'survival_year' must be between 1 and 6 ('{survival_year}' was provided)!")
    return survival_estimate


def get_new_parameters(parameters):
    new_parameters = dict({key: value for key, value in parameters.items()})
    new_parameters['NYHA Class'] = 0 if parameters['NYHA Class'] in [1, 2] else 1
    new_parameters['Ejection fraction (%)'] = 0 if parameters['Ejection fraction (%)'] <= 45 else 1
    new_parameters['log(HF Duration in months)'] = math.log(parameters['HF Duration in months'])
    loop_diuretic_dose = parameters['Loop Diuretic Furosemide Dose'] + 4 * parameters['Loop Diuretic Torasemide Dose']
    new_parameters['Furosemide Dose 1'] = 1 if 0 < loop_diuretic_dose <= 40 else 0
    new_parameters['Furosemide Dose 2'] = 1 if 40 < loop_diuretic_dose <= 80 else 0
    new_parameters['Furosemide Dose 3'] = 1 if loop_diuretic_dose > 80 else 0
    if 'NT-proBNP in pg/mL' in parameters:
        new_parameters['log(NT-proBNP in pg/mL)'] = \
            0 if parameters['NT-proBNP in pg/mL'] == 0 else math.log(parameters['NT-proBNP in pg/mL'])
    if 'hs-cTnT in ng/L' in parameters:
        new_parameters['log(hs-cTnT in ng/L)'] = \
            0 if parameters['hs-cTnT in ng/L'] == 0 else math.log(parameters['hs-cTnT in ng/L'])
        new_parameters['Squared log(hs-cTnT in ng/L)'] = math.pow(new_parameters['log(hs-cTnT in ng/L)'], 2)
    if 'ST2 (ng/mL)' in parameters:
        new_parameters['ST2_div_10'] = parameters['ST2 (ng/mL)'] / 10
        new_parameters['Squared ST2_div_10'] = math.pow(new_parameters['ST2_div_10'], 2)
    return new_parameters


def get_scores(file, model, new_parameters):
    scores = []
    with file.open('r', encoding='utf-8') as f:
        model_beta_coefficients = pd.read_csv(f, index_col='Variables')
    coefficients, sum_product = get_coefficients(model, model_beta_coefficients)
    if file.name == 'barcelona_hf_v3_hosp_coefficients.csv':
        sum_product_all_parameters = sum(
            [new_parameters[parameter] * coeff for parameter, coeff in coefficients.items() if
             parameter in new_parameters]
        )
    else:
        new_parameters_copy = {key: value for key, value in new_parameters.items()}
        new_parameters_copy['Hospitalisation Prev. Year'] = bool(new_parameters_copy['Hospitalisation Prev. Year'])
        sum_product_all_parameters = sum(
            [new_parameters_copy[parameter] * coeff for parameter, coeff in coefficients.items() if
             parameter in new_parameters_copy]
        )
    for year in range(1, 6):
        survival_estimate = get_survival_estimate(model, year, model_beta_coefficients)
        score = (1 - math.pow(survival_estimate, math.exp(sum_product_all_parameters - sum_product))) * 100
        scores.append(round(score, 1))
    return scores


def calc_life_expectancy(model, new_parameters):
    coefficients_life_expectancy = (ir.files(bcn_resources) / 'barcelona_hf_v3_life_expectancy_coefficients.csv')
    life_expectancy_limits = (ir.files(bcn_resources) / 'life_expectancy_limits.csv')
    with (coefficients_life_expectancy.open('r', encoding='utf-8') as f1,
          life_expectancy_limits.open('r', encoding='utf-8') as f2):
        le_coefficients = pd.read_csv(f1, index_col='Variables')
        le_limits = pd.read_csv(f2)
    coefficients = le_coefficients[model.name][:-2]
    new_parameters_copy = dict({key: value for key, value in new_parameters.items()})
    new_parameters_copy['Hospitalisation Prev. Year'] = bool(new_parameters_copy['Hospitalisation Prev. Year'])
    sum_product_all_parameters = sum(
        [new_parameters_copy[parameter] * coeff for parameter, coeff in coefficients.items() if
         parameter in new_parameters_copy]
    )
    intercept = le_coefficients[model.name]['Intercept']
    gamma_value = le_coefficients[model.name]['Gamma Value']
    le = math.exp(intercept + sum_product_all_parameters) * gamma_value
    key = 'Women' if new_parameters['Female'] else 'Men'
    age = int(new_parameters['Age (years)'])
    if age in list(le_limits['Age']):
        if (key == 'Men' and age > 63) or (key == 'Women' and age > 67):
            upper_limit = le_limits.loc[le_limits['Age'] == int(new_parameters['Age (years)']), key].iloc[0]
            if le > float(upper_limit):
                le = upper_limit
    if le > 20:
        if key == 'Men' and age <= 63:
            le = '>20'
        elif key == 'Women' and age <= 67:
            le = '>20'
    return le


def _round_life_expectancy(model, parameters):
    life_expectancy = calc_life_expectancy(model, parameters)
    try:
        life_expectancy = round(float(life_expectancy), 1)
    except ValueError:
        pass
    return life_expectancy


@batch_process
@check_ranges
def calc_barcelona_hf_score(parameters: Parameters) -> dict[str, dict[str, list[float] | Any]]:
    all_scores = {}
    coefficients_death_file = (ir.files(bcn_resources) / 'barcelona_hf_v3_death_coefficients.csv')
    coefficients_hosp_file = (ir.files(bcn_resources) / 'barcelona_hf_v3_hosp_coefficients.csv')
    coefficients_hosp_death_file = (ir.files(bcn_resources) / 'barcelona_hf_v3_hosp_death_coefficients.csv')
    model = get_model(parameters)

    for param in MIN_MAX_MEDIAN.index.to_list():
        if param in parameters:
            parameters[param] = check_values(parameters[param], param, MIN_MAX_MEDIAN)  # type: ignore
        elif param in IMPUTABLE_PARAMETERS:
            parameters[param] = check_values(None, param, MIN_MAX_MEDIAN)  # type: ignore

    new_parameters = get_new_parameters(parameters)
    endpoints_without_biomarkers, endpoints_with_biomarkers = {}, {}
    for file in [coefficients_death_file, coefficients_hosp_file, coefficients_hosp_death_file]:
        suffix = file.name[16:-17]
        scores_without_biomarkers = get_scores(file, Model.MODEL_1, new_parameters)
        endpoints_without_biomarkers[suffix] = scores_without_biomarkers

        if model.name != 'MODEL_1':
            scores_with_biomarkers = get_scores(file, model, new_parameters)
            endpoints_with_biomarkers[suffix] = scores_with_biomarkers

        if file.name == 'barcelona_hf_v3_death_coefficients.csv':
            le_without_biomarkers = _round_life_expectancy(Model.MODEL_1, new_parameters)
            endpoints_without_biomarkers['life_expectancy'] = str(le_without_biomarkers)

            if model.name != 'MODEL_1':
                le_with_biomarkers = _round_life_expectancy(model, new_parameters)
                endpoints_with_biomarkers['life_expectancy'] = str(le_with_biomarkers)

    all_scores['without_biomarkers'] = endpoints_without_biomarkers
    if model.name != 'MODEL_1':
        all_scores['with_biomarkers'] = endpoints_with_biomarkers

    return all_scores
