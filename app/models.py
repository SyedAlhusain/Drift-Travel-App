from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))


class Account(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    location = db.Column(db.String(40), nullable=False)
    user_name = db.Column(db.String(16), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(), nullable=False)

    # If object is deleted also delete all objects that require it as a foreign key
    post = db.relationship('Post', backref='user_post', cascade='all,delete', lazy=True)
    comment = db.relationship('Comment', backref='user_comment', cascade='all,delete', lazy=True)
    comment_like = db.relationship('CommentLike', backref='user_comment_like', cascade='all,delete', lazy=True)
    post_like = db.relationship('PostLike', backref='user_post_like', cascade='all,delete', lazy=True)
    destination_folder = db.relationship('DestinationFolder', backref='destination_folder', cascade='all,delete', lazy=True)
    to_do_list = db.relationship('ToDoList', backref='to_do_list', cascade='all,delete', lazy=True)

    def get_id(self):
        return (self.user_id)


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    fk_user_id = db.Column(db.Integer, db.ForeignKey('account.user_id'), nullable=False)
    location = db.Column(db.String(40), nullable=False)
    post_title = db.Column(db.String(20), nullable=False)
    post_content = db.Column(db.String(256), nullable=False)
    image = db.Column(db.String(), nullable=False)

    post_like = db.relationship('PostLike', backref='post_like', cascade='all,delete', lazy=True)
    lodging_visit = db.relationship('LodgingVisit', backref='post_lodging_visit', cascade='all,delete', lazy=True)
    saved_destination = db.relationship('SavedDestination', backref='post_saved_destination', cascade='all,delete', lazy=True)
    comment = db.relationship('Comment', backref='post_comment', cascade='all,delete', lazy=True)


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    fk_user_id = db.Column(db.Integer, db.ForeignKey('account.user_id'), nullable=False)
    fk_post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
    comment_content = db.Column(db.String(100), nullable=False)

    comment_like = db.relationship('CommentLike', backref='comment_like', cascade='all,delete', lazy=True)


class CommentLike(db.Model):
    fk_user_id = db.Column(db.Integer, db.ForeignKey('account.user_id'), primary_key=True, nullable=False)
    fk_comment_id = db.Column(db.Integer, db.ForeignKey('comment.comment_id'), primary_key=True, nullable=False)


class PostLike(db.Model):
    fk_user_id = db.Column(db.Integer, db.ForeignKey('account.user_id'), primary_key=True, nullable=False)
    fk_post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), primary_key=True, nullable=False)


class Lodging(db.Model):
    lodging_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    lodging_name = db.Column(db.String(30), nullable=False)
    location = db.Column(db.String(40), nullable=False)

    lodging_visit = db.relationship('LodgingVisit', backref='lodging_visit', cascade='all,delete', lazy=True)


class LodgingVisit(db.Model):
    lodging_visit_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    fk_post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
    fk_lodging_id = db.Column(db.Integer, db.ForeignKey('lodging.lodging_id'), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(60), nullable=False)


class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    tag_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(50))

    post_tag = db.relationship('PostTag', backref='post_tag', cascade='all,delete', lazy=True)


class PostTag(db.Model):
    fk_tag_id = db.Column(db.Integer, db.ForeignKey('tag.tag_id'), primary_key=True, nullable=False)
    fk_post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), primary_key=True, nullable=False)


class ToDoList(db.Model):
    list_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    fk_user_id = db.Column(db.Integer, db.ForeignKey('account.user_id'), primary_key=True, nullable=False)
    to_do_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=False)


class DestinationFolder(db.Model):
    folder_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    fk_user_id = db.Column(db.Integer, db.ForeignKey('account.user_id'), nullable=False)
    folder_name = db.Column(db.String(16), nullable=False)

    saved_destination = db.relationship('SavedDestination', backref='saved_destination', cascade='all,delete', lazy=True)


class SavedDestination(db.Model):
    fk_folder_id = db.Column(db.Integer, db.ForeignKey('destination_folder.folder_id'), primary_key=True, nullable=False)
    fk_post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), primary_key=True, nullable=False)
