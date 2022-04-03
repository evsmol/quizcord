import sqlalchemy
from .db_session import SqlAlchemyBase


class Quiz(SqlAlchemyBase):
    __tablename__ = 'quizzes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.VARCHAR(length=256))
    server_id = sqlalchemy.Column(sqlalchemy.BIGINT)
    author_id = sqlalchemy.Column(sqlalchemy.BIGINT)
    players = sqlalchemy.Column(sqlalchemy.JSON)
    questions = sqlalchemy.Column(sqlalchemy.JSON)