from __future__ import annotations
import os
from typing import List

from sqlalchemy.orm import relationship, Mapped
from libcloud.storage.drivers.local import LocalStorageDriver
from sqlalchemy_file import File, FileField
from sqlalchemy_file.storage import StorageManager
from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy


class Followers(Base):
    __tablename__ = 'followers'

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  #тот кто подписывается
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)  #тот на кого подписываются
    followers: Mapped[Users] = relationship("Users", back_populates='followers_associations', lazy='joined', foreign_keys=[follower_id])  #подписчики
    following: Mapped[Users] = relationship("Users",back_populates='following_associations', lazy='joined', foreign_keys=[user_id])  #подписки

    __table_args__ = (
        PrimaryKeyConstraint("follower_id", "user_id"),
    )




class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    api_key = Column(String(50), nullable=False)
    followers_associations: Mapped[List[Followers]] = relationship("Followers", back_populates='followers',
                                                                   cascade="all, delete-orphan", lazy='selectin',
                                                                   foreign_keys=[Followers.follower_id])
    followers_list: AssociationProxy[List[Users]] = association_proxy('followers_associations', 'following',
                                                                      creator=lambda user_obj: Followers(Followers.follower_id == user_obj))

    following_associations: Mapped[List[Followers]] = relationship("Followers", back_populates='following',
                                                                   cascade="all, delete-orphan", lazy='selectin',
                                                                   foreign_keys=[Followers.user_id])
    following_list: AssociationProxy[List[Users]] = association_proxy('following_associations', 'followers',
                                                                      creator=lambda user_obj: Followers(
                                                                          Followers.user_id == user_obj))

    def to_json(self):
        return {'id': self.id, 'name': self.name}





class Tweets(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    attachments = relationship("Media", backref='tweet', lazy='joined', cascade="all")
    author = Column(Integer, ForeignKey("users.id"), nullable=False)
    likes = relationship("Likes", backref='tweet', lazy='joined', cascade="all")

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    content = Column(FileField)

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Likes(Base):
    __tablename__ = 'likes'

    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("tweet_id", "user_id"),
    )





os.makedirs("./upload_dir/attachment", 0o777, exist_ok=True)
container = LocalStorageDriver("./upload_dir").get_container("attachment")
StorageManager.add_storage("default", container)
