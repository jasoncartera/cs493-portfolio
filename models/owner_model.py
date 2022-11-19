from google.cloud import datastore
from flask import request

import constants

client = datastore.Client()

creds = constants.creds


def get_boat_by_owner(owner_id):
    query = client.query(kind=constants.boats)
    query.add_filter("public", "=", True)
    query.add_filter("owner", "=", owner_id)
    results = list(query.fetch())
    for e in results:
        e["id"] = e.key.id
        e["self"] = request.base_url + "/" + str(e.key.id)
    return results
