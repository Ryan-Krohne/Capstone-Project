import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Health endpoint
@app.route('/health', methods=['GET'])
def health():
    print("Health was pinged")
    return "API is healthy!", 200

# AI endpoint
@app.route('/AI', methods=['GET'])
def AI():
    return "AI API is healthy!", 200


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
