import datetime
import dateutil.tz

from flask import Blueprint, render_template, request, url_for, redirect, abort
from . import model
from . import db
from flask_login import current_user
import flask_login

bp = Blueprint("main", __name__)

@bp.route("/user/<int:user_id>")
@flask_login.login_required
def user_profile(user_id):
    # get the public data of the user from the database
    user = db.session.get(model.User, user_id)
    if not user:
        abort(404, "user id {} doesn't exist.".format(user_id))
    
    # Get the top 10 most recent posts for that user_id
    query = db.select(model.Message).where((model.Message.user_id == user_id) and 
            (model.Message.response_to == None)).order_by(model.Message.timestamp.desc()).limit(10)
    posts = db.session.execute(query).scalars().all()
    
    return render_template("main/user_profile.html", user=user, posts=posts)


@bp.route("/")
@flask_login.login_required
def index():
    query = db.select(model.Message).order_by(model.Message.timestamp.desc()).limit(10)
    posts = db.session.execute(query).scalars().all()
    return render_template("main/index.html", posts=posts)


@bp.route("/post/<int:message_id>")
@flask_login.login_required
def post(message_id):
    message = db.session.get(model.Message, message_id)
    if not message:
        abort(404, "Post id {} doesn't exist.".format(message_id))
    return render_template("main/post.html", post=message)


@bp.route("/new_post", methods=["POST"])
@flask_login.login_required
def new_post(): 
    ptext = request.form.get("postText") # Get the text of the msg received from the form

   # Create a new msg object 
    message = model.Message(
            user=flask_login.current_user,
            text=ptext,
            timestamp=datetime.datetime.now(dateutil.tz.tzlocal()),
    )
    db.session.add(message)
    db.session.commit()
    return redirect(url_for("main.post", message_id=message.id))