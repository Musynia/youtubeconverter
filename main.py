import logging
import os
from gunicorn.app.base import BaseApplication
from app_init import create_initialized_flask_app
from flask import request, jsonify, send_file
import yt_dlp
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app creation should be done by create_initialized_flask_app to avoid circular dependency problems.
app = create_initialized_flask_app()

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    format = request.form.get('format')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }] if format == 'mp3' else [],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if format == 'mp3':
                    filename = os.path.splitext(filename)[0] + '.mp3'
                
                return send_file(filename, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        return jsonify({'error': 'Conversion failed'}), 500

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.application = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        # Apply configuration to Gunicorn
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    options = {
        "bind": "0.0.0.0:8080",
        "workers": 4,
        "loglevel": "info",
        "accesslog": "-",
        "timeout": 120,
        "preload": True
    }
    StandaloneApplication(app, options).run()