from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from urllib.parse import quote
import threading
import time

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuração da IA
URL_BASE = "https://gen.pollinations.ai/text/"
KEY = "pk_sDy7Mrbxv4kDwl6C"
MODELO = "openai"
INSTRUCOES = "Você é a Cyb3rAI, especialista em gerar scripts Lua para Roblox. Responda apenas com código Lua funcional e bem comentado."

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    pergunta = data.get('prompt', '').strip()
    
    if not pergunta:
        return jsonify({'error': 'Sem pergunta'}), 400
    
    # Prompt especializado para gerar código Lua
    prompt_completo = f"{INSTRUCOES} Gere um script Lua para: {pergunta}"
    prompt_codificado = quote(prompt_completo)
    url_final = f"{URL_BASE}{prompt_codificado}?model={MODELO}&key={KEY}"
    
    try:
        r = requests.get(url_final, timeout=30)
        if r.status_code == 200 and r.text:
            # Formata a resposta como código Lua
            resposta = r.text.strip()
            return jsonify({'response': resposta})
        else:
            return jsonify({'error': f'Erro na API: {r.status_code}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'online', 'service': 'Cyb3rAI'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
