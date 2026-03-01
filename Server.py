from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import requests
from urllib.parse import quote
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='elements')
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

# Cache simples
cache_scripts = {}

def get_cache(prompt):
    return cache_scripts.get(prompt)

def set_cache(prompt, resposta):
    cache_scripts[prompt] = resposta

@app.route('/')
def index():
    """Serve o arquivo HTML principal da pasta elements"""
    # Proteção básica (descomente e configure quando estiver em produção)
    # referer = request.headers.get("Referer")
    # if referer and "seusite.com" not in referer:
    #     return abort(403, "Acesso negado")
    
    try:
        return send_from_directory('elements', 'index.html')
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
        
        # Validação
        if not pergunta:
            return jsonify({'error': 'Por favor, descreva o script que você precisa'}), 400
        if len(pergunta) < 10:
            return jsonify({'error': 'Detalhe mais o que você quer no script'}), 400
        
        # Verifica cache
        cache = get_cache(pergunta)
        if cache:
            logger.info("📦 Script retornado do cache")
            return jsonify({'response': cache})
        
        logger.info(f"Gerando script para: {pergunta[:50]}...")
        
        # Prompt especializado para código Lua
        prompt_completo = f"""{INSTRUCOES}
        
        Solicitação do usuário: {pergunta}
        
        Gere um script Lua completo e funcional:"""
        
        prompt_codificado = quote(prompt_completo)
        url_final = f"{URL_BASE}{prompt_codificado}?model={MODELO}&key={KEY}"
        
        # Timeout de 60 segundos para scripts complexos
        r = requests.get(url_final, timeout=60)
        
        if r.status_code == 200 and r.text:
            resposta = r.text.strip()
            
            # Formata a resposta
            if not resposta.startswith('--'):
                resposta = f"-- Script gerado pela Cyb3rAI\n-- Para: {pergunta}\n\n{resposta}"
            
            # Salva no cache
            set_cache(pergunta, resposta)
            
            logger.info(f"✅ Script gerado - Tamanho: {len(resposta)} caracteres")
            return jsonify({'response': resposta})
        else:
            return jsonify({'error': f'Erro na API: {r.status_code}'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': '⏰ Script muito complexo, tempo esgotado! Tente dividir em partes.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '🔌 Erro de conexão com a IA'}), 503
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

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando Cyb3rAI na porta {port}")
    logger.info(f"Pasta estática: elements/")
    logger.info(f"Arquivo index: elements/index.html")
    logger.info(f"Cache ativo: {len(cache_scripts)} scripts em memória")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )