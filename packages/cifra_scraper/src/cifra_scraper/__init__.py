from flask import Flask
from cifra_scraper.interface.http.routes import bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp, url_prefix='/api')  # Prefixo '/api'
    return app

app = create_app()

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=3000, debug=True)