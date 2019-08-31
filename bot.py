
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import json
from tinydb import TinyDB, Query
import yagmail


def main():

    db = TinyDB('jobs.json')
    Job = Query()

    user_credentials = {}
    url_home = "https://my.wobbjobs.com"
    url_histories = url_home + "/v2/users/job_histories"

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
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

    job_card_len = 0
    job_cards = driver.find_elements_by_class_name("job-card")

    try:

        while len(job_cards) > job_card_len:
            job_card_len = len(job_cards)
            view_more = driver.find_element_by_class_name("button-settings")
            view_more.click()
            time.sleep(5)
            job_cards = driver.find_elements_by_class_name("job-card")
    except NoSuchElementException:
        pass

    # Update job cards list again with all the visible cards
    job_cards = driver.find_elements_by_class_name("job-card")

    inserted_jobs = []
    updated_jobs = []

    # Traverse each job card and extract job information
    for card in job_cards:
        title = card.find_element_by_class_name("mdc-typography--subtitle1").text
        company = card.find_element_by_class_name("mdc-typography--subtitle2").text
        status = card.find_element_by_class_name("mdc-chip__text").text
        date = card.find_element_by_class_name("ja-created-at").text

        # Check if the job exists in the database, if not, insert it.
        if not db.contains((Job.title == title) & (Job.company == company) & (Job.date == date)):
            db.insert({'title': title, 'company': company, 'status': status, 'date': date})
            inserted_jobs.append(db.get((Job.title == title) & (Job.company == company) & (Job.date == date)))
        else:
            # If the job exists, check if the status has been updated and add to the 'updated' list accordingly
            job = db.get((Job.title == title) & (Job.company == company) & (Job.date == date))
            if job['status'] != status:
                db.update({'status': status}, (Job.title == title) & (Job.company == company) & (Job.date == date))
                updated_jobs.append(job)
            pass

    yag = yagmail.SMTP(user_credentials['dev-email'], user_credentials['dev-email-password'])
    target = user_credentials['target-email']
    body = ""

    # Send email notification of the new job insertions
    if len(inserted_jobs) > 0:
        subject = "Wobb - New Jobs Found"
        for job in inserted_jobs:
            body += "\n\nTitle: " + job['title'] + "\nCompany: " + job['company'] + "\nStatus: " + job['status'] + "\nCreated At: " + job['date']
        yag.send(target, subject, body)

    # Send email notification of the updated jobs
    if len(updated_jobs) > 0:
        subject = "Wobb - Jobs Updated!"
        for job in updated_jobs:
            body += "\n\nTitle: " + job['title'] + "\nCompany: " + job['company'] + "\nStatus: " + job['status'] + "\nCreated At: " + job['date']
        yag.send(target, subject, body)

    driver.quit()


if __name__ == "__main__":
    main()
