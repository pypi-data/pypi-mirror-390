import time
import unittest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from parameter_generator import generate_abc_af_bleeding_parameters
from acribis_scores.abc_af_bleeding import calc_abc_af_bleeding_score, Parameters


class TestABCAFBleeding(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_abc_af_bleeding(self):
        for i in range(10):
            parameters = generate_abc_af_bleeding_parameters()

            r_score = self.__get_r_score(parameters)
            python_score = round(calc_abc_af_bleeding_score(parameters), 2)
            self.assertEqual(python_score, r_score, 'ABC-AF Bleeding')

            if parameters['Aspirin']:
                continue
            online_score, equal = self.__get_online_score(parameters)
            if equal:
                self.assertEqual(online_score, python_score, 'ABC-AF Bleeding')
            else:
                self.assertGreaterEqual(python_score, online_score, 'ABC-AF Bleeding')

    def __get_online_score(self, parameters: Parameters) -> tuple[float, bool]:
        self.driver.get('https://www.ucr.uu.se/en/services/abc-risk-calculators')
        if self.driver.find_elements(By.ID, 'cookiehintsubmit'):
            self.driver.find_element(By.ID, 'cookiehintsubmit').click()
        i_frame = self.driver.find_elements(By.TAG_NAME, 'iframe')[0]
        self.driver.execute_script('arguments[0].scrollIntoView()', i_frame)
        time.sleep(1)
        self.driver.switch_to.frame(i_frame)
        self.driver.find_element(By.LINK_TEXT, "ABC-Bleeding risk").click()
        if parameters['Prior Bleeding']:
            self.driver.find_element(By.NAME, "prior_bleeding").click()
        self.driver.find_element(By.NAME, "age").send_keys(str(parameters['Age']))
        self.driver.find_element(By.NAME, "cTnT").send_keys(str(parameters['Troponin T in ng/L']))
        self.driver.find_element(By.NAME, "GDF15").send_keys(str(parameters['GDF-15 in ng/L']))
        self.driver.find_element(By.NAME, "HB").send_keys(str(parameters['Hemoglobin in g/dL']))
        time.sleep(0.5)
        self.driver.execute_script('arguments[0].scrollIntoView()', i_frame)
        time.sleep(0.5)
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(6) input").click()
        text = self.driver.find_element(By.CSS_SELECTOR, "form").text
        search_string = 'Predicted one year bleeding risk '
        sign = text.find(search_string) + len(search_string)
        start = sign + 2 if text[sign] == '=' else sign + 1
        end = text.find('%', start)
        percentage_string = text[start:end]
        return float(percentage_string), text[sign] == '='

    def __get_r_score(self, parameters: Parameters) -> float:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='ABC-AF Bleeding Score']").click()
        if parameters['Prior Bleeding'] != (self.driver.find_element(By.ID, "prior_bleeding").get_attribute('checked') is not None):
            self.driver.find_element(By.ID, "prior_bleeding").click()
        element = self.driver.find_element(By.ID, "abc_age")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Age']))
        element = self.driver.find_element(By.ID, "troponin_t")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Troponin T in ng/L']))
        element = self.driver.find_element(By.ID, "gdf_15")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['GDF-15 in ng/L']))
        element = self.driver.find_element(By.ID, "abc_hemoglobin")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Hemoglobin in g/dL']))
        if parameters['DOAC'] != (self.driver.find_element(By.ID, "doac").get_attribute('checked') is not None):
            self.driver.find_element(By.ID, "doac").click()
        if parameters['Aspirin'] != (self.driver.find_element(By.ID, "aspirin").get_attribute('checked') is not None):
            self.driver.find_element(By.ID, "aspirin").click()
        self.driver.find_element(By.ID, "calculate_abc_af_bleeding").click()
        text = self.driver.find_element(By.ID, "score_output_abc_af_bleeding").text
        return float(text.split(': ')[1])


if __name__ == '__main__':
    unittest.main()
