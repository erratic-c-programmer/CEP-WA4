from schemeinterp import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from schemeinterp import login

from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))
    email = db.Column(db.String(120), index=True, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    posts = db.relationship(
        "Post", backref="user", lazy="joined"
    )  # ONE TO MANY relship
    replies = db.relationship("Reply", backref="user", lazy="joined")
    tags = db.relationship("Tag", backref="user", lazy="joined")  # ONE TO MANY relship

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String(256))
    tdate = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tags = db.relationship("Tag", backref="posts", lazy=True)
    replies = db.relationship("Reply", backref="reply", lazy=True)


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply_content = db.Column(db.String(500))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # Which user did this tag belong to?
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))


def insert_dummy_data(db):
    db.drop_all()
    db.create_all()
    admin = User(username="admin", email="admin@example.com")
    guest = User(username="guest", email="guest@example.com")
    admin.set_password("secretpassword")
    guest.set_password("secretpassword")

    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()

    # Adding Todo1, and linking it to its' user owner directly
    post1 = Post(
        name="How to do this",
        description="scheme stuff",
        tdate=datetime.now(),
        user_id=admin.id,
    )

    db.session.add(post1)

    # Adding Todo2, without specifying which owner
    post2 = Post(
        name="I love scheme",
        description="scheme loves me",
        tdate=datetime.now() + timedelta(days=14),
    )

    # specifying todo2's owner through the User.tasks list append method.
    admin.posts.append(post2)

    # Adding Todo3 and not specifying who it belongs to
    post3 = Post(
        name="ddd", description="sss", tdate=datetime.now() + timedelta(days=7)
    )

    # Adding Todo4 and not specifying who it belongs to
    post4 = Post(
        name="sdfad", description="adgwbg", tdate=datetime.now() + timedelta(days=7)
    )

    # Link todo3 and todo4 to admin user using the User.tasks list extend method.
    admin.posts.extend([post3, post4])

    db.session.commit()

    # Adding new tags relating to the admin user
    ceptag = Tag(name="Help", user_id=admin.id)
    cletag = Tag(name="Praise", user_id=admin.id)
    worktag = Tag(name="Work", user_id=guest.id)
    ccatag = Tag(name="Others", user_id=admin.id)

    db.session.add(ceptag)
    db.session.add(cletag)
    db.session.add(worktag)
    db.session.add(ccatag)
    db.session.commit()

    # Tagging todo1 using append method
    post1.tags.append(cletag)  # add tags one by one
    post1.tags.append(worktag)  # add tags one by one

    # Adding multiple tags to todo2, todo3 and todo4 using extend method
    post2.tags.extend([worktag, ceptag])  # add tags as a list
    post3.tags.extend([worktag, ceptag])  # add tags as a list
    post3.tags.append(ccatag)
    db.session.commit()

    reply1 = Reply(
        reply_content="Hi, here is how i can help you",
        post_id=post1.id,
        user_id=post1.user_id,
    )
    reply2 = Reply(
        reply_content="ok, thank you for the praise!",
        post_id=post2.id,
        user_id=post2.user_id,
    )
    reply3 = Reply(
        reply_content="what are you saying", post_id=post2.id, user_id=post2.user_id
    )

    db.session.add(reply1)
    db.session.add(reply2)
    db.session.add(reply3)
    db.session.commit()
