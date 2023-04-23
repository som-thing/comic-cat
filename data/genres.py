import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Genres(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'genres'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    association_table = sqlalchemy.Table(
        'assoc_genres',
        SqlAlchemyBase.metadata,
        sqlalchemy.Column('comics', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('comics.id')),
        sqlalchemy.Column('genres', sqlalchemy.Integer,
                          sqlalchemy.ForeignKey('genres.id'))
    )
