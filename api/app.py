import os

from flask import Flask
from flasgger import Swagger

from views.api_arquivopt import api_arquivopt

from settings import config


def create_app():
    app = Flask(__name__)

    app.config.from_object(config[os.getenv('FLASK_CONFIG') or 'default'])

    app.config['SWAGGER'] = {
        'title': 'Contamehistorias API',
    }
    swagger = Swagger(app)

    app.register_blueprint(api_arquivopt, url_prefix='/api/arquivopt')

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5001")
