from transitions import Machine


class QuizDetector(object):
    states = [
        'quiz_set_server'
        
        'quiz_edit', 'quiz_set_title', 'quiz_set_description',

        'question_select', 'question_edit', 'question_set_text',
        'question_set_explanation', 'question_set_media',
        'question_set_answers'
    ]

    def __init__(self, quiz_id=None, question_id=None):
        self.quiz_id = quiz_id
        self.question_id = question_id

        self.machine = Machine(model=self, states=QuizDetector.states,
                               initial='quiz_edit')

        self.machine.add_transition(trigger='edit_quiz_server',
                                    source='quiz_set_server',
                                    dest='quiz_edit')

        self.machine.add_transition(trigger='edit_quiz_title',
                                    source='quiz_edit',
                                    dest='quiz_set_title')
        self.machine.add_transition(trigger='edit_quiz_title',
                                    source='quiz_set_title',
                                    dest='quiz_edit')

        self.machine.add_transition(trigger='edit_quiz_description',
                                    source='quiz_edit',
                                    dest='quiz_set_description')
        self.machine.add_transition(trigger='edit_quiz_description',
                                    source='quiz_set_description',
                                    dest='quiz_edit')

        self.machine.add_transition(trigger='select_question',
                                    source='quiz_edit',
                                    dest='question_select')
        self.machine.add_transition(trigger='select_question_left',
                                    source='question_select',
                                    dest='question_select')
        self.machine.add_transition(trigger='select_question_right',
                                    source='question_select',
                                    dest='question_select')
        self.machine.add_transition(trigger='select_question_return',
                                    source='question_select',
                                    dest='quiz_edit')

        self.machine.add_transition(trigger='edit_question',
                                    source='question_select',
                                    dest='question_edit')
        self.machine.add_transition(trigger='edit_question_up',
                                    source='question_edit',
                                    dest='question_edit')
        self.machine.add_transition(trigger='edit_question_down',
                                    source='question_edit',
                                    dest='question_edit')

        self.machine.add_transition(trigger='edit_question_delete',
                                    source='question_edit',
                                    dest='question_select')
        self.machine.add_transition(trigger='edit_question_return',
                                    source='question_edit',
                                    dest='question_select')

        self.machine.add_transition(trigger='edit_question_text',
                                    source='question_edit',
                                    dest='question_set_text')
        self.machine.add_transition(trigger='edit_question_text',
                                    source='question_set_text',
                                    dest='question_edit')

        self.machine.add_transition(trigger='edit_question_explanation',
                                    source='question_edit',
                                    dest='question_set_explanation')
        self.machine.add_transition(trigger='edit_question_explanation',
                                    source='question_set_explanation',
                                    dest='question_edit')

        self.machine.add_transition(trigger='edit_question_media',
                                    source='question_edit',
                                    dest='question_set_media')
        self.machine.add_transition(trigger='edit_question_media',
                                    source='question_set_media',
                                    dest='question_edit')

        self.machine.add_transition(trigger='edit_question_answers',
                                    source='question_edit',
                                    dest='question_set_answers')
        self.machine.add_transition(trigger='edit_question_answers',
                                    source='question_set_answers',
                                    dest='question_edit')