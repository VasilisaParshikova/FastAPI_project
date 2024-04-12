from __future__ import annotations
import os
from sqlalchemy.orm import relationship
from libcloud.storage.drivers.local import LocalStorageDriver
from sqlalchemy_file import File, FileField
from sqlalchemy_file.storage import StorageManager
from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, UniqueConstraint


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    api_key = Column(String(50), nullable=False)


class Tweets(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    attachments = relationship("Media", backref='tweet_id', lazy='joined', cascade="all")
    author = Column(Integer, ForeignKey("users.id"), nullable=False)
    likes = relationship("Likes", backref='tweet_id', lazy='joined', cascade="all")


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    content = Column(FileField)


class Likes(Base):
    __tablename__ = 'likes'

    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("tweet_id", "user_id"),
    )


class Followers(Base):
    __tablename__ = 'followers'

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("follower_id", "user_id"),
    )


os.makedirs("./upload_dir/attachment", 0o777, exist_ok=True)
container = LocalStorageDriver("./upload_dir").get_container("attachment")
StorageManager.add_storage("default", container)
