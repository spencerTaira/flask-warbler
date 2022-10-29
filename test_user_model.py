"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, connect_db
from sqlalchemy.exc import IntegrityError

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
        """ Clean up fouled transactions """

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

    #2 #TODO: add db.session.commit() after 73. Is u2 follow u1
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

    #4 #TODO: Commit changes after 90
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

    #6 #TODO: adding, 
    def test_user_signup(self):

        with self.client as c:

            u3 = User.signup("test_user", "user@gmail.com", "password", None)

            self.assertIsInstance(u3, User)
            self.assertTrue(u3.password.startswith('$2b$')) #NOTE: testing password was hashed


    #7
    def test_user_signup_fail(self):

        # If username already exists
        with self.assertRaises(IntegrityError):
            u3 = User.signup("u1", "user@gmail.com", "password", None)
            db.session.add(u3)
            db.session.commit()
            

        # If email already exists
        with self.assertRaises(IntegrityError):
            db.session.rollback()
            u4 = User.signup("u3", "u1@email.com", "password", None)
            db.session.add(u4)
            db.session.commit()
        

    #8 #TODO: query database for exact User instance. Check match of two
    def test_user_model_authenticate(self):

        with self.client as c: 

            u1 = User.authenticate("u1", "password")

            self.assertIsInstance(u1, User)

    #9 & #10 
    def test_user_model_authenticate_fail(self):

        with self.client as c:

            # This is checking for when username is invalid #clear comments/two separate tests
            u1 = User.authenticate("u1", "pas")
            self.assertFalse(u1)

            u2 = User.authenticate("user", "password")
            self.assertFalse(u2)

            # This is checking for when password is invalid
            # data = {
            #     'username' : 'u1',
            #     'password': 'invalid_password'
            # }

            # resp = c.post(
            #     '/login',
            #     data=data,
            #     follow_redirects=True
            # )

            # html = resp.get_data(as_text=True)
            # self.assertEqual(resp.status_code, 200)
            # self.assertIn('Login', html)
            # self.assertIn('Invalid credentials', html)


