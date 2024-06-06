import factory
from factory.alchemy import SQLAlchemyModelFactory
from src.models import Users, Tweets, Media, Followers, Likes
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import session




class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Users
        sqlalchemy_session = session

    name = factory.Sequence(lambda n: f'User {n}')
    api_key = factory.Faker('uuid4')


class TweetFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Tweets
        sqlalchemy_session = session

    content = factory.Faker('text', max_nb_chars=50)
    author = factory.SubFactory(UserFactory)


class MediaFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Media
        sqlalchemy_session = session

    extension = '.jpg'



class FollowersFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Followers
        sqlalchemy_session = session

    user_id = factory.SubFactory(UserFactory)
    follower_id = factory.SubFactory(UserFactory)


class LikesFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Likes
        sqlalchemy_session = session

    user_id = factory.SubFactory(UserFactory)
    tweet_id = factory.SubFactory(TweetFactory)
