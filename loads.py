from flask import Blueprint, request
from google.cloud import datastore
from models import load_model as model

client = datastore.Client()
bp = Blueprint('loads', __name__, url_prefix='/loads')


@bp.route('', methods=['POST', 'GET'])
def loads_get_post():
    if request.method == 'POST':
        content = request.get_json()
        return model.add_load(content)

    elif request.method == 'GET':
        cursor = request.args.get("next")
        result, next_cursor = model.get_loads(cursor)
        return result
    else:
        return 'Method not recognized'


@bp.route('/<id>', methods=['PATCH', 'PUT', 'DELETE', 'GET'])
def load_patch_delete_get(id):
    if request.method == 'PATCH':
        content = request.get_json()
        return model.update_load_patch(content, id)
    elif request.method == 'PUT':
        content = request.get_json()
        return model.update_load_put(content, id)
    elif request.method == 'DELETE':
        return model.delete_load(id)
    elif request.method == 'GET':
        return model.get_load_by_key(id)
    else:
        return 'Method not recognized'

