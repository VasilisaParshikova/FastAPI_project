import pytest
from httpx import AsyncClient
from .factories import UserFactory, TweetFactory, MediaFactory, LikesFactory, FollowersFactory
from src.main import session
from src.models import Likes, Followers
from sqlalchemy.future import select


@pytest.mark.asyncio
async def test_create_media(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    session.add(test_user)
    await session.commit()

    file = {'file': ('test.jpg', b'test file content', 'image/jpeg')}
    headers = {"api_key": test_user.api_key}
    response = await ac.post("/api/medias", files=file, headers=headers)

    assert response.status_code == 200
    assert response.json()['result']


@pytest.mark.asyncio
async def test_post_tweet(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    test_media = MediaFactory.create()
    session.add(test_user)
    session.add(test_media)
    await session.commit()
    headers = {"api-key": test_user.api_key}
    tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": [test_media.id]}

    response = await ac.post("/api/tweets", json=tweet_data, headers=headers)

    assert response.status_code == 200
    assert response.json()['result']
    assert response.json()['id'] is not None


@pytest.mark.asyncio
async def test_tweet_delete(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    session.add(test_user)
    await session.commit()
    test_tweet = TweetFactory.create(author=test_user.id)

    session.add(test_tweet)
    await session.commit()
    headers = {"api-key": test_user.api_key}
    response = await ac.delete(f"/api/tweets/{test_tweet.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()['result']


@pytest.mark.asyncio
async def test_like_post(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    test_user2 = UserFactory.create()
    session.add(test_user)
    session.add(test_user2)
    await session.commit()
    test_tweet = TweetFactory.create(author=test_user2.id)
    session.add(test_tweet)
    await session.commit()
    headers = {"api-key": test_user.api_key}
    response = await ac.post(f"/api/tweets/{test_tweet.id}/likes", headers=headers)

    assert response.status_code == 200
    assert response.json()['result']
    like = await session.execute(
        select(Likes).where(Likes.tweet_id == test_tweet.id)
    )
    like = like.scalars().all()
    assert len(like) == 1
    assert like[0].user_id == test_user.id


@pytest.mark.asyncio
async def test_like_delete(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    test_user2 = UserFactory.create()
    session.add(test_user)
    session.add(test_user2)
    await session.commit()
    test_tweet = TweetFactory.create(author=test_user2.id)
    session.add(test_tweet)
    await session.commit()
    test_like = LikesFactory(tweet_id=test_tweet.id, user_id=test_user.id)
    session.add(test_like)
    await session.commit()
    like = await session.execute(
        select(Likes).where(Likes.tweet_id == test_tweet.id)
    )
    like = like.scalars().all()
    assert len(like) == 1
    headers = {"api-key": test_user.api_key}
    response = await ac.delete(f"/api/users/{test_tweet.id}/likes", headers=headers)

    assert response.status_code == 200
    assert response.json()['result']
    like = await session.execute(
        select(Likes).where(Likes.tweet_id == test_tweet.id)
    )
    like = like.scalars().all()
    assert len(like) == 0


@pytest.mark.asyncio
async def test_follow_post(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    test_user2 = UserFactory.create()
    session.add(test_user)
    session.add(test_user2)
    await session.commit()
    headers = {"api-key": test_user.api_key}
    response = await ac.post(f"/api/users/{test_user2.id}/follow", headers=headers)

    assert response.status_code == 200
    assert response.json()['result']
    follow = await session.execute(select(Followers).where(Followers.user_id == test_user.id))
    follow = follow.scalars().all()
    assert len(follow) == 1
    assert follow[0].follower_id == test_user2.id


@pytest.mark.asyncio
async def test_follow_delete(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    test_user2 = UserFactory.create()
    session.add(test_user)
    session.add(test_user2)
    await session.commit()
    test_follow = FollowersFactory(user_id=test_user.id, follower_id=test_user2.id)
    session.add(test_follow)
    await session.commit()
    follow = await session.execute(select(Followers).where(Followers.user_id == test_user.id))
    follow = follow.scalars().all()
    assert len(follow) == 1
    headers = {"api-key": test_user.api_key}
    response = await ac.delete(f"/api/tweets/{test_user2.id}/follow", headers=headers)

    assert response.status_code == 200
    assert response.json()['result']
    follow = await session.execute(select(Followers).where(Followers.user_id == test_user.id))
    follow = follow.scalars().all()
    assert len(follow) == 0


@pytest.mark.asyncio
async def test_tweets_get(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    test_user2 = UserFactory.create()
    test_user3 = UserFactory.create()
    session.add(test_user)
    session.add(test_user2)
    session.add(test_user3)
    await session.commit()
    test_follow = FollowersFactory(user_id=test_user.id, follower_id=test_user2.id)
    session.add(test_follow)
    test_follow2 = FollowersFactory(user_id=test_user.id, follower_id=test_user3.id)
    session.add(test_follow2)
    await session.commit()
    test_tweet = TweetFactory.create(author=test_user2.id)
    test_tweet2 = TweetFactory.create(author=test_user3.id)
    session.add(test_tweet)
    session.add(test_tweet2)
    await session.commit()
    headers = {"api-key": test_user.api_key}
    response = await ac.get("/api/tweets", headers=headers)
    assert response.status_code == 200
    assert response.json()['result']
    assert len(response.json()["tweets"]) == 2


@pytest.mark.asyncio
async def test_personal_page_get(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    test_user2 = UserFactory.create()
    test_user3 = UserFactory.create()
    session.add(test_user)
    session.add(test_user2)
    session.add(test_user3)
    await session.commit()
    test_follow = FollowersFactory(user_id=test_user.id, follower_id=test_user2.id)
    session.add(test_follow)
    test_follow2 = FollowersFactory(user_id=test_user.id, follower_id=test_user3.id)
    session.add(test_follow2)
    test_follow3 = FollowersFactory(user_id=test_user2.id, follower_id=test_user.id)
    session.add(test_follow3)
    await session.commit()

    headers = {"api-key": test_user.api_key}
    response = await ac.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()['result']
    assert response.json()["user"]['name'] == test_user.name
    assert len(response.json()["user"]["followers"]) == 1
    assert len(response.json()["user"]['following']) == 2


@pytest.mark.asyncio
async def test_user_page_get(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()
    test_user2 = UserFactory.create()
    test_user3 = UserFactory.create()
    session.add(test_user)
    session.add(test_user2)
    session.add(test_user3)
    await session.commit()
    test_follow = FollowersFactory(user_id=test_user.id, follower_id=test_user2.id)
    session.add(test_follow)
    test_follow2 = FollowersFactory(user_id=test_user3.id, follower_id=test_user2.id)
    session.add(test_follow2)
    test_follow3 = FollowersFactory(user_id=test_user2.id, follower_id=test_user.id)
    session.add(test_follow3)
    await session.commit()

    headers = {"api-key": test_user.api_key}
    response = await ac.get(f"/api/users/{test_user2.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()['result']
    assert response.json()["user"]['name'] == test_user2.name
    assert len(response.json()["user"]["followers"]) == 2
    assert len(response.json()["user"]['following']) == 1


@pytest.mark.asyncio
async def test_user_page_get_error(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()

    await session.commit()

    response = await ac.get(f"/api/users/{test_user.id}")
    assert response.status_code == 400
    assert response.json()["error"] == 'Valid api-key token is missing in headers'


@pytest.mark.asyncio
async def test_user_page_get_error_wrong_api_key(ac: AsyncClient, init_db, logger):
    test_user = UserFactory.create()

    await session.commit()
    headers = {"api-key": 'test_user.api_key'}
    response = await ac.get(f"/api/users/{test_user.id}", headers=headers)

    assert response.status_code == 400
    assert response.json()["error"] == 'Sorry. Wrong api-key token in headers. This user does not exist.'
