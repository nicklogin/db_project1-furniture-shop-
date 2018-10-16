from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime as dt
# from dbmanager import write_data
import sqlite3


def write_data(form_data):
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    customer_id = cursor.execute('''select count(id) from customer''').fetchall()[0][0]
    purchase_id = cursor.execute('''select count(id) from purchase''').fetchall()[0][0]
    complaint_id = cursor.execute('''select count(id) from complaint''').fetchall()[0][0]
    # insert into customer
    cursor.execute(f'''INSERT INTO customer VALUES
    ('{customer_id}','{form_data['name']}','{form_data['surname']}','{form_data['patername']}',
    '{form_data['prefix'] + form_data['number']}','{form_data['email']}')''')
    # insert into purchase
    try:
        datetime = dt.strptime(form_data['datetime'],r"%Y-%m-%dT%H:%M")
        date = str(datetime.date())
        time = str(datetime.time())
    except ValueError:
        date = None
        time =None
    item_id = get_id(form_data['item-name'])
    cursor.execute("INSERT INTO purchase VALUES (?,?,?,?,?)",
    (purchase_id, item_id, customer_id, time, date))
    # insert into complaint
    cursor.execute(f'''INSERT INTO complaint VALUES
    ('{complaint_id}','{form_data["complaint_text"]}',
    '{item_id}','{purchase_id}') ''')
    connection.commit()
    connection.close()


def get_id(item_name):
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    item_id = cursor.execute(f"SELECT id FROM item WHERE name = '{item_name}'").fetchall()[0][0]
    connection.close()
    return item_id


def get_item_names():
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    item_names = [i[0] for i in cursor.execute("SELECT name FROM item").fetchall()]
    connection.close()
    return item_names


def get_table_options():
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    table_names = [i[0] for i in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    connection.close()
    return table_names


def get_col_names(table_name):
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    col_names = [i[1] for i in cursor.execute(f'PRAGMA table_info({table_name})').fetchall()]
    connection.close()
    return col_names


def get_table_data(table_name):
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    table_data = cursor.execute(f"SELECT * FROM '{table_name}'").fetchall()
    connection.close()
    return table_data


def delete_row(table_name, row_id):
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM '{table_name}' WHERE id='{row_id}';")
    connection.commit()
    connection.close()


def get_id_column(table_name):
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    outp = [i[0] for i in cursor.execute(f"SELECT id FROM '{table_name}'").fetchall()]
    connection.close()
    return outp


def get_row(table_name, row_id):
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    row = cursor.execute(f"SELECT * FROM '{table_name}' WHERE id='{row_id}';").fetchall()[0]
    connection.close()
    col_names = get_col_names(table_name)
    outp = dict()
    for index, col_name in enumerate(col_names):
        if col_name.endswith('_id'):
            outp[col_name] = (row[index], get_id_column(col_name[:-3]))
        else:
            outp[col_name] = (row[index], None)
    return outp


def get_table_as_markup(table_name):
    table_data = get_table_data(table_name)
    col_names = get_col_names(table_name)
    return render_template('response.html', selected_table = table_data,
    col_names = col_names)


def commit_changes(new_dict):
    table_name = new_dict.pop('table')
    rowId = new_dict.pop('id')
    setting = ""
    for key, val in new_dict.items():
        setting += f"{key} = '" + val + "', "
    setting = setting.strip(', ')
    connection = sqlite3.connect('complaint.db')
    cursor = connection.cursor()
    query = f"UPDATE {table_name} SET " + setting + "WHERE id = " + rowId + ";"
    cursor.execute(query)
    connection.commit()
    connection.close()

app = Flask(__name__)


@app.route('/', methods = ['GET','POST'])
def display_form():
    if request.form:
        print(request.form)
        write_data(request.form)
        return render_template("thank_you.html")
    else:
        return render_template("form.html", item_name_options = get_item_names())

@app.route('/adminpage', methods = ['GET'])
def show_admin_page():
    if request.method == 'GET' and request.args:
        if request.args['action'] == 'getTable':
            tablename = request.args['table']
            return get_table_as_markup(tablename)
        elif request.args['action'] == 'deleteRow':
            tablename = request.args['table']
            row_id = request.args['id']
            delete_row(tablename, row_id)
            return "success"

    return render_template("adminpage.html", table_options = get_table_options(), col_names = get_col_names('item'),
    selected_table = get_table_data('item'))

@app.route('/changeData', methods = ['GET','POST'])
def change_data():
    if request.method == 'GET' and request.args:
        if request.args['action'] == 'openEditor':
            tablename = request.args['table']
            row_id = request.args['id']
            row_data = get_row(tablename, row_id)
            row_data.pop('id')
            return render_template("changeData.html", row_data = row_data,
            table_name = tablename, row_id = row_id)
    elif request.method == 'POST' and request.form:
        form = {key: request.form[key] for key in request.form}
        if form['action'] == 'commitChanges':
            tablename = form['table']
            row_id = form['id']
            form.pop('action')
            commit_changes(form)
            return 'success'
    elif request.method == 'GET':
        return "no table and row selected"


if __name__ == '__main__':
    app.run(debug=True)