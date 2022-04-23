from data import db_session
from data.quiz_func import del_quiz
from data.models.quizzes import Quiz
from data.models.questions import Question


def delete_empty_quizzes():
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).all()
    quizzes_id = []
    if questions:
        for question in questions:
            quizzes_id.append(question.quiz_id)
        quizzes = db_sess.query(Quiz).filter(Quiz.id not in quizzes_id).all()
        for quiz in quizzes:
            del_quiz(quiz.id)
    else:
        quizzes = db_sess.query(Quiz).filter(Quiz.id >= 0).all()
        for quiz in quizzes:
            del_quiz(quiz.id)
    db_sess.commit()
    db_sess.close()
