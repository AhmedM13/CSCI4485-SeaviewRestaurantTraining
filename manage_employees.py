# Author(s): Pranjal Singh, Parth Patel, Ahmed Malik
# This file contains the code that is used to manage employee accounts,
# such as being able to register new employees.

import re
import smtplib
import sqlite3
import ssl

from flask import Flask, render_template, redirect, url_for, session, request

import credentials
import database
from routes import website


@website.route('/register_employee')
def register_employee():

    cursor = database.conn.cursor()

    cursor.execute('SELECT * FROM Roles ')
    roles = cursor.fetchall()

    cursor.execute('SELECT ID, FIRST_NAME, LAST_NAME '
                   'FROM USERS '
                   'WHERE ROLE_ID = 1 ')
    managers = cursor.fetchall()
    print(managers)

    return render_template('register_employee.html', managers=managers)

@website.route('/manage_employee')
def manage_employee():
    cursor = database.conn.cursor()

    cursor.execute('SELECT u.ID, u.USERNAME, u.FIRST_NAME || \' \' || u.LAST_NAME, u.EMAIL, r.ROLE_NAME, u.MANAGER_ID, m.FIRST_NAME || \' \' || m.LAST_NAME '
                   'FROM Users u JOIN Roles r ON u.ROLE_ID = r.ID LEFT JOIN Users m  ON u.MANAGER_ID = m.ID')
    users = cursor.fetchall()



    return render_template('manage_employee.html', users = users)


@website.route('/registration', methods=['GET', 'POST'])
def registration():
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form\
    and 'first_name' in request.form and 'last_name' in request.form and 'role_id' in request.form and 'manager' in request.form\
    and 'confirm_password' in request.form and request.form['manager'] != '0':
        # Create variables for easy access
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role_id = request.form['role_id']
        manager_id = request.form['manager']
        confirm_pass = request.form['confirm_password']
        print(role_id)
        print(manager_id)
        print(type(manager_id))
        isRestricted = 0

        cursor = database.conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Username=?', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        elif password != confirm_pass:
            msg = 'Passwords do not match!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO Users (username, first_name, last_name, password, email, role_id, IsRestricted, manager_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (username, first_name, last_name, password, email, role_id, isRestricted,manager_id))
            database.conn.commit()
            msg = 'You have successfully registered!'

            cursor.execute(
                'SELECT u.ID, u.USERNAME, u.FIRST_NAME || \' \' || u.LAST_NAME, u.EMAIL, r.ROLE_NAME, u.MANAGER_ID, m.FIRST_NAME || \' \' || m.LAST_NAME '
                'FROM Users u JOIN Roles r ON u.ROLE_ID = r.ID LEFT JOIN Users m  ON u.MANAGER_ID = m.ID')
            users = cursor.fetchall()



            return render_template('manage_employee.html', users=users)


    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    print(msg)
    cursor.execute('SELECT ID, FIRST_NAME, LAST_NAME '
                   'FROM USERS '
                   'WHERE ROLE_ID = 1 ')
    managers = cursor.fetchall()
    return render_template('register_employee.html', msg=msg, managers=managers)

def delete_item(item_id):
    cursor = database.conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id=?", (item_id,))
    database.conn.commit()

@website.route('/delete/<int:item_id>', methods=['GET'])
def delete_route(item_id):
    delete_item(item_id)
    return redirect(url_for('manage_employee'))

@website.route('/restrict/<int:item_id>', methods=['GET'])
def restrict_route(item_id):
    restrict_account(item_id)
    return redirect(url_for('manage_employee'))

def restrict_account(item_id):
    with sqlite3.connect('./Seaview_DB.db') as conn:
        cursor = conn.cursor()
        value = 1
        cursor.execute("UPDATE Users SET IsRestricted = ? WHERE id = ?", (value, item_id,))
        conn.commit()

@website.route('/edit_employee/<int:item_id>', methods=['GET', 'POST'])
def edit_employee(item_id):
    cursor = database.conn.cursor()
    # If it's a POST request, update the role
    if request.method == 'POST':
        new_role_id = request.form.get('role')
        new_manager_id = request.form.get('manager')
        if new_manager_id == 'None':
            new_manager_id = None
        cursor.execute("UPDATE Users SET ROLE_ID = ?, MANAGER_ID = ? WHERE ID = ?", (new_role_id, new_manager_id, item_id))

        database.conn.commit()
        print(new_role_id)
        if new_role_id == '1':
            return redirect(url_for('manage_employee'))
        else:
            return redirect(url_for('authenticate_user'))

    # For a GET request, show the edit form with current role
    cursor.execute('SELECT DISTINCT u.ROLE_ID, r.ROLE_NAME '
                   'FROM USERS u JOIN ROLES r ON u.ROLE_ID = r.ID '
                   'WHERE ROLE_ID IN '
                   '    (SELECT ROLE_ID '
                   '    FROM USERS '
                   '    WHERE ID = ?) ', (item_id,))

    curr_role = cursor.fetchone()

    cursor.execute('SELECT DISTINCT u.ROLE_ID, r.ROLE_NAME '
                   'FROM USERS u JOIN ROLES r ON u.ROLE_ID = r.ID '
                   'WHERE ROLE_ID NOT IN'
                   '    (SELECT ROLE_ID'
                   '    FROM USERS'
                   '    WHERE ID = ?) ', (item_id,))

    other_role = cursor.fetchone()

    roles = []
    roles.append(curr_role)
    roles.append(other_role)


    you = None
    if session['role'] == 1:
        cursor.execute('SELECT ID, FIRST_NAME || \' \' || LAST_NAME AS NAME '
                       'FROM USERS '
                       'WHERE ID = ?', (item_id,))
        you = cursor.fetchone()

    cursor.execute('SELECT ID, FIRST_NAME || \' \' || LAST_NAME AS NAME '
                   'FROM USERS '
                   'WHERE ROLE_ID = 1')
    query = cursor.fetchall()
    managers = query
    managers.append((None, None))


    cursor.execute('SELECT e.MANAGER_ID, m.FIRST_NAME || \' \' || m.LAST_NAME AS NAME '
                   'FROM USERS e JOIN USERS m ON e.MANAGER_ID = m.ID '
                   'WHERE e.ID = ? ', (item_id,))
    curr_manager = cursor.fetchone()

    if curr_manager is None:
        curr_manager = (None, None)

    if curr_manager in managers:
        managers.remove(curr_manager)

    if you is not None and you in managers:
        managers.remove(you)

    managers.insert(0,curr_manager)




    return render_template('edit_employee.html', curr_role_id=curr_role[0], curr_manager_id=curr_manager[0], roles=roles, managers=managers, user_id=item_id)

