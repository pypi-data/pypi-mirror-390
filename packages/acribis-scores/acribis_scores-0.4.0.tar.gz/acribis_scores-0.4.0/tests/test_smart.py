import random
import unittest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from parameter_generator import generate_smart_parameters
from acribis_scores.smart import calc_smart_score, Parameters


class TestSMARTCalculator(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_smart(self):
        for i in range(10):
            creatinine = random.uniform(0.57, 2.26)
            parameters = generate_smart_parameters(creatinine)

            r_score = self.__get_r_score(parameters)
            python_score = calc_smart_score(parameters)
            self.assertEqual(round(python_score, 2), r_score, msg='SMART Score')

    def __get_r_score(self, parameters: Parameters) -> float:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='SMART Score']").click()
        mapping_bool: dict[str, str] = {
            'Male': 'smart_male',
            'Current smoker': 'smart_smoker',
            'Diabetic': 'smart_diabetic',
            'History of coronary artery disease': 'smart_cad',
            'History of cerebrovascular disease': 'smart_cvd',
            'Abdominal aortic aneurysm': 'smart_aaa',
            'Peripheral artery disease': 'smart_pad',
            'Antithrombotic treatment': 'smart_antithrombotic'
        }
        mapping_number: dict[str, str] = {
            'Age in years': 'smart_age',
            'Systolic blood pressure in mmHg': 'smart_systolic_bp',
            'Years since first diagnosis of vascular disease': 'smart_years_vd',
            'HDL-cholesterol in mmol/L': 'smart_hdl',
            'Total cholesterol in mmol/L': 'smart_tc',
            'eGFR in mL/min/1.73m²': 'smart_egfr',
            'hs-CRP in mg/L': 'smart_hscrp'
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
        self.driver.find_element(By.ID, "calculate_smart").click()
        text = self.driver.find_element(By.ID, "score_output_smart").text
        return float(text.split(': ')[1])


if __name__ == '__main__':
    unittest.main()
