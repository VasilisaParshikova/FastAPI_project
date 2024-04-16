from fastapi import FastAPI, Path, File, UploadFile
from database import engine, session
from models import Base, Tweets, Media, Users
from sqlalchemy.future import select
from schemas import TweetPost, TweetAnswer, PostAnswer, Answer, UserAnswer, ApiKey, User

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()


@app.post("/api/tweets", response_model=PostAnswer)
async def tweet_post(tweet: TweetPost):
    pass


@app.post("/api/medias", response_model=PostAnswer)
async def media_post(api_key: ApiKey, file: UploadFile):
    pass

@app.delete("/api/tweets/{id}", response_model=Answer)
async def tweet_delete(api_key: ApiKey, id: int = Path(title="Id of the tweet")):
    pass


@app.post("/api/tweets/{id}/likes", response_model=Answer)
async def like_tweet(api_key: ApiKey, id: int = Path(title="Id of the tweet")):
    pass


@app.delete("/api/tweets/{id}/likes", response_model=Answer)
async def delete_like(api_key: ApiKey, id: int = Path(title="Id of the tweet")):
    pass


@app.post("/api/users/{id}/follow", response_model=Answer)
async def follow(api_key: ApiKey, id: int = Path(title="Id of the user")):
    pass


@app.delete("/api/users/{id}/follow", response_model=Answer)
async def unfollow(api_key: ApiKey, id: int = Path(title="Id of the user")):
    pass


@app.get("/api/tweets", response_model=TweetAnswer)
async def get_tweets(api_key: ApiKey):
    pass


@app.get("/api/users/me", response_model=User)
async def personal_page(api_key: ApiKey):
    res = await session.execute(select(Users).where(Users.id == 1))
    res = res.scalars().first()
    print(res)
    return res


@app.get("/api/users/{id}", response_model=UserAnswer)
async def user_page(api_key: str, id: int = Path(title="Id of the user")):
    pass
