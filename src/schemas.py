from pydantic import BaseModel
from typing import Union

class ApiKey(BaseModel):
    api_key: str


class TweetBase(BaseModel):
    content: str


class Media(BaseModel):
    pass


class TweetPost(TweetBase):
    tweet_media_ids: Union[list[int], None] = None


class MediaLink(BaseModel):
    link: str


class User(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class Like(BaseModel):
    user_id: int
    name: str


class Answer(BaseModel):
    result: bool


class PostAnswer(Answer):
    id: int

class TweetInlist(TweetBase):
    id: int
    attachments: list[MediaLink] = []
    author: User
    likes: list[Like] = []

    class Config:
        orm_mode = True

class TweetAnswer(Answer):
    tweets: list[TweetInlist]
class UserPage(User):
    followers: list[User]
    following: list[User]

class UserAnswer(Answer):
    user: UserPage

