from data import db_session
from data.quiz_func import del_quiz
from data.models.quizzes import Quiz


def delete_empty_quizzes():
    db_sess = db_session.create_session()

    quizzes = db_sess.query(Quiz).all()

    for quiz in quizzes:
        if not quiz.questions:
            del_quiz(quiz.id)

    db_sess.commit()
    db_sess.close()