# imports all files and programs needed
from schemeinterp import app, db
from datetime import datetime
from flask import render_template, request, flash, url_for, redirect

from schemeinterp.forms import TaskForm, LoginForm, CreateAccount, ReplyForm
from schemeinterp.models import User, Post, Tag, Reply

from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.urls import url_parse


import os
import json
from flask import render_template, request, redirect

import userlib as ul


@app.route("/index")
@app.route("/")
def root():
    subs_json_file = open(
        os.path.join("userdata", "PROT", "subs.json"), "r"
    )  # {"subid": {"author":, "file":}}
    ret = render_template("index.html.jinja", submissions=json.load(subs_json_file))
    subs_json_file.close()
    return ret


@app.route("/getsub", methods=["GET"])
def getsub():
    subs_json_file = open(os.path.join("userdata", "PROT", "subs.json"), "r")
    data = json.load(subs_json_file)
    subid = request.args.get("subid")

    with open(os.path.join("userdata", data[subid]["file"]), "r") as f:
        code = f.read()

        ret = render_template(
            "getsub.html.jinja",
            subid=subid,
            author=data[subid]["author"],
            file=data[subid]["file"],
            code=json.dumps(code),
            codepy=code,  # can't seem to get jinja to parse JSON ;-;
        )
        return ret


@app.route("/submit", methods=["GET", "POST"])
def submit():
    return render_template("submit.html.jinja")


@app.route("/postsubmit", methods=["POST"])
def postsubmit():
    try:

        mtitle = request.form["title"].replace("/", "")  # strip /

        # Create file if it does not exist, else do nothing
        f = open(os.path.join("userdata", mtitle), "x")
        f.close()
        f = open(os.path.join("userdata", mtitle), "w")
        f.write(request.form["codebox"])
        f.close()

        with open(os.path.join("userdata", "PROT", "subs.json"), "r+") as subsf:
            # add it to our submission JSON file
            curdata = json.loads(subsf.read())
            curdata[mtitle] = {
                "author": request.form["author"],
                "file": mtitle,
            }
            subsf.seek(0)
            subsf.truncate()
            subsf.write(json.dumps(curdata))

            uf = ul.UserFile(
                os.path.join("userdata", "PROT", "passwd"),
                os.path.join("userdata", "PROT", "shadow"),
            )

            uf("add_user")(mtitle, request.form["passwd"])

    except OSError:  # ...no overwriting other submissions, sorry mate
        pass

    return redirect("/")


@app.route("/editsub", methods=["GET", "POST"])
def editsub():
    with open(os.path.join("userdata", "PROT", "subs.json"), "r+") as subsf:
        curdata = json.loads(subsf.read())
        with open(
            os.path.join("userdata", curdata[request.args.get("subid")]["file"]), "r+"
        ) as cbf:
            return render_template(
                "edit.html.jinja", subid=request.args.get("subid"), codebox=cbf.read()
            )


@app.route("/auth", methods=["GET", "POST"])
def auth():
    return render_template(
        "auth.html.jinja",
        action=request.args.get("action"),
        subid=request.args.get("subid"),
        codebox=request.form.get("codebox"),
    )


@app.route("/postauth", methods=["GET", "POST"])
def postauth():
    uf = ul.UserFile(
        os.path.join("userdata", "PROT", "passwd"),
        os.path.join("userdata", "PROT", "shadow"),
    )

    # If the auth failed:
    if not uf("check")(request.args.get("subid"), request.form["passwd"]):
        return """
<link rel="stylesheet" href="static/css/style.css">
<title>Authentication failure</title>
<center><h1>Authentication failure</h1></center>
<center><a class="button" href="/">Go back</a></center>
            """
    if request.args.get("action") == "delete":
        # Delete
        with open(os.path.join("userdata", "PROT", "subs.json"), "r+") as subsf:
            curdata = json.loads(subsf.read())
            try:
                os.remove(
                    os.path.join("userdata", curdata[request.args.get("subid")]["file"])
                )  # remove the file...
            except OSError:
                #  for some reason the file did not exist... or maybe permissions messed up?
                pass

            uf("del_user")(request.args.get("subid"))
            del curdata[request.args.get("subid")]  # remove that entry...

            subsf.seek(0)
            subsf.truncate()
            subsf.write(json.dumps(curdata))  # and write the new one

        return redirect("/")

    else:
        # Edit
        with open(os.path.join("userdata", "PROT", "subs.json"), "r+") as subsf:
            curdata = json.loads(subsf.read())
        with open(
            os.path.join("userdata", curdata[request.args.get("subid")]["file"]), "w"
        ) as cbf:
            cbf.write(request.form["codebox"])
        return redirect("/")


##### FORUM

# starting page
@app.route("/forum")
def forum():
    return render_template("forumindex.html")


# page to show replies and posts
@app.route("/postpage/<int:post_id>", methods=["GET"])
@login_required
def viewpost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    user = User.query.filter_by(id=post.user_id).first().username
    user_replies = []
    # gets the post requested by current user and also gets the replies and user creater of the post
    for i in range(len(post.replies)):
        user_replies.append(
            User.query.filter_by(id=post.replies[i].user_id).first().username
        )
    # creates a reply list
    return render_template(
        "postpage.html", post=post, username=user, user_replies=user_replies
    )


# page to show all the posts of the forum
@app.route("/mainpage")
@login_required
def index():
    posts = Post.query.order_by(Post.tdate).all()
    # gets all of the posts from database
    users = []
    for i in range(len(posts)):
        users.append(User.query.filter_by(id=posts[i].user_id).first().username)
    return render_template("mainpage.html", tasks=posts, users=users)


# page for form to create account
@app.route("/signup", methods=["GET", "POST"])
def signup():
    account = CreateAccount()
    # creates account and inserts it in the database
    if request.method == "POST":
        if account.validate_on_submit():
            newuser = User(
                username=account.username.data,
                email=account.email.data,
                date_created=datetime.now(),
            )
            newuser.set_password(account.password.data)
            db.session.add(newuser)
            db.session.commit()

            flash("User added successfully", category="success")
            return redirect(url_for("login"))
        else:
            flash("Failure to submit form {}".format(account.errors), category="danger")

    return render_template("signup.html", account=account)


# page for form to create post
@app.route("/wtform", methods=["GET", "POST"])
@login_required
def wtform():
    form = TaskForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # create and update DB on newpost
            newpost = Post(
                name=form.name.data,
                description=form.description.data,
                tdate=datetime.now(),
                user_id=current_user.id,
            )
            db.session.add(newpost)
            db.session.commit()

            # extract and clean up each tag before inserting into the database
            tags = [tag.strip() for tag in form.tags.data.split(",")]

            for tag in tags:
                # find out if this user already created this tag already
                gotTagByThisUser = Tag.query.filter_by(
                    user_id=current_user.id, name=tag
                ).first()
                if (
                    not gotTagByThisUser
                ):  # if current user does not have this tag, create new tag under this user
                    newtag = Tag(name=tag, user_id=current_user.id)  # create new tag
                    db.session.add(newtag)  # add to db
                    db.session.commit()  # commit to db
                    newpost.tags.append(newtag)  # add newtag to current newtodo
                else:
                    newpost.tags.append(
                        gotTagByThisUser
                    )  # add the existing tag to current newtodo

                db.session.commit()  # ensure that all tags link to current newtodo is commited to db

            flash("Task added successfully", category="success")
            return redirect(url_for("index"))
        else:
            flash("Failure to submit form {}".format(form.errors), category="danger")
    return render_template("wtform.html", form=form)


# page to go to form which create new reply
@app.route("/replyform/<int:postid>", methods=["GET", "POST"])
@login_required
def replyform(postid):
    reply = ReplyForm()
    if request.method == "POST":
        if reply.validate_on_submit():
            # creates and updates reply db
            newreply = Reply(
                reply_content=reply.reply_content.data,
                user_id=current_user.id,
                post_id=postid,
            )
            db.session.add(newreply)
            db.session.commit()
            flash("Reply added successfully", category="success")
            return redirect(url_for("index"))
        else:
            flash("Failure to submit reply {}".format(reply.errors), category="danger")
    return render_template("replyform.html", reply=reply)


# page to login to a page
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "GET":
        return render_template("login.html", form=form)
    else:
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None:  # wrong user
                flash("No such user", category="danger")
                return redirect(url_for("login"))
            elif not user.check_password(form.password.data):  # Wrong password
                flash("Wrong Password", category="danger")
                return redirect(url_for("login"))
            else:  # authorise login
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get("next")
                if not next_page or url_parse(next_page).netloc != "":
                    next_page = url_for("index")
                return redirect(next_page)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


"""
@app.route("/update/<int:task_id>", methods=["GET", "POST"])
@login_required
def updatetask(task_id):
  form = TaskForm()
  if request.method == "GET":
    if task_id: #if a task_id param is passed in
        task = Post.query.filter_by(user_id = current_user.id, id = task_id).first()
        form.name.data = task.name
        form.description.data = task.description
        form.tdate.data = task.tdate
        form.completed.data = task.completed
        form.tags.data = ", ".join([tag.name for tag in task.tags])
    else:
      flash("No such record.")
  

  else: #request.method == "POST":
    if form.validate_on_submit():
      task = Todo.query.filter_by(user_id = current_user.id, id = task_id).first()
      task.name = form.name.data
      task.description = form.description.data
      task.completed = form.completed.data
      task.tdate = form.tdate.data

      task.tags = [] #flush away all the tags, and start afresh - lazy way ;p 

      #extract and clean up each tag before inserting into the database
      tags = [tag.strip() for tag in form.tags.data.split(",")]
      
      for tag in tags:
        #find out if this user already created this tag already
        gotTagByThisUser = Tag.query.filter_by(user_id = current_user.id, name = tag).first()
        if not gotTagByThisUser: #if current user does not have this tag, create new tag under this user
          newtag = Tag(name=tag, user_id = current_user.id) #create new tag
          db.session.add(newtag) #add to db
          db.session.commit() #commit to db
          task.tags.append(newtag) #add newtag to current newtodo
          
        else:
          task.tags.append(gotTagByThisUser) #add the existing tag to current newtodo
        
        db.session.commit() #ensure that all tags link to current newtodo is commited to db

      db.session.commit()
      flash("Task updated successfully", category="success")
      return redirect(url_for("index"))
    else:
      flash("Failure to submit form {}".format(form.errors))
  return render_template("wtform.html", form=form)

@app.route("/delete/<int:task_id>")
def deletetask(task_id):
  tasktodel = Post.query.filter_by(user_id = current_user.id, id = task_id).first()
  if tasktodel:
    db.session.delete(tasktodel)
    db.session.commit()
    flash("Task deleted successfully", category="success")
  else:
     flash("No such task", category="danger")
  return redirect(url_for("index"))"""
