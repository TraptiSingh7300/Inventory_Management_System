from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import pymysql
from datetime import date


def connect_database():
    try:
        conn = pymysql.connect(host='localhost', user='root', password='singh')
        cursor = conn.cursor()
    except Exception as  e:
        messagebox.showerror('Error', f'Error due to {e}')
        return None, None

    return cursor, conn


def create_database_table():
    cursor, conn = connect_database()
    cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_system')
    cursor.execute('USE inventory_system')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS employee_data (emp_id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), gender VARCHAR(50), dob VARCHAR(30), contact VARCHAR(30), employment_type VARCHAR(50), education VARCHAR(50), work_shift VARCHAR(50), address VARCHAR(100), doj VARCHAR(30), salary VARCHAR(50), usertype VARCHAR(50), password VARCHAR(50))')


def treeview_data():
    cursor, conn = connect_database()
    if not cursor or not conn:
        return
    cursor.execute('USE inventory_system')
    try:
        cursor.execute('SELECT * FROM employee_data')
        employee_records = cursor.fetchall()
        employee_treeview.delete(*employee_treeview.get_children())
        for record in employee_records:
            employee_treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        cursor.close()
        conn.close()


def select_data(event, empid_entry, name_entry, email_entry, dob_entry, gender_combobox,
                contact_entry, employment_type_combobox, education_combobox,
                work_shift_combobox, address_entry, doj_entry, salary_entry,
                usertype_combobox, password_entry):
    index = employee_treeview.selection()
    content = employee_treeview.item(index)
    row = content['values']
    clear_fields(empid_entry, name_entry, email_entry, dob_entry, gender_combobox,
                 contact_entry, employment_type_combobox, education_combobox,
                 work_shift_combobox, address_entry, doj_entry, salary_entry,
                 usertype_combobox, password_entry, False)
    empid_entry.insert(0, row[0])
    name_entry.insert(0, row[1])
    email_entry.insert(0, row[2])
    gender_combobox.set(row[3])
    dob_entry.set_date(row[4])
    contact_entry.insert(0, row[5])
    employment_type_combobox.set(row[6])
    education_combobox.set(row[7])
    work_shift_combobox.set(row[8])
    address_entry.insert(1.0, row[9])
    doj_entry.set_date(row[10])
    salary_entry.insert(0, row[11])
    usertype_combobox.set(row[12])
    password_entry.insert(0, row[13])


def add_employee(empid, name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary,
                 usertype, password):
    if (
            empid == '' or name == '' or email == '' or gender == 'Select' or contact == '' or employment_type == 'Select' or education == 'Select' or work_shift == 'Select' or address == '\n' or salary == '' or usertype == 'Select' or password == ''):
        messagebox.showerror('Error', 'All fields are required')
    else:
        cursor, conn = connect_database()
        if not cursor or not conn:
            return
        cursor.execute('USE inventory_system')
        try:
            cursor.execute('SELECT emp_id from employee_data WHERE emp_id=%s', (empid,))
            if cursor.fetchone():
                messagebox.showerror('Error', 'Id already exists')
                return
            address=address.strip()
            cursor.execute('INSERT INTO employee_data VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                           (empid, name, email, gender, dob, contact, employment_type, education, work_shift, address,
                            doj,
                            salary,
                            usertype, password))
            conn.commit()
            treeview_data()
            messagebox.showinfo('Success', 'Data is inserted successfully')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            conn.close()


def clear_fields(empid_entry, name_entry, email_entry, dob_entry, gender_combobox, contact_entry,
                 employment_type_combobox, education_combobox, work_shift_combobox, address_entry, doj_entry,
                 salary_entry, usertype_combobox, password_entry, check):
    empid_entry.delete(0, END)
    name_entry.delete(0, END)
    email_entry.delete(0, END)
    dob_entry.set_date(date.today())
    gender_combobox.set('Select')
    contact_entry.delete(0, END)
    employment_type_combobox.set('Select')
    education_combobox.set('Select')
    work_shift_combobox.set('Select')
    address_entry.delete(1.0, END)
    doj_entry.set_date(date.today())
    salary_entry.delete(0, END)
    usertype_combobox.set('Select')
    password_entry.delete(0, END)
    if check:
        employee_treeview.selection_remove(employee_treeview.selection())


def update_employee(empid, name, email, gender, dob, contact, employment_type, education, work_shift, address, doj,
                    salary,
                    usertype, password):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No row is selected')
    else:
        cursor, conn = connect_database()
        if not cursor or not conn:
            return
        try:
            cursor.execute('use inventory_system')
            cursor.execute('SELECT * from employee_data WHERE emp_id=%s',(empid,))
            current_data=cursor.fetchone()
            current_data=current_data[1:]
            address=address.strip()
            new_data=(name, email, gender, dob, contact, employment_type, education, work_shift, address, doj,
                        salary,
                        usertype, password)

            if current_data==new_data:
                messagebox.showinfo('Information','No changes made')
                return

            cursor.execute(
                'UPDATE employee_data SET name=%s, email=%s, gender=%s, dob=%s, contact=%s, employment_type=%s, education=%s, work_shift=%s, address=%s, doj=%s, salary=%s, usertype=%s, password=%s WHERE emp_id=%s', (name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary,
                     usertype, password,empid))
            conn.commit()
            treeview_data()
            messagebox.showinfo('Success', 'Data is updated successfully')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            conn.close()

def delete_data(empid,):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No row is selected')
    else:
        result=messagebox.askyesno('Confirm','Do you really want to delete this employee?')
        if result:
            cursor,conn=connect_database()
            if not cursor or not conn:
                return
            try:
                cursor.execute('use inventory_system')
                cursor.execute('DELETE from employee_data WHERE emp_id=%s',(empid,))
                conn.commit()
                treeview_data()
                messagebox.showinfo('Success', 'Data is deleted successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Error due to {e}')
            finally:
                cursor.close()
                conn.close()

def search_employee(search_option,value):
    if search_option=='Search By':
        messagebox.showerror('Error','No search option selected')
    elif value=='':
        messagebox.showerror('Error','Enter the value to search')
    else:
        search_option=search_option.replace(' ','_')
        cursor,conn=connect_database()
        if not cursor or not conn:
            return
        try:
            cursor.execute('use inventory_system')
            cursor.execute(f'SELECT * from employee_data WHERE {search_option} like %s',f'%{value}%')
            records=cursor.fetchall()
            employee_treeview.delete(*employee_treeview.get_children())
            for record in records:
                employee_treeview.insert("", "end", values=record)
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            conn.close()

def show_all(search_combobox,search_entry):
    treeview_data()
    search_combobox.set('Search By')
    search_entry.delete(0,END)

# GUI part
def employee_form(root):
    global back_image, employee_treeview
    employee_frame = Frame(root, width=1070, height=567, bg='white')
    employee_frame.place(x=200, y=100)
    heading_label = Label(employee_frame, text='Manage Employee Details', font=('times new roman', 16, 'bold'),
                          bg='#434E78', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    back_image = PhotoImage(file='images/back.png')

    top_frame = Frame(employee_frame, bg='white')
    top_frame.place(x=0, y=40, relwidth=1, height=190)
    back_button = Button(top_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: employee_frame.place_forget())
    back_button.place(x=20, y=0)
    search_frame = Frame(top_frame, bg="white")
    search_frame.pack()
    search_combobox = ttk.Combobox(search_frame,
                                   values=('Emp ID', 'Name', 'Email', 'Employment type', 'Work shift', 'Education',
                                           'Salary'), font=('times new roman', 12), state='readonly')
    search_combobox.set('Search By')
    search_combobox.grid(row=0, column=0, padx=20)
    search_entry = Entry(search_frame, font=('times new roman', 12), bg='light yellow')
    search_entry.grid(row=0, column=1)
    search_button = Button(search_frame, text='Search', font=('times new roman', 12), width=10, cursor='hand2',
                           fg='white', bg='#434E78',command=lambda:search_employee(search_combobox.get(),search_entry.get()))
    search_button.grid(row=0, column=2, padx=20)
    show_button = Button(search_frame, text='Show All', font=('times new roman', 12), width=10, cursor='hand2',
                         fg='white', bg='#434E78',command=lambda :show_all(search_combobox,search_entry))
    show_button.grid(row=0, column=3)

    horizontal_scrollbar = Scrollbar(top_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(top_frame, orient=VERTICAL)

    employee_treeview = ttk.Treeview(top_frame,
                                     columns=('empid', 'name', 'email', 'gender', 'dob', 'contact', 'employment_type',
                                              'education', 'work_shift', 'address', 'doj', 'salary', 'usertype'),
                                     show='headings', yscrollcommand=vertical_scrollbar.set,
                                     xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side=BOTTOM, fill=X)
    vertical_scrollbar.pack(side=RIGHT, fill=Y, pady=(10, 0))
    employee_treeview.pack(pady=(10, 0))
    horizontal_scrollbar.config(command=employee_treeview.xview)
    vertical_scrollbar.config(command=employee_treeview.yview)

    employee_treeview.heading('empid', text='Employee ID')
    employee_treeview.heading('name', text='Employee Name')
    employee_treeview.heading('email', text='Employee Email')
    employee_treeview.heading('gender', text='Gender')
    employee_treeview.heading('dob', text='Date Of Birth')
    employee_treeview.heading('contact', text='Contact')
    employee_treeview.heading('employment_type', text='Employment Type')
    employee_treeview.heading('education', text='Education')
    employee_treeview.heading('work_shift', text='Work Shift')
    employee_treeview.heading('address', text='Address')
    employee_treeview.heading('doj', text='Date Of Joining')
    employee_treeview.heading('salary', text='Salary')
    employee_treeview.heading('usertype', text='User Type')

    employee_treeview.column('empid', width=68)
    employee_treeview.column('name', width=140)
    employee_treeview.column('email', width=180)
    employee_treeview.column('gender', width=80)
    employee_treeview.column('contact', width=100)
    employee_treeview.column('dob', width=100)
    employee_treeview.column('employment_type', width=120)
    employee_treeview.column('education', width=120)
    employee_treeview.column('work_shift', width=100)
    employee_treeview.column('address', width=200)
    employee_treeview.column('doj', width=100)
    employee_treeview.column('salary', width=140)
    employee_treeview.column('usertype', width=120)

    treeview_data()

    detail_frame = Frame(employee_frame, bg='white')
    detail_frame.place(x=20, y=250)

    empid_label = Label(detail_frame, text='Emp ID', font=('times new roman', 12), bg='white')
    empid_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
    empid_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    empid_entry.grid(row=0, column=1, padx=20, pady=10)

    name_label = Label(detail_frame, text='Name', font=('times new roman', 12), bg='white')
    name_label.grid(row=0, column=2, padx=20, pady=10, sticky='w')
    name_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    name_entry.grid(row=0, column=3, padx=20, pady=10)

    email_label = Label(detail_frame, text='Email', font=('times new roman', 12), bg='white')
    email_label.grid(row=0, column=4, padx=20, pady=10, sticky='w')
    email_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    email_entry.grid(row=0, column=5, padx=20, pady=10)

    gender_label = Label(detail_frame, text='Gender', font=('times new roman', 12), bg='white')
    gender_label.grid(row=1, column=0, padx=20, pady=10, sticky='w')
    gender_combobox = ttk.Combobox(detail_frame, values=('Male', 'Female'), state='readonly',
                                   font=('times new roman', 12), width=18)
    gender_combobox.set('Select')
    gender_combobox.grid(row=1, column=1, padx=20, pady=10)

    dob_label = Label(detail_frame, text='date Of Birth', font=('times new roman', 12), bg='white')
    dob_label.grid(row=1, column=2, padx=20, pady=10, sticky='w')
    dob_entry = DateEntry(detail_frame, font=('times new roman', 12), width=18, state='readonly',
                          date_pattern='dd/mm/yyyy')
    dob_entry.grid(row=1, column=3, padx=20, pady=10)

    contact_label = Label(detail_frame, text='Contact', font=('times new roman', 12), bg='white')
    contact_label.grid(row=1, column=4, padx=20, pady=10, sticky='w')
    contact_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    contact_entry.grid(row=1, column=5, padx=20, pady=10)

    employment_type_label = Label(detail_frame, text='Employment Type', font=('times new roman', 12), bg='white')
    employment_type_label.grid(row=2, column=0, padx=20, pady=10, sticky='w')
    employment_type_combobox = ttk.Combobox(detail_frame, values=('Full Time', 'Part Time', 'Contract', 'Intern'),
                                            state='readonly', font=('times new roman', 12), width=18)
    employment_type_combobox.set('Select')
    employment_type_combobox.grid(row=2, column=1, padx=20, pady=10)

    education_label = Label(detail_frame, text='Education', font=('times new roman', 12), bg='white')
    education_label.grid(row=2, column=2, padx=20, pady=10, sticky='w')
    education_list = ['B.Tech', 'B.Com', 'M.Tech', 'M.Com', 'BCA', 'MCA', 'BBA', 'MBA']
    education_combobox = ttk.Combobox(detail_frame, values=education_list, state='readonly',
                                      font=('times new roman', 12), width=18)
    education_combobox.set('Select')
    education_combobox.grid(row=2, column=3, padx=20, pady=10)

    work_shift_label = Label(detail_frame, text='Work Shift', font=('times new roman', 12), bg='white')
    work_shift_label.grid(row=2, column=4, padx=20, pady=10, sticky='w')
    work_shift_combobox = ttk.Combobox(detail_frame, values=('Morning', 'Evening', 'Night'), state='readonly',
                                       font=('times new roman', 12), width=18)
    work_shift_combobox.set('Select')
    work_shift_combobox.grid(row=2, column=5, padx=20, pady=10)

    address_label = Label(detail_frame, text='Address', font=('times new roman', 12), bg='white')
    address_label.grid(row=3, column=0, padx=20, pady=10, sticky='w')
    address_entry = Text(detail_frame, font=('times new roman', 12), width=20, height=3, bg='lightyellow')
    address_entry.grid(row=3, column=1, padx=20, pady=10, rowspan=2)

    doj_label = Label(detail_frame, text='Date Of Joining', font=('times new roman', 12), bg='white')
    doj_label.grid(row=3, column=2, padx=20, pady=10, sticky='w')
    doj_entry = DateEntry(detail_frame, font=('times new roman', 12), width=18, state='readonly',
                          date_pattern='dd/mm/yyyy')
    doj_entry.grid(row=3, column=3, padx=20, pady=10)

    salary_label = Label(detail_frame, text='Salary', font=('times new roman', 12), bg='white')
    salary_label.grid(row=3, column=4, padx=20, pady=10, sticky='w')
    salary_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    salary_entry.grid(row=3, column=5, padx=20, pady=10)

    usertype_label = Label(detail_frame, text='User Type', font=('times new roman', 12), bg='white')
    usertype_label.grid(row=4, column=2, padx=20, pady=10, sticky='w')
    usertype_combobox = ttk.Combobox(detail_frame, values=('Admin', 'Employee'), state='readonly',
                                     font=('times new roman', 12), width=18)
    usertype_combobox.set('Select')
    usertype_combobox.grid(row=4, column=3, padx=20, pady=10)

    password_label = Label(detail_frame, text='Password', font=('times new roman', 12), bg='white')
    password_label.grid(row=4, column=4, padx=20, pady=10, sticky='w')
    password_entry = Entry(detail_frame, font=('times new roman', 12), bg='lightyellow')
    password_entry.grid(row=4, column=5, padx=20, pady=10)

    button_frame = Frame(employee_frame, bg='white')
    button_frame.place(x=200, y=500)

    add_button = Button(button_frame, text='Add', font=('times new roman', 12), width=10, cursor='hand2',
                        fg='white', bg='#434E78',
                        command=lambda: add_employee(empid_entry.get(), name_entry.get(), email_entry.get(),
                                                     gender_combobox.get(), dob_entry.get(), contact_entry.get(),
                                                     employment_type_combobox.get(), education_combobox.get(),
                                                     work_shift_combobox.get(), address_entry.get(1.0, END),
                                                     doj_entry.get(),
                                                     salary_entry.get(), usertype_combobox.get(), password_entry.get()))
    add_button.grid(row=0, column=0, padx=20)
    update_button = Button(button_frame, text='Update', font=('times new roman', 12), width=10, cursor='hand2',
                           fg='white', bg='#434E78',
                           command=lambda: update_employee(empid_entry.get(), name_entry.get(), email_entry.get(),
                                                           gender_combobox.get(), dob_entry.get(), contact_entry.get(),
                                                           employment_type_combobox.get(), education_combobox.get(),
                                                           work_shift_combobox.get(), address_entry.get(1.0, END),
                                                           doj_entry.get(),
                                                           salary_entry.get(), usertype_combobox.get(),
                                                           password_entry.get()))
    update_button.grid(row=0, column=1, padx=20)
    delete_button = Button(button_frame, text='Delete', font=('times new roman', 12), width=10, cursor='hand2',
                           fg='white', bg='#434E78',command=lambda: delete_data(empid_entry.get(),))
    delete_button.grid(row=0, column=2, padx=20)
    clear_button = Button(button_frame, text='Clear', font=('times new roman', 12), width=10, cursor='hand2',
                          fg='white', bg='#434E78',
                          command=lambda: clear_fields(empid_entry, name_entry, email_entry, dob_entry, gender_combobox,
                                                       contact_entry, employment_type_combobox, education_combobox,
                                                       work_shift_combobox, address_entry, doj_entry, salary_entry,
                                                       usertype_combobox, password_entry, True))
    clear_button.grid(row=0, column=3, padx=20)
    employee_treeview.bind('<ButtonRelease-1>',
                           lambda event: select_data(event, empid_entry, name_entry, email_entry, dob_entry,
                                                     gender_combobox,
                                                     contact_entry, employment_type_combobox, education_combobox,
                                                     work_shift_combobox, address_entry, doj_entry, salary_entry,
                                                     usertype_combobox, password_entry))
    create_database_table()
    return employee_frame