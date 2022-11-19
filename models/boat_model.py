from google.cloud import datastore
from flask import request
import json
import constants

client = datastore.Client()


def add_boat(content):
    new_boat = datastore.Entity(key=client.key(constants.boats))
    try:
        new_boat.update(
            {
                "name": content["name"],
                "type": content["type"],
                "length": content["length"]
            }
        )
        new_boat["loads"] = []
        client.put(new_boat)
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = request.base_url + "/" + str(new_boat.key.id)
        return new_boat, 201
    except KeyError:
        return {"Error": "The request object is missing at least one of the"
                         " required attributes"}, 400


def get_boats(cursor=None):
    query = client.query(kind=constants.boats)
    query_iter = query.fetch(start_cursor=cursor, limit=3)
    pages = next(query_iter.pages)
    results = list(pages)
    next_cursor = query_iter.next_page_token
    for e in results:
        e["id"] = e.key.id
        e["self"] = request.base_url + "/" + str(e.key.id)
        for load in e["loads"]:
            load["self"] = request.url_root + constants.loads + "/" + str(
                load["id"])
    response = {"boats": results}
    if next_cursor:
        response["next"] = request.base_url + "?next=" + next_cursor.decode()
    return json.loads(json.dumps(response)), next_cursor


def get_boat_by_key(boat_id):
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=boat_key)
    if boat:
        boat["id"] = int(boat_id)
        boat["self"] = request.base_url
        for load in boat["loads"]:
            load["self"] = request.url_root + constants.loads + "/" + str(
                load["id"])
        return boat
    else:
        return {"Error": "No boat with this boat_id exists"}, 404


def update_boat(content, boat_id):
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=boat_key)
    if boat:
        try:
            boat.update(
                {
                    "name": content["name"],
                    "type": content["type"],
                    "length": content["length"],
                }
            )
            if content.get("loads"):
                boat["loads"] = content["loads"]
            client.put(boat)
            for load in boat["loads"]:
                load["self"] = request.url_root + constants.loads + "/" + \
                               str(load["id"])
            boat["id"] = int(boat_id)
            boat["self"] = request.base_url + "/" + str(boat.key.id)
            return boat
        except KeyError:
            return {"Error": "The request object is missing at least one of "
                             "the required attributes"}, 400
    else:
        return {"Error": "No boat with this boat_id exists"}, 404


def delete_boat(boat_id):
    key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=key)
    if client.get(key):
        loads = list(boat["loads"])
        # Remove loads from deleted boats
        if loads:
            for load in loads:
                load_key = client.key(constants.loads, load["id"])
                load = client.get(key=load_key)
                load.update(
                    {
                        "volume": load["volume"],
                        "carrier": None,
                        "item": load["item"],
                        "creation_date": load["creation_date"]
                    }
                )
                client.put(load)

        client.delete(key)
        return '', 204
    else:
        return {"Error": "No boat with this boat_id exists"}, 404


def put_load_to_boat(bid, lid):
    load_key = client.key(constants.loads, int(lid))
    boat_key = client.key(constants.boats, int(bid))
    load = client.get(key=load_key)
    boat = client.get(key=boat_key)
    if boat and load:
        if is_load_on_boat(int(lid)):
            return {"Error": "The load is already loaded on another boat"}, 403
        else:
            boat_loads = list(boat["loads"])
            new_load = {"id": load.key.id}
            boat_loads.append(new_load)
            boat.update(
                {
                    "name": boat["name"],
                    "type": boat["type"],
                    "length": boat["length"],
                    "loads": boat_loads,
                }
            )
            client.put(boat)

            carrier_load = {"id": boat.key.id, "name": boat["name"]}
            load.update(
                {
                    "volume": load["volume"],
                    "carrier": carrier_load,
                    "item": load["item"],
                    "creation_date": load["creation_date"]
                }
            )
            client.put(load)
            return '', 204
    else:
        return {"Error": "The specified boat and/or load does not exist"}, 404


def delete_load_from_boat(bid, lid):
    load_key = client.key(constants.loads, int(lid))
    boat_key = client.key(constants.boats, int(bid))
    load = client.get(key=load_key)
    boat = client.get(key=boat_key)
    if boat and load:
        if not is_load_on_boat(int(lid)):
            return {"Error": "No boat with this boat_id is loaded with the "
                             "load with this load_id"}, 404
        else:
            boat_loads = list(boat["loads"])
            for boat_load in boat_loads:
                if boat_load["id"] == int(lid):
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
            load.update(
                {
                    "volume": load["volume"],
                    "carrier": None,
                    "item": load["item"],
                    "creation_date": load["creation_date"]
                }
            )
            client.put(load)
            return '', 204
    else:
        return {"Error": "No boat with this boat_id is loaded with the "
                         "load with this load_id"}, 404


def get_loads_from_boat(bid):
    boat_key = client.key(constants.boats, int(bid))
    boat = client.get(key=boat_key)
    if boat:
        if boat["loads"]:
            loads = []
            for load in boat["loads"]:
                load_key = client.key(constants.loads, load["id"])
                load = client.get(key=load_key)
                load["self"] = request.url_root + constants.loads + "/" + str(
                    load.key.id)
                loads.append(load)
        return {"loads": loads}
    else:
        return {"Error": "No boat with this boat_id exists"}, 404


def is_load_on_boat(lid):
    query = client.query(kind=constants.boats)
    results = list(query.fetch())
    for boat in results:
        if boat.get("loads"):
            for load in boat["loads"]:
                if load["id"] == lid:
                    return True
    return False



