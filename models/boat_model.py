from google.cloud import datastore
from flask import request
import json
import constants
from utils import utils

client = datastore.Client()
creds = constants.creds


def add_boat(content):
    """ Adds a boat. Must have a valid JWT token. """
    idinfo = utils.verify_token(request.headers, creds)
    new_boat = datastore.Entity(key=client.key(constants.boats))
    try:
        new_boat.update(
            {
                "name": content["name"],
                "type": content["type"],
                "length": content["length"],
                "owner": idinfo["sub"]
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
    """ Gets all boats for an authorized user. """
    idinfo = utils.verify_token(request.headers, creds)
    query = client.query(kind=constants.boats)
    query.add_filter("owner", "=", idinfo["sub"])
    query_iter = query.fetch(start_cursor=cursor, limit=5)
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
    """
    Gets a boat by key
    Returns: the boat if authorized
    """
    idinfo = utils.verify_token(request.headers, creds)
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=boat_key)
    if boat:
        if boat.get("owner") != idinfo.get("sub"):
            return {"Error": "Not authorized to view this boat"}, 403
        boat["id"] = int(boat_id)
        boat["self"] = request.base_url
        for load in boat["loads"]:
            load["self"] = request.url_root + constants.loads + "/" + str(
                load["id"])
        return boat
    else:
        return {"Error": "No boat with this boat_id exists"}, 404


def update_boat_put(content, boat_id):
    """ Updates a boat with PUT method """
    idinfo = utils.verify_token(request.headers, creds)
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=boat_key)
    if boat:
        if boat.get("owner") != idinfo.get("sub"):
            return {"Error": "Not authorized to edit this boat"}, 403
        try:
            boat.update(
                {
                    "name": content["name"],
                    "type": content["type"],
                    "length": content["length"],
                    "owner": boat["owner"],
                    "loads": boat["loads"]
                }
            )
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


def update_boat_patch(content, boat_id):
    """ Updates a boat with PATCH """
    idinfo = utils.verify_token(request.headers, creds)
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=boat_key)
    if boat:
        if boat.get("owner") != idinfo.get("sub"):
            return {"Error": "Not authorized to edit this boat"}, 403
        for key in content:
            boat.update(
                {
                    key: content[key]
                }
            )
        client.put(boat)
        for load in boat["loads"]:
            load["self"] = request.url_root + constants.loads + "/" + \
                           str(load["id"])
        boat["id"] = int(boat_id)
        boat["self"] = request.base_url + "/" + str(boat.key.id)
        return boat

    else:
        return {"Error": "No boat with this boat_id exists"}, 404


def delete_boat(boat_id):
    idinfo = utils.verify_token(request.headers, creds)
    key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=key)
    if client.get(key):
        if boat.get("owner") != idinfo.get("sub"):
            return {"Error": "Not authorized to delete a"
                             " load from this boat"}, 403
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
    """ Puts a load to a boat only if authorized as the boat owner """
    idinfo = utils.verify_token(request.headers, creds)
    load_key = client.key(constants.loads, int(lid))
    boat_key = client.key(constants.boats, int(bid))
    load = client.get(key=load_key)
    boat = client.get(key=boat_key)
    if boat and load:
        if boat["owner"] == idinfo["sub"]:
            if is_load_on_boat(int(lid)):
                return {"Error": "The load is already loaded on another "
                                 "boat"}, 403
            else:
                boat_loads = list(boat["loads"])
                new_load = {"id": load.key.id}
                boat_loads.append(new_load)
                boat.update(
                    {
                        "name": boat["name"],
                        "type": boat["type"],
                        "length": boat["length"],
                        "owner": boat["owner"],
                        "loads": boat_loads
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
            return {"Error": "Not authorized to add a load to this boat"}, 403
    else:
        return {"Error": "The specified boat and/or load does not exist"}, 404


def delete_load_from_boat(bid, lid):
    """ Deletes a load from a boat if authorized as boat owner """
    idinfo = utils.verify_token(request.headers, creds)
    load_key = client.key(constants.loads, int(lid))
    boat_key = client.key(constants.boats, int(bid))
    load = client.get(key=load_key)
    boat = client.get(key=boat_key)
    if boat and load:
        if boat["owner"] == idinfo["sub"]:
            if not is_load_on_boat(int(lid)):
                return {"Error": "No boat with this boat_id is loaded with "
                                 "the load with this load_id"}, 404
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
                        "owner": boat["owner"],
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
            return {"Error": "Not authorized to delete a load from this "
                             "boat"}, 403
    else:
        return {"Error": "No boat with this boat_id is loaded with the "
                         "load with this load_id"}, 404


def is_load_on_boat(lid):
    """ Utility function to check if a boat is on a load. """
    query = client.query(kind=constants.boats)
    results = list(query.fetch())
    for boat in results:
        if boat.get("loads"):
            for load in boat["loads"]:
                if load["id"] == lid:
                    return True
    return False



