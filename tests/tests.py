from unittest import TestCase

from models import MODELS, Tweet, Comment
from tests.utils import db, create_user


class DBTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        db.create_tables(MODELS)


    def tearDown(self):
        db.drop_tables(MODELS)


class TweetModelTestCase(DBTestCase):
    def test_create_tweet(self):
        data = {
            "tweet_id": "1565686132842569730",
            "language": 0
        }
        tweet = Tweet.create(**data)
        self.assertEqual(Tweet.select().count(), 1, msg="There must be 1 tweet created.")

        for key in data.keys():
            self.assertTrue(hasattr(tweet, key), msg=f"Tweet {tweet.id} has no attribute <{key}>")


class CommentModelTestCase(DBTestCase):
    def setUp(self) -> None:
        self.user = create_user(user_id="102030")

    def test_create_comment(self):
        data = {
            "user": self.user,
            "text": "Reply"
        }
        comment = Comment.create(**data)
        self.assertEqual(Comment.select().count(), 1, msg="There must be 1 comment created.")

        for key in data.keys():
            self.assertTrue(hasattr(comment, key), msg=f"Comment {comment.id} has no attribute <{key}>")
