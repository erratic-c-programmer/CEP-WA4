from simpleapp import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from simpleapp import login

from flask_login import UserMixin


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lifemoto = db.Column(db.String(256))
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )  # ONE TO ONE relationship with User


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
    profile = db.relationship(
        "Profile", backref="user", lazy="joined", uselist=False
    )  # ONE TO ONE relationship with Profile

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Helper table - Many-To-Many Relship between Todo and Tag table
categories = db.Table(
    "categories",
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    description = db.Column(db.String(256))
    tdate = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    tags = db.relationship(
        "Tag", secondary="categories", backref=db.backref("posts", lazy="dynamic")
    )
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

    admin_pro = Profile(lifemoto="Eat Sleep Code Repeat", user_id=admin.id)
    guest_pro = Profile(lifemoto="Live Laugh Love", user_id=guest.id)
    db.session.add(guest_pro)
    db.session.add(admin_pro)
    db.session.commit()

    # Adding Todo1, and linking it to its' user owner directly
    post1 = Post(
        name="Prepare CLE",
        description="Print worksheets",
        tdate=datetime.now(),
        completed=False,
        user_id=admin.id,
    )

    db.session.add(post1)

    # Adding Todo2, without specifying which owner
    post2 = Post(
        name="Prepare CEP notes",
        description="Email teachers for project specifications",
        tdate=datetime.now() + timedelta(days=14),
        completed=False,
    )

    # specifying todo2's owner through the User.tasks list append method.
    admin.tasks.append(post2)

    # Adding Todo3 and not specifying who it belongs to
    post3 = Post(
        name="WA4",
        description="Issue WA4 requirements",
        tdate=datetime.now() + timedelta(days=7),
        completed=False,
    )

    # Adding Todo4 and not specifying who it belongs to
    post4 = Post(
        name="CCA records",
        description="Update CCA records",
        tdate=datetime.now() + timedelta(days=7),
        completed=False,
    )

    # Link todo3 and todo4 to admin user using the User.tasks list extend method.
    admin.tasks.extend([post3, post4])

    db.session.commit()

    # Adding new tags relating to the admin user
    ceptag = Tag(name="CEP", user_id=admin.id)
    cletag = Tag(name="CLE", user_id=admin.id)
    worktag = Tag(name="Work", user_id=guest.id)
    ccatag = Tag(name="CCA", user_id=admin.id)

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
