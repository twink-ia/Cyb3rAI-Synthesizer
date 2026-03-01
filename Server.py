from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import quote
import os

app = Flask(__name__)

# URL CORRETA com a KEY fixa
URL_BASE = "https://gen.pollinations.ai/text/"
KEY = "pk_sDy7Mrbxv4kDwl6C"
MODELO = "openai"
INSTRUCOES = "Você é a Cyb3rAI, especialista em gerar scripts Lua para Roblox. Responda sempre com código Lua funcional, bem comentado e organizado. Inclua -- comentários no código."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gerar", methods=["POST"])
def gerar():
    pergunta = request.form.get("pergunta", "").strip()
    if not pergunta:
        return jsonify({"resposta": "-- Erro: Você não descreveu o script 😅"})
    
    # Junta instruções + pergunta
    prompt_completo = f"{INSTRUCOES} {pergunta}"
    
    # Codifica o texto para URL
    prompt_codificado = quote(prompt_completo)
    
    # Monta a URL final
    url_final = f"{URL_BASE}{prompt_codificado}?model={MODELO}&key={KEY}"
    
    print(f"URL gerada: {url_final}")  # Log para debug
    
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
    
    return jsonify({"resposta": resposta})

@app.route("/health")
def health():
    return jsonify({"status": "online", "mensagem": "Cyb3rAI funcionando!"})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host="0.0.0.0", port=port, debug=True)