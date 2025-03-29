import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.environ["capstoneGemini"])

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
    You are an AI assistant designed to help Dave understand his social media performance. Based on the following statistics, generate a friendly and informative message that explains the key metrics and provides insights.

    ### Social Media Statistics:
    - Total Followers: 15,432
    - Total Likes: 98,543
    - Total Comments: 4,123
    - Engagement Rate: 3.5%
    - Total Shares: 1,278
    - Average Post Reach: 7,896
    - Top Performing Post: "Our latest product launch went viral, reaching 50,000+ people!"
    - Week-over-Week Growth: +2.3% in followers
    - Top Demographics: 60% Female, 40% Male, Most active age group: 25-34

    ### Request:
    Generate a message that highlights these statistics in a way that is easy to understand and insightful for the client. The message should:
    - Acknowledge key achievements (e.g., follower growth, top-performing posts)
    - Mention the engagement rate and provide a brief explanation of its significance
    - Provide insights into the client’s audience demographics
    - Suggest areas for improvement or focus, if applicable

    The tone should be friendly, professional, and encouraging.

    ### Example output structure:
    "Hi Dave, here's an update on your social media performance:

    - Your total followers have increased to 15,432, with a week-over-week growth of +2.3%!
    - Your engagement rate of 3.5% is great, indicating strong interaction with your audience.
    - The post on [date] about your product launch performed exceptionally well, reaching 50,000+ people!
    - Your top demographic is 25-34-year-olds, with 60% of your audience being female.

    Keep up the great work! To further improve, you may want to focus on increasing the number of shares and engaging your male audience more. 
    Keep an eye on the upcoming trends and continue to create content that resonates with your followers!"

    """)

    summary = response.text
    print(summary)

    return summary



# Health endpoint
@app.route('/health', methods=['GET'])
def health():
    print("Health was pinged")
    return "API is healthy!", 200

# AI endpoint
@app.route('/AI', methods=['GET'])
def AI():
    gemini_answer = ai_stuff()
    
    return gemini_answer, 200


def ping_health():
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        if response.status_code != 200:
            print(f"Health check failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error during health check: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(ping_health, 'interval', seconds=840)

if __name__ == "__main__":
    scheduler.start()
    
    app.run(debug=True)
