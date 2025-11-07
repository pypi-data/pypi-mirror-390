import time
import unittest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from parameter_generator import generate_abc_af_stroke_parameters
from acribis_scores.abc_af_stroke import calc_abc_af_stroke_score, Parameters


class TestABCAFStroke(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_abc_af_stroke(self):
        for i in range(10):
            parameters = generate_abc_af_stroke_parameters()

            r_score = self.__get_r_score(parameters)
            python_score = round(calc_abc_af_stroke_score(parameters), 2)
            self.assertEqual(python_score, r_score, 'ABC-AF Stroke')

            if parameters['Aspirin']:
                continue
            online_score, equal = self.__get_online_score(parameters)
            if equal:
                self.assertEqual(online_score, python_score, 'ABC-AF Stroke')
            else:
                self.assertGreaterEqual(python_score, online_score, 'ABC-AF Stroke')

    def __get_online_score(self, parameters: Parameters) -> tuple[float, bool]:
        self.driver.get('https://www.ucr.uu.se/en/services/abc-risk-calculators')
        if self.driver.find_elements(By.ID, 'cookiehintsubmit'):
            self.driver.find_element(By.ID, 'cookiehintsubmit').click()
        i_frame = self.driver.find_elements(By.TAG_NAME, 'iframe')[0]
        self.driver.execute_script('arguments[0].scrollIntoView()', i_frame)
        time.sleep(1)
        self.driver.switch_to.frame(i_frame)
        self.driver.find_element(By.LINK_TEXT, 'ABC-Stroke risk').click()
        if parameters['Prior Stroke/TIA']:
            self.driver.find_element(By.NAME, "prior_stroke").click()
        self.driver.find_element(By.NAME, 'age').send_keys(str(parameters['Age']))
        self.driver.find_element(By.NAME, 'cTnT').send_keys(str(parameters['Troponin T in ng/L']))
        self.driver.find_element(By.NAME, 'BNP').send_keys(str(parameters['NT-proBNP in ng/L']))
        time.sleep(0.5)
        self.driver.execute_script('arguments[0].scrollIntoView()', i_frame)
        time.sleep(0.5)
        self.driver.find_element(By.CSS_SELECTOR, 'tr:nth-child(5) input').click()
        text = self.driver.find_element(By.CSS_SELECTOR, "form").text
        search_string = 'Predicted one year stroke/SE risk '
        sign = text.find(search_string) + len(search_string)
        start = sign + 2 if text[sign] == '=' else sign + 1
        end = text.find('%', start)
        percentage_string = text[start:end]
        return float(percentage_string), text[sign] == '='

    def __get_r_score(self, parameters: Parameters) -> float:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='ABC-AF Stroke Score']").click()
        if parameters['Prior Stroke/TIA'] != (
                self.driver.find_element(By.ID, "prior_stroke_tia").get_attribute('checked') is not None):
            self.driver.find_element(By.ID, "prior_stroke_tia").click()
        element = self.driver.find_element(By.ID, "abc_stroke_age")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Age']))
        element = self.driver.find_element(By.ID, "troponin_t_stroke")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Troponin T in ng/L']))
        element = self.driver.find_element(By.ID, "nt_pro_bnp_stroke")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['NT-proBNP in ng/L']))
        if parameters['DOAC'] != (self.driver.find_element(By.ID, "doac").get_attribute('checked') is not None):
            self.driver.find_element(By.ID, "doac_stroke").click()
        if parameters['Aspirin'] != (self.driver.find_element(By.ID, "aspirin").get_attribute('checked') is not None):
            self.driver.find_element(By.ID, "aspirin_stroke").click()
        self.driver.find_element(By.ID, "calculate_abc_af_stroke").click()
        text = self.driver.find_element(By.ID, "score_output_abc_af_stroke").text
        return float(text.split(': ')[1])


if __name__ == '__main__':
    unittest.main()
