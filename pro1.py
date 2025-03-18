import streamlit as st_app
import mysql.connector as sql_connector
import pandas as pd_app
import os


def establish_connection():
    return sql_connector.connect(
        host="127.0.0.1",
        user="root",
        password=os.getenv("DB_PASS", "anushks"),
        database="taskdb",
        auth_plugin="mysql_native_password"
    )


def initialize_database():
    connection = establish_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_table (
            task_id INT AUTO_INCREMENT PRIMARY KEY,
            task_description VARCHAR(255) NOT NULL,
            task_due DATE NOT NULL
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()


def execute_db_command(command, parameters=None, fetch=False):
    connection = establish_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if parameters:
            cursor.execute(command, parameters)
        else:
            cursor.execute(command)
        if fetch:
            results = cursor.fetchall()
        else:
            connection.commit()
            results = None
    except sql_connector.Error as db_error:
        st_app.error(f"Database error encountered: {db_error}")
        results = None
    finally:
        cursor.close()
        connection.close()
    return results


initialize_database()

st_app.title("📝 Task Management System")
option = st_app.sidebar.selectbox("Navigation", ["Add Task", "View Tasks", "Edit Task", "Remove Task"])

if option == "Add Task":
    st_app.subheader("Add a New Task")
    task_input = st_app.text_input("Task Description")
    task_date = st_app.date_input("Due Date")
    add_btn = st_app.button("Add")
    if add_btn:
        if not task_input.strip():
            st_app.warning("Task description is required!")
        else:
            execute_db_command("INSERT INTO task_table (task_description, task_due) VALUES (%s, %s)", (task_input, task_date))
            st_app.success("Task has been successfully added!")

elif option == "View Tasks":
    st_app.subheader("Task Overview")
    task_records = execute_db_command("SELECT * FROM task_table", fetch=True)
    if task_records:
        task_df = pd_app.DataFrame(task_records)
        st_app.write(task_df)
    else:
        st_app.info("No tasks available to display!")

elif option == "Edit Task":
    st_app.subheader("Update Existing Task")
    task_records = execute_db_command("SELECT * FROM task_table", fetch=True)
    if task_records:
        task_df = pd_app.DataFrame(task_records)
        st_app.write(task_df)
        task_id = st_app.number_input("Task ID", min_value=1, step=1)
        updated_description = st_app.text_input("New Description")
        updated_date = st_app.date_input("New Due Date")
        update_btn = st_app.button("Update Task")
        if update_btn:
            if not updated_description.strip():
                st_app.warning("Description cannot be empty!")
            else:
                execute_db_command("UPDATE task_table SET task_description = %s, task_due = %s WHERE task_id = %s", (updated_description, updated_date, task_id))
                st_app.success("Task updated successfully!")
    else:
        st_app.info("No tasks found for updating!")

elif option == "Remove Task":
    st_app.subheader("Delete a Task")
    task_records = execute_db_command("SELECT * FROM task_table", fetch=True)
    if task_records:
        task_df = pd_app.DataFrame(task_records)
        st_app.write(task_df)
        task_id = st_app.number_input("Task ID to Remove", min_value=1, step=1)
        delete_btn = st_app.button("Delete")
        delete_all_btn = st_app.button("Delete All")
        if delete_btn:
            execute_db_command("DELETE FROM task_table WHERE task_id = %s", (task_id,))
            st_app.success("Task has been removed!")
        if delete_all_btn:
            confirm_delete = st_app.checkbox("Confirm removal of all tasks")
            if confirm_delete:
                execute_db_command("DELETE FROM task_table")
                st_app.success("All tasks have been deleted!")
    else:
        st_app.info("No tasks to remove!")
