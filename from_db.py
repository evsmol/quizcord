from data import db_session
from data.questions import Question
from data.quizzes import Quiz


def add_question():
    question = Question()
    question.text = None
    question.explanation = None
    question.answers = []
    question.right_answer = None
    question.media = None

    db_sess = db_session.create_session()
    db_sess.add(question)
    db_sess.flush()
    db_sess.refresh(question)
    db_sess.commit()
    return question.id


def add_quiz():
    quiz = Quiz()
    quiz.title = None
    quiz.server_id = None
    quiz.author_id = None
    quiz.players = []
    quiz.questions = []

    db_sess = db_session.create_session()
    db_sess.add(quiz)
    db_sess.flush()
    db_sess.refresh(quiz)
    db_sess.commit()
    return quiz.id
