from flask import Flask, render_template, request, redirect, url_for
from google.cloud import datastore
import google_auth_oauthlib.flow
import hashlib
import os

import constants


app = Flask(__name__)

client = datastore.Client()
creds = constants.creds


@app.route('/')
def index():  # put application's code here
    return render_template("login.html")


@app.route('/button', methods=['GET'])
def button():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        creds,
        scopes=["https://www.googleapis.com/auth/userinfo.profile"])
    flow.redirect_uri = url_for('oauth_callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        state=hashlib.sha256(os.urandom(1024)).hexdigest(),
        include_granted_scopes='true')
    return redirect(authorization_url)


@app.route('/oauth', methods=['GET', 'POST'])
def oauth_callback():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        creds,
        scopes=["https://www.googleapis.com/auth/userinfo.profile"])
    flow.redirect_uri = url_for('oauth_callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    return render_template('user_info.html', user=flow.credentials.id_token)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
