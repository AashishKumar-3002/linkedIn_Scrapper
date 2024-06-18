from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

class LinkedInScrapper: 
    def __init__(self , LINKEDIN_USERNAME, LINKEDIN_PASSWORD):
        self.LINKEDIN_USERNAME = LINKEDIN_USERNAME
        self.LINKEDIN_PASSWORD = LINKEDIN_PASSWORD
        self.WAIT_FOR_ELEMENT_TIMEOUT = 60
        self.TOP_CARD = "pv-top-card"

    def wait_for_element_to_load(self, driver,  by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    by,
                    name
                )
            )
        )
    
    def scroll_to_half(self , driver):
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )

    def scroll_to_bottom(self , driver):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

    def initialize_driver(self):
        options = Options()
        # use the below in production
        # note : use ratelimiting to avoid getting blocked , use proxies , use headless mode, create a new acc for the scraper , to avoid getting block use kv store cache to store the data
        # options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def login_to_linkedin(self , driver):
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        
        username_input.send_keys(self.LINKEDIN_USERNAME)
        password_input.send_keys(self.LINKEDIN_PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(30)

    def get_experiences(self , driver, profile_url):
        url = os.path.join(profile_url, "details/experience")
        driver.get(url)
        driver.execute_script('alert("Focus window")')
        driver.switch_to.alert.accept()
        main = self.wait_for_element_to_load( driver=driver , by=By.TAG_NAME, name="main")
        self.scroll_to_half(driver=driver)
        self.scroll_to_bottom(driver=driver)
        main_list = self.wait_for_element_to_load(driver=driver, name="pvs-list__paged-list-item", base=main)

        positions = driver.find_elements(By.CSS_SELECTOR,"li.pvs-list__paged-list-item")

        length = len(positions)
        print(f"Number of positions: {length}")
        experiences = []
        for position in positions:
            inner_positions = position.find_elements(By.CSS_SELECTOR,"li.pvs-list__paged-list-item")
            if len(inner_positions) > 0:
                is_inner = True
                html_content = position.get_attribute("outerHTML")
                parent_dict = self.get_html_content(html_content , is_inner=is_inner , is_parent=True , parent_dict=None)
                for inner_position in inner_positions:
                    html_content = inner_position.get_attribute("outerHTML")
                    dict = self.get_html_content(html_content , is_inner=is_inner , is_parent=False , parent_dict=parent_dict)
            else:
                is_inner = False
                html_content = position.get_attribute("outerHTML")
                dict = self.get_html_content(html_content , is_inner=is_inner , is_parent=False , parent_dict=None)

            experiences.append(dict)

        return experiences

    def get_html_content(self, html_content , is_inner=False , is_parent=False , parent_dict=None):

        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        if not is_inner:
            # Extracting elements
            company_url = soup.find('a', class_='optional-action-target-wrapper')['href']
            job_title = soup.find('div', class_='t-bold').text.strip()
            company_name_element = soup.find('span', class_='t-14')
            company_name = company_name_element.text.strip().split(' · ')[0]
            role_type = (company_name_element.text.strip().split(' · ')[1]).replace(company_name, '')
            duration_element = soup.find('span', class_='t-black--light')
            duration = duration_element.text.strip().split(' · ')[0]
            time = ''.join(filter(str.isdigit, (duration_element.text.strip().split(' · ')[1]).replace(duration, '')))
            location = soup.find_all('span', class_='t-14 t-normal t-black--light')
            #extract the second one from the above list
            if len(location) > 1:
                location = location[1].text.strip()
            else:
                location = "N/A"
            job_description = soup.find('div', class_='display-flex align-items-center t-14 t-normal t-black')
            if job_description:
                job_description = job_description.text.strip()
            get_medias = soup.find_all('figure', class_='pvs-thumbnail')
            #extract src from it
            medias = []
            if get_medias:
                for media in get_medias:
                    media_src = media.find('img')['src']
                    medias.append(media_src)

            experience = {
                "contains_inner_subrole": is_inner,
                "company_url": company_url,
                "job_title": job_title,
                "company_name": company_name,
                "role_type": role_type,
                "duration": duration,
                "time": time,
                "location": location,
                "job_description": job_description,
                "media": medias
            }

            return experience
        
        else:
            if is_parent:
                company_url = soup.find('a', class_='optional-action-target-wrapper')['href']
                company_name = soup.find('div', class_='t-bold').text.strip()
                company_element = soup.find('span', class_='t-14')
                role_type = company_element.text.strip().split(' · ')[0]
                duration = (company_element.text.strip().split(' · ')[1]).replace(company_name, '')
                company_name_element = soup.find('span', class_='t-black--light')
                location = company_name_element.text.strip().split(' · ')[0]
                job_type = ''.join(filter(str.isdigit, (company_name_element.text.strip().split(' · ')[1]).replace(duration, '')))
                
                main_dict = {
                    "contains_inner_subrole": is_inner,
                    "company_url": company_url,
                    "company_name": company_name,
                    "role_type": role_type,
                    "duration": duration,
                    "location": location,
                    "job_type": job_type
                }

                return main_dict
            
            else:
                if not parent_dict:
                    return None
                
                job_title = soup.find('div', class_='t-bold').text.strip()
                duration_element = soup.find('span', class_='t-black--light')
                duration = duration_element.text.strip().split(' · ')[0]
                time = ''.join(filter(str.isdigit, (duration_element.text.strip().split(' · ')[1]).replace(duration, '')))
                job_description = soup.find('div', class_='display-flex align-items-center t-14 t-normal t-black')
                if job_description:
                    job_description = job_description.text.strip()
                get_medias = soup.find_all('figure', class_='pvs-thumbnail')
                #extract src from it
                medias = []
                if get_medias:
                    for media in get_medias:
                        media_src = media.find('img')['src']
                        medias.append(media_src)
                
                sub_experience = {
                        "job_title": job_title,
                        "duration": duration,
                        "time": time,
                        "job_description": job_description,
                        "media": medias
                    }
                # extract role and check if it's empty list create and append it else just append it
                if "role" not in parent_dict:
                    parent_dict["role"] = []
                    parent_dict["role"].append(sub_experience)
                else:
                    parent_dict["role"].append(sub_experience)

                return parent_dict
    
if __name__ == '__main__':
    username = 'edattox@gmail.com'
    password = 'Markstain1'
    scrapper = LinkedInScrapper(username, password)
    driver = scrapper.initialize_driver()
    scrapper.login_to_linkedin(driver)
    #code breaks here
    bio_text = scrapper.get_experiences(driver, 'https://www.linkedin.com/in/aashish-kumar-iiit/')
    print(bio_text)
    driver.quit()