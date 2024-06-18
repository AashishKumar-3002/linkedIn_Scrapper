# LINKEDIN EXPERIENCE SCRAPPER

## Description
This is a flask server that scrapes the experience section of a LinkedIn profile and returns the data in a JSON format.

## Installation
1. Clone the repository
2. Install the requirements
```bash
pip install -r requirements.txt
```
3. Make sure to set the .env file with the following variables:
```bash
LINKEDIN_USERNAME=your_email
LINKEDIN_PASSWORD=your_password
```
4. Run the server
```bash
python app.py
```

5. Make a POST request to the server with the following body:
```json
{
    "url": "linkedin_profile_url"
}
```

6. Sample cURL request:
```bash
curl --location 'http://localhost:5000/scrape' \
--header 'Content-Type: application/json' \
--data '{
    "url" : "https://www.linkedin.com/in/aashish-kumar-iiit/"
}'
```

## NOTE

1. FOR PRODUCTION use a headless browser like selenium and uncomment the code in the LinkedIn_Scrapper.py file inside the initiallize_driver fn.

2. USE PROXIES

3. USE RATE LIMITING

4. USE KV STORE CACHE

5. USE A NEW ACCOUNT FOR SCRAPING

6. USE A PROXY ROTATOR

