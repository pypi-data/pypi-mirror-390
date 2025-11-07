import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By

from parameter_generator import generate_has_bled_parameters
from acribis_scores.has_bled import calc_has_bled_score, Parameters


class TestHASBLEDCalculator(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_has_bled(self):
        for i in range(10):
            parameters = generate_has_bled_parameters()

            online_score = self.__get_online_score(parameters)
            r_score = self.__get_r_score(parameters)
            python_score = calc_has_bled_score(parameters)
            self.assertEqual(python_score, r_score, 'HAS-BLED')
            self.assertEqual(online_score, python_score, 'HAS-BLED')

    def __get_online_score(self, parameters: Parameters) -> int:
        self.driver.get("https://www.chadsvasc.org/")
        if parameters['Uncontrolled hypertension']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q0 > .td2 > div > div").click()
        if parameters['Abnormal Liver Function']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q1 > .td2 > div > div").click()
        if parameters['Abnormal Renal Function']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q2 > .td2").click()
        if parameters['Stroke']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q3 > .td2").click()
        if parameters['Bleeding history or predisposition']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q4 > .td2 > div > div").click()
        if parameters['Labile international normalized ratio (INR)']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q5 > .td2 > div > div").click()
        if parameters['Elderly']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q6 > .td2 > div > div").click()
        if parameters['Drugs']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q7 > .td2 > div > div").click()
        if parameters['Alcohol']:
            self.driver.find_element(By.CSS_SELECTOR, ".table2 .q8 > .td2 > div > div").click()
        element = self.driver.find_element(By.CSS_SELECTOR, ".result2 > div > div")
        return int(element.text)

    def __get_r_score(self, parameters: Parameters) -> int:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='HAS-BLED Score']").click()
        mapping: dict[str, str] = {
            'Uncontrolled hypertension': 'uncontrolled_htn',
            'Abnormal Renal Function': 'renal_function',
            'Abnormal Liver Function': 'liver_function',
            'Stroke': 'stroke',
            'Bleeding history or predisposition': 'bleeding',
            'Labile international normalized ratio (INR)': 'labile_inr',
            'Elderly': 'elderly',
            'Drugs': 'drugs',
            'Alcohol': 'alcohol'
        }
        for key, value in parameters.items():
            if value != (self.driver.find_element(By.ID, mapping[key]).get_attribute('checked') is not None):
                self.driver.find_element(By.ID, mapping[key]).click()
        self.driver.find_element(By.ID, "calculate_has_bled").click()
        text = self.driver.find_element(By.ID, "score_output_has_bled").text
        return int(text.split(': ')[1])


if __name__ == '__main__':
    unittest.main()
