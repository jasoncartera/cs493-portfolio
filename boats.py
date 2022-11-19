from flask import Blueprint, request, jsonify
from google.cloud import datastore
from models import boat_model as model
from utils import utils

client = datastore.Client()
bp = Blueprint('boats', __name__, url_prefix='/boats')


@bp.errorhandler(utils.AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@bp.route('', methods=['POST','GET'])
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        return model.add_boat(content)

    elif request.method == 'GET':
        cursor = request.args.get("next")
        result, next_cursor = model.get_boats(cursor)
        return result
    else:
        return 'Method not recognized'


@bp.route('/<id>', methods=['PATCH','DELETE','GET'])
def boat_patch_delete_get(id):
    if request.method == 'PATCH':
        content = request.get_json()
        return model.update_boat(content, id)

    elif request.method == 'DELETE':
        return model.delete_boat(id)

    elif request.method == 'GET':
        return model.get_boat_by_key(id)
    else:
        return 'Method not recognized'


@bp.route('/<bid>/loads/<lid>', methods=['PUT', 'DELETE'])
def boat_put_load(lid, bid):
    if request.method == 'PUT':
        return model.put_load_to_boat(bid, lid)
    if request.method == 'DELETE':
        return model.delete_load_from_boat(bid, lid)


@bp.route('/<bid>/loads', methods=['GET'])
def get_all_loads_for_boat(bid):
    if request.method == 'GET':
        return model.get_loads_from_boat(bid)
    else:
        return 'Method not recognized'
