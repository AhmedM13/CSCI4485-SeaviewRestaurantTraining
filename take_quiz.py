# Author(s): Ryan Minneo, Ryan Nguyen
# This file contains the code that allows the employees to take quizzes

from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website


@website.route('/take_quiz', methods=['GET'])
def take_quiz():
    quiz_id = request.args.get('id')
    # Connect to SQLite database
    cursor = database.conn.cursor()

    # Fetch questions from the database  --------------------------------- This quiz_id is undefined, fetch from the url.
    cursor.execute("SELECT QUESTION_ID, QUESTION FROM QUESTIONS WHERE QUIZ_ID = ?", quiz_id)
    questions = []
    for row in cursor.fetchall():
        question_id, question = row
        cursor.execute("SELECT ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUESTION_ID = ?", (question_id))
        answers = [{'answer_a': ANSWER_A, 'answer_b': ANSWER_B, 'answer_c': ANSWER_C, 'answer_d': ANSWER_D, 'correct_answer': CORRECT_ANSWER}
                   for ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER in cursor.fetchall()]
        questions.append({'id': question_id, 'question_text': question, 'options': answers})

    cursor.close()

    return render_template('take_quiz.html', questions=questions)