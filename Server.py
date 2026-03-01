from flask import Flask, request, jsonify, send_from_directory
import requests
from urllib.parse import quote
import os

app = Flask(__name__, static_folder='elements')  # Sua pasta é 'elements'

# Configuração da IA (igual ao seu que funciona)
URL_BASE = "https://gen.pollinations.ai/text/"
KEY = "pk_sDy7Mrbxv4kDwl6C"
MODELO = "openai"
INSTRUCOES = "Você é a Cyb3rAI, especialista em gerar scripts Lua para Roblox. Responda apenas com código Lua funcional, bem comentado e organizado."

@app.route('/')
def index():
    """Serve o index.html da pasta elements"""
    return send_from_directory('elements', 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Endpoint para gerar scripts (igual ao seu /perguntar)"""
    data = request.json
    pergunta = data.get('prompt', '').strip()
    
    if not pergunta:
        return jsonify({"error": "Escreve algo aí maninho 😅"})
    
    # Junta instruções + pergunta (igual ao seu código)
    prompt_completo = f"{INSTRUCOES} {pergunta}"
    
    # Codifica o texto para URL
    prompt_codificado = quote(prompt_completo)
    
    # Monta a URL final
    url_final = f"{URL_BASE}{prompt_codificado}?model={MODELO}&key={KEY}"
    
    print(f"URL gerada: {url_final}")  # Log
    
    try:
        r = requests.get(url_final, timeout=27)
        
        if r.status_code == 200 and r.text:
            resposta = r.text.strip()
            # Garante que comece com comentário Lua
            if not resposta.startswith('--'):
                resposta = f"-- Script gerado pela Cyb3rAI\n-- {pergunta}\n\n{resposta}"
        else:
            resposta = f"-- Erro na API (código {r.status_code}) 😢"
            
    except Exception as e:
        print("Erro:", e)
        resposta = f"-- Erro ao conectar: {str(e)}"
    
    return jsonify({"response": resposta})

@app.route('/health')
def health():
    return {"status": "online", "message": "Cyb3rAI funcionando!"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)