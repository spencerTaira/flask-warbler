"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User, connect_db, Follows, MessagesLiked

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

connect_db(app)

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.add(u1)

        # m1 = Message(text="m1-text", user_id=u1.id)
        # db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        # self.m1_id = m1.id

        self.client = app.test_client()

    def tearDown(self):
        """ Clean up fouled transactions """

        db.session.rollback()

class UserAddViewTestCase(UserBaseViewTestCase):
    def test_user_signup(self):


        with self.client as c:

            #test get request
            resp = c.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Signup', html)

            #test valid post request
            data = {
                'username': 'test_user',
                'password': 'password',
                'email': 'test_user@gmail.com'
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

            #test invalid post request
            # data = {
            #     'username': 'u1', #same username
            #     'password': 'password',
            #     'email': 'test_user1@gmail.com'
            # }
            # resp = c.post(
            #     '/signup',
            #     data=data,
            #     follow_redirects=True
            #     )
            # html = resp.get_data(as_text=True)
            # breakpoint()
            # self.assertEqual(resp.status_code, 200)
            # self.assertIn('Signup', html)
            # self.assertIn('Username already taken', html)

    def test_user_login(self):

        with self.client as c:
            #test get request
            resp = c.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Login', html)

            #test valid post request
            data = {
                'username': 'u1',
                'password': 'password'
            }
            resp = c.post(
                '/login',
                data=data,
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'Hello, {user.username}!', html)
            self.assertIn('Homepage', html)

            #test invalid post request
            data = {
                'username': 'u0',
                'password': 'password'
            }
            resp = c.post(
                '/login',
                data=data,
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid credentials.', html)
            self.assertIn('Login', html)


    def test_user_logout(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Home Signup', html)
            # self.assertEqual(sess.get(CURR_USER_KEY), False)
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        # with self.client as c:
        #     with c.session_transaction() as sess:
        #         sess[CURR_USER_KEY] = self.u1_id

        #     # Now, that session setting is saved, so we can have
        #     # the rest of ours test
        #     resp = c.post("/messages/new", data={"text": "Hello"})

        #     self.assertEqual(resp.status_code, 302)

        #     Message.query.filter_by(text="Hello").one()
