import os
import re
from datetime import datetime, date
from email.mime.application import MIMEApplication

from flask import Flask, render_template, redirect, url_for, session, request, make_response
import database
from routes import website
import pdfkit

def generate_certificate():
    cursor = database.conn.cursor()
    cursor.execute('SELECT MAX(ATTEMPT_NUMBER), QUIZ_ID, IS_COMPLETED '
                   'FROM ATTEMPT_HISTORY_LOG '
                   'WHERE EMPLOYEE_ID = ? AND QUIZ_ID IN ('
                   '    SELECT QUIZ_ID'
                   '    FROM QUIZZES'
                   '    WHERE IS_DELETED = 0)'
                   'GROUP BY QUIZ_ID ', (session['id'],))
    query = cursor.fetchall()
    complete = False
    for result in query:
        if result[2] == 1:
            complete = True
        else:
            complete = False
            break
    num_completed = len(query)
    cursor.execute('SELECT QUIZ_ID FROM QUIZZES WHERE IS_DELETED=0 ')
    query = cursor.fetchall()
    num_quizzes = len(query)
    if complete and num_completed == num_quizzes:
        complete = True
    else:
        complete = False

    if complete:
        cursor.execute('UPDATE USERS SET IS_COMPLETED = ? WHERE ID = ? ', (1, session['id']))
        database.conn.commit()

        cursor.execute('SELECT First_Name, Last_Name FROM Users WHERE Username=? AND Password=?', (session['username'], session['password'],))

        user_profile = cursor.fetchone()
        certificate = render_template('certificate.html', user_profile=user_profile, date=date.today())
        cert_pdf = pdfkit.from_string(certificate, False)

        with open('certificate.pdf', 'wb') as f:
            f.write(cert_pdf)

        send_certificate()


import smtplib
import ssl
import credentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def send_certificate():

    cursor = database.conn.cursor()

    cursor.execute('SELECT FIRST_NAME, LAST_NAME, EMAIL '
                   'FROM USERS '
                   'WHERE ID = ? ', (session['id'],))
    first_name, last_name, email = cursor.fetchone()

    port = 587
    smtp_server = "smtp.office365.com"
    sender_email = credentials.email
    receiver_email = email
    password = credentials.password



    # Create the email message
    message = MIMEMultipart()
    message["Subject"] = f"Certificate of Completion for {first_name} {last_name}"
    message["From"] = sender_email
    message["To"] = receiver_email



    with open('certificate.pdf', 'rb') as pdf:
        cert_pdf = MIMEApplication(pdf.read(), _subtype='pdf')
        cert_pdf.add_header('Content-Disposition', 'attachment', filename='certificate.pdf')
        message.attach(cert_pdf)


    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)

    os.remove('certificate.pdf')
    print("Certificate sent successfully")