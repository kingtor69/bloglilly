"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag
from datetime import datetime
from helpers import generate_preview

app = Flask(__name__)

app.config['SECRET_KEY'] = "bigfuckinsecret230las@1!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bloglilly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route('/')
def display_homepage():
    """load homepage, which may at some point show a list of recent posts"""

    users_top5 = User.query.order_by(User.id.desc()).limit(5).all()
    posts_top5 = Post.query.order_by(Post.created_on.desc()).limit(5).all()
    top5posts_tags = []

    for post in posts_top5:
        author = User.query.get(post.user_id)
        top5posts_tags.append({post: (PostTag.list_tags_for_one_post(post), author)})

    return render_template('home.html', users=users_top5, posts_with_tags=top5posts_tags)

##################################### User paths
@app.route('/users')
def display_user_list():
    """display a list of all users"""
    users = User.query.all()
    # this is a many to many idea for future improvement with a UserPost model
    # most_recent_posts = Post.query.order_by(Post.created_on).desc().all()
    return render_template('users.html', users=users)
# future TODO: make this users/0 which shows 20 users -- then users/1 is offset by 20, &c.

@app.route('/user/<int:user_id>')
def display_user_profile(user_id):
    """display a specific user's profile and a list of their posts"""
    user = User.query.get_or_404(user_id)
    
    all_user_posts = Post.query.filter_by(user_id = user_id).order_by(Post.created_on.desc())
    num_posts = len(list(all_user_posts))
    if num_posts < 6:
        everything_here = True
        top5_user_posts = all_user_posts 
    else:
        everything_here = False
        top5_user_posts = []
        for i in range(5):
            top5_user_posts.append(all_user_posts[i])
    posts_with_tags=[]
    for post in top5_user_posts:    
        posts_with_tags.append({post: PostTag.list_tags_for_one_post(post)})
    return render_template('user.html', user=user, posts_with_tags=posts_with_tags, everything_here = everything_here)

@app.route('/user')
def redirect_null_user_home():
    """redirect a null user entry back home"""
    return redirect('/')

@app.route('/new-user')
def load_new_user_form():
    """load the edit-or-new-user form without sending a user"""
    return render_template('new-user.html')

@app.route('/edit-user/<int:user_id>')
def load_edit_user_form(user_id):
    """load the edit-or-new-user form sending an user to edit"""
    user = User.query.get_or_404(user_id)
    return render_template('edit-user.html', user=user)

@app.route('/new-user', methods=['POST'])
def generate_new_user():
    """make a new database entry for new user"""
    image_url = request.form["image-url"] if (not request.form["image-url"] == "") else None
    statement = request.form["statement"]
    statement_medium = generate_preview(statement, 144)
    statement_short = generate_preview(statement, 30)
    new_user = User(first_name=request.form["first-name"], last_name=request.form["last-name"], image_url=image_url,
    statement=statement, statement_medium=statement_medium, statement_short=statement_short)
    # new_user.full_name = new_user.full_name()

    db.session.add(new_user)
    db.session.commit()

    return redirect(f'user/{new_user.id}')

@app.route('/edit-user/<int:user_id>', methods=['POST'])
def edited_user_to_database(user_id):
    """update the database with the post data from the user edit form"""
    user = User.query.get_or_404(user_id)
    image_url = request.form["image-url"] if (not request.form["image-url"] == "") else None
    statement = request.form["statement"]
    statement_medium = generate_preview(statement, 144)
    statement_short = generate_preview(statement, 30)
    user.first_name = request.form["first-name"]
    user.last_name = request.form["last-name"]
    user.image_url = request.form["image-url"]
    user.statement = statement
    user.statement_medium = statement_medium
    user.statement_short = statement_short

    db.session.add(user)
    db.session.commit()

    return redirect(f'../user/{user.id}')

# TODO: delete is violating a constraint on table posts or some shit like that
@app.route('/delete-user/<int:user_id>')
def delete_this_user(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect('/users')

######## User's new post transitions into....
@app.route('/user/<int:user_id>/new-post')
def new_post_form(user_id):
    """ load form for a new post from this user_id """
    tags = Tag.query.all()
    user = User.query.get(user_id)
    return render_template('new-post.html', user=user, tags=tags)

############################### ...Post paths
@app.route('/post/new', methods=['POST'])
def display_new_post():
    """generate database entry for and display on screen the new post"""
    title = request.form['title']
    content = request.form['content']
    user_id = request.form['user_id']
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    post = Post(title=title, content=content, content_medium=generate_preview(content, 222), content_short = generate_preview(content, 42), user_id=user_id, created_on = datetime.utcnow())
    post.pretified_creation_datetime = post.pretify_creation_datetime()

    db.session.add(post)
    db.session.commit()

    posts_tags = []
    for tag in tags:
        posts_tags.append(PostTag(post_id=post.id, tag_id=tag.id))
    
    db.session.add_all(posts_tags)
    db.session.commit()

    user = User.query.get(user_id)
    # db.session.add(post)
    # db.session.commit()
    
    return render_template('post.html', post=post, user=user, tags=tags)

@app.route('/edit-post/<int:post_id>')
def edit_a_post(post_id):
    post = Post.query.get(post_id)
    user = User.query.get(post.user_id)
    tags = Tag.query.all()
    # reset any old values for Tag.this_post_has
    for tag in tags:
        tag.this_post_has = False
    post_tags = PostTag.get_tags_for_post(post)
    for post_tag in post_tags: 
        post_tag.this_post_has = True
    db.session.add_all(tags)
    db.session.commit()
    return render_template('edit-post.html', post=post, tags=tags, user=user)

# TODO tags aren't getting in the database
@app.route('/post/<int:post_id>/edited', methods=['POST'])
def process_edited_post_and_display(post_id):
    """process an edited post, place the edits in the database entry, and display that post via post.html"""

    # gather the form data
    edited_title = request.form['title']
    edited_content = request.form['content']
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    # future development TODO: add an updated_datetime and an 'edited' flag...?
    # get the old post up in this joint
    edited_post = Post.query.get(post_id)
    user = User.query.get(edited_post.user_id)

    # now update the edited values:
    edited_post.title = edited_title
    edited_post.content = edited_content
    # tags is an empty list no matter what was checked on edit page

    db.session.add(edited_post)
    db.session.commit()

    # TODO: tags are showing up on page, but not sticking in database
    post_tags = PostTag.query.filter(PostTag.post_id == post_id)
    add_post_tags = []
    for post_tag in post_tags:
        for tag in tags:
            if not post_tag == tag.id:
                add_post_tags.append(PostTag(post_id = post_id, tag_id = tag.id))

    db.session.add_all(add_post_tags)
    # re TODO: I tried the below and it made 0 difference
    # db.session.add_all(tags)
    db.session.commit()

    # reset Tag.this_post_has to default on all tags:
    tags = Tag.query.all()
    for tag in tags:
        tag.this_post_has = False

    db.session.add_all(tags)
    db.session.commit()
    # re_got_tag_ids = PostTag.query.filter(PostTag.post_id == post_id).all()
    # re_got_tags = []
    # for tag_id in re_got_tag_ids:
    #     re_got_tags.append(Tag.query.get(id))

    return render_template('post.html', post=edited_post, tags=tags, user=user)

@app.route('/post/<int:post_id>')
def display_post_by_id(post_id):
    """ display a post by it's primary key id """
    post = Post.query.get_or_404(post_id)
    tags = PostTag.get_tags_for_post(post)
    user = User.query.get(post.user_id)
    
    return render_template('post.html', post=post, tags=tags, user=user)
    
# future development TODO: a page option for the /posts route 
    # I think I can see how:
        # /posts/0 is first 20, posts/1 is offset by 20, &c
@app.route('/posts')
def display_all_posts():
    """display all posts with title, content_medium, link to /post/post_id, tags (as links to all posts of that tag)"""
    posts = Post.query.order_by(Post.created_on.desc()).all()
    posts_keying_tags = []

    for post in posts:
        author = User.query.get(post.user_id)
        posts_keying_tags.append({post: (PostTag.list_tags_for_one_post(post), author)})

    return render_template('posts.html', posts_keying_tags=posts_keying_tags)

# TODO: this throws and error, I think that delete thing got lost moving to/from studio...?
@app.route('/delete-post/<int:post_id>')
def delete_specified_post(post_id):
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()
    return redirect('/posts')

########### and Post gets sorted by Tag, transitioning into...
@app.route('/posts-by-tag/<int:sort_by_tag_id>')
def display_tagged_posts(sort_by_tag_id):
    """ display the tag name at the head of the page and a table of posts using that tag """
    # retried posts_tags rows that have this tag_id
    pts = PostTag.query.filter(PostTag.tag_id == sort_by_tag_id)
    # make and empty list
    tagged_posts = []
    got_one = False
    preview = False
    # loop through post_ids in that selected rows
    for pt in pts:
        # add post from that entry to the list
        matched_posts = Post.query.filter(Post.id == pt.post_id).all()
        for post in matched_posts:
            post.length = len(post.content)
            tagged_posts.append(post)
            if post.length > 219:
                preview = True
            got_one = True
    
    return render_template('tag.html', tag=Tag.query.get(sort_by_tag_id), posts=tagged_posts, got_one=got_one, preview=preview)

##################################### ... Tag routes
@app.route('/tags')
def show_tags_table():
    """show tags list with options to edit or add tags"""
    tags = Tag.query.all()

    return render_template('tags.html', tags=tags)

@app.route('/new-tag')
def add_new_tag():
    """enter a new tag"""
    return render_template('new-tag.html')

@app.route('/new-tag', methods=['POST'])
def process_new_tag_form():
    """receive info from new-tag form and enter in database"""
    new_tag = request.args['tag']
    matching_tag = Tag.query.filter_by(tag=new_tag).first()
    if matching_tag:
        return render_template('new-tag.html', error=True)
    else:
        new_tag = Tag(tag=request.args['tag'])
        db.session.add(new_tag)
        db.session.commit()
        return redirect('/tags')

@app.route('/tag-edit/<int:tag_id>')
def edit_tag(tag_id):
    """open page to edit a tag, identified by Tag.id"""
    return render_template('edit-tag.html', edit_tag=Tag.query.get(tag_id), new_tag=False)

@app.route('/tag-edit/<int:tag_id>', methods=['POST'])
def process_edit_tag_form(tag_id):
    """receive edited tag name, check if it's unique and proceed accordingly"""
    # make sure edited tag doesn't duplicate another tag
    unedited_tags = Tag.query.all()
    tag_to_edit = Tag.query.get(tag_id)
    for tag in unedited_tags:
        if tag_to_edit.tag == tag.tag:
            flash (f'The tag {{ tag.tag }} already exists. <br> Please try another.', 'warning')
            flash ('or return to tag list', 'info')
            return render_template('edit-tag.html')
    
    tag_to_edit.tag = request.args['tag']
    db.session.add(tag_to_edit)
    db.session.commit()
    # go back to list of tags
    return redirect("/tags")

@app.route('/tag/<int:tag_id>', methods=["POST"])
def process_new_tag(tag_id):
    """displays a page showing info about a new or edited tag, with a button to redirect to '/tags'"""
    # make sure it's unique
    # get all tags and save form response to variable
    tags = Tag.query.all()
    proby_tag = request.args['tag']
    # check if the tag already exists
    for tag in tags:
        if proby_tag == tag.tag:
            flash (f'The tag {{ tag.tag }} already exists. <br> Please try another.', 'warning')
            flash ('or return to tag list', 'info')
            return render_template('new-tag.html')

    # all good, so make the model and save it to the database
    new_tag = Tag(tag=proby_tag)
    db.session.add(new_tag) 
    db.session.commit()
    return redirect(f'/posts-by-tag/{new_tag.id}')

@app.route('/edit-tag/<int:tag_id>')
def edit_a_tag(tag_id):
    tag_to_edit = Tag.query.get(tag_id)
    return render_template('edit-tag.html', tag=tag_to_edit)

@app.route('/tag/<tag_name>')
def redirect_to_tag_by_id(tag_name):
    """find out the id of the tag and redirect to the tag/<int:tag_id>"""
    tagged_tag = Tag.query.filter_by(tag=tag_name).first()
    return redirect(f'/posts-by-tag/{tagged_tag.id}')
    
# error handling
@app.errorhandler(404)
def page_not_found(e):
    """redirect to home page with a flashed error message."""
    flash('That page was not found. Please try again.', 'danger')

    return redirect('/')

# TODO: improve taggibility to edited posts
    # currently they lose all tags when the edit page opens
    # need logic both here and in template to pre-check pre-existing tags on a past

# fixed? untested
# TODO: what happens to posts when user is deleted