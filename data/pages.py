import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Pages(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'pages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    chapter_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("chapters.id"))
    chapter = orm.relationship('Chapters')
    page = sqlalchemy.Column(sqlalchemy.BLOB)
