from data import db_session
from data.models.quizzes import Quiz
from data.models.questions import Question


def add_quiz(author_id, server_id=None):
    quiz = Quiz()

    quiz.title = None
    quiz.description = None
    quiz.server_id = server_id
    quiz.author_id = author_id
    quiz.players = {}
    quiz.questions = []

    db_sess = db_session.create_session()

    db_sess.add(quiz)
    db_sess.flush()
    db_sess.refresh(quiz)

    db_sess.commit()

    try:
        return quiz.id
    finally:
        db_sess.close()


def get_quiz(quiz_id):
    db_sess = db_session.create_session()

    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()

    try:
        return quiz
    finally:
        db_sess.close()


def get_server_quizzes(server_id):
    db_sess = db_session.create_session()

    quizzes = db_sess.query(Quiz).filter(
        Quiz.server_id == server_id,
        Quiz.publication == True
    ).order_by(Quiz.id).all()

    try:
        return quizzes
    finally:
        db_sess.close()


def get_user_quizzes(user_id, server_id=None):
    db_sess = db_session.create_session()

    if server_id:
        quizzes = db_sess.query(Quiz).filter(
            Quiz.author_id == user_id, Quiz.server_id ==
            server_id
        ).order_by(Quiz.id).all()

    else:
        quizzes = db_sess.query(Quiz).filter(
            Quiz.author_id == user_id
        ).order_by(Quiz.id).all()

    try:
        return quizzes
    finally:
        db_sess.close()


def get_quiz_questions(quiz_id):
    db_sess = db_session.create_session()

    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    questions_id = quiz.questions

    questions = []
    for question_id in questions_id:
        question = \
            db_sess.query(Question).filter(Question.id == question_id).first()
        questions.append(question)

    try:
        return questions
    finally:
        db_sess.close()


def del_quiz(quiz_id):
    db_sess = db_session.create_session()

    db_sess.query(Quiz).filter(Quiz.id == quiz_id).delete()
    db_sess.query(Question).filter(Question.quiz_id == quiz_id).delete()

    db_sess.commit()
    db_sess.close()


def update_quiz(quiz_id, title=None, description=None, server_id=None,
                players=None, publication=None, questions=None):
    db_sess = db_session.create_session()

    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()

    if title:
        if title == '_':
            pass
        else:
            quiz.title = title

    if description is not None:
        if description == '':
            quiz.description = None
        elif description == '_':
            pass
        else:
            quiz.description = description

    if server_id:
        quiz.server_id = server_id

    if players:
        quiz.players = players

    if publication is not None:
        quiz.publication = publication

    if questions:
        quiz.questions = questions

    db_sess.commit()
    db_sess.close()


def check_quiz_for_publication(quiz_id):
    db_sess = db_session.create_session()

    resolution = True

    quiz = db_sess.query(Quiz).filter(Quiz.id == quiz_id).first()
    questions = quiz.questions

    for question_id in questions:
        question = db_sess.query(Question).filter(
            Question.id == question_id
        ).first()

        if question.answers:
            continue
        else:
            resolution = False
            break

    db_sess.close()

    return resolution
