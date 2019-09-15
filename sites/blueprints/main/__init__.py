from flask import Blueprint


main_bp = Blueprint('main', __name__)


from sites.blueprints.main import blog
from sites.blueprints.main import chat
from sites.blueprints.main import main
from sites.blueprints.main import photo
from sites.blueprints.main import todolist