import pytest

from .factories import UserFactory, TweetFactory, MediaFactory, LikesFactory, FollowersFactory
from src.models import Likes, Followers, Users, Tweets, Media
from httpx import AsyncClient
from src.main import session
from sqlalchemy.future import select


@pytest.mark.asyncio
async def test_create_user(ac: AsyncClient, init_db):
    user = UserFactory.create()
    session.add(user)
    await session.commit()
    assert user.id is not None
    users = await session.execute(select(Users))
    users = users.scalars().all()
    assert len(users) == 1


@pytest.mark.asyncio
async def test_create_media(ac: AsyncClient, init_db):
    media = MediaFactory()
    session.add(media)
    await session.commit()
    assert media.id is not None
    assert media.extension == '.jpg'
    medias = await session.execute(select(Media))
    medias = medias.scalars().all()
    assert len(medias) == 1


@pytest.mark.asyncio
async def test_create_tweet(ac: AsyncClient, init_db):
    user = UserFactory.create()
    session.add(user)
    await session.commit()
    tweet = TweetFactory(author=user.id)
    session.add(tweet)
    await session.commit()
    assert tweet.id is not None
    tweets = await session.execute(select(Tweets))
    tweets = tweets.unique().scalars().all()
    assert len(tweets) == 1


@pytest.mark.asyncio
async def test_create_like(ac: AsyncClient, init_db):
    user = UserFactory.create()
    user1 = UserFactory.create()
    session.add(user)
    session.add(user1)
    await session.commit()
    tweet = TweetFactory(author=user.id)
    session.add(tweet)
    await session.commit()
    like = LikesFactory(user_id=user.id, tweet_id=tweet.id)
    session.add(like)
    await session.commit()
    likes = await session.execute(select(Likes))
    likes = likes.scalars().all()
    assert len(likes) == 1
    assert likes[0].user_id == user.id


@pytest.mark.asyncio
async def test_create_follow(ac: AsyncClient, init_db):
    user = UserFactory.create()
    user1 = UserFactory.create()
    session.add(user)
    session.add(user1)
    await session.commit()
    follow = FollowersFactory(user_id=user.id, follower_id=user1.id)
    session.add(follow)
    await session.commit()
    follows = await session.execute(select(Followers))
    follows = follows.scalars().all()
    assert len(follows) == 1
    assert follows[0].user_id == user.id
