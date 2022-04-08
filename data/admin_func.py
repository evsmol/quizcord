from data import db_session
from data.models.quizzes import Quiz
from data.models.questions import Question


def delete_empty_quizzes():
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).all()
    quizzes_id = []
    if questions:
        for question in questions:
            quizzes_id.append(question.quiz_id)
        db_sess.query(Quiz).filter(Quiz.quiz_id not in quizzes_id).delete()
    else:
        db_sess.query(Quiz).filter(Quiz.id >= 0).delete()
    db_sess.commit()
