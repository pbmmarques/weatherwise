from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Puxa a chave da variável de ambiente de forma segura
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Chave de API não encontrada! Verifique seu arquivo .env")

genai.configure(api_key=api_key)

# Inicializa o modelo (se após atualizar o pip o erro persistir, tente "gemini-1.5-flash-latest")
model = genai.GenerativeModel("gemini-flash-latest")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "weatherwise.html")

@app.route("/chat", methods=["POST"])
def chat():
    body = request.json
    system = body.get("system", "")
    messages = body.get("messages", [])

    if not messages:
        return jsonify({"error": "Nenhuma mensagem fornecida"}), 400

    # Monta o histórico no formato esperado pelo Gemini
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    # Última mensagem é a atual
    last_message = system + "\n\n" + messages[-1]["content"] if system else messages[-1]["content"]

    try:
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(last_message)
        return jsonify({"content": [{"text": response.text}]})
    except Exception as e:
        print(f"Erro ao comunicar com a API do Gemini: {e}")
        return jsonify({"error": "Erro interno do servidor ao gerar resposta."}), 500

if __name__ == "__main__":
    print("Servidor rodando em http://localhost:5000")
    app.run(port=5000)