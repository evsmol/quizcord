import sqlalchemy

from data.db_session import SqlAlchemyBase


class Quiz(SqlAlchemyBase):
    __tablename__ = 'quizzes'

    id = sqlalchemy.Column(
        sqlalchemy.INTEGER,
        primary_key=True,
        autoincrement=True
    )

    title = sqlalchemy.Column(
        sqlalchemy.VARCHAR(length=200)
    )

    description = sqlalchemy.Column(
        sqlalchemy.VARCHAR(length=2000)
    )

    server_id = sqlalchemy.Column(
        sqlalchemy.BIGINT
    )

    author_id = sqlalchemy.Column(
        sqlalchemy.BIGINT,
        nullable=False
    )

    players = sqlalchemy.Column(
        sqlalchemy.JSON
    )

    questions = sqlalchemy.Column(
        sqlalchemy.JSON
    )

    publication = sqlalchemy.Column(
        sqlalchemy.BOOLEAN,
        default=False,
        nullable=False
    )
