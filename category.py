from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connect_database

def delete(treeview):
    index = treeview.selection()
    content=treeview.item(index[0],'values')
    # row=content['values'][0]
    id=content[0]
    if not index:
        messagebox.showerror('Error', 'No row is selected')
        return

    result=messagebox.askyesno('Confirm','Do you really want to delete this category?')
    if result:
        cursor, conn = connect_database()
        if not cursor or not conn:
            return
        try:
            cursor.execute('use inventory_system')
            cursor.execute('delete from category_data where id=%s', id)
            conn.commit()
            treeview_data(treeview)
            messagebox.showinfo('Info', 'Data is deleted')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            conn.close()


def clear(id_entry,category_name_entry,description_entry):
    id_entry.delete(0,END)
    category_name_entry.delete(0,END)
    description_entry.delete(1.0,END)

def treeview_data(treeview):
    cursor, conn = connect_database()
    if not cursor or not conn:
        return
    try:
        cursor.execute('use inventory_system')
        cursor.execute('SELECT * FROM category_data')
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error',f'Error due to {e}')
    finally:
        cursor.close()
        conn.close()

def add_category(id,name,description,treeview):
    if id=='' or name=='' or description=='':
        messagebox.showerror('Error', 'All fields are required')
    else:
        cursor, conn = connect_database()
        if not cursor or not conn:
            return
        try:
            cursor.execute('USE inventory_system')
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS category_data(id INT PRIMARY KEY, name VARCHAR(100), description TEXT)')
            cursor.execute('Select * from category_data where id=%s', id)
            if cursor.fetchone():
                messagebox.showerror('Error', 'Id already exists')
                return
            cursor.execute('INSERT INTO category_data VALUES(%s,%s,%s)', (id, name, description))
            conn.commit()
            messagebox.showinfo('Info', 'Data is inserted successfully')
            treeview_data(treeview)
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            conn.close()

def category_form(root):
    global back_image,logo
    category_frame = Frame(root, width=1070, height=567, bg='white')
    category_frame.place(x=200, y=100)
    heading_label = Label(category_frame, text='Manage Category Details', font=('times new roman', 16, 'bold'),
                          bg='#434E78', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    back_image = PhotoImage(file='images/back.png')

    back_button = Button(category_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: category_frame.place_forget())
    back_button.place(x=20, y=35)

    logo=PhotoImage(file='images/product-category.png')
    label=Label(category_frame, image=logo, bd=0, bg='white')
    label.place(x=80,y=150)

    details_frame=Frame(category_frame, bd=0, bg='white')
    details_frame.place(x=500, y=50)

    id_label = Label(details_frame, text='ID', font=('times new roman', 14, 'bold'), bg='white')
    id_label.grid(row=0, column=0, padx=(20, 40), sticky='w')
    id_entry = Entry(details_frame, font=('times new roman', 14, 'bold'), bg='lightyellow')
    id_entry.grid(row=0, column=1)

    category_name_label = Label(details_frame, text='Category Name', font=('times new roman', 14, 'bold'), bg='white')
    category_name_label.grid(row=1, column=0, padx=(20, 40), sticky='w')
    category_name_entry = Entry(details_frame, font=('times new roman', 14, 'bold'), bg='lightyellow')
    category_name_entry.grid(row=1, column=1, pady=20)

    description_label = Label(details_frame, text='Description', font=('times new roman', 14, 'bold'), bg='white')
    description_label.grid(row=2, column=0, padx=(20, 40), sticky='nw', pady=25)
    description_entry = Text(details_frame, font=('times new roman', 14, 'bold'), bg='lightyellow', width=20, height=4,
                             bd=1)
    description_entry.grid(row=2, column=1)

    button_frame = Frame(details_frame, bg='white')
    button_frame.grid(row=5, columnspan=2, pady=20)

    add_button = Button(button_frame, text='Add', font=('times new roman', 14), width=7, cursor='hand2',
                        fg='white', bg='#434E78',command=lambda:add_category(id_entry.get(),category_name_entry.get(),description_entry.get(1.0,END).strip(),treeview))
    add_button.grid(row=5, column=0, padx=(95,40))

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 14), width=7, cursor='hand2',
                           fg='white', bg='#434E78',command=lambda:delete(treeview))
    delete_button.grid(row=5, column=1,padx=(0,40))

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 14), width=7, cursor='hand2',
                           fg='white', bg='#434E78',command=lambda:clear(id_entry,category_name_entry,description_entry))
    clear_button.grid(row=5, column=2)

    treeview_frame=Frame(category_frame, bg='yellow')
    treeview_frame.place(x=520,y=340,width=500,height=200)

    scrolly = Scrollbar(treeview_frame, orient=VERTICAL)
    scrollx = Scrollbar(treeview_frame, orient=HORIZONTAL)

    treeview = ttk.Treeview(treeview_frame, columns=('id', 'name', 'description'), show='headings',
                            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrolly.config(command=treeview.yview)
    scrollx.config(command=treeview.xview)
    treeview.pack(fill=BOTH, expand=1)
    treeview.heading('id', text='ID')
    treeview.heading('name', text='Category Name')
    treeview.heading('description', text='Description')

    treeview.column('id', width=80)
    treeview.column('name', width=140)
    treeview.column('description', width=300)

    treeview_data(treeview)

    return category_frame