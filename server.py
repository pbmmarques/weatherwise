from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "weatherwise.html")

@app.route("/chat", methods=["POST"])
def chat():
    body = request.json
    system = body.get("system", "")
    messages = body.get("messages", [])
    last_message = system + "\n\n" + messages[-1]["content"] if system else messages[-1]["content"]

    response = model.generate_content(last_message)
    return jsonify({"content": [{"text": response.text}]})

if __name__ == "__main__":
    print("Servidor rodando em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000)