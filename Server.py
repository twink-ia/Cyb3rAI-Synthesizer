from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import quote

app = Flask(__name__)

# URL CORRETA com a KEY fixa
URL_BASE = "https://gen.pollinations.ai/text/"
KEY = "pk_sDy7Mrbxv4kDwl6C"
MODELO = "openai"
INSTRUCOES = "Você é a TWINK IA. Criador: Jone. Responda sempre em português, com emojis e de forma divertida."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/perguntar", methods=["POST"])
def perguntar():
    pergunta = request.form.get("pergunta", "").strip()
    if not pergunta:
        return jsonify({"resposta": "Você não escreveu nada 😅"})
    
    # Junta instruções + pergunta
    prompt_completo = f"{INSTRUCOES} {pergunta}"
    
    # Codifica o texto para URL (ex: "gostosa" vira "gostosa", mas espaços viram %20)
    prompt_codificado = quote(prompt_completo)
    
    # Monta a URL final: base/text/PERGUNTA?model=openai&key=CHAVE
    url_final = f"{URL_BASE}{prompt_codificado}?model={MODELO}&key={KEY}"
    
    print(f"URL gerada: {url_final}")  # Log para debug
    
    try:
        r = requests.get(url_final, timeout=27)
        
        if r.status_code == 200 and r.text:
            resposta = r.text.strip()
        else:
            resposta = f"Erro na API (código {r.status_code}) 😢"
            
    except Exception as e:
        print("Erro:", e)
        resposta = f"Erro ao conectar: {str(e)}"
    
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)