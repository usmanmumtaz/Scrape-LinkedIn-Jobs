import os
from flask import Flask, render_template, request, send_file
import pandas as pd
from selenium import webdriver
import time
from config import EMAIL, PASSWORD
from selenium.webdriver.chrome.options import Options
import random 
app = Flask(__name__)

filename = "jobs.csv"

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    url = request.form['linkedinUrl']
    pages = int(request.form['pages'])
    extract(url, pages)
    return send_file(
        filename,
        mimetype='text/csv',
        as_attachment=True
    )

def extract(url, pages):
    output = []
    file_name_inc = 0
    while os.path.exists("jobs%s.csv" % file_name_inc):
        file_name_inc += 1
    global filename
    filename = f"jobs{file_name_inc}.csv"
    print("A")
    # options = Options() # Uncomment for Headless Mode
    # options.headless = True # Uncomment for Headless Mode
    # browser = webdriver.Chrome('./chromedriver', chrome_options=options) # Uncomment for Headless Mode
    # browser.set_window_size(1440, 900) # Uncomment for Headless Mode
    browser = webdriver.Chrome('./chromedriver') # Comment for Headless Mode
    print("FOUND")
    browser.get(url)



    try:
        browser.find_element("xpath", "//a[contains(@data-tracking-control-name,'nav-header-signin')]").click()
        username = browser.find_element("id", "username")
        username.send_keys(EMAIL)
        password = browser.find_element("id", "password")
        password.send_keys(PASSWORD)
        browser.find_element("xpath", "//button[@data-litms-control-urn='login-submit']").click()
    except Exception:
        pass
    time.sleep(5)
    for page in range(pages):
        print("\nPAGE: ", page+1)
        if page > 0:
            browser.get(url+f'&start={page*25}')
            time.sleep(3)
        try:
            no_jobs = browser.find_elements("xpath", "//div[@class='jobs-search-no-results-banner__image']")
        except Exception:
            no_jobs = ''
        if no_jobs:
            print('No Data on: ', page+1)
            continue
        else:
            jobs = browser.find_elements("xpath", "//li[contains(@class,'jobs-search-results__list-item')]")
            print('Number of Jobs: ',len(jobs))
            jobs_id_list = []
            for j in jobs:
                jobs_id = j.get_attribute("data-occludable-job-id")
                # print('\njobs_id: ', jobs_id)
                jobs_id_list.append(jobs_id)



        cc = 0
        for jj in jobs_id_list:
            print("\nCOUNT: ",cc,' - ',jj)
            cc+=1
            kk = browser.find_element("xpath", f"//li[@data-occludable-job-id='{jj}']")
            browser.execute_script("arguments[0].scrollIntoView();", kk)
            time.sleep(0.5)
            kk = browser.find_element("xpath", f"//li[@data-occludable-job-id='{jj}']/div/div/div/div/a[contains(@class,'job-card-container__link')]")
            kk.click()
            time.sleep(0.5)
            try:
                title = browser.find_element("xpath", "//h2[contains(@class,' jobs-unified-top-card__job-title')]").text.strip()
                print('title: ', title)
            except Exception:
                title = ''
                print('title: No Title')
            try:
                company = browser.find_element("xpath", "//span[@class='jobs-unified-top-card__company-name']").text.strip()
            except Exception:
                company = ''
            try:
                location = browser.find_element("xpath", "//span[@class='jobs-unified-top-card__bullet']").text.strip()
            except Exception:
                location = ''
            try:
                hiring_manager_name = browser.find_element("xpath", "//span[contains(@class,'jobs-poster__name')]").text.strip()
            except Exception:
                hiring_manager_name = ''
            try:
                search_text = 'View '+ hiring_manager_name
                hiring_manager_linkedin_profile = browser.find_element("xpath", f"//a[contains(@aria-label,'{search_text}')]").get_attribute('href')
            except Exception:
                hiring_manager_linkedin_profile = ''
            try:
                url_of_the_job_post_raw_material = jobs[i].get_attribute('data-occludable-job-id')
                url_of_the_job_post = f'https://www.linkedin.com/jobs/view/{url_of_the_job_post_raw_material}'
            except Exception:
                url_of_the_job_post = ''
            notes = ['', '', '']
            try: 
                elements = browser.find_elements("xpath", "//li[contains(@class,'jobs-unified-top-card__job-insight')]/span")
                for i in range(3): 
                    if i < len(elements): 
                        notes[i] = elements[i].text.strip()
            except Exception:
                print("elements") 
            job = {
                'title': title,
                'company': company,
                'location': location,
                'hiring_manager_name': hiring_manager_name,
                'hiring_manager_linkedin_profile': hiring_manager_linkedin_profile,
                'url_of_the_job_post': url_of_the_job_post,
                'notes1': notes[0],
                'notes2': notes[1],
                'notes3': notes[2]
            }
            output.append(job)
        df = pd.DataFrame(output)
        df.to_csv(filename)
        

    browser.close()
    browser.quit()
