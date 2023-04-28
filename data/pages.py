import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Pages(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'pages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    page = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    comics_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("comics.id"))
