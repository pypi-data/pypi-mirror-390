import unittest
import platform
import os

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element
from typing import Literal

from parameter_generator import generate_barcelona_hf_v3_parameters
from acribis_scores.barcelona_hf_v3 import calc_barcelona_hf_score, Parameters

TEST_EXCEL = False
if (platform.system() == 'Windows' and os.path.isfile('resources/calculator_death_v03.xlsm')
        and os.path.isfile('resources/calculator_hosp_competingrisk_v03.xlsm')
        and os.path.isfile('resources/calculator_hosp_death_v03.xlsm')):
    import openpyxl
    import win32com.client as win32

    # TEST_EXCEL = True


class TestBarcelonaBioHF(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_barcelona_bio_hf(self):
        for i in range(10):
            parameters = generate_barcelona_hf_v3_parameters()
            print(Parameters.__annotations__)
            print(parameters)
            r_score = self.__get_r_score(parameters)
            python_score = calc_barcelona_hf_score(parameters)
            p_le_wob = python_score['without_biomarkers']['life_expectancy']
            r_le_wob = r_score['without_biomarkers']['life_expectancy']
            try:
                p_le_wob = float(python_score['without_biomarkers']['life_expectancy'])
                r_le_wob = float(r_score['without_biomarkers']['life_expectancy'])
            except ValueError:
                pass
            self.assertEqual(p_le_wob, r_le_wob)

            if 'with_biomarkers' in python_score:
                p_le_wb = python_score['with_biomarkers']['life_expectancy']
                r_le_wb = r_score['with_biomarkers']['life_expectancy']
                try:
                    p_le_wb = float(python_score['with_biomarkers']['life_expectancy'])
                    r_le_wb = float(r_score['with_biomarkers']['life_expectancy'])
                except ValueError:
                    pass
                self.assertEqual(p_le_wb, r_le_wb)

            if 'with_biomarkers' in python_score:
                del python_score['with_biomarkers']['life_expectancy']
                del r_score['with_biomarkers']['life_expectancy']
            del python_score['without_biomarkers']['life_expectancy']
            del r_score['without_biomarkers']['life_expectancy']
            self.assertEqual(python_score, r_score)
            if TEST_EXCEL:
                excel_score = self.__get_excel_score(parameters)
                print(python_score)
                print(excel_score)

    def __get_r_score(self, parameters: Parameters) -> dict[str, dict[str, None | list[float] | str]]:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='Barcelona HF Score']").click()
        mapping_bool: dict[str, str] = {
            'Female': 'female',
            'Statin': 'statin',
            'ACEi/ARB': 'acei_arb',
            'Betablockers': 'betablocker',
            'Diabetes Mellitus': 'diabetes',
            'MRA': 'mra',
            'ICD': 'icd',
            'CRT': 'crt',
            'ARNI': 'arni',
            'SGLT2i': 'sglt2i'
        }
        mapping_number: dict[str, str] = {
            'Age (years)': 'barcelona_age',
            'Ejection fraction (%)': 'barcelona_ef',
            'Sodium (mmol/L)': 'sodium',
            'eGFR in mL/min/1.73m²': 'egfr',
            'Hemoglobin (g/dL)': 'hemoglobin',
            'Loop Diuretic Furosemide Dose': 'loop_diuretic_furosemide',
            'Loop Diuretic Torasemide Dose': 'loop_diuretic_torasemide',
            'HF Duration in months': 'hf_duration',
            'Hospitalisation Prev. Year': 'hosp_prev_year'
        }
        mapping_not_required: dict[Literal['NT-proBNP in pg/mL', 'hs-cTnT in ng/L', 'ST2 (ng/mL)'], str] = {
            'NT-proBNP in pg/mL': 'nt_pro_bnp',
            'hs-cTnT in ng/L': 'hs_ctnt',
            'ST2 (ng/mL)': 'st2'
        }

        self.driver.find_elements(By.CSS_SELECTOR, ".selectize-input")[1].click()
        self.driver.find_element(By.CSS_SELECTOR,
                                 f"div[class*='option'][data-value='{parameters['NYHA Class']}']").click()
        for key, value in parameters.items():
            if key not in mapping_number:
                continue
            element = self.driver.find_element(By.ID, mapping_number[key])
            element.click()
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(str(value))
        for key, value in parameters.items():
            if key not in mapping_bool:
                continue
            if value != (self.driver.find_element(By.ID, mapping_bool[key]).get_attribute('checked') is not None):
                self.driver.find_element(By.ID, mapping_bool[key]).click()
        with_biomarkers = False
        for key in mapping_not_required:
            element = self.driver.find_element(By.ID, mapping_not_required[key])
            element.click()
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.DELETE)
            if key in parameters:
                element.send_keys(str(parameters[key]))
                with_biomarkers = True
        self.driver.find_element(By.ID, "calculate_barcelona").click()
        WebDriverWait(self.driver, 5).until(
            text_to_be_present_in_element((By.ID, "score_output_barcelona"), "The calculated Barcelona HF scores are:"))
        text = self.driver.find_element(By.ID, "score_output_barcelona").text
        text = text.removeprefix('The calculated Barcelona HF scores are:\n')
        lines = text.split('\n')
        results = {line.split(' : ')[0]: line.split(' : ')[1] for line in lines}
        all_scores: dict[str, dict[str, None | list[float] | str]] = {'without_biomarkers': {'death': None,
                                                                                             'life_expectancy': None,
                                                                                             'hosp': None,
                                                                                             'hosp_death': None}}
        if with_biomarkers:
            all_scores['with_biomarkers'] = {'death': None,
                                             'life_expectancy': None,
                                             'hosp': None,
                                             'hosp_death': None}
        for key, value in results.items():
            value_list = []
            split_values = value.split(', ')
            if len(split_values) > 1:
                for v in split_values:
                    value_list.append(float(v))
            model_endpoint = key.split('$')
            all_scores[model_endpoint[0]][model_endpoint[1]] = value_list if len(value_list) > 0 else split_values[0]
        return all_scores

    @staticmethod
    def __get_excel_score(parameters: Parameters) -> dict[str, dict[str, None | list[float] | str]]:
        directory = os.path.dirname(os.path.abspath(__file__))
        scores: dict[str, dict[str, None | list[float] | str]] = {'without_biomarkers': {}}
        for f in ['calculator_death_v03', 'calculator_hosp_competingrisk_v03', 'calculator_hosp_death_v03']:
            current_file_original = os.path.join(directory, f"resources/{f}.xlsm")
            current_file_tmp = os.path.join(directory, f"resources/{f}_TMP.xlsm")

            wb = openpyxl.load_workbook(current_file_original, keep_vba=True)
            ws1 = wb['Calculadora']
            ws2 = wb['Values']

            ws1['B7'] = parameters['Age (years)']
            ws1['B32'] = parameters['Sodium (mmol/L)']
            ws1['B36'] = parameters['eGFR in mL/min/1.73m²']
            ws1['B40'] = parameters['Hemoglobin (g/dL)']
            ws1['B44'] = parameters['Ejection fraction (%)']
            ws1['B48'] = parameters['HF Duration in months']

            model_mapping = {(True, False, False): (5, 'C'),
                             (False, True, False): (6, 'D'),
                             (False, False, True): (7, 'E'),
                             (True, False, True): (8, 'F'),
                             (True, True, False): (9, 'G'),
                             (False, True, True): (10, 'H'),
                             (True, True, True): (11, 'I')}
            result_mapping = {'calculator_death_v03': 'death',
                              'calculator_hosp_competingrisk_v03': 'hosp',
                              'calculator_hosp_death_v03': 'hosp_death'}

            if 'hs-cTnT in ng/L' in parameters:
                ws1['H7'] = parameters['hs-cTnT in ng/L']
            else:
                ws1['H7'] = None
            if 'ST2 (ng/mL)' in parameters:
                ws1['H12'] = parameters['ST2 (ng/mL)']
            else:
                ws1['H12'] = None
            if 'NT-proBNP in pg/mL' in parameters:
                ws1['H17'] = parameters['NT-proBNP in pg/mL']
            else:
                ws1['H17'] = None

            ws2['B41'] = 2 if parameters['Female'] else 1
            ws2['B42'] = 1 if parameters['NYHA Class'] < 3 else 2
            ws2['B43'] = 1 if parameters['Statin'] else 2
            ws2['B44'] = 1 if parameters['ACEi/ARB'] else 2
            ws2['B45'] = 1 if parameters['Betablockers'] else 2
            ws2['B46'] = 1 if parameters['Diabetes Mellitus'] else 2
            ws2['B47'] = 1 if parameters['MRA'] else 2
            ws2['B48'] = 1 if parameters['ICD'] else 2
            ws2['B49'] = 1 if parameters['CRT'] else 2
            ws2['B51'] = 1 if parameters['ARNI'] else 2
            ws2['B52'] = 1 if parameters['SGLT2i'] else 2

            if f == 'calculator_hosp_competingrisk_v03':
                ws1['B28'] = parameters['Hospitalisation Prev. Year']
            else:
                ws2['B50'] = 1 if parameters['Hospitalisation Prev. Year'] > 0 else 2

            wb.save(current_file_tmp)
            wb.close()

            excel = win32.gencache.EnsureDispatch('Excel.Application')
            workbook = excel.Workbooks.Open(current_file_tmp)
            workbook.Save()
            workbook.Close()
            excel.Quit()

            wb = openpyxl.load_workbook(current_file_tmp, data_only=True)
            result_sheet = wb['Calculadora']
            basic1 = result_sheet['M4'].value
            basic2 = result_sheet['O4'].value
            basic3 = result_sheet['Q4'].value
            basic4 = result_sheet['S4'].value
            basic5 = result_sheet['U4'].value
            scores['without_biomarkers'][result_mapping[f]] = [basic1, basic2, basic3, basic4, basic5]
            if any(p in parameters for p in ['NT-proBNP in pg/mL', 'hs-cTnT in ng/L', 'ST2 (ng/mL)']):
                if 'with_biomarkers' not in scores:
                    scores['with_biomarkers'] = {}
                row = model_mapping[
                    ('NT-proBNP in pg/mL' in parameters, 'hs-cTnT in ng/L' in parameters, 'ST2 (ng/mL)' in parameters)]
                bm1 = result_sheet[f"M{row[0]}"].value
                bm2 = result_sheet[f"O{row[0]}"].value
                bm3 = result_sheet[f"Q{row[0]}"].value
                bm4 = result_sheet[f"S{row[0]}"].value
                bm5 = result_sheet[f"U{row[0]}"].value
                scores['with_biomarkers'][result_mapping[f]] = [bm1, bm2, bm3, bm4, bm5]
                if f == 'calculator_death_v03' and all(
                        p in parameters for p in ['NT-proBNP in pg/mL', 'hs-cTnT in ng/L', 'ST2 (ng/mL)']):
                    le = str(wb['Esperanza de vida'][f"I30"].value)
                    if le == '30+' or int(le) >= 20:
                        le = '>20'
                    scores['with_biomarkers']['life_expectancy'] = le
                    le = str(wb['Esperanza de vida']['B30'].value)
                    if le == '30+' or int(le) >= 20:
                        le = '>20'
                    scores['without_biomarkers']['life_expectancy'] = le
            return scores


if __name__ == '__main__':
    unittest.main()
