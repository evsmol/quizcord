import sqlalchemy
from data.db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    quiz_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.VARCHAR(length=200))
    explanation = sqlalchemy.Column(sqlalchemy.VARCHAR(length=2048))
    answers = sqlalchemy.Column(sqlalchemy.JSON)
    right_answer = sqlalchemy.Column(sqlalchemy.INTEGER)
    media = sqlalchemy.Column(sqlalchemy.TEXT)
