from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import default_exceptions, HTTPException
import sqlite3
import json

app = Flask( __name__ )

@app.route("/west", methods=["GET"])
def read():
    conn = sqlite3.connect('/tmp/wall.db')
    conn.execute(''' SELECT * FROM queue WHERE id = ( SELECT MAX(id) FROM queue ) ''')
    print curr.fetchone()
    
@app.route("/west", methods=["POST"])
def write():
    conn = sqlite3.connect('/tmp/wall.db')
    conn.execute(''' INSERT INTO queue (ttl, data) VALUES (30, ?) ''', ( request.form["mesg"] ) )
    conn.close()

    return True

def make_json_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code
                            if isinstance(ex, HTTPException)
                            else 500)
    return response

for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = make_json_error

def mesg_str(mesg):
    return "\tttl:  " + str(mesg["ttl"]) + "\n" + \
           "\tdata: " + str(mesg["data"]) + "\n"

def sendMessageToFriends(mesg, exclude):
    friends = ['192.168.15.142', '127.0.0.1']

    dests = list(set(friends) - set(exclude))

    return dests

@app.route("/gms", methods=['POST'])
def gms():

    progress = ""

    # Confirm request is JSON
    if not request.json:
        return "That's not JSON."

    progress += "Request is JSON\n"

    mesg = request.json

    # Confirm request is actually a Message
    if mesg and ("ttl" not in mesg or "data" not in mesg):
        return "That's not a Message."

    progress += "Request is Message\n"
    progress += mesg_str(mesg)

    # Decrement TTL
    mesg["ttl"] -= 1;

    progress += "Decremented TTL\n"
    progress += mesg_str(mesg)

    dests = sendMessageToFriends(mesg, [request.remote_addr])

    progress += "Sent message to:\n"
    for dest in dests:
        progress += "\t" + dest + "\n"

    # TODO: Put Message on LMS
    
    return progress

@app.route("/gms", methods=["GET"])
def gmsInterface():
    return """
<form method="post">
<input type="text" name="ttl" value="30">
<input type="submit">
</form>

    """;

if __name__ == '__main__':
    app.debug = True
    app.run()

