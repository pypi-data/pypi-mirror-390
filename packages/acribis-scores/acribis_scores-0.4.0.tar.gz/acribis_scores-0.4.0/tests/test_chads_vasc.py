import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By

from parameter_generator import generate_chads_vasc_parameters
from acribis_scores.chads_vasc import calc_chads_vasc_score, Parameters


class TestCHADSVAScCalculator(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_chads_vasc(self):
        for i in range(10):
            parameters = generate_chads_vasc_parameters()
            online_score = self.__get_online_score(parameters)
            r_score = self.__get_r_score(parameters)
            python_score = calc_chads_vasc_score(parameters)
            self.assertEqual(python_score, r_score, 'CHA2DS2-VASc')
            self.assertEqual(online_score, python_score, 'CHA2DS2-VASc')

    def __get_online_score(self, parameters: Parameters) -> int:
        self.driver.get("https://www.chadsvasc.org/")
        if parameters['Congestive heart failure/LV dysfunction']:
            self.driver.find_element(By.CSS_SELECTOR, ".table1 .q0 > .td2 > div > div").click()
        if parameters['Hypertension']:
            self.driver.find_element(By.CSS_SELECTOR, ".table1 .q1 > .td2 > div > div").click()
        if parameters['Age ≥75y']:
            self.driver.find_element(By.CSS_SELECTOR, ".table1 .q2 > .td2 > div > div").click()
        if parameters['Age 65-74y']:
            self.driver.find_element(By.CSS_SELECTOR, ".table1 .q3 > .td2 > div > div").click()
        if parameters['Diabetes mellitus']:
            self.driver.find_element(By.CSS_SELECTOR, ".table1 .q4 > .td2 > div > div").click()
        if parameters['Stroke/TIA/TE']:
            self.driver.find_element(By.CSS_SELECTOR, ".table1 .q5 > .td2 > div > div").click()
        if parameters['Vascular diseases']:
            self.driver.find_element(By.CSS_SELECTOR, ".table1 .q6 > .td2 > div > div").click()
        if parameters['Sex category']:
            self.driver.find_element(By.CSS_SELECTOR, ".table1 .q7 > .td2 > div > div").click()
        element = self.driver.find_element(By.CSS_SELECTOR, ".result1 > div > div")
        return int(element.text)

    def __get_r_score(self, parameters: Parameters) -> int:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='CHADS-VASc Score']").click()
        mapping: dict[str, str] = {
            'Congestive heart failure/LV dysfunction': 'chf_lv_dysfunction',
            'Hypertension': 'hypertension',
            'Age ≥75y': 'age_75_or_more',
            'Diabetes mellitus': 'diabetes_mellitus',
            'Stroke/TIA/TE': 'stroke_tia_te',
            'Vascular diseases': 'vascular_diseases',
            'Age 65-74y': 'age_65_to_74',
            'Sex category': 'sex_category'
        }
        for key, value in parameters.items():
            if value != (self.driver.find_element(By.ID, mapping[key]).get_attribute('checked') is not None):
                self.driver.find_element(By.ID, mapping[key]).click()
        self.driver.find_element(By.ID, "calculate_chads_vasc").click()
        text = self.driver.find_element(By.ID, "score_output_chads_vasc").text
        return int(text.split(': ')[1])


if __name__ == '__main__':
    unittest.main()
