import time
import unittest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from parameter_generator import generate_maggic_parameters
from acribis_scores.maggic import calc_maggic_score, Parameters


class TestMAGGIC(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_maggic(self):
        for i in range(10):
            parameters = generate_maggic_parameters()
            online_score = self.__get_online_score(parameters)
            r_score = self.__get_r_score(parameters)
            python_score = calc_maggic_score(parameters)
            self.assertEqual(python_score, r_score, 'MAGGIC')
            self.assertEqual(online_score, python_score, 'MAGGIC')

    def __get_online_score(self, parameters: Parameters) -> int:
        self.driver.get('http://www.heartfailurerisk.org/')
        yes_no = {True: 'yes', False: 'no'}
        accept_button = self.driver.find_element(By.ID, 'accept-terms')
        if accept_button.is_displayed():
            self.driver.find_element(By.ID, 'accept-terms').click()
            time.sleep(1)
        self.driver.find_element(By.ID, 'age').send_keys(str(parameters['Age (years)']))
        ActionChains(self.driver).move_by_offset(100, 0).click().perform()
        time.sleep(0.5)
        gender = 'Male' if parameters['Male'] else 'Female'
        dropdown = self.driver.find_element(By.ID, 'gender')
        dropdown.find_element(By.XPATH, f"//option[. = '{gender}']").click()
        self.driver.find_element(By.ID, f"diabetic-{yes_no[parameters['Diabetic']]}").click()
        self.driver.find_element(By.ID, f"copd-{yes_no[parameters['Diagnosis of COPD']]}").click()
        self.driver.find_element(By.ID,
                                 f"heart-failure-{yes_no[parameters['First diagnosis of heart failure in the past 18 months']]}").click()
        self.driver.find_element(By.ID, f"smoker-{yes_no[parameters['Current smoker']]}").click()
        dropdown = self.driver.find_element(By.ID, "nyha")
        dropdown.find_element(By.XPATH, f"//option[. = '{parameters['NYHA Class']}']").click()
        self.driver.find_element(By.ID, f"beta-blockers-{yes_no[not parameters['Not on beta blocker']]}").click()
        self.driver.find_element(By.ID, f"ace-{yes_no[not parameters['Not on ACEI/ARB']]}").click()
        self.driver.find_element(By.ID, "bmi").send_keys(str(parameters['BMI (kg/m²)']))
        self.driver.find_element(By.ID, "bp").send_keys(str(parameters['Systolic blood pressure (mmHg)']))
        self.driver.find_element(By.ID, "creatinine").send_keys(str(parameters['Creatinine (µmol/l)']))
        self.driver.find_element(By.ID, "ejection-fraction").send_keys(str(parameters['Ejection fraction (%)']))
        self.driver.find_element(By.ID, "calculate").click()
        time.sleep(1)
        online_score = int(self.driver.find_element(By.ID, "score-result").text)
        time.sleep(1)
        return online_score

    def __get_r_score(self, parameters: Parameters) -> int:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='MAGGIC Score']").click()
        mapping_bool: dict[str, str] = {
            'Male': 'male',
            'Current smoker': 'smoker',
            'Diabetic': 'diabetic',
            'Diagnosis of COPD': 'copd',
            'First diagnosis of heart failure in the past 18 months': 'first_diagnosis',
            'Not on beta blocker': 'no_beta_blocker',
            'Not on ACEI/ARB': 'no_acei_arb'
        }
        mapping_number: dict[str, str] = {
            'Ejection fraction (%)': 'ef',
            'Age (years)': 'age',
            'Systolic blood pressure (mmHg)': 'sbp',
            'BMI (kg/m²)': 'bmi',
            'Creatinine (µmol/l)': 'creatinine'
        }
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

        self.driver.find_element(By.CSS_SELECTOR, ".selectize-input").click()
        self.driver.find_element(By.CSS_SELECTOR, f"div[class*='option'][data-value='{parameters['NYHA Class']}']").click()
        self.driver.find_element(By.ID, "calculate_maggic").click()
        text = self.driver.find_element(By.ID, "score_output_maggic").text
        return int(text.split(': ')[1])


if __name__ == '__main__':
    unittest.main()
