import requests
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import google.generativeai as genai
import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
genai.configure(api_key=os.environ["capstoneGemini"])
rapid_api_key = os.getenv('RAPIDAPI_KEY')
EMAIL_PASSWORD = os.getenv("EMAIL_API_PASSWORD")
HEALTH_CHECK_URL = os.getenv("CAPSTONE_HEALTH_URL")
OTHER_SERVER_URL = os.getenv("OTHER_SERVER_URL")

already_sent_on_sunday = False
last_emailed_day = None
todays_data={}

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

#talks to Gemini model to summarize social media data
def gemini_summary(data):
    chat_session = model.start_chat()
        
    response = chat_session.send_message(f"""
    You are an AI assistant designed to determine social media growth.
    Based on the following json statistics, generate a friendly and informative message that explains the key metrics and provides a summary blurb.
    Keep it short, and use bullet points.
    Do not have any introduction, we just need a short summary in bullet point format (5 lines max)

    ### Request:
    Generate a message that highlights these statistics in a clear and concise format. The message should:
    - Clearly list the total engagements and the specific platform engagement metrics for different social media accounts
    - Provide a brief summary blurb that offers a general overview or insight based on the provided data.
    - If certain Data is null/empty, you do not need to provide a summary for it.

    The tone should be friendly and informative.
                                         
    Example:
                                         
    Facebook:\n
        - Followers grew by X (+Y%)
        - Likes grew by X (+Y%)
    Instagram:\n
        - Followers grew by X (+Y%)
        - Media count grew by X (+Y%).
    etc.

    ### Social Media Statistics:
    {data}

    """)

    summary = response.text

    return summary

def get_weekly_growth():
    global todays_data
    last_week = call_get_data_api()  # Get last week's data
    if not todays_data or todays_data["date"]!=datetime.datetime.today().strftime("%-m/%-d/%Y"):
        print("fetched api")
        todays_data = social_media_data()
    today = todays_data

    # Define platforms and their respective stats
    platforms = {
        'facebook': ['followers', 'likes'],
        'instagram': ['followers', 'media_count'],
        'linkedin': ['followers'],
        'tiktok': ['followers', 'likes']
    }

    growth = {}

    # Loop through each platform
    for platform, stats in platforms.items():
        platform_growth = {}

        # Loop through each stat for the current platform
        for stat in stats:
            last_week_stat = last_week.get(platform, {}).get(stat, 0)
            today_stat = today.get(platform, {}).get(stat, 0)

            if last_week_stat != 0:  # Avoid division by zero
                growth_value = today_stat - last_week_stat
                growth_percentage = (growth_value / last_week_stat) * 100
            else:
                growth_value = today_stat
                growth_percentage = 'N/A'  # In case there's no data from last week

            platform_growth[stat] = {
                'growth': growth_value,
                'growth_percentage': growth_percentage
            }

        growth[platform] = platform_growth

    print(growth)
    return growth

def call_get_data_api():
    api_url = OTHER_SERVER_URL+"/get_data"
    print(api_url)
    
    try:
        payload = {
            'password': EMAIL_PASSWORD
        }
    
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    
def call_update_data_api(new_data):
    api_url = OTHER_SERVER_URL + "/update_data"

    try:
        payload = {
            'password': EMAIL_PASSWORD,
            'new_data': new_data
        }

        response = requests.post(api_url, json=payload)
        response.raise_for_status()

        # Return True if successful
        return True

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def social_media_data():
    social_data = {}

    #facebook
    #https://rapidapi.com/krasnoludkolo/api/facebook-scraper3/playground/apiendpoint_847dc586-dd05-4660-a838-128c872a1407
    #https://www.facebook.com/greenplanetfarms/

    url = "https://facebook-scraper3.p.rapidapi.com/page/details"

    querystring = {"url":"https://www.facebook.com/greenplanetfarms/"}

    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        if data and "results" in data:
            results = data["results"]
            social_data["facebook"] = {
                "followers": results.get("followers", "N/A"),
                "likes": results.get("likes", "N/A")
            }
        else:
            social_data["facebook"] = {
            "followers":'0',
            "likes": '0'
        }
    else:
        social_data["facebook"] = {
            "followers":'0',
            "likes": '0'
        }




    #insta
    #https://rapidapi.com/social-lens-social-lens-default/api/instagram-social-api
    #https://www.instagram.com/futureacresfarm/

    url = "https://instagram-social-api.p.rapidapi.com/v1/info"
    querystring = {"username_or_id_or_url":"futureacresfarm"}
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "instagram-social-api.p.rapidapi.com"
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
            social_data["instagram"] = {
                "followers":'0',
                "media_count": '0'
            }
    else:
        social_data["instagram"] = {
            "followers":'0',
            "media_count": '0'
        }

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
            social_data["tiktok"] = {
                "followers":'0',
                "likes": '0'
            }

    else:
        social_data["tiktok"] = {
            "followers":'0',
            "likes": '0'
        }



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
            social_data["linkedin"] = {
            "followers":"0"
        }

    else:
        social_data["linkedin"] = {
            "followers":"0"
        }
    
    social_data["date"] = datetime.datetime.today().strftime("%-m/%-d/%Y")
    print(social_data)
    return social_data

def send_weekly_update(data):
    print("Sending Weekly Email!")
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL")

    today_date = datetime.datetime.today().strftime("%-m/%-d/%Y")

    subject = f"Weekly Social Media Growth Update - Dave ({today_date})"
    body = f"Hey Dave, here are your weekly social media growth statistics:\n\n{data}\n\n" \
           "- The George Mason University Capstone Team"

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    if not sender_email or not sender_password or not receiver_email:
        print("Error: One or more email environment variables not set.")
        return

    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        print(f"Email sent successfully to {receiver_email}")

    except Exception as e:
        print(f"Error sending email: {e}")

# Health endpoint
# If health is called and there's a password, it'll send the email (this will happen every sunday)
@app.route('/health', methods=['POST'])
def health():
    global todays_data
    provided_password = request.form.get('password')

    if not provided_password:
        print("Health was pinged")
        return "API is healthy!", 200

    if provided_password != EMAIL_PASSWORD:
        return jsonify({"error": "Access Denied"}), 401
    else:
        print("hit health email")
        if not todays_data:
            todays_data = social_media_data()
        data = get_weekly_growth()
        email_text = gemini_summary(data)
        send_weekly_update(email_text)
        call_update_data_api(todays_data)
        return "Email Sent", 200


@app.route('/test_growth', methods=['GET'])
def test_growth():
    data = get_weekly_growth()
    return jsonify(data)


@app.route('/test_get', methods=['GET'])
def test_get():
    data = call_get_data_api()
    return jsonify(data)

# This is just a test for our demo
@app.route('/email_test', methods=['POST'])
def trigger_weekly_email():
    provided_password = request.form.get('password')

    if not provided_password or provided_password != EMAIL_PASSWORD:
        return jsonify({"error": "Access Denied"}), 401
    

    data = get_weekly_growth()
    email_text = gemini_summary(data)
    send_weekly_update(email_text)
    return jsonify({"message": "Email Sent"}), 200


#This is a testing function, I commented it out for now since it's not needed
# @app.route('/update', methods=['POST'])
# def update():
#     global todays_data
#     yesterday = datetime.date.today() - datetime.timedelta(days=1)
#     todays_data["date"] = yesterday.strftime("%-m/%-d/%Y")
#     return jsonify({"message": f"todays_data['date'] updated to {todays_data['date']}"}), 200


#This endpoint is called through the power automate workflow daily
@app.route('/data', methods=['GET'])
def data():
    global todays_data

    if not todays_data or todays_data["date"]!=datetime.datetime.today().strftime("%-m/%-d/%Y"):
        print("fetched api")
        data = social_media_data()
        todays_data=data
        return jsonify(data)
    else:
        print("did not fetch api")
        return jsonify(todays_data)

def ping_health():
    global already_sent_on_sunday
    global last_emailed_day
    data = {'password': EMAIL_PASSWORD}
    now = datetime.datetime.now()
    current_day = now.weekday()
    
    #this is a normal health check
    #if it's sunday and the email hasn't been sent yet, it will send an email.
    try:
        if current_day == 6:  # It's Sunday
            if not already_sent_on_sunday or last_check_day != current_day:
                if EMAIL_PASSWORD:
                    try:
                        data = {'password': EMAIL_PASSWORD}
                        response = requests.post(HEALTH_CHECK_URL, data=data)
                        if response.status_code == 200:
                            print("Email sent successfully via health check.")
                            already_sent_on_sunday = True
                            last_check_day = current_day
                        elif response.status_code != 200:
                            print(f"Health check (with email trigger) failed with status code: {response.status_code}")
                        else:
                            print(f"Health check responded: {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error during health check (with email trigger): {e}")
                else:
                    print("EMAIL_PASSWORD not configured, skipping email trigger.")
            else:
                print("Already sent email today (Sunday).")
                try:
                    response = requests.post(HEALTH_CHECK_URL)
                    if response.status_code != 200:
                        print(f"Regular health check failed: {response.status_code}")
                    else:
                        print(response.text)
                except requests.exceptions.RequestException as e:
                    print(f"Error during regular health check: {e}")
        else:
            already_sent_on_sunday = False
            try:
                response = requests.post(HEALTH_CHECK_URL)
                if response.status_code != 200:
                    print(f"Regular health check failed: {response.status_code}")
                else:
                    print(response.text)
            except requests.exceptions.RequestException as e:
                print(f"Error during regular health check: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error during health check: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(ping_health, 'interval', seconds=600)
scheduler.start()
