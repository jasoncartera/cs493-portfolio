from google.cloud import datastore
from flask import request

import constants


client = datastore.Client()

creds = constants.creds


def add_user(idinfo):
    """ Adds a user to Datastore """
    new_user = datastore.Entity(key=client.key(constants.users))
    if not check_user_exists(idinfo):
        new_user.update(
            {
                "first": idinfo["given_name"],
                "last": idinfo["family_name"],
                "uid": idinfo["sub"]
            }
        )
        client.put(new_user)


def get_users():
    """ Gets all users """
    query = client.query(kind=constants.users)
    results = list(query.fetch())
    for e in results:
        e["id"] = e.key.id
    return results


def get_boat_by_user(owner_id):
    """ Gets public boats for a user """
    query = client.query(kind=constants.boats)
    query.add_filter("public", "=", True)
    query.add_filter("owner", "=", owner_id)
    results = list(query.fetch())
    for e in results:
        e["id"] = e.key.id
        e["self"] = request.base_url + "/" + str(e.key.id)
    return results


def check_user_exists(idinfo):
    """ Checks if a user exists or not """
    query = client.query(kind=constants.users)
    query.add_filter("uid", "=", idinfo["sub"])
    results = list(query.fetch())
    if len(results) == 0:
        return False
    return True
