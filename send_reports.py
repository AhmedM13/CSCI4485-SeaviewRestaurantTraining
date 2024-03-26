# Author(s): Parth Patel

import datetime
import os
from datetime import date
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
from flask import Flask, render_template, redirect, url_for, session, request
from matplotlib import pyplot as plt

import database, smtplib, ssl, credentials, datetime
from routes import website


# This is for after you submit a quiz
def send_report():
    pass

# This is for the manager dashboard
@website.route('/progress_report/<int:user_id>', methods=['GET'])
def send_report(user_id):
    cursor = database.conn.cursor()
    cursor.execute('SELECT m.EMAIL FROM USERS u LEFT JOIN USERS m on u.MANAGER_ID = m.ID WHERE u.ID=? ',(user_id,))
    manager_email = cursor.fetchone()[0]

    create_double_bar_graph(user_id)




    if manager_email is not None:

        subject="Test Report"
        body="Testing"
        send_mail(subject,body,manager_email)
    return redirect('/manage_employee')

def create_double_bar_graph(user_id):
    cursor = database.conn.cursor()
    query = cursor.fetchall()

    cursor.execute('SELECT FIRST_NAME, LAST_NAME FROM USERS WHERE ID=?',(user_id,))
    query = cursor.fetchone()

    name = "".join(f"{query[0]} {query[1]}")

    cursor.execute('SELECT QUIZ_NAME, NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) FROM ATTEMPT_HISTORY_LOG ah '
                   'RIGHT JOIN QUIZZES q ON ah.QUIZ_ID = q.QUIZ_ID '
                   'WHERE EMPLOYEE_ID=?'
                   'GROUP BY q.QUIZ_ID ', (user_id,))
    query = cursor.fetchall()
    correct = []
    incorrect = []
    quiz_names = []
    if query is not None:
        for row in query:
            correct.append(row[1])
            incorrect.append(row[2])
            quiz_names.append(row[0])

    bar_width = 0.25
    x = np.arange(len(quiz_names))

    plt.bar(x - bar_width / 2, correct, bar_width, label='Correct')
    plt.bar(x + bar_width / 2, incorrect, bar_width, label='Incorrect')

    plt.xlabel('Quizzes')
    plt.ylabel('Num Of Answers')
    plt.title(f"{name}'s Quiz Progress")
    plt.xticks(x, quiz_names)
    plt.legend()

    plt.savefig(f'Quiz_Progress.png')

    plt.close()







# This one is used for the report function
def send_mail(subject, body, recipient_email):

    port = 587
    smtp_server = "smtp.office365.com"
    sender_email = credentials.email
    password = credentials.password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject


    with open('Quiz_Progress.png', 'rb') as attachment_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='Quiz_Progress.png')
        message.attach(part)

    message.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)

    os.remove('Quiz_Progress.png')
    print("Email sent successfully")


