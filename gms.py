from flask import Flask, request
import sqlite3

app = Flask( __name__ )

@app.route("/", methods=["GET"])
def read():
    try:
        with open("/tmp/wall", 'r') as wall:
            status = ""
            for line in wall:
                status += line
            wall.truncate(0)
    except Except as e:
        status = str(e)
    finally:
        return status

@app.route("/", methods=["POST"])
def write():
    try:
        with open("/tmp/wall", 'w') as wall:
            wall.write(request.form['mesg'])
            status = "Success"
    except Exception as e:
        status = str(e)
    finally:
        return status
    

if __name__ == "__main__":
    app.run(debug=True)
