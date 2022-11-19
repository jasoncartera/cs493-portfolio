from flask import Blueprint, request
from google.cloud import datastore
from models import owner_model as model

client = datastore.Client()
bp = Blueprint('owners', __name__, url_prefix='/owners')


@bp.route('<id>/boats', methods=['GET'])
def get_owner_boats(id):
    if request.method == 'GET':
        results = model.get_boat_by_owner(id)
        return results, 200
    else:
        return 'Method not recognized'