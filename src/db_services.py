from database import session
from models import Tweets, Media, Users, Followers, Likes
from sqlalchemy.future import select
from typing import List
from sqlalchemy.orm import selectinload


class UserService:
    @classmethod
    async def get_user_api_key(cls, api_key: str) -> Users:
        user = await session.execute(select(Users).where(Users.api_key == api_key))
        user = user.scalars().first()
        return user

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> Users:
        user = await session.execute(select(Users).where(Users.id == user_id))
        user = user.scalars().first()
        return user


class TweetService:
    @classmethod
    async def get_tweet(cls, id: int) -> Tweets:
        tweet = await session.execute(select(Tweets).where(Tweets.id == id))
        tweet = tweet.scalars().first()
        return tweet

    @classmethod
    async def get_tweet_lst(cls, user_id: int) -> List[Tweets]:
        tweets_list = await session.execute(
            select(Tweets)
            .join(Users, Tweets.author == Users.id)
            .join(Followers, Followers.user_id == user_id)
            .where(Tweets.author == Followers.follower_id)
            .options(selectinload(Tweets.attachments), selectinload(Tweets.likes))
        )
        tweets_list = tweets_list.unique().scalars().all()
        return tweets_list


class MediaService:
    @classmethod
    async def get_media_lst(cls, id_lst: List[int]) -> List[Media]:
        media_objects = await session.execute(select(Media).where(Media.id.in_(id_lst)))
        media_list = media_objects.scalars().all()
        return media_list


class LikesService:
    @classmethod
    async def get_like(cls, tweet_id: int, user_id: int) -> Likes:
        like = await session.execute(
            select(Likes).where(Likes.tweet_id == tweet_id, Likes.user_id == user_id)
        )
        like = like.scalars().first()
        return like


class FollowersService:
    @classmethod
    async def get_follow(cls, user_id: int, follower_id: int) -> Followers:
        follow = await session.execute(
            select(Followers).where(
                Followers.user_id == user_id, Followers.follower_id == follower_id
            )
        )
        follow = follow.scalars().first()
        return follow

    @classmethod
    async def get_followers_lst(cls, user_id: int) -> List[Users]:
        followers_list = await session.execute(
            select(Users)
            .join(Followers, Followers.user_id == Users.id)
            .where(Followers.follower_id == user_id)
        )
        followers_list = followers_list.scalars().all()
        return followers_list

    @classmethod
    async def get_following_lst(cls, user_id: int) -> List[Users]:
        following_list = await session.execute(
            select(Users)
            .join(Followers, Followers.follower_id == Users.id)
            .where(Followers.user_id == user_id)
        )
        following_list = following_list.scalars().all()
        return following_list
