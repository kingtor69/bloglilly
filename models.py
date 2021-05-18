"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """a class for users table"""
    __tablename__ = "users"

    def __repr__ (self):
        """show info about User"""
        u = self
        return f"{u.id}: {u.first_name} {u.last_name}. {u.image_url}"

    id = db.Column(db.Integer,
                primary_key=True,
                autoincrement=True)
    first_name = db.Column(db.String(20),
                nullable=False)
    last_name = db.Column(db.String(20),
                default="")
    image_url = db.Column(db.String(2083),
                default="https://images.unsplash.com/photo-1455390582262-044cdead277a?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=966&q=80")
    statement = db.Column(db.Text)
    statement_medium = db.Column(db.String(144))
    statement_short = db.Column(db.String(42))
    full_name = db.Column(db.String(41))

    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")


    @property
    def full_name(self):
        """outputs a single string of first and last name with a space between"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

class Post(db.Model):
    """a class for posts"""
    __tablename__ = "posts"

    def __repr__ (self):
        """show info about the user"""
        p = self
        return f"{p.id}: {p.title}\n{p.content_short}\nposted at {p.created_on} by {p.user_id}(FK)"

    id = db.Column(db.Integer,
                primary_key=True,
                autoincrement=True)
    title = db.Column(db.String(50),
                default="blog-like post")
    content = db.Column(db.Text,
                nullable=False)
    content_medium = db.Column(db.String(222),
                nullable=False)
    content_short = db.Column(db.String(42),
                nullable=False)
    created_on = db.Column(db.DateTime,
                default=datetime.utcnow(),
                nullable=False)
    user_id = db.Column(db.Integer,
                db.ForeignKey('users.id'), 
                nullable=False)
    pretified_creation_datetime = db.Column(db.String(31), default="")

    # posts_tags = db.relationship("PostTag", backref="post", cascade="all, delete")

    # future development TODO: add an updated_datetime and an 'edited' flag...?

    def pretify_creation_datetime(self):
        """generate user-readable and pretty-looking date/time from SQL datetime"""

        # pretify month
        month_num = self.created_on.month
        months = ['no zero month', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        month = months[self.created_on.month]

        hour = self.created_on.hour
        ampm = "am"
        if hour > 12:
            hour = hour - 12
            ampm = "pm"

        return f"{self.created_on.year} {month} {self.created_on.day} at {hour}:{self.created_on.minute}{ampm} UTC"

        # db.session.add(self)
        # db.session.commit()

class Tag(db.Model):
    """this is a model for tags to be used in categorizing blog posts"""
    __tablename__ = "tags"

    def __repr__(self):
        """show info about the tag"""
        t = self
        return f"{t.id} '{t.tag}' {t.this_post_has}"

    id = db.Column(db.Integer,
                primary_key = True,
                autoincrement = True)
    tag = db.Column(db.String(26),
                nullable=False,
                unique=True)
    # this_post_has = db.Column(db.Boolean, default=False)

    posts = db.relationship(
        'Post',
        secondary="posts_tags",
        # cascade="all,delete",
        backref="tags",
    )

class PostTag(db.Model):
    """many-to-many reference matching tags with posts"""
    __tablename__ = "posts_tags"

    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id'),
                        primary_key=True)
    tag_id = db.Column(db.Integer,
                   db.ForeignKey('tags.id'),
                   primary_key=True)

    # primary_key = (post_id, tag_id)

    def __repr__ (self):
        """show the references"""
        pt = self
        return f"post_id={pt.post_id} tag_id={pt.tag_id}"

    @classmethod
    def list_tags_for_one_post(cls, post):
        post_tags = cls.query.all()
        ret_tags = []
        for post_tag in post_tags:
            if post_tag.post_id == post.id:
                matched_tag = Tag.query.get(post_tag.tag_id)
                ret_tags.append(matched_tag.tag)
        return ret_tags

    @classmethod
    def list_tags_for_multiple_posts(cls, posts):
        tags_keyed_to_post = []
        for post in posts:
            tags_keyed_to_post.append({post: cls.list_tags_for_one_post(post)})

        return tags_keyed_to_post

    @classmethod
    def get_tags_for_post(cls, post):
        post_tags = cls.query.all()
        ret_tags = []
        for post_tag in post_tags:
            if post_tag.post_id == post.id:
                tag_in_post = Tag.query.get(post_tag.tag_id)
                ret_tags.append(tag_in_post)
        return ret_tags

    @classmethod
    def get_tags_for_multiple_posts(cls, posts):
        tags_keyed_to_post = []
        for post in posts:
            tags_keyed_to_post.append({post: cls.get_tags_for_post(post)})
        return tags_keyed_to_post