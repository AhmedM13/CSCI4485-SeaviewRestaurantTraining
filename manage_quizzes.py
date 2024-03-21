# Author(s): Ryan Minneo, Ryan Nguyen
# This file contains the code that is used to manage quizzes,
# such as being able to register new quizzes, edit existing quizzes, and delete quizzes if need be.

import re
from flask import Flask, render_template, redirect, url_for, session, request
import database
from __main__ import website

@website.route('/manage_quizzes')
def manage_quizzes():
    cursor = database.conn.cursor()

    cursor.execute('SELECT * FROM QUIZZES')
    quizzes = cursor.fetchall()
    return render_template('manage_quizzes.html', quizzes = quizzes)

#Routes quiz list to the quiz editor
@website.route('/quiz_editor')
def quiz_editor():
    cursor = database.conn.cursor()
    return render_template('quiz_editor.html')

@website.route('/quiz_editing', methods=['GET', 'POST'])
def quiz_editing():
    count = 0
    file_data = None  # Define file_data variable outside the conditional block
    # Check if the quiz name, quiz description, and material name is inputted into their text boxes.
    if request.method == 'POST' and 'quiz_name' in request.form and 'quiz_desc' in request.form and 'material_name' in request.form:
        # Retrieve data from the HTML form
        quiz_name = request.form['quiz_name']
        quiz_desc = request.form['quiz_desc']
        material_name = request.form['material_name']

        # Retrieve questions and answers dynamically
        questions = []
        for key, value in request.form.items():
            if key.startswith('question'):
                question_number = key.replace('question', '')
                question = {
                    'QUESTION': value,
                    'ANSWER_A': request.form[f'option{question_number}A'],
                    'ANSWER_B': request.form[f'option{question_number}B'],
                    'ANSWER_C': request.form[f'option{question_number}C'],
                    'ANSWER_D': request.form[f'option{question_number}D'],
                    'CORRECT_ANSWER': request.form[f'correctAnswer{question_number}']
                }
                count = count + 1
                questions.append(question)

        cursor = database.conn.cursor()

        cursor.execute('INSERT INTO QUIZZES (QUIZ_NAME, TOTAL_QUESTIONS, EMPLOYER_ID, TOTAL_CORRECT, TOTAL_INCORRECT, IS_VISIBLE, QUIZ_DESC) VALUES (?, ?, ?, ?, ?, ?, ?)', (quiz_name, count, 1, 0, 0, 1, quiz_desc))

        #for question in questions:
        #    cursor.execute('''INSERT INTO QUESTIONS (QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER)
        #                          VALUES (?, ?, ?, ?, ?, ?)''',
        #                   (question['QUESTION'], question['ANSWER_A'], question['ANSWER_B'],
         #                   question['ANSWER_C'], question['ANSWER_D'], question['CORRECT_ANSWER']))

        # Retrieve data for pdf images
        # Handle file upload
        if request.method == 'POST':
            # Check if the file is present in the request
            if 'file' in request.files:
                file = request.files['file']
                file_data = file.read() # Assign value to file_data variable if 'file' is present
                if file_data is not None:
                    cursor.execute('INSERT INTO TRAINING_MATERIALS (MATERIAL_NAME, MATERIAL_BYTES) VALUES (?, ?)',(material_name, file_data))



        # Commit changes to the database
        database.conn.commit()

    return render_template('manage_quizzes.html')

