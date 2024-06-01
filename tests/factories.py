import factory
from factory.alchemy import SQLAlchemyModelFactory
from src.models import Users, Tweets, Media, Followers, Likes
from sqlalchemy.ext.asyncio import AsyncSession


class AsyncSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        async with cls._meta.sqlalchemy_session() as session:
            obj = model_class(*args, **kwargs)
            session.add(obj)
            await session.commit()
            return obj


class UserFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Users
        sqlalchemy_session = AsyncSession

    name = factory.Sequence(lambda n: f'User {n}')
    api_key = factory.Faker('uuid4')


class TweetFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Tweets
        sqlalchemy_session = AsyncSession

    content = factory.Faker('text', max_nb_chars=500)
    author = factory.SubFactory(UserFactory)


class MediaFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Media
        sqlalchemy_session = AsyncSession

    tweet_id = factory.SubFactory(TweetFactory)


class FollowersFactory(AsyncSQLAlchemyModelFactory):

    class Meta:
        model = Followers
        sqlalchemy_session = AsyncSession

    user_id = factory.SubFactory(UserFactory)
    follower_id = factory.SubFactory(UserFactory)


class LikesFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Likes
        sqlalchemy_session = AsyncSession

    user_id = factory.SubFactory(UserFactory)
    tweet_id = factory.SubFactory(TweetFactory)
