from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import Account
from flask_login import current_user


# Form data fields for creating a student object
class RegistrationForm(FlaskForm):
    user_name = StringField('User Name', validators=[DataRequired(), Length(min=1, max=16)])
    location = StringField('Location', validators=[DataRequired(), Length(min=1, max=40)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=40)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=40)])
    password = StringField('Password', validators=[DataRequired(), Length(min=1, max=40)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired(), Length(min=1, max=40), EqualTo('password')])

    submit = SubmitField('Submit')

    # Checks if username already in use
    def validate_username(self, username):
        user = Account.query.filter_by(user_name=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please use a different one.')


class LogInForm(FlaskForm):
    user_name = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class LodgingForm(FlaskForm):
    lodging_name = StringField('Lodging Name', validators=[DataRequired(), Length(min=1, max=30)])
    location = StringField('Location', validators=[DataRequired(), Length(min=1, max=40)])

    submit = SubmitField('Submit')


class TagForm(FlaskForm):
    tag_name = StringField('Tag Name', validators=[DataRequired(), Length(min=1, max=40)])
    description = StringField('Description', validators=[DataRequired(), Length(min=1, max=40)])

    submit = SubmitField('Submit')


class ListForm(FlaskForm):
    to_do_name = StringField('To Do Name', validators=[DataRequired(), Length(min=1, max=20)])
    description = StringField('Description', validators=[Length(min=1, max=100)])

    submit = SubmitField('Submit')


class FolderForm(FlaskForm):
    folder_name = StringField('Folder Name', validators=[DataRequired(), Length(min=1, max=40)])

    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired(), Length(min=1, max=40)])
    post_title = StringField('Post Title', validators=[DataRequired(), Length(min=1, max=20)])
    post_content = StringField('Post Content', validators=[DataRequired(), Length(min=1, max=256)])
    image = FileField('Picture', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    comment_content = StringField('Comment Content', validators=[DataRequired(), Length(min=1, max=100)])

    submit = SubmitField('Submit')


class LikeCommentForm(FlaskForm):
    fk_comment_id = IntegerField('Student ID', validators=[DataRequired()])
    fk_user_id = IntegerField('User ID', validators=[DataRequired()])

    submit = SubmitField('Submit')


class LikePostForm(FlaskForm):
    fk_post_id = IntegerField('Student ID', validators=[DataRequired()])
    fk_user_id = IntegerField('User ID', validators=[DataRequired()])

    submit = SubmitField('Submit')


class PostTagForm(FlaskForm):
    fk_post_id = IntegerField('Student ID', validators=[DataRequired()])
    fk_tag_id = IntegerField('User ID', validators=[DataRequired()])

    submit = SubmitField('Submit')


class LodgingVisitForm(FlaskForm):
    cost = IntegerField('Cost', validators=[DataRequired()])
    rating = IntegerField('Rating', validators=[DataRequired()])
    comment = StringField('Lodging Name', validators=[DataRequired(), Length(min=1, max=60)])

    submit = SubmitField('Submit')


class UpdateAccountForm(FlaskForm):
    user_name = StringField('User Name', validators=[DataRequired(), Length(min=1, max=16)])
    location = StringField('Location', validators=[DataRequired(), Length(min=1, max=40)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=40)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=40)])

    def validate_username(self, user_name):
        if user_name.data != current_user.username:
            user = Account.query.filter_by(username=user_name.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    submit = SubmitField('Submit')


class UpdatePostForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired(), Length(min=1, max=40)])
    post_title = StringField('Post Title', validators=[DataRequired(), Length(min=1, max=20)])
    post_content = StringField('Post Content', validators=[DataRequired(), Length(min=1, max=256)])
    image = FileField('Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Submit')
