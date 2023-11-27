import secrets
import os

import psycopg2
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LogInForm, FolderForm, PostForm, TagForm, CommentForm, LodgingForm, LodgingVisitForm, ListForm, UpdateAccountForm, UpdatePostForm
from app.models import Account, DestinationFolder, Post, PostLike, CommentLike, SavedDestination, Tag, PostTag, Comment, Lodging, LodgingVisit, ToDoList
from flask_login import login_user, current_user, logout_user, login_required


# Route for the home page
@app.route("/")
def home():
    return render_template('home.html')


# Route for creating an account
@app.route("/register", methods=['GET', 'POST'])
def register():
    # Checks if user is already logged in to an account and redirects them if they are
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    # If user input data is valid hash the password and create a user account with the data
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Account(location=form.location.data, user_name=form.user_name.data, first_name=form.first_name.data,
                       last_name=form.last_name.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.user_name.data}! You can now log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# Route for the login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Checks if user is already logged in to an account and redirects them if they are
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LogInForm()
    # Checks if user input correct login details and logs them in if they are correct
    if form.validate_on_submit():
        account = Account.query.filter_by(user_name=form.user_name.data).first()
        if account and bcrypt.check_password_hash(account.password_hash, form.password.data):
            login_user(account, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Incorrect Login information. Please try again')
    return render_template('login.html', title="Log in", form=form)


# Route for the logout page
@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Route for viewing the account information of the currently logged-in user
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html')


# Route for changing the account information of the currently logged-in user
@app.route("/account/modify", methods=['GET', 'POST'])
@login_required
def modify_account():
    form = UpdateAccountForm()
    # If user input data is valid then update their account information
    if form.validate_on_submit():
        current_user.user_name = form.user_name.data
        current_user.location = form.location.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    # Has the form start with the current account information filled in
    elif request.method == 'GET':
        form.user_name.data = current_user.user_name
        form.location.data = current_user.location
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    return render_template('modify_account.html', form=form)


# Route deleting the currently logged-in user account
@app.route("/account/delete", methods=['GET', 'POST'])
@login_required
def delete_account():
    user = Account.query.get_or_404(current_user.user_id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))


# Function for saving an image being added to a post
def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_name = random_hex + f_ext
    image_path = os.path.join(app.root_path, 'static/post_pics', image_name)
    form_image.save(image_path)
    return image_name


# Route for creating a post
@app.route("/post/create", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        image_file = save_image(form.image.data)
        post = Post(post_title=form.post_title.data, location=form.location.data, post_content=form.post_content.data,
                    image=image_file, fk_user_id=current_user.user_id)
        db.session.add(post)
        db.session.commit()
        flash(f'New post {form.post_title.data} created!', category='success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title="Create Post", form=form)


# Route for viewing all posts
@app.route("/posts", methods=['GET', 'POST'])
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.post_id.desc()).paginate(page=page, per_page=1)
    visits = LodgingVisit.query
    return render_template('posts.html', posts=posts, check=1, visits=visits)


# Route for viewing all posts for the logged-in user
@app.route("/your_posts/<int:user_id>", methods=['GET', 'POST'])
@login_required
def your_posts(user_id):
    if user_id != current_user.user_id:
        return redirect(url_for('home'))
    else:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(fk_user_id=user_id).paginate(page=page, per_page=1)
        visits = LodgingVisit.query
        likes = PostLike.query
    return render_template('your_posts.html', title="Your Posts", posts=posts, likes=likes, visits=visits, user_id=user_id)


@app.route("/your_posts/update/<int:post_id>", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    form = UpdatePostForm()
    post = Post.query.filter_by(post_id=post_id).first()
    # If current user does not own the post redirect them to home
    if post.fk_user_id != current_user.user_id:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        # If new image is uploaded save it and delete the old image
        if form.image.data:
            old_image_path = os.path.join(app.root_path, 'static/post_pics', post.image)
            image_file = save_image(form.image.data)
            post.image = image_file
            os.remove(old_image_path)
        post.post_title = form.post_title.data
        post.location = form.location.data
        post.post_content = form.post_content.data
        db.session.commit()
    elif request.method == 'GET':
        form.post_title.data = post.post_title
        form.location.data = post.location
        form.post_content.data = post.post_content
    return render_template('create_post.html', title="Update Post", form=form)


# Route for deleting a post
@app.route("/your_posts/<int:user_id>/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(user_id, post_id):
    if user_id == current_user.user_id:
        post = Post.query.get_or_404(post_id)
        image_path = os.path.join(app.root_path, 'static/post_pics', post.image)
        db.session.delete(post)
        db.session.commit()
        os.remove(image_path)
        flash('The Post has been deleted', category='success')
        return redirect(url_for('your_posts', user_id=current_user.user_id))
    else:
        return redirect(url_for('home'))


# Route for creating a comment
@app.route("/comment/<int:post_id>/create", methods=['GET', 'POST'])
@login_required
def create_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(comment_content=form.comment_content.data, fk_user_id=current_user.user_id, fk_post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash(f'Your comment was created!', category='success')
        return redirect(request.referrer or url_for('home'))
    return render_template('create_comment.html', title="Create Comment", form=form)


# Route for viewing a post's comments
@app.route("/post/<int:post_id>/comments", methods=['GET', 'POST'])
@login_required
def view_comments(post_id):
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(fk_post_id=post_id).paginate(page=page, per_page=10)
    return render_template('view_comments.html', title="Comments", comments=comments)


@app.route("/your_comments/update/<int:comment_id>", methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    # If current user does not own the comment redirect them to home
    if comment.fk_user_id != current_user.user_id:
        return redirect(url_for('home'))
    form = CommentForm()
    if form.validate_on_submit():
        comment.comment_content = form.comment_content.data
        db.session.commit()
        return redirect(url_for('your_comments'))
    elif request.method == 'GET':
        form.comment_content.data = comment.comment_content
    return render_template('create_comment.html', title="Update Post", form=form)


# Route for deleting a comment
@app.route("/your_comments/<int:user_id>/<int:comment_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_comment(user_id, comment_id):
    if user_id == current_user.user_id:
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash('The Comment has been deleted', category='success')
        return redirect(url_for('your_comments', user_id=current_user.user_id))
    else:
        return redirect(url_for('home'))


# Route for viewing all comments for the logged-in user
@app.route("/your_comments", methods=['GET', 'POST'])
@login_required
def your_comments():
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(fk_user_id=current_user.user_id).paginate(page=page, per_page=2)
    likes = CommentLike.query
    return render_template('your_comments.html', title="Your Comments", comments=comments, likes=likes)


# Route for viewing the current logged-in user's destination folders
@app.route("/destination_folders", methods=['GET', 'POST'])
@login_required
def destination_folders():
    folders = DestinationFolder.query.filter(DestinationFolder.fk_user_id == current_user.user_id)
    return render_template('destination_folders.html', folders=folders)


# Route for creating a new destination folder
@app.route("/destination_folders/create", methods=['GET', 'POST'])
@login_required
def create_destination_folder():
    form = FolderForm()
    if form.validate_on_submit():
        folder = DestinationFolder(fk_user_id=current_user.user_id, folder_name=form.folder_name.data)
        db.session.add(folder)
        db.session.commit()
        flash(f'Destination folder {form.folder_name.data} created!', category='success')
        return redirect(url_for('destination_folders'))
    return render_template('create_destination_folder.html', title="Create a Destination Folder", form=form)


# Route for updating a destination folder
@app.route("/destination_folders/update/<int:folder_id>", methods=['GET', 'POST'])
@login_required
def update_destination_folder(folder_id):
    form = FolderForm()
    folder = DestinationFolder.query.filter_by(folder_id=folder_id).first()
    if folder.fk_user_id != current_user.user_id:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        folder.folder_name = form.folder_name.data
        db.session.commit()
        flash(f'Destination folder {form.folder_name.data} has been updated!', category='success')
        return redirect(url_for('destination_folders'))
    elif request.method == 'GET':
        form.folder_name.data = folder.folder_name
    return render_template('create_destination_folder.html', title="Create a Destination Folder", form=form)


# Route for opening a destination folder
@app.route("/destination_folders/<int:folder_id>", methods=['GET', 'POST'])
@login_required
def destinations(folder_id):
    name = DestinationFolder.query.get_or_404(folder_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.join(SavedDestination).filter_by(fk_folder_id=folder_id).paginate(page=page, per_page=1)
    visits = LodgingVisit.query
    if name.fk_user_id != current_user.user_id:
        return redirect(url_for('home'))
    return render_template('view_destination_posts.html', name=name, posts=posts, folder_id=folder_id, visits=visits)


# Route for selecting a destination folder to save a post to
@app.route("/save_destination/select_folder/<int:post_id>", methods=['GET', 'POST'])
@login_required
def select_save_folder(post_id):
    folders = DestinationFolder.query.filter(DestinationFolder.fk_user_id == current_user.user_id)
    return render_template('select_folder.html', title="Saved Destination", folders=folders, post_id=post_id)


# Route for saving a post to the specified destination folder
@app.route("/save_destination/select_folder/<int:post_id>/<int:folder_id>", methods=['GET', 'POST'])
@login_required
def save_destination(post_id, folder_id):
    save = SavedDestination(fk_folder_id=folder_id, fk_post_id=post_id)
    db.session.add(save)
    db.session.commit()
    flash(f'Destination saved to your folder!', category='success')
    return redirect(url_for('destination_folders'))


# Route for adding a post to a destination folder
@app.route("/select_folder/<int:post_id>/<int:folder_id>", methods=['GET', 'POST'])
@login_required
def add_destination(post_id, folder_id):
    if SavedDestination.query.filter_by(fk_folder_id=folder_id).filter_by(fk_post_id=post_id).first():
        flash(f'The Destination Folder already contains that post', category='error')
    else:
        destination = SavedDestination(fk_folder_id=folder_id, fk_post_id=post_id)
        db.session.add(destination)
        db.session.commit()
        flash(f'Post added to the Destination Folder!', category='success')
        return redirect(url_for('destination_folders'))
    return redirect(request.referrer or url_for('home'))


# Route for viewing all tags
@app.route("/tags", methods=['GET', 'POST'])
def tags():
    page = request.args.get('page', 1, type=int)
    tags = Tag.query.paginate(page=page, per_page=10)
    return render_template('view_tags.html', title="Tags", tags=tags)


# Route for viewing all posts that contain the specified tag
@app.route("/tags/sort_by/<int:tag_id>", methods=['GET', 'POST'])
def sort_posts(tag_id):
    page = request.args.get('page', 1, type=int)
    posts = Post.query.join(PostTag).filter_by(fk_tag_id=tag_id).paginate(page=page, per_page=1)
    visits = LodgingVisit.query
    return render_template('view_tagged_posts.html', posts=posts, tag_id=tag_id, visits=visits)


# Route for creating a new tag
@app.route("/tags/create", methods=['GET', 'POST'])
@login_required
def create_tag():
    form = TagForm()
    if form.validate_on_submit():
        if Tag.query.filter_by(tag_name=form.tag_name.data).first():
            flash(f'There is already a Tag named {form.tag_name.data}. Please use a different name.', category='error')
        else:
            tag = Tag(tag_name=form.tag_name.data, description=form.description.data)
            db.session.add(tag)
            db.session.commit()
            flash(f'New Tag has been created!', category='success')
            return redirect(url_for('tags'))
    return render_template('create_tag.html', title="Create a New Tag", form=form)


# Route for selecting a tag to add to a post
@app.route("/post/<int:post_id>/select_tag", methods=['GET', 'POST'])
@login_required
def select_tag(post_id):
    page = request.args.get('page', 1, type=int)
    tags = Tag.query.paginate(page=page, per_page=10)
    return render_template('select_tag.html', title="Tags", tags=tags, post_id=post_id)


# Route for adding the specified tag to a post
@app.route("/post/<int:post_id>/<tag_id>", methods=['GET', 'POST'])
@login_required
def add_tag(post_id, tag_id):
    if PostTag.query.filter_by(fk_post_id=post_id).filter_by(fk_tag_id=tag_id).first():
        flash(f'The Post already has that tag added to it', category='error')
    else:
        post_tag = PostTag(fk_post_id=post_id, fk_tag_id=tag_id)
        db.session.add(post_tag)
        db.session.commit()
        flash(f'The Tag has been added to your Post!', category='success')
        return redirect(url_for('destination_folders'))
    return redirect(request.referrer or url_for('home'))


# Route for viewing all lodgings
@app.route("/lodgings", methods=['GET', 'POST'])
def lodgings():
    page = request.args.get('page', 1, type=int)
    lodgings = Lodging.query.order_by(Lodging.lodging_name).paginate(page=page, per_page=10)
    return render_template('lodgings.html', lodgings=lodgings)


# Route for viewing all visits for a lodging
@app.route("/lodging/<int:lodging_id>", methods=['GET', 'POST'])
def view_lodging(lodging_id):
    lodging = Lodging.query.get_or_404(lodging_id)
    page = request.args.get('page', 1, type=int)
    visits = LodgingVisit.query.filter(LodgingVisit.fk_lodging_id == lodging_id).order_by(LodgingVisit.lodging_visit_id.desc()).paginate(page=page, per_page=10)
    return render_template('view_lodging.html', title=lodging.name, lodging=lodging, visits=visits)


# Route for creating a lodging
@app.route("/lodgings/create", methods=['GET', 'POST'])
@login_required
def create_lodging():
    form = LodgingForm()
    if form.validate_on_submit():
        lodging = Lodging(lodging_name=form.lodging_name.data, location=form.location.data)
        db.session.add(lodging)
        db.session.commit()
        flash(f'New lodging has been created!', category='success')
        return redirect(url_for('lodgings'))
    return render_template('create_lodging.html', title="Create a lodging", form=form)


# Route for creating a to do list item
@app.route("/to_do/create", methods=['GET', 'POST'])
@login_required
def create_to_do():
    form = ListForm()
    if form.validate_on_submit():
        list = ToDoList(fk_user_id=current_user.user_id, to_do_name=form.to_do_name.data, description=form.description.data)
        db.session.add(list)
        db.session.commit()
        flash(f'To Do List Updated!', category='success')
        return redirect(url_for('to_do'))
    return render_template('create_to_do.html', form=form)


# Route for modifying a to do list item
@app.route("/to_do/modify/<int:list_id>", methods=['GET', 'POST'])
@login_required
def modify_to_do(list_id):
    list = ToDoList.query.filter_by(list_id=list_id).first()
    if list.fk_user_id != current_user.user_id:
        return redirect(url_for('home'))
    form = ListForm()
    if form.validate_on_submit():
        list.to_do_name = form.to_do_name.data
        list.description = form.description.data
        db.session.commit()
        flash('Your To Do List Has Been Updated!', 'success')
        return redirect(url_for('to_do'))
    elif request.method == 'GET':
        form.to_do_name.data = list.to_do_name
        form.description.data = list.description
    return render_template('create_to_do.html', form=form)


# Route for viewing the to do list
@app.route("/to_do", methods=['GET', 'POST'])
@login_required
def to_do():
    page = request.args.get('page', 1, type=int)
    to_dos = ToDoList.query.filter_by(fk_user_id=current_user.user_id).paginate(page=page, per_page=10)
    return render_template('view_to_do.html', to_dos=to_dos)


# Route for deleting a to do list item
@app.route("/to_do/<int:user_id>/delete/<int:list_id>", methods=['GET', 'POST'])
@login_required
def delete_to_do(user_id, list_id):
    if user_id == current_user.user_id:
        list = ToDoList.query.get_or_404(list_id)
        db.session.delete(list)
        db.session.commit()
        flash('The To Do List Item has been Completed!', category='success')
        return redirect(url_for('to_do', user_id=current_user.user_id))
    else:
        return redirect(url_for('home'))


# Route for liking a post
@app.route("/post/<int:post_id>/like", methods=['GET', 'POST'])
@login_required
def like_post(post_id):
    if PostLike.query.filter_by(fk_post_id=post_id).filter_by(fk_user_id=current_user.user_id).first():
        flash(f'You already liked this post', category='error')
    else:
        like_post = PostLike(fk_post_id=post_id, fk_user_id=current_user.user_id)
        db.session.add(like_post)
        db.session.commit()
        flash(f'You liked the post!', category='success')
    return redirect(request.referrer or url_for('home'))


# Route for liking a comment
@app.route("/post/<int:post_id>/like", methods=['GET', 'POST'])
@login_required
def like_comment(comment_id):
    if CommentLike.query.filter_by(fk_comment_id=comment_id).filter_by(fk_user_id=current_user.user_id).first():
        flash(f'You already liked this comment', category='error')
    else:
        like_comment = CommentLike(fk_comment_id=comment_id, fk_user_id=current_user.user_id)
        db.session.add(like_comment)
        db.session.commit()
        flash(f'You liked the comment!', category='success')
    return redirect(request.referrer or url_for('home'))


# Route for selecting a lodging for a visit
@app.route("/post/<int:post_id>/select_lodging", methods=['GET', 'POST'])
@login_required
def select_lodging(post_id):
    page = request.args.get('page', 1, type=int)
    lodgings = Lodging.query.paginate(page=page, per_page=10)
    return render_template('select_lodging.html', title="Lodging", lodgings=lodgings, post_id=post_id)


# Route for adding a lodging visit
@app.route("/post/<int:post_id>/add/lodging/<int:lodging_id>", methods=['GET', 'POST'])
@login_required
def add_lodging(post_id, lodging_id):
    form = LodgingVisitForm()
    if LodgingVisit.query.filter_by(fk_post_id=post_id).first():
        flash(f'The Post already has a lodging visit', category='error')
    else:
        if form.validate_on_submit():
            visit = LodgingVisit(fk_post_id=post_id, fk_lodging_id=lodging_id, cost=form.cost.data, rating=form.rating.data, comment=form.comment.data)
            db.session.add(visit)
            db.session.commit()
            flash(f'The Lodging visit has been added to your Post!', category='success')
            return redirect(request.referrer or url_for('home'))
    return render_template('create_visit.html', form=form)


# Route for viewing a lodging visit
@app.route("/<int:post_id>/visit", methods=['GET', 'POST'])
@login_required
def view_visit(post_id):
    visit = LodgingVisit.query.filter_by(fk_post_id=post_id).first()
    lodging = Lodging.query.filter_by(lodging_id=visit.fk_lodging_id).first()
    return render_template('view_visit.html', visit=visit, lodging=lodging)


# Route for viewing all visits for a lodging
@app.route("/lodging/<int:lodging_id>/visits", methods=['GET', 'POST'])
def view_visits(lodging_id):
    page = request.args.get('page', 1, type=int)
    visits = LodgingVisit.query.filter_by(fk_lodging_id=lodging_id).paginate(page=page, per_page=5)
    return render_template('view_visits.html', visits=visits, lodging_id=lodging_id)
