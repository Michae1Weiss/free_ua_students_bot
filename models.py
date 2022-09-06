from peewee import *

database_proxy = DatabaseProxy()


LANGUAGE_CHOICES = (
    (0, 'English'),
    (1, 'Ukrainian'),
    (2, 'German')
)

LANGUAGES = {
    'English': 0,
    'Ukrainian': 1,
    'German': 2
}


class BaseModel(Model):

    class Meta:
        database = database_proxy


class User(BaseModel):
    user_id = IntegerField(unique=True)
    is_superuser = BooleanField(default=False)


class Tweet(BaseModel):
    tweet_id = CharField(unique=True)
    description = CharField()
    language = IntegerField(choices=LANGUAGE_CHOICES)


class Facebook(BaseModel):
    ...


class Comment(BaseModel):
    user = ForeignKeyField(User, backref='users')
    text = TextField()
    language = IntegerField(choices=LANGUAGE_CHOICES, null=True)


class CommentedTweet(BaseModel):
    user = ForeignKeyField(User, backref='users')
    tweet = ForeignKeyField(Tweet, backref='tweets')
    comment = ForeignKeyField(Comment, backref='comments', null=True)

    in_work = BooleanField(default=True)


MODELS = [User, Tweet, Comment, CommentedTweet]
