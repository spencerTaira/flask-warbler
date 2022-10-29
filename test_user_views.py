"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from flask import session, url_for
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
        MessagesLiked.query.delete()
        Message.query.delete()
        User.query.delete()
        

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u3 = User.signup("u3", "u3@email.com", "password", None)
        db.session.add_all([u1, u2, u3])

        u1.following.append(u2)
        u3.following.append(u1)
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        
        # Create link for user and liked message
        u1.liked_messages.append(m1)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id
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

    def test_user_signup_invalid(self):

        with self.client as c:
            # test invalid post request
            data = {
                'username': 'u1', #same username
                'password': 'password',
                'email': 'test_user1@gmail.com'
            }

            resp = c.post(
                '/signup',
                data=data,
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Signup', html)
            self.assertIn('Username already taken', html)

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

            #test invalid post request #TODO: break to another test
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

            # assert session.get(CURR_USER_KEY) == None NOTE: another test

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Home Signup', html)
            self.assertEqual(session.get(CURR_USER_KEY), None)


    def test_show_users_list(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Users Index", html)

    def test_show_users_list_invalid(self):

        with self.client as c:

            resp = c.get('/users', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_user_profile(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f'/users/{self.u1_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Users Show", html) #TODO: test that you are seeing user information

    def test_user_profile_invalid(self):

        with self.client as c:
            # profile_url = url_for('show_user', user_id=self.u1_id)

            # resp = c.get(profile_url, follow_redirects=True)
            resp = c.get(f'/users/{self.u1_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Home Signup", html)
            self.assertIn("Access unauthorized.", html)

    def test_user_following(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

        resp = c.get(f'users/{self.u1_id}/following')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("CODE FOR TESTING: Following", html)
        self.assertIn('u2', html) #TODO: assertNotIn someone you are not following

    def test_user_following_invalid(self):

        with self.client as c:
            resp = c.get(f'users/{self.u1_id}/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Home Signup", html)
            self.assertIn("Access unauthorized.", html)

    def test_user_followers(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f'users/{self.u1_id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("CODE FOR TESTING: Followers", html)
            self.assertIn('u3', html) #TODO: assertNotIn someone you are not following

    def test_user_followers_invalid(self):

        with self.client as c:
            resp = c.get(f'users/{self.u1_id}/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Home Signup", html)
            self.assertIn("Access unauthorized.", html)

    def test_user_start_following(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'users/follow/{self.u3_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id) #NOTE: dont neccessarily need
            following = user.following
            following_u3 = any(f for f in following if f.id == self.u3_id)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("CODE FOR TESTING: Following", html)
            self.assertIn('u3', html)
            self.assertTrue(following_u3)

    def test_user_start_following_invalid(self):

        with self.client as c:
            resp = c.post(f'users/follow/{self.u3_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Home Signup", html)
            self.assertIn("Access unauthorized.", html)

    def test_user_stop_following(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f'users/stop-following/{self.u2_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id)
            following = user.following
            following_u2 = any(f for f in following if f.id == self.u2_id)
#TODO: assert user is not in the page
            self.assertEqual(resp.status_code, 200)
            self.assertIn("CODE FOR TESTING: Following", html)
            self.assertEqual(following_u2, False)

    def test_user_stop_following_invalid(self):

        with self.client as c:
            resp = c.post(f'users/stop-following/{self.u2_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Home Signup", html)
            self.assertIn("Access unauthorized.", html)

    def test_user_edit_profile_get(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get('/users/profile')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('CODE FOR TEST: User Profile Edit', html)

    def test_user_edit_profile_post(self):

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1_id

                data = {
                    'username': 'u0',
                    'email': 'u1@gmail.com',
                    'password': 'password'
                }
                resp = c.post(
                    '/users/profile',
                    data=data,
                    follow_redirects=True)
                html = resp.get_data(as_text=True)

                user = User.query.get(self.u1_id)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('Users Show', html)
                self.assertIn('u0', html)
                self.assertEqual('u0', user.username)

    def test_user_edit_profile_post_invalid_data(self):

            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1_id

                data = {
                    'username': 'u0',
                    'email': 'u1@gmail.com',
                    'password': 'pass'
                }
                resp = c.post(
                    '/users/profile',
                    data=data,
                    follow_redirects=True)
                html = resp.get_data(as_text=True)

                user = User.query.get(self.u1_id)

                self.assertEqual(resp.status_code, 200)
                self.assertIn('Invalid credentials.', html)
                self.assertIn('u0', html)

    def test_user_edit_profile_invalid(self):

        with self.client as c:

            resp = c.get('/users/profile', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Home Signup", html)
            self.assertIn("Access unauthorized.", html)

    def test_user_liked_messages(self):

        with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1_id

                resp=c.get(f'/users/{self.u1_id}/likedmessages', follow_redirects=True)
                html = resp.get_data(as_text=True)   

                self.assertEqual(resp.status_code, 200)
                self.assertIn('User Liked Messages', html)
                self.assertIn('m1-text', html)

    def test_user_deleted(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id


            resp = c.post('/users/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            user = User.query.get(self.u1_id)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Signup', html)
            self.assertEqual(user, None)


