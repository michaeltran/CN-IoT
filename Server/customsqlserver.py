#!/usr/bin/env python

# pylint: disable=C0111,C0301,C0325

import pyodbc

# SQL SERVER INITIALIZATION

def get_connection():
    conn = pyodbc.connect("Driver={SQL Server};"
                      "Server=34.238.10.240;"
                      "Database=FACEDB;"
                      "UID=sa;"
                      "PWD=password1234;")
    return conn

def get_face_data_sql(person_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql_command = "SELECT [ID], [FIRST_NAME], [LAST_NAME], [MIN_DISTANCE], [MAX_DISTANCE] FROM [PERSON] WHERE [ID] = '%s'" % person_id
        cursor.execute(sql_command)
        row = cursor.fetchone()
        return row
    except Exception as e:
        print e
    finally: 
        cursor.close()
        conn.close()

def add_person_sql(first_name, last_name, min_distance, max_distance):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql_command = "EXEC [dbo].[PR_ADD_PERSON] '%s', '%s', '%s', '%s'" % (first_name, last_name, min_distance, max_distance)
        cursor.execute(sql_command)
        conn.commit()
        sql_command = "SELECT [ID] FROM [PERSON] WHERE [FIRST_NAME] = '%s' AND [LAST_NAME] = '%s'" % (first_name, last_name)
        cursor.execute(sql_command)
        row = cursor.fetchone()
        return row
    except Exception as e:
        print e
    finally: 
        cursor.close()
        conn.close()
