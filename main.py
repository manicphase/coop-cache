from flask import Flask, send_from_directory, render_template, request, send_file, Response, redirect, make_response
from hashlib import sha256 as SHA256
import ConfigParser
import key_stuff

app = Flask("__name__")

cs = {}
config = ConfigParser.RawConfigParser()

def get_local_keys():
    global cs
    config = ConfigParser.RawConfigParser()
    config.read('sessions.cfg')
    for section in config.sections():
        username = config.get(section, "username")
        cs[section] = key_stuff.CryptoStuff(username)
        
get_local_keys()

@app.route("/")
def index():
    session = request.cookies.get('session')    
    config = ConfigParser.RawConfigParser()
    config.read('sessions.cfg')
    return "hello %s" % config.get(session, "username")
        
    global cs
    try:
        cs = key_stuff.CryptoStuff()
    except:
        return redirect("/create_user", code=302)        
    return "hello dave"
    
@app.route("/create_user", methods=["POST","GET"])
def create_user():
    if request.remote_addr in ["127.0.0.1", "localhost"]:
        if request.method == "GET":
            return render_template("create_user.html")
        elif request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            passhash = SHA256(password).hexdigest()
            config.add_section(passhash)
            config.set(passhash, "username", username)
            config.set(passhash, "password", password)
            key_stuff.CreateUser(username)
            with open('sessions.cfg', 'wb') as configfile:
                config.write(configfile)
                
            resp = make_response(redirect("/", code=302))
            resp.set_cookie("session", passhash)
            return resp           
    return "Only local users may create accounts"

@app.route("/public_key")
def public_key():
    session = request.cookies.get('session')
    return cs[session].public_key()
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8900, debug=True)
