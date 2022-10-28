"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, connect_db, MessagesLiked

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

class MessageModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()
        u1 = User.signup("u1", "u1@email.com", "password", None)
        
        db.session.commit()

        m1 = Message(text="test1",user_id=u1.id)
        m2 = Message(text="test2", user_id=u1.id)

        db.session.add_all([m1,m2])
        db.session.commit()
        self.m1_id = m1.id
        self.m2_id = m2.id
        self.u1_id = u1.id

        m1_liked = MessagesLiked(message_id=self.m1_id, user_id=self.u1_id)
        db.session.add(m1_liked)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """ Clean up fouled transactions """

        db.session.rollback()

    def test_message_model(self):

        message1 = Message.query.get(self.m1_id)
        message2 = Message.query.get(self.m2_id)
        user = User.query.get(self.u1_id)
        m1 = message1.is_liked_by(user)
        m2 = message2.is_liked_by(user)

        self.assertTrue(m1)
        self.assertFalse(m2)
        

        # with self.client as c:
        #     data = {
        #         "text" : "testing message",
        #         "user_id" : self.u1_id
        #     }

        #     resp = c.post(
        #         '/messages/new',
        #         data=data,
        #         follow_redirects=True
        #     )

        #     html = resp.get_data(as_text=True)
        #     user = User.query.get(self.u1_id)

        #     self.assertEqual(resp.status_code, 200)
        #     self.assertRedirects(resp, f"/users/{user.id}")
        #     self.assertIn(user.username, html)





