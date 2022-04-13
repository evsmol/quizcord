from data import db_session
from data.models.questions import Question
from data.models.quizzes import Quiz


def add_question(quiz_id):
    question = Question()
    question.quiz_id = quiz_id
    question.text = None
    question.explanation = None
    question.answers = []
    question.right_answer = None
    question.media = None

    db_sess = db_session.create_session()
    db_sess.add(question)
    db_sess.flush()
    db_sess.refresh(question)

    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    quiz.questions.append(question.id)

    db_sess.commit()
    return question.id


def get_question(question_id):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id ==
                                              question_id).first()
    return question


def del_question(question_id):
    db_sess = db_session.create_session()
    db_sess.query(Question).filter(Question.id == question_id).delete()
    db_sess.commit()


def update_question(question_id, text=None, explanation=None, answers=None,
                    right_answer=None, media=None):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id ==
                                              question_id).first()
    if text:
        question.text = text
    if explanation:
        question.explanation = explanation
    if answers:
        question.answers = answers
    if right_answer:
        question.right_answer = right_answer
    if media:
        question.media = media
    db_sess.commit()