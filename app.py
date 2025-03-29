from flask import Flask

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return "API is healthy!", 200



@app.route('/AI', methods=['GET'])
def AI():
    return "AI API is healthy!", 200


if __name__ == "__main__":
    app.run(debug=True)
