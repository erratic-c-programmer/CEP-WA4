from schemeinterp import app, db
from datetime import datetime
from flask import render_template, request, flash, url_for, redirect

from schemeinterp.forms import TaskForm, LoginForm, CreateAccount, ReplyForm
from schemeinterp.models import User, Post, Tag, Reply

from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.urls import url_parse


@app.route("/")
def start():
    return render_template("index.html")


@app.route("/postpage/<int:post_id>", methods=["GET"])
@login_required
def viewpost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    user = User.query.filter_by(id=post.user_id).first().username
    user_replies = []
    for i in range(len(post.replies)):
        user_replies.append(
            User.query.filter_by(id=post.replies[i].user_id).first().username
        )
    return render_template(
        "postpage.html", post=post, username=user, user_replies=user_replies
    )


@app.route("/mainpage")
@login_required
def index():
    posts = Post.query.order_by(Post.tdate).all()
    users = []
    for i in range(len(posts)):
        users.append(User.query.filter_by(id=posts[i].user_id).first().username)
    return render_template("mainpage.html", tasks=posts, users=users)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    account = CreateAccount()
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


@app.route("/wtform", methods=["GET", "POST"])
@login_required
def wtform():
    form = TaskForm()
    if request.method == "POST":
        if form.validate_on_submit():
            # create and update DB on newtodo
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


@app.route("/replyform/<int:postid>", methods=["GET", "POST"])
@login_required
def replyform(postid):
    reply = ReplyForm()
    if request.method == "POST":
        if reply.validate_on_submit():
            # create and update DB on newtodo
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
