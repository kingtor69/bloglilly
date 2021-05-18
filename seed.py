from models import db, User, Post, Tag, PostTag
from app import app
from helpers import generate_preview
from datetime import datetime

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create all tables
db.drop_all()
db.create_all()

# If tables aren't empty, empty it
User.query.delete()
Post.query.delete()

# Add users
seed_users = [
    User(first_name="Bobby", last_name="Bob", image_url="https://images.unsplash.com/photo-1614072076713-9573d6a55376?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1051&q=80"), 
    User(first_name="Thom", last_name="Yorke", image_url="https://images.unsplash.com/photo-1602531952812-f552155bcd07?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1048&q=80"), 
    User(first_name="Bosephus", image_url="https://images.unsplash.com/photo-1520167112707-56e25f2d7d6e?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1234&q=80", statement="My neck is red AF."), 
    User(first_name="Oscar", last_name="Wilde"),
    User(first_name="Vivaldi", image_url="https://images.unsplash.com/photo-1522598313109-86ffbe01de13?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=334&q=80", statement="I like food. I mean, I really like food. I'm always thinking about food. Like when am I going to eat again? Are they going to feed me? Are they going to feed me? And I run around in circles sometimes. And whine. I love whining and running around in circles. Like whine, run in a circle, whine, run in a circle, whine, run in a circle. Man, I could do that all day. If they didn't feed me, that is. When they feed me I stop going that. Until I'm done eating in about 13 seconds. And you might think I stop thinking about food when I'm sleeping, but I don't. I dream about eating all night long. Well, that and whining. And running in circles.")
    ]

seed_posts = [
    Post(title="first title", content="first content", user_id="2", created_on="2021-04-25 23:21:29.23451"), 
    Post(title="showoff", content="really, Thom, who cares?", user_id="3", created_on="2121-04-26 17:32:11.928492"), 
    Post(content="Shut up, ya' redneck.", user_id="2", created_on="2021-04-26 21:23:19.385712"), 
    Post(title="Guys...?", content="What in the love of Pete is a 'blog-lilly?'", user_id="1"), 
    Post(title="literary geniuses", content="I'm so fortunate to be here with so many literary geniuses. The conversation is scinilating. Now if you'll excuse me, I'm going to go get more heroin.", user_id="4"), 
    Post(title="bro country", content="hey, bro, pass me a bud, would ya?", user_id = "3"), 
    Post(title="speechless", content="Right? I thought there was some literary value in this site. I've only been here for a few minutes, and I'm bored.", user_id="2"), 
    Post(title="Anyone else hungry?", content="I'm really hungry guys. I might start whining and running in circles.", user_id="5"), 
    Post(title="Seriously", content="Are you guys listening? Have you not noticing my whining and my running around in circles? Whine, run, stop, whine, run, stop, whine, run, stop...", user_id="5")]

seed_tags = [
    Tag(tag="food"), 
    Tag(tag="rednecks"), 
    Tag(tag="bored"),
    Tag(tag="litrachur")
    ]

seed_posts_tags = [
    PostTag(post_id=2, tag_id=3),
    PostTag(post_id=3, tag_id=2),
    PostTag(post_id=8, tag_id=1),
    PostTag(post_id=9, tag_id=1),
    PostTag(post_id=5, tag_id=4),
    PostTag(post_id=6, tag_id=2),
    PostTag(post_id=6, tag_id=3),
    PostTag(post_id=6, tag_id=1)
    ]

# get preview statements to put in database:
for user in seed_users:
    if user.statement:
        user.statement_short = generate_preview(user.statement, 42)
        user.statement_medium = generate_preview(user.statement, 144)
    # user.full_name = user.full_name()

# Add seed users to session and commit to database
db.session.add_all(seed_users)
db.session.commit()

for post in seed_posts:
    post.content_short = generate_preview(post.content, 42)
    post.content_medium = generate_preview(post.content, 222)
    post.created_on = datetime.utcnow()
    post.pretified_creation_datetime = post.pretify_creation_datetime()
    
# posts are dependent on users
db.session.add_all(seed_posts)
db.session.commit()

db.session.add_all(seed_tags)
db.session.commit()

# posts_tags are dependent on posts and tags
db.session.add_all(seed_posts_tags)
db.session.commit()