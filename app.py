import requests
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.environ["capstoneGemini"])

rapid_api_key = os.getenv('RAPIDAPI_KEY')


generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8000,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-8b",
  generation_config=generation_config,
)


def ai_stuff():

    chat_session = model.start_chat()
        
    response = chat_session.send_message(f"""
    You are an AI assistant designed to help Dave understand his social media performance. Based on the following statistics, generate a friendly and informative message that explains the key metrics and provides a summary blurb.

    ### Social Media Statistics:
    - Total Engagements this Week: 543
    - Facebook Likes this Week: 210
    - Facebook Comments this Week: 35
    - X Likes this Week: 150
    - X Comments this Week: 20
    - Instagram Likes this Week: 100
    - Instagram Comments this Week: 28

    ### Request:
    Generate a message that highlights these statistics in a clear and concise format. The message should:
    - Clearly list the total engagements and the specific platform engagement metrics for Facebook, X (formerly Twitter), and Instagram.
    - Provide a brief summary blurb that offers a general overview or insight based on the provided data.

    The tone should be professional and informative.

    ### Expected output structure:
    "Total Engagements this Week: ###
    Facebook Likes this Week: ###
    Facebook Comments this Week: ###
    X Likes this Week: ###
    X Comments this Week: ###
    Instagram Likes this Week: ###
    Instagram Comments this Week: ###
    Summary Blurb: ......."

    """)

    summary = response.text

    return {"response": summary}

def social_media_data():
    social_data = {}

    #facebook
    #https://rapidapi.com/ousema.frikha/api/facebook-pages-scraper2/playground/apiendpoint_81eac290-2e49-43c4-89ec-99f86338265a
    #https://www.facebook.com/greenplanetfarms/

    url = "https://facebook-pages-scraper2.p.rapidapi.com/get_facebook_pages_details"

    querystring = {"link":"https://www.facebook.com/greenplanetfarms"}

    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "facebook-pages-scraper2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        if data:
            social_data["facebook"] = {
                "followers": data[0].get('followers_count', 'N/A'),
                "likes": data[0].get('likes_count', 'N/A')
            }
    else:
        social_data["facebook"] = ""

    #insta
    #https://rapidapi.com/allapiservice/api/real-time-instagram-scraper-api1/playground/apiendpoint_aea8f1b9-3ea7-4cc3-9796-8551248b30e7
    #https://www.instagram.com/futureacresfarm/

    url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v1/user_info"
    querystring = {"username_or_id":"futureacresfarm"}
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "real-time-instagram-scraper-api1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        if data:
            social_data["instagram"] = {
                "followers": data["data"].get('follower_count', 'N/A'),
                "media_count": data["data"].get('media_count', 'N/A')
            }
        else:
            print("Unexpected JSON format:")
    else:
        social_data["instagram"] = ""

    #tiktok
    #https://rapidapi.com/Lundehund/api/tiktok-api23/playground/apiendpoint_c1dca90d-a452-4ec8-9ac8-5d6fe43c9d62
    #https://www.tiktok.com/@future.acres.farm

    url = "https://tiktok-api23.p.rapidapi.com/api/user/info"
    querystring = {"uniqueId":"future.acres.farm"}
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        if data:
            social_data["tiktok"] = {
                "followers": data["userInfo"]["stats"].get('followerCount', 'N/A'),
                "likes": data["userInfo"]["stats"].get('heartCount', 'N/A')
            }
    else:
        social_data["tiktok"] = ""


    #linkedin
    #https://rapidapi.com/freshdata-freshdata-default/api/fresh-linkedin-profile-data/playground/apiendpoint_f3214d12-9f90-42f6-a2fd-dc42547ba463
    #dave-littere-a23791286

    url = "https://fresh-linkedin-profile-data.p.rapidapi.com/get-linkedin-profile"

    querystring = {"linkedin_url":"https://www.linkedin.com/in/dave-littere-a23791286/","include_skills":"false","include_certifications":"false","include_publications":"false","include_honors":"false","include_volunteers":"false","include_projects":"false","include_patents":"false","include_courses":"false","include_organizations":"false","include_profile_status":"false","include_company_public_url":"false"}

    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "fresh-linkedin-profile-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        if data:
            social_data["linkedin"] = {
                "followers": data["data"].get("follower_count", "No follower count found")
            }
    else:
        social_data["linkedin"] = ""
    

    #youtube?

    return social_data

# Health endpoint
@app.route('/health', methods=['GET'])
def health():
    print("Health was pinged")
    return "API is healthy!", 200

# AI endpoint
@app.route('/AI', methods=['GET'])
def AI():
    gemini_answer = ai_stuff()
    
    return jsonify(gemini_answer), 200


@app.route('/testing', methods=['GET'])
def testing():

    data = social_media_data()
    return jsonify(data) 
    
    

def ping_health():
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        if response.status_code != 200:
            print(f"Health check failed with status code: {response.status_code}")
        else:
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during health check: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(ping_health, 'interval', seconds=600)

if __name__ == "__main__":
    scheduler.start()
    
    app.run(debug=True)
