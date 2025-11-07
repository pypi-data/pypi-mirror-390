from typing import TypedDict, Annotated

from acribis_scores.batch_processing import batch_process
from acribis_scores.value_range import ValueRange, check_ranges

# See: https://doi.org/10.1093/eurheartj/ehs337
# And: https://academic.oup.com/view-large/figure/89301700/ehs33702.jpeg
# Online calculator: http://www.heartfailurerisk.org/

Parameters = TypedDict('Parameters', {
    'Ejection fraction (%)': Annotated[int, ValueRange(1, 95)],
    'Age (years)': Annotated[int, ValueRange(18, 110)],
    'Systolic blood pressure (mmHg)': Annotated[int, ValueRange(50, 250)],
    'BMI (kg/m²)': Annotated[int, ValueRange(10, 50)],
    'Creatinine (µmol/l)': Annotated[int, ValueRange(20, 1400)],
    'NYHA Class': Annotated[int, ValueRange(1, 4)],
    'Male': bool,
    'Current smoker': bool,
    'Diabetic': bool,
    'Diagnosis of COPD': bool,
    'First diagnosis of heart failure in the past 18 months': bool,
    'Not on beta blocker': bool,
    'Not on ACEI/ARB': bool
})


def get_ef_score(lv_ef: int) -> int:
    if lv_ef < 20:
        return 7
    if lv_ef <= 24:
        return 6
    if lv_ef <= 29:
        return 5
    if lv_ef <= 34:
        return 3
    if lv_ef <= 39:
        return 2
    return 0


def get_age_score(age: int, lv_ef: int) -> int:
    score_matrix = [[0, 1, 2, 4, 6, 8, 10],
                    [0, 2, 4, 6, 8, 10, 13],
                    [0, 3, 5, 7, 9, 12, 15]]
    if lv_ef < 30:
        lv_ef_index = 0
    elif lv_ef <= 39:
        lv_ef_index = 1
    else:
        lv_ef_index = 2

    if age < 55:
        age_index = 0
    elif age <= 59:
        age_index = 1
    elif age <= 64:
        age_index = 2
    elif age <= 69:
        age_index = 3
    elif age <= 74:
        age_index = 4
    elif age <= 79:
        age_index = 5
    else:
        age_index = 6
    return score_matrix[lv_ef_index][age_index]


def get_sbp_score(sbp: int, lv_ef: int) -> int:
    score_matrix = [[5, 4, 3, 2, 1, 0],
                    [3, 2, 1, 1, 0, 0],
                    [2, 1, 1, 0, 0, 0]]
    if lv_ef < 30:
        lv_ef_index = 0
    elif lv_ef <= 39:
        lv_ef_index = 1
    else:
        lv_ef_index = 2

    if sbp < 110:
        sbp_index = 0
    elif sbp <= 119:
        sbp_index = 1
    elif sbp <= 129:
        sbp_index = 2
    elif sbp <= 139:
        sbp_index = 3
    elif sbp <= 149:
        sbp_index = 4
    else:
        sbp_index = 5
    return score_matrix[lv_ef_index][sbp_index]


def get_bmi_score(bmi: int) -> int:
    if bmi < 15:
        return 6
    if bmi <= 19:
        return 5
    if bmi <= 24:
        return 3
    if bmi <= 29:
        return 2
    return 0


def get_creatinine_score(creatinine: int) -> int:
    if creatinine < 90:
        return 0
    if creatinine <= 109:
        return 1
    if creatinine <= 129:
        return 2
    if creatinine <= 149:
        return 3
    if creatinine <= 169:
        return 4
    if creatinine <= 209:
        return 5
    if creatinine <= 249:
        return 6
    else:
        return 8


def get_nyha_class_score(nyha_class: int) -> int:
    score_array = [0, 2, 6, 8]
    return score_array[nyha_class - 1]


@batch_process
@check_ranges
def calc_maggic_score(parameters: Parameters) -> int:
    return (get_ef_score(parameters['Ejection fraction (%)']) +
            get_age_score(parameters['Age (years)'], parameters['Ejection fraction (%)']) +
            get_sbp_score(parameters['Systolic blood pressure (mmHg)'], parameters['Ejection fraction (%)']) +
            get_bmi_score(parameters['BMI (kg/m²)']) +
            get_creatinine_score(parameters['Creatinine (µmol/l)']) +
            get_nyha_class_score(parameters['NYHA Class']) +
            parameters['Male'] +
            parameters['Current smoker'] +
            parameters['Diabetic'] * 3 +
            parameters['Diagnosis of COPD'] * 2 +
            (not parameters['First diagnosis of heart failure in the past 18 months']) * 2 +
            parameters['Not on beta blocker'] * 3 +
            parameters['Not on ACEI/ARB'])
