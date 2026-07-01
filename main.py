from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_cors import CORS
import user_management as dbHandler
import secrets
from flask_wtf import CSRFProtect
from urllib.parse import urlparse
from flask import session
from datetime import timedelta



def is_safe_local_path(path):
    if not path:
        return False
    parsed = urlparse(path)
    if parsed.scheme or parsed.netloc:
        return False
    return path.startswith("/") and not path.startswith("//")

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(32)
csrf = CSRFProtect(app)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
# Enable CORS to allow cross-origin requests (needed for CSRF demo in Codespaces)
CORS(app)


@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if not session.get("username"):
        return redirect("/")
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        if is_safe_local_path(url):
            return redirect(url, code=302)
        return render_template("/index.html")
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insertFeedback(feedback)
        feedback_list = dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back", feedback_list=feedback_list)
    else:
        feedback_list = dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back", feedback_list=feedback_list)


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        if is_safe_local_path(url):
            return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        dbHandler.insertUser(username, password, DoB)
        return render_template("/index.html")
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
def home():
    # Simple Dynamic menu
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        if is_safe_local_path(url):
            return redirect(url, code=302)
    # Pass message to front end
    elif request.method == "GET":
        msg = request.args.get("msg", "")
        return render_template("/index.html", msg=msg)
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            session.clear()
            session.permanent = True
            session["username"] = username
            feedback_list = dbHandler.listFeedback()
            return render_template("/success.html", value=username, state=isLoggedIn, feedback_list=feedback_list)
        else:
            return render_template("/index.html", msg="Invalid username or password.")
    else:
        return render_template("/index.html")


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=False, host="0.0.0.0", port=5000)
