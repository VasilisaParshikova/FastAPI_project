import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from .factories import UserFactory, TweetFactory, MediaFactory, LikesFactory, FollowersFactory


@pytest.mark.asyncio
async def test_create_media(client, setup_db):
    async with AsyncSession(bind=setup_db) as session:
        test_user = await UserFactory.create(session=session)

    file = {'file': ('test.jpg', b'test file content', 'image/jpeg')}
    headers = {"api_key": test_user.api_key}
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/api/medias", files=file, headers=headers)

    assert response.status_code == 200
    assert response.json()['result'] == 'true'