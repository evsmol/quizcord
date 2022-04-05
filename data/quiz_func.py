from data import db_session
from data.models.quizzes import Quiz
from data.models.questions import Question


def add_quiz(author_id, server_id=None):
    quiz = Quiz()
    quiz.title = None
    quiz.description = None
    quiz.server_id = server_id
    quiz.author_id = author_id
    quiz.players = []

    db_sess = db_session.create_session()
    db_sess.add(quiz)
    db_sess.flush()
    db_sess.refresh(quiz)
    db_sess.commit()
    return quiz.id


def get_quiz(quiz_id):
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    return quiz


def get_server_quizzes(server_id):
    db_sess = db_session.create_session()
    quizzes = db_sess.query(Quiz).filter(Quiz.server_id == server_id,
                                         Quiz.publication is True)
    return quizzes


def get_user_quizzes(user_id, server_id=None):
    db_sess = db_session.create_session()
    if server_id:
        quizzes = db_sess.query(Quiz).filter(Quiz.author_id == user_id,
                                             Quiz.server_id == server_id)
    else:
        quizzes = db_sess.query(Quiz).filter(Quiz.author_id == user_id)
    return quizzes


def get_quiz_questions(quiz_id):
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).filter(Question.quiz_id == quiz_id)
    return questions


def del_quiz(quiz_id):
    db_sess = db_session.create_session()
    db_sess.query(Quiz).filter(Quiz.id == quiz_id).delete()
    db_sess.query(Question).filter(Question.quiz_id == quiz_id).delete()
    db_sess.commit()


def update_quiz(quiz_id, title=None, description=None, server_id=None,
                players=None, publication=None):
    db_sess = db_session.create_session()
    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    if title:
        quiz.title = title
    if description:
        quiz.description = description
    if server_id:
        quiz.server_id = server_id
    if players:
        quiz.players = players
    if players:
        quiz.publication = publication
    db_sess.commit()
