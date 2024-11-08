import os

from dotenv import load_dotenv
from fastapi import FastAPI, Path, UploadFile, Depends, Request
from typing import Annotated, Union
from fastapi import HTTPException, Header
from http import HTTPStatus
from fastapi.responses import JSONResponse
from pathlib import Path as Path_l
from aiofiles import open as aio_open

load_dotenv()

from src.database import engine, session
from src.models import Base, Tweets, Media, Users, Followers, Likes
from src.schemas import TweetPost, TweetAnswer, PostAnswer, Answer, UserAnswer, MediaAnswer
from src.logging_config import get_logger
from src.db_services import (
    UserService,
    TweetService,
    MediaService,
    LikesService,
    FollowersService,
)

app = FastAPI()
logger = None


async def initialize_logger():
    global logger
    logger = await get_logger()


async def shutdown_logger():
    await logger.shutdown()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await initialize_logger()


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()
    await shutdown_logger()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    await logger.info(f"{request.method} {request.url} - {response.status_code}")
    return response


async def token_required(api_key: Annotated[Union[str, None], Header()] = None):
    if api_key is None:
        await logger.warning("Authorization without api_key")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Valid api-key token is missing in headers",
        )

    current_user = await UserService.get_user_api_key(api_key)

    if current_user is None:
        await logger.warning("Authorization with invalid api_key")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Sorry. Wrong api-key token in headers. This user does not exist.",
        )
    return current_user


async def get_tweet(id: int = Path(title="Id of the tweet")):
    tweet = await TweetService.get_tweet(id)
    if tweet is None:
        await logger.warning(f"Wrong request to database for tweet id = {id}")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="No such tweet in database."
        )
    return tweet


@app.post(
    "/api/tweets", dependencies=[Depends(token_required)], response_model=PostAnswer
)
async def tweet_post(tweet: TweetPost, current_user: Users = Depends(token_required)):
    new_tweet = Tweets(author=current_user.id, content=tweet.tweet_data)
    if tweet.tweet_media_ids:
        media_list = await MediaService.get_media_lst(tweet.tweet_media_ids)
        new_tweet.attachments.extend(media_list)
    session.add(new_tweet)
    await session.commit()
    await logger.debug(f"User {current_user} has posted tweet {tweet}")
    return {"result": "true", "id": new_tweet.id}


@app.post("/api/medias", response_model=MediaAnswer)
async def media_post(file: UploadFile):
    file_extension = Path_l(file.filename).suffix

    new_media = Media(extension=file_extension)
    session.add(new_media)
    await session.commit()

    file_path = Path_l("storage") / (str(new_media.id) + file_extension)

    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True)

    async with aio_open(file_path, "wb") as f:
        contents = await file.read()
        await f.write(contents)
    await logger.debug(f"Media {new_media} has been created, directory:{file_path}")

    return {"result": "true", "media_id": new_media.id}


@app.delete(
    "/api/tweets/{id}",
    dependencies=[Depends(token_required), Depends(get_tweet)],
    response_model=Answer,
)
async def tweet_delete(
        current_user: Users = Depends(token_required), tweet: Tweets = Depends(get_tweet)
):
    if tweet.author != current_user.id:
        await logger.warning(f"User {current_user} tried to delete tweet {tweet} of {tweet.author}")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You cannot delete tweet of the other user.",
        )

    await session.delete(tweet)
    await session.commit()
    await logger.debug(f"User {current_user} has deleted tweet {tweet}")

    return {"result": "true"}


@app.post(
    "/api/tweets/{id}/likes",
    dependencies=[Depends(token_required), Depends(get_tweet)],
    response_model=Answer,
)
async def like_tweet(
        id: int = Path(title="Id of the tweet"),
        current_user: Users = Depends(token_required),
):
    like = await LikesService.get_like(id, current_user.id)
    if like:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You have already liked this tweet.",
        )
    new_like = Likes(user_id=current_user.id, tweet_id=id)
    session.add(new_like)
    await session.commit()
    await logger.debug(f"User {current_user} has liked tweet id = {id}")

    return {"result": "true"}


@app.delete(
    "/api/tweets/{id}/likes",
    dependencies=[Depends(token_required), Depends(get_tweet)],
    response_model=Answer,
)
async def delete_likeid(
        id: int = Path(title="Id of the tweet"),
        current_user: Users = Depends(token_required),
):
    like = await LikesService.get_like(id, current_user.id)
    if not like:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="You have not liked this tweet."
        )
    await session.delete(like)
    await session.commit()
    await logger.debug(f"User {current_user} has deleted liked for tweet id = {id}")

    return {"result": "true"}


@app.post(
    "/api/users/{id}/follow",
    dependencies=[Depends(token_required)],
    response_model=Answer,
)
async def follow(
        id: int = Path(title="Id of the user"),
        current_user: Users = Depends(token_required),
):
    if current_user.id == id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Sorry. You cannot follow yourself.",
        )

    check_follow = await FollowersService.get_follow(current_user.id, id)
    if check_follow:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Sorry. You have been already following this user.",
        )
    new_follow_record = Followers(user_id=current_user.id, follower_id=id)
    session.add(new_follow_record)
    await session.commit()
    await logger.debug(f"User {current_user} has followed user id = {id}")

    return {"result": "true"}


@app.delete(
    "/api/users/{id}/follow",
    dependencies=[Depends(token_required)],
    response_model=Answer,
)
async def unfollow(
        id: int = Path(title="Id of the user"),
        current_user: Users = Depends(token_required),
):
    check_follow = await FollowersService.get_follow(current_user.id, id)
    if check_follow is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Sorry. You are not following this user.",
        )
    await session.delete(check_follow)
    await session.commit()
    await logger.debug(f"User {current_user} has unfollowed user id = {id}")

    return {"result": "true"}


@app.get(
    "/api/tweets", dependencies=[Depends(token_required)], response_model=TweetAnswer
)
async def get_tweets(current_user: Users = Depends(token_required)):
    await logger.debug(f"Get tweet for user {current_user}")
    tweets_list = await TweetService.get_tweet_lst(current_user.id)
    tweets = []
    for tweet in tweets_list:
        author = await UserService.get_user_by_id(tweet.author)
        likes_u = []
        for like in tweet.likes:
            user_like = await UserService.get_user_by_id(like.user_id)
            likes_u.append({"user_id": user_like.id, "name": user_like.name})

        tweets.append(
            {
                "id": tweet.id,
                "content": tweet.content,
                "attachments": [
                    attachment.to_json()["url"] for attachment in tweet.attachments
                ],
                "author": author.to_json(),
                "likes": likes_u,
            }
        )
    result = {"result": "true", "tweets": tweets}
    return result


@app.get(
    "/api/users/me", dependencies=[Depends(token_required)], response_model=UserAnswer
)
async def personal_page(current_user: Users = Depends(token_required)) -> Users:
    await logger.debug(f"User {current_user} visit personal page")
    followers_list = await FollowersService.get_followers_lst(current_user.id)
    followers_list = [follower.to_json() for follower in followers_list]

    following_list = await FollowersService.get_following_lst(current_user.id)
    following_list = [follow.to_json() for follow in following_list]

    current_user = current_user.to_json()
    current_user["followers"] = followers_list
    current_user["following"] = following_list
    result = {"result": "true", "user": current_user}
    return result


@app.get(
    "/api/users/{id}", dependencies=[Depends(token_required)], response_model=UserAnswer
)
async def user_page(id: int = Path(title="Id of the user"), current_user: Users = Depends(token_required)) -> Users:
    await logger.debug(f"User {current_user} visit personal page of user id =  {id}")
    followers_list = await FollowersService.get_followers_lst(id)
    followers_list = [follower.to_json() for follower in followers_list]

    following_list = await FollowersService.get_following_lst(id)
    following_list = [follow.to_json() for follow in following_list]

    user = await UserService.get_user_by_id(id)
    user = user.to_json()
    user["followers"] = followers_list
    user["following"] = following_list
    result = {"result": "true", "user": user}
    return result


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f'status_code: {exc.status_code}, error: {exc.detail}')
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
