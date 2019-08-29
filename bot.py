
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json

def main():

    options = webdriver.ChromeOptions()

    user_credentials = {}

    url_home = "https://my.wobbjobs.com"
    url_histories = url_home + "/v2/users/job_histories"

    driver = webdriver.Chrome()
    driver.get(url_home)

    # Wobb has the same tab title when logged in or out.
    # So we will check our login status by looking for the login button
    login_button = driver.find_element_by_class_name("sign_up_dialog_btn")

    if login_button:
        # Load user credentials and proceed to login
        with open("credentials.json", "r") as f:
            user_credentials = json.loads(f.read())
        login_button.click()
        email_field = driver.find_element_by_id("email-sign-in")
        email_field.clear()
        email_field.send_keys(user_credentials['email'])
        password_field = driver.find_element_by_id("user_password")
        password_field.clear()
        password_field.send_keys(user_credentials['password'])
        sign_in_button = driver.find_element_by_id("sign-in-password")
        sign_in_button.click()

    # Navigate to job histories section
    driver.get(url_histories)
    applied_tab = driver.find_element_by_class_name("mdc-tab")
    applied_tab.click()

    time.sleep(10)
    driver.quit()


if __name__ == "__main__":
    main()
