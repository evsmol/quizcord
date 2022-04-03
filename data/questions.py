import sqlalchemy
from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.VARCHAR(length=256))
    explanation = sqlalchemy.Column(sqlalchemy.VARCHAR(length=2048))
    answers = sqlalchemy.Column(sqlalchemy.JSON)
    right_answer = sqlalchemy.Column(sqlalchemy.INTEGER)
    media = sqlalchemy.Column(sqlalchemy.TEXT)