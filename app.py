from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from LinkedIn_Scrapper import LinkedInScrapper

# Load environment variables
load_dotenv()

app = Flask(__name__)

# LinkedIn login credentials
LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    profile_url = data.get('url')
    
    if not profile_url:
        return jsonify({"error": "URL is required"}), 400
    
    scrapper = LinkedInScrapper(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
    
    driver = scrapper.initialize_driver()
    try:
        scrapper.login_to_linkedin(driver)
        bio_text = scrapper.scrape_linkedin_bio(driver, profile_url)
        return jsonify({"bio": bio_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '_main_':
    app.run(debug=True)