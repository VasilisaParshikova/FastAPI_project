from fastapi import FastAPI, Path, File, UploadFile, Depends
from database import engine, session
from models import Base, Tweets, Media, Users, Followers, Likes
from sqlalchemy.future import select
from schemas import TweetPost, TweetAnswer, PostAnswer, Answer, UserAnswer
from typing import Annotated, Union
from fastapi import HTTPException, Header
from http import HTTPStatus
from fastapi.responses import JSONResponse
from sqlalchemy.orm import selectinload

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()

async def token_required(api_key: Annotated[Union[str, None], Header()] = None):
    if api_key is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Valid api-key token is missing in headers'
        )

    current_user = await session.execute(select(Users).where(Users.api_key == api_key))
                                         #options(selectinload(Users.followers_list)))
    current_user = current_user.scalars().first()
    if current_user is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Sorry. Wrong api-key token in headers. This user does not exist.'
        )
    return current_user

@app.post("/api/tweets",  dependencies=[Depends(token_required)], response_model=PostAnswer)
async def tweet_post(tweet: TweetPost, current_user: Users = Depends(token_required)):
    new_tweet = Tweets(author=current_user.id, content=tweet.content)
    if tweet.tweet_media_ids:
        media_objects = await session.execute(
            select(Media).where(Media.id.in_(tweet.tweet_media_ids))
        )
        media_list = media_objects.scalars().all()
        new_tweet.attachments.extend(media_list)
    session.add(new_tweet)
    await session.commit()
    return {'result': 'true', 'id': new_tweet.id}


@app.post("/api/medias", response_model=PostAnswer)
async def media_post(file: UploadFile):
    pass

@app.delete("/api/tweets/{id}", dependencies=[Depends(token_required)], response_model=Answer)
async def tweet_delete(id: int = Path(title="Id of the tweet"), current_user: Users = Depends(token_required)):
    tweet = await session.execute(select(Tweets).where(Tweets.id == id))
    tweet = tweet.scalars().first()
    if tweet is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No such tweet in database.'
        )
    if tweet.author != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='You cannot delete tweet of the other user.'
        )
    await session.delete(tweet)
    await session.commit()

    return {'result': 'true'}


@app.post("/api/tweets/{id}/likes", dependencies=[Depends(token_required)], response_model=Answer)
async def like_tweet(id: int = Path(title="Id of the tweet"), current_user: Users = Depends(token_required)):

    tweet = await session.execute(select(Tweets).where(Tweets.id == id))
    tweet = tweet.scalars().first()
    if tweet is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No such tweet in database.'
        )
    like = await session.execute(select(Likes).where(Likes.tweet_id == id, Likes.user_id == current_user.id))
    like = like.scalars().first()
    if like:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='You have already liked this tweet.'
        )
    new_like = Likes(user_id=current_user.id, tweet_id=id)
    session.add(new_like)
    await session.commit()

    return {'result': 'true'}


@app.delete("/api/tweets/{id}/likes", dependencies=[Depends(token_required)], response_model=Answer)
async def delete_likeid(id: int = Path(title="Id of the tweet"), current_user: Users = Depends(token_required)):
    tweet = await session.execute(select(Tweets).where(Tweets.id == id))
    tweet = tweet.scalars().first()
    if tweet is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='No such tweet in database.'
        )
    like = await session.execute(select(Likes).where(Likes.tweet_id == id, Likes.user_id == current_user.id))
    like = like.scalars().first()
    if not like:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='You have not liked this tweet.'
        )
    await session.delete(like)
    await session.commit()

    return {'result': 'true'}


@app.post("/api/users/{id}/follow", dependencies=[Depends(token_required)], response_model=Answer)
async def follow(id: int = Path(title="Id of the user"), current_user: Users = Depends(token_required)):
    if current_user.id == id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Sorry. You cannot follow yourself.'
        )
    check_follow = await session.execute(
        select(Followers).where(Followers.user_id == current_user.id, Followers.follower_id == id))
    check_follow = check_follow.scalars().first()
    if check_follow:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Sorry. You have been already following this user.'
        )
    new_follow_record = Followers(user_id=current_user.id, follower_id=id)
    session.add(new_follow_record)
    await session.commit()

    return {'result': 'true'}


@app.delete("/api/users/{id}/follow", dependencies=[Depends(token_required)], response_model=Answer)
async def unfollow(id: int = Path(title="Id of the user"), current_user: Users = Depends(token_required)):
    check_follow = await session.execute(select(Followers).where(Followers.user_id == current_user.id, Followers.follower_id == id))
    check_follow = check_follow.scalars().first()
    if check_follow is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Sorry. You are not following this user.'
        )
    await session.delete(check_follow)
    await session.commit()

    return {'result': 'true'}


@app.get("/api/tweets", dependencies=[Depends(token_required)], response_model=TweetAnswer)
async def get_tweets(current_user: Users = Depends(token_required)):
    tweets_list = await session.execute(
        select(Tweets).join(Users, Tweets.author == Users.id).
        join(Followers, Followers.user_id == current_user.id).where(Tweets.author == Followers.follower_id).
        options(selectinload(Tweets.attachments), selectinload(Tweets.likes)))
    tweets_list = tweets_list.unique().scalars().all()
    tweets = []
    for tweet in tweets_list:
        author = await session.execute(select(Users).where(Users.id == tweet.author))
        author = author.scalars().first()
        likes_u = []
        for like in tweet.likes:
            print(like.user_id)
            user_like = await session.execute(select(Users).where(Users.id == like.user_id))
            user_like = user_like.scalars().first()
            likes_u.append({'user_id': user_like.id, 'name': user_like.name})
        tweets.append({'id': tweet.id,
                       'content': tweet.content,
                       'attachment': [str(attachment.id) for attachment in tweet.attachments],
                       'author': author.to_json(),
                       'likes': likes_u})
    result = {'result': 'true', 'tweets': tweets}
    return result


@app.get("/api/users/me", dependencies=[Depends(token_required)], response_model=UserAnswer)
async def personal_page(current_user: Users = Depends(token_required)) -> Users:
    followers_list = await session.execute(
        select(Users).join(Followers, Followers.user_id == Users.id).where(Followers.follower_id == current_user.id))
    followers_list = followers_list.scalars().all()
    followers_list = [follower.to_json() for follower in followers_list]

    following_list = await session.execute(
        select(Users).join(Followers, Followers.follower_id == Users.id).where(Followers.user_id == current_user.id))
    following_list = following_list.scalars().all()
    following_list = [follow.to_json() for follow in following_list]
    current_user = current_user.to_json()
    current_user['followers'] = followers_list
    current_user['following'] = following_list
    result = {'result': 'true', 'user': current_user}
    return result


@app.get("/api/users/{id}", dependencies=[Depends(token_required)], response_model=UserAnswer)
async def user_page(id: int = Path(title="Id of the user"))-> Users:
    followers_list = await session.execute(
        select(Users).join(Followers, Followers.user_id == Users.id).where(Followers.follower_id == id))
    followers_list = followers_list.scalars().all()
    followers_list = [follower.to_json() for follower in followers_list]

    following_list = await session.execute(
        select(Users).join(Followers, Followers.follower_id == Users.id).where(Followers.user_id == id))
    following_list = following_list.scalars().all()
    following_list = [follow.to_json() for follow in following_list]
    user = await session.execute(select(Users).where(Users.id == id))
    user = user.scalars().first()
    user = user.to_json()
    user['followers'] = followers_list
    user['following'] = following_list
    result = {'result': 'true', 'user': user}
    return result

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )