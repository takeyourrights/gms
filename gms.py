from flask import Flask, request, jsonify, make_response
import json, requests
from werkzeug.exceptions import default_exceptions, HTTPException
import sqlite3
import json
from config import config

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
    friends = config['friends']

    dests = list(set(friends) - set(exclude))

    statuses = {}

    for dest in dests:
        r = requests.post('http://' + dest + ':5000/gms', mesg);

        try:    
            rj = r.json()

            if rj.error:
                status = 'POST failed: ' + str(rj.error)
            elif rj.success:
                status = 'POST Succeeded: ' + str(rj.success)
            else:
                status = 'POST failed: Error Status Undeterminable'

        except:
            print str(r.text)
            status = 'JSON unrecognized: ' + str(r.text)

        statuses[dest] = status

    return statuses

def craftResponse(progress, success=None, error=None):
    res = {}

    res['progress'] = progress
    
    if success:
        res['success'] = success

    if error:
        res['error'] = error

    if not success and not error:
        res['error'] = 'Could not determine success status on the remote side'

    return json.dumps(res)

@app.route("/gms", methods=['POST'])
def gms():

    progress = ""

    # Confirm request is JSON
    if not request.json:
        return craftResponse(progress, error="That's not JSON.")

    progress += "Request is JSON\n"

    mesg = request.json

    # Confirm request is actually a Message
    if mesg and ("ttl" not in mesg or "data" not in mesg):
        return craftResponse(progress, error="That's not a message.")

    progress += "Request is Message\n"
    progress += mesg_str(mesg)

    # Decrement TTL
    mesg["ttl"] -= 1;

    progress += "Decremented TTL\n"
    progress += mesg_str(mesg)

    statuses = sendMessageToFriends(mesg, [request.remote_addr])

    progress += "Sent message to:\n"
    for address, status in statuses:
        progress += "\t" + address + ": " + status + "\n"

    # TODO: Put Message on LMS
    
    return craftResponse(progress, success="We did it wooooo")

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
    
    if config['listen']:
        app.run(config['listen'])
    else:
        app.run()

