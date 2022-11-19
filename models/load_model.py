from google.cloud import datastore
from flask import request, jsonify
import json
import constants

client = datastore.Client()


def add_load(content):
    new_load = datastore.Entity(key=client.key(constants.loads))
    try:
        new_load.update(
            {
                "volume": content["volume"],
                "item": content["item"],
                "creation_date": content["creation_date"]
            }
        )
        new_load["carrier"] = None
        client.put(new_load)
        new_load["id"] = new_load.key.id
        new_load["self"] = request.base_url + "/" + str(new_load.key.id)
        return new_load, 201
    except KeyError:
        return {"Error": "The request object is missing at least one of the"
                         " required attributes"}, 400


def get_loads(cursor=None):
    query = client.query(kind=constants.loads)
    query_iter = query.fetch(start_cursor=cursor, limit=3)
    pages = next(query_iter.pages)
    results = list(pages)
    print(dict(pages))
    next_cursor = query_iter.next_page_token
    for e in results:
        e["id"] = e.key.id
        e["self"] = request.base_url + "/" + str(e.key.id)
        if e.get("carrier"):
            e["carrier"]["self"] = request.url_root + constants.boats + "/" \
                                   + str(e["carrier"]["id"])
    response = {"loads": results}
    if next_cursor:
        response["next"] = request.base_url + "?next=" + next_cursor.decode()
    return json.loads(json.dumps(response)), next_cursor


def get_load_by_key(load_id):
    load_key = client.key(constants.loads, int(load_id))
    load = client.get(key=load_key)
    if load:
        print(load.key.id)
        load["id"] = load.key.id
        load["self"] = request.base_url
        if load.get("carrier"):
            load["carrier"]["self"] = request.url_root + constants.boats + \
                                      "/" + str(load["carrier"]["id"])
        return load
    else:
        return {"Error": "No load with this load_id exists"}, 404


def delete_load(load_id):
    load_key = client.key(constants.loads, int(load_id))
    load = client.get(key=load_key)
    if load:
        if load["carrier"]:
            boat_id = load["carrier"]["id"]
            boat_key = client.key(constants.boats, boat_id)
            boat = client.get(key=boat_key)
            boat_loads = list(boat["loads"])
            for boat_load in boat_loads:
                if boat_load["id"] == load.key.id:
                    boat_loads.remove(boat_load)
            boat.update(
                {
                    "name": boat["name"],
                    "type": boat["type"],
                    "length": boat["length"],
                    "loads": boat_loads,
                }
            )
            client.put(boat)
            client.delete(load_key)
            return '', 204
    else:
        return {"Error": "No load with this load_id exists"}, 404
