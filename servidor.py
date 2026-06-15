from flask import Flask, request, send_file, make_response
from flask_cors import CORS
import yt_dlp
import os
import time
import urllib.parse

app = Flask(__name__)
# Permitimos a exposição do header para que o front-end consiga ler o nome do arquivo corretamente
CORS(app, expose_headers=["Content-Disposition"])

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# ROTA PRINCIPAL: Entrega o arquivo HTML da interface para o navegador
@app.route('/')
def index():
    return send_file('index.html')

# ROTA DE DOWNLOAD: Processa o link e baixa a mídia
@app.route('/download', methods=['POST'])
def download_media():
    data = request.json
    video_url = data.get('url')
    formato = data.get('format', 'mp4') # 'mp4' como padrão se não for enviado

    if not video_url:
        return {"erro": "URL não fornecida"}, 400

    timestamp = int(time.time())
    
    # Configuração dinâmica baseada no formato escolhido pelo usuário
    if formato == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s_{timestamp}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        # Configuração para Vídeo MP4 (Une o melhor vídeo com o melhor áudio)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, f'%(title)s_{timestamp}.%(ext)s'),
            'merge_output_format': 'mp4',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            
            # Localiza o caminho correto gerado pelo processo
            if formato == 'mp3':
                caminho_arquivo = f"{ydl.prepare_filename(info).rsplit('.', 1)[0]}.mp3"
            else:
                caminho_arquivo = f"{ydl.prepare_filename(info).rsplit('.', 1)[0]}.mp4"

        if not os.path.exists(caminho_arquivo):
            return {"erro": "Falha ao processar ou mesclar o arquivo de mídia"}, 500
        
        # Define o nome que o usuário verá ao salvar localmente
        extensao = 'mp3' if formato == 'mp3' else 'mp4'
        nome_download = f"{info.get('title', 'midia')}.{extensao}"
        
        response = make_response(send_file(caminho_arquivo, as_attachment=True))
        
        # Codifica o nome para suportar acentos e emojis sem quebrar o header HTTP
        nome_codificado = urllib.parse.quote(nome_download)
        response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{nome_codificado}"
        return response

    except Exception as e:
        return {"erro": str(e)}, 500

if __name__ == '__main__':
    # Roda o servidor local na porta 5000, escutando a rede toda (0.0.0.0)
    app.run(host='0.0.0.0', port=5000, debug=True)