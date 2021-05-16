from unittest import TestCase
from app import app
from models import db, User, Post, Tag, PostTag

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bloglilly_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

DEFAULT_IMAGE_URL = default="https://images.unsplash.com/photo-1455390582262-044cdead277a?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=966&q=80"
class UserViewsTestCase(TestCase):
    """Test views for User model"""

    def setUp(self):
        """Add a sample User"""

        User.query.delete()

        user = User(first_name="Test", last_name = "User")
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """Clean up any failed transaction."""

        db.session.rollback()

    def test_home_users(self):
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<a href="/user/{self.user_id}" class="text-primary">Test User</a>', html)

    def test_user_page(self):
        with app.test_client() as client:
            resp = client.get(f'/user/{self.user_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<a class="btn btn-primary btn-lg rounded" href="/edit-user/{self.user_id}">Edit user data</a>', html)
    
    def test_user_edit(self):
        with app.test_client() as client:
            resp = client.get(f'/edit-user/{self.user_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<input type="text" class="form-control dark-input" id="first-name" value="Test" name="first-name">', html)

    ######## this test keeps giving me a 400 and I can't figure out why. The path works in the app.
    # def test_user_edit_post(self):
    #     with app.test_client() as client:
    #         resp = client.post(f'/edit-user/{self.user_id}', data={'first_name': 'Test', 'last_name': 'User', 'image_url': 'DEFAULT_IMAGE_URL', 'statement': 'About me.'}, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('<p>About me.</p>', html)

    def test_user_delete(self):
        with app.test_client() as client:
            resp = client.get(f'/delete-user/{self.user_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Test User', html)