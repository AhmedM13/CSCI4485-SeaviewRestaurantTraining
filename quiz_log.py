# Author(s): Parth Patel, Ahmed Malik
# This file contains the code that is used to view the quiz history log,


import re
from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website

@website.route('/quiz_log', methods=['GET', 'POST'])
def quiz_log():
    cursor = database.conn.cursor()
    sort_by = request.args.get('sort', 'CHANGE_ID')
    order = request.args.get('order', 'asc')

    cursor.execute(f"SELECT log.CHANGE_ID, log.EMPLOYEE_ID, u.FIRST_NAME, u.LAST_NAME, q.QUIZ_ID, q.QUIZ_NAME, log.DATE_TIME, log.ACTION_TYPE "
                   f"FROM QUIZ_HISTORY_LOG log, QUIZZES q, USERS u "
                   f"WHERE log.QUIZ_ID = q.QUIZ_ID AND log.EMPLOYEE_ID = u.ID "
                   f"ORDER BY {sort_by} {order}")
    history_logs = cursor.fetchall()
    return render_template('quiz_log.html', history_logs=history_logs, sort_by=sort_by, order=order)
