from data import db_session
from data.models.questions import Question
from data.quiz_func import update_quiz, get_quiz


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

    # UPDATE QUIZ
    quiz = get_quiz(quiz_id)
    quiz.questions.append(question.id)
    update_quiz(quiz_id, questions=quiz.questions)

    db_sess.commit()

    try:
        return question.id
    finally:
        db_sess.close()


def get_question(question_id):
    db_sess = db_session.create_session()

    question = \
        db_sess.query(Question).filter(Question.id == question_id).first()

    try:
        return question
    finally:
        db_sess.close()


def del_question(question_id):
    db_sess = db_session.create_session()

    question = \
        db_sess.query(Question).filter(Question.id == question_id).first()

    quiz_id = question.quiz_id

    db_sess.query(Question).filter(Question.id == question_id).delete()

    # UPDATE QUIZ
    quiz = get_quiz(quiz_id)
    del quiz.questions[quiz.questions.index(question_id)]
    update_quiz(quiz_id, questions=quiz.questions)

    db_sess.commit()
    db_sess.close()


def update_question(question_id, text=None, explanation=None, answers=None,
                    right_answer=None, media=None):
    db_sess = db_session.create_session()

    question = \
        db_sess.query(Question).filter(Question.id == question_id).first()

    if text:
        if text == '_':
            pass
        else:
            question.text = text

    if explanation is not None:
        if explanation == '':
            question.explanation = None
        elif explanation == '_':
            pass
        else:
            question.explanation = explanation

    if answers:
        if answers == '_':
            pass
        else:
            question.answers = answers

    if right_answer is not None:
        if answers == '_':
            pass
        else:
            question.right_answer = right_answer

    if media is not None:
        if media == '':
            question.media = None
        elif media == '_':
            pass
        else:
            question.media = media

    db_sess.commit()
    db_sess.close()
