import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Comics(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comics'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    genres = orm.relationship("Genres",
                              secondary="assoc_genres",
                              backref="comics")
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    chapters = orm.relationship("Chapters", back_populates='comic')
    reviews = orm.relationship("Reviews", back_populates='comic')
    association_table = sqlalchemy.Table(
        'assoc_favs',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('users', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('users.id')),
        sqlalchemy.Column('comics', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('comics.id'))
    )
