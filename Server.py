from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from urllib.parse import quote
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='elements')  # ← Mudei para 'elements'
CORS(app)

# Configuração da IA
URL_BASE = "https://gen.pollinations.ai/text/"
KEY = os.environ.get('POLLINATIONS_KEY', 'pk_sDy7Mrbxv4kDwl6C')
MODELO = os.environ.get('MODELO_IA', 'openai')
INSTRUCOES = os.environ.get('INSTRUCOES_IA', 
    "Você é a Cyb3rAI, especialista em gerar scripts Lua para Roblox. "
    "Responda apenas com código Lua funcional, bem comentado e organizado. "
    "Use -- para comentários e formate corretamente."
)

@app.route('/')
def index():
    """Serve o arquivo HTML principal da pasta elements"""
    try:
        return send_from_directory('elements', 'index.html')  # ← Agora procura em elements/
    except Exception as e:
        logger.error(f"Erro ao servir index.html: {e}")
        return jsonify({'error': 'Arquivo index.html não encontrado na pasta elements'}), 404

@app.route('/<path:path>')
def serve_static(path):
    """Serve arquivos estáticos da pasta elements"""
    try:
        return send_from_directory('elements', path)
    except Exception:
        return jsonify({'error': 'Arquivo não encontrado'}), 404

@app.route('/generate', methods=['POST'])
def generate():
    """Endpoint para gerar scripts com IA"""
    try:
        data = request.json
        pergunta = data.get('prompt', '').strip()
        
        if not pergunta:
            return jsonify({'error': 'Por favor, descreva o script que você precisa'}), 400
        
        logger.info(f"Gerando script para: {pergunta[:50]}...")
        
        # Prompt especializado para código Lua
        prompt_completo = f"""{INSTRUCOES}
        
        Solicitação do usuário: {pergunta}
        
        Gere um script Lua completo e funcional:"""
        
        prompt_codificado = quote(prompt_completo)
        url_final = f"{URL_BASE}{prompt_codificado}?model={MODELO}&key={KEY}"
        
        # Faz a requisição
        r = requests.get(url_final, timeout=30)
        
        if r.status_code == 200 and r.text:
            resposta = r.text.strip()
            
            # Formata a resposta
            if not resposta.startswith('--'):
                resposta = f"-- Script gerado pela Cyb3rAI\n-- Para: {pergunta}\n\n{resposta}"
            
            return jsonify({'response': resposta})
        else:
            return jsonify({'error': f'Erro na API: {r.status_code}'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Tempo limite excedido'}), 504
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint de saúde"""
    return jsonify({
        'status': 'online',
        'service': 'Cyb3rAI',
        'version': '2.0',
        'static_folder': 'elements'
    })

# Handler para erros 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando Cyb3rAI na porta {port}")
    logger.info(f"Pasta estática: elements/")
    logger.info(f"Arquivo index: elements/index.html")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )