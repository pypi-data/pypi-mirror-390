import unittest

from acribis_scores.abc_af_death import calc_abc_af_death_score, Parameters
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from tests.parameter_generator import generate_abc_af_death_parameters


class TestABCAFStroke(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def test_abc_af_stroke(self):
        for i in range(10):
            parameters = generate_abc_af_death_parameters()

            r_score_model_a, r_score_model_b = self.__get_r_score(parameters)
            python_score_model_a, python_score_model_b = calc_abc_af_death_score(parameters)
            self.assertEqual(round(python_score_model_a, 2), r_score_model_a)
            self.assertEqual(round(python_score_model_b, 2), r_score_model_b)

    def __get_r_score(self, parameters: Parameters) -> tuple[float, float]:
        self.driver.get("http://localhost/")
        self.driver.find_element(By.CSS_SELECTOR, "a[data-value='ABC-AF Death Score']").click()
        if parameters['Heart Failure'] != (
                self.driver.find_element(By.ID, "heart_failure").get_attribute('checked') is not None):
            self.driver.find_element(By.ID, "heart_failure").click()
        element = self.driver.find_element(By.ID, "abc_death_age")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Age']))
        element = self.driver.find_element(By.ID, "nt_pro_bnp_death")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['NT-proBNP in ng/L']))
        element = self.driver.find_element(By.ID, "gdf_15_death")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['GDF-15 in ng/L']))
        element = self.driver.find_element(By.ID, "troponin_t_death")
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(str(parameters['Troponin T in ng/L']))
        self.driver.find_element(By.ID, "calculate_abc_af_death").click()
        text_a = self.driver.find_element(By.ID, "score_output_abc_af_death_a").text
        text_b = self.driver.find_element(By.ID, "score_output_abc_af_death_b").text
        return float(text_a.split(': ')[1]), float(text_b.split(': ')[1])


if __name__ == '__main__':
    unittest.main()
