from flask import Blueprint, request, jsonify
from google.cloud import datastore
from models import users_model as users
from utils import utils

client = datastore.Client()
bp = Blueprint('users', __name__, url_prefix='/users')


@bp.errorhandler(utils.AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@bp.route('', methods=['GET'])
def get_users():
    results = users.get_users()
    return results
