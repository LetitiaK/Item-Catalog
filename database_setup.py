#!/usr/bin/env python
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=False)
    email = Column(String(500), nullable=False)
    picture = Column(String(500))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    image_url = Column(String(1000), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'image_url': self.image_url,
                'user_id': self.user_id
                }


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    description = Column(String(5000), nullable=False)
    price = Column(String(20), nullable=False)
    link = Column(String(5000), nullable=False)
    img_url = Column(String(1000), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                'price': self.price,
                'link': self.link,
                'img_url': self.img_url,
                'category_id': self.category_id,
                'user_id': self.user_id
                }


engine = create_engine('postgresql+psycopg2://lilly:12345@localhost/items_db')

Base.metadata.create_all(engine)
