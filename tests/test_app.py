import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from .factories import UserFactory, TweetFactory, MediaFactory, LikesFactory, FollowersFactory
from src.main import session


@pytest.mark.asyncio
async def test_create_media(ac: AsyncClient, init_db):
    test_user = UserFactory.create()
    session.add(test_user)
    await session.commit()

    file = {'file': ('test.jpg', b'test file content', 'image/jpeg')}
    headers = {"api_key": test_user.api_key}
    response = await ac.post("/api/medias", files=file, headers=headers)

    assert response.status_code == 200
    assert response.json()['result'] == 'true'


@pytest.mark.asyncio
async def test_post_tweet(ac: AsyncClient, init_db):
    test_user = UserFactory.create()
    test_media = MediaFactory.create()
    session.add(test_user)
    session.add(test_media)
    await session.commit()
    headers = {"api-key": test_user.api_key}
    tweet_data = {"tweet_data": "Test tweet", "tweet_media_ids": [test_media.id]}

    response = await ac.post("/api/tweets", json=tweet_data, headers=headers)

    assert response.status_code == 200
    assert response.json()['result'] == True
    assert response.json()['id'] is not None
