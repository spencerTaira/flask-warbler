"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, connect_db

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app
app.config['WTF_CSRF_ENABLED'] = False
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

connect_db(app)

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    #1
    def test_user_model_repr(self):
        u1 = User.query.get(self.u1_id)
        u1_repr = repr(u1)
        test_repr = f'<User #{u1.id}: {u1.username}, {u1.email}>'

        self.assertEqual(test_repr, u1_repr)

    #2
    def test_user_model_is_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u1.following.append(u2)

        is_following = u1.is_following(u2)
        self.assertEqual(is_following, True)

    #3
    def test_user_model_is_not_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        is_following = u1.is_following(u2)
        self.assertEqual(is_following, False)

    #4
    def test_user_model_is_followed(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u1.followers.append(u2)

        is_followed = u1.is_followed_by(u2)
        self.assertEqual(is_followed, True)

    #5
    def test_user_model_is_not_followed(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        is_followed = u1.is_followed_by(u2)
        self.assertEqual(is_followed, False)

    #6
    def test_user_signup(self):

        with self.client as c:
            data = {
                'username': 'test_user',
                'password': 'password',
                'email': 'user@gmail.com'
            }

            resp = c.post(
                '/signup',
                data=data,
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Homepage', html)
            self.assertIn('test_user', html)

    #7
    def test_user_signup_fail(self):

        with self.client as c:
            data = {
                'username': 'u1',
                'password': 'password',
                'email': 'user@gmail.com'
            }

            resp = c.post(
                '/signup',
                data=data,
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username already taken", html)