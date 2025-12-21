from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from employees import connect_database, treeview_data

def show_all(treeview,search_entry):
    treeview_data(treeview)
    search_entry.delete(0,END)

def search_supplier(search_value,treeview):
    if search_value=='':
        messagebox.showerror('Error','Please enter invoice no.')
    else:
        cursor,conn=connect_database()
        if not cursor or not conn:
            return
        try:
            cursor.execute('use inventory_system')
            cursor.execute('select * from supplier_data where invoice=%s', search_value)
            record = cursor.fetchone()
            if not record:
                messagebox.showerror('Error', 'No record found')
                return
            treeview.delete(*treeview.get_children())
            treeview.insert('', END, values=record)
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            cursor.close()
            conn.close()

def clear(invoice_entry,name_entry,contact_entry,description_entry,treeview):
    invoice_entry.delete(0,END)
    name_entry.delete(0, END)
    contact_entry.delete(0, END)
    description_entry.delete(1.0, END)
    treeview.selection_remove(treeview.selection())

def delete_supplier(invoice,treeview):
    index = treeview.selection()
    if not index:
        messagebox.showerror('Error', 'No row is selected')
        return
    cursor, conn = connect_database()
    if not cursor or not conn:
        return
    try:
        cursor.execute('use inventory_system')
        cursor.execute('delete from supplier_data where invoice=%s',invoice)
        conn.commit()
        treeview_data(treeview)
        messagebox.showinfo('Info','Data is deleted')
    except Exception as e:
        messagebox.showerror('Error',f'Error due to {e}')
    finally:
        cursor.close()
        conn.close()

def update_supplier(invoice,name,contact,description,treeview):
    index=treeview.selection()
    if not index:
        messagebox.showerror('Error','No row is selected')
        return
    cursor, conn = connect_database()
    if not cursor or not conn:
        return
    try:
        cursor.execute('use inventory_system')
        cursor.execute('select * from supplier_data where invoice=%s',invoice)
        current_data=cursor.fetchone()
        current_data=current_data[1:]
        new_data=(name,contact,description)
        if current_data==new_data:
            messagebox.showinfo('Info','No changes made')
            return
        cursor.execute('update supplier_data set name=%s, contact=%s, description=%s where invoice=%s',(name,contact,description,invoice))
        conn.commit()
        messagebox.showinfo('Info','Data is updated')
        treeview_data(treeview)
    except Exception as e:
        messagebox.showerror('Error',f'Error due to {e}')
    finally:
        cursor.close()
        conn.close()


def select_data(event,invoice_entry,name_entry,contact_entry,description_entry,treeview):
    index=treeview.selection()
    content=treeview.item(index)
    row=content['values']
    invoice_entry.delete(0,END)
    name_entry.delete(0, END)
    contact_entry.delete(0, END)
    description_entry.delete(1.0, END)
    invoice_entry.insert(0,row[0])
    name_entry.insert(0, row[1])
    contact_entry.insert(0, row[2])
    description_entry.insert(1.0, row[3])

def treeview_data(treeview):
    cursor, conn = connect_database()
    if not cursor or not conn:
        return
    try:
        cursor.execute('use inventory_system')
        cursor.execute('SELECT * FROM supplier_data')
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error',f'Error due to {e}')
    finally:
        cursor.close()
        conn.close()

def add_supplier(invoice,name,contact,description,treeview):
    if invoice=='' or name=='' or contact=='' or description=='':
        messagebox.showerror('Error','All fields are required')
    else:
        cursor, conn = connect_database()
        if not cursor or not conn:
            return
        try:
            cursor.execute('USE inventory_system')
            cursor.execute('CREATE TABLE IF NOT EXISTS supplier_data(invoice INT PRIMARY KEY, name VARCHAR(100), contact VARCHAR(15), description TEXT)')
            cursor.execute('Select * from supplier_data where invoice=%s', invoice)
            if cursor.fetchone():
                messagebox.showerror('Error', 'Invoice No. already exists')
                return

            cursor.execute('INSERT INTO supplier_data VALUES(%s,%s,%s,%s)',(invoice,name,contact,description))
            conn.commit()
            messagebox.showinfo('Info','Data is inserted successfully')
            treeview_data(treeview)
        except Exception as e:
            messagebox.showerror('Error',f'Error due to {e}')
        finally:
            cursor.close()
            conn.close()

def supplier_form(root):
    global back_image
    supplier_frame = Frame(root, width=1070, height=567, bg='white')
    supplier_frame.place(x=200, y=100)
    heading_label = Label(supplier_frame, text='Manage Supplier Details', font=('times new roman', 16, 'bold'),
                          bg='#434E78', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)
    back_image = PhotoImage(file='images/back.png')

    back_button = Button(supplier_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: supplier_frame.place_forget())
    back_button.place(x=20, y=35)

    left_frame = Frame(supplier_frame, bg='white',pady=60)
    left_frame.place(x=10, y=100)

    left_frame_label = Label(supplier_frame, text='Supplier Form', font=('times new roman', 18, 'bold'),
                          bg='white', fg='#434E78')
    left_frame_label.place(x=150, y=90)

    invoice_label=Label(left_frame, text='Invoice No.', font=('times new roman', 14, 'bold'),bg='white')
    invoice_label.grid(row=1,column=0,padx=(20,40),sticky='w')
    invoice_entry=Entry(left_frame,font=('times new roman', 14, 'bold'),bg='lightyellow')
    invoice_entry.grid(row=1,column=1)

    name_label = Label(left_frame, text='Supplier Name', font=('times new roman', 14, 'bold'), bg='white')
    name_label.grid(row=2, column=0, padx=(20,40),pady=25,sticky='w')
    name_entry = Entry(left_frame, font=('times new roman', 14, 'bold'), bg='lightyellow')
    name_entry.grid(row=2, column=1)

    contact_label = Label(left_frame, text='Contact', font=('times new roman', 14, 'bold'), bg='white')
    contact_label.grid(row=3, column=0, padx=(20,40),sticky='w')
    contact_entry = Entry(left_frame, font=('times new roman', 14, 'bold'), bg='lightyellow')
    contact_entry.grid(row=3, column=1)

    description_label = Label(left_frame, text='Description', font=('times new roman', 14, 'bold'), bg='white')
    description_label.grid(row=4, column=0, padx=(20,40),sticky='nw',pady=25)
    description_entry=Text(left_frame, font=('times new roman', 14, 'bold'), bg='lightyellow',width=20, height=4, bd=1)
    description_entry.grid(row=4, column=1, pady=25)

    button_frame=Frame(left_frame, bg='white')
    button_frame.grid(row=5, columnspan=2,pady=20)

    add_button = Button(button_frame, text='Add', font=('times new roman', 14), width=7, cursor='hand2',
                           fg='white', bg='#434E78',command=lambda:add_supplier(invoice_entry.get(),name_entry.get(),contact_entry.get(),description_entry.get(1.0,END).strip(),treeview))
    add_button.grid(row=5, column=0, padx=20)

    update_button = Button(button_frame, text='Update', font=('times new roman', 14), width=7, cursor='hand2',
                        fg='white', bg='#434E78',command=lambda:update_supplier(invoice_entry.get(),name_entry.get(),contact_entry.get(),description_entry.get(1.0,END).strip(),treeview))
    update_button.grid(row=5, column=1)

    delete_button = Button(button_frame, text='Delete', font=('times new roman', 14), width=7, cursor='hand2',
                           fg='white', bg='#434E78',command=lambda:delete_supplier(invoice_entry.get(),treeview))
    delete_button.grid(row=5, column=2, padx=20)

    clear_button = Button(button_frame, text='Clear', font=('times new roman', 14), width=7, cursor='hand2',
                        fg='white', bg='#434E78',command=lambda:clear(invoice_entry,name_entry,contact_entry,description_entry,treeview))
    clear_button.grid(row=5, column=3)

    right_frame=Frame(supplier_frame, bg='white',pady=60)
    right_frame.place(x=520,y=90,width=500,height=450)

    right_frame_label = Label(supplier_frame, text='Supplier Details', font=('times new roman', 18, 'bold'),
                             bg='white', fg='#434E78')
    right_frame_label.place(x=665, y=90)

    search_frame=Frame(right_frame, bg='white')
    search_frame.pack(pady=(0,10))

    search_label = Label(search_frame, text='Invoice No.', font=('times new roman', 14, 'bold'), bg='white')
    search_label.grid(row=0, column=0, padx=10, sticky='w')
    search_entry = Entry(search_frame, font=('times new roman', 14, 'bold'), bg='lightyellow', width=10)
    search_entry.grid(row=0, column=1)

    search_button = Button(search_frame, text='Search', font=('times new roman', 14), width=7, cursor='hand2',
                          fg='white', bg='#434E78',command=lambda:search_supplier(search_entry.get(),treeview))
    search_button.grid(row=0, column=2,padx=20)

    show_button = Button(search_frame, text='Show All', font=('times new roman', 14), width=7, cursor='hand2',
                          fg='white', bg='#434E78',command=lambda:show_all(treeview,search_entry))
    show_button.grid(row=0, column=3)

    scrolly=Scrollbar(right_frame,orient=VERTICAL)
    scrollx = Scrollbar(right_frame, orient=HORIZONTAL)

    treeview=ttk.Treeview(right_frame,columns=('invoice_no','name','contact','description'),show='headings',yscrollcommand=scrolly.set,xscrollcommand=scrollx.set)
    scrolly.pack(side=RIGHT,fill=Y)
    scrollx.pack(side=BOTTOM,fill=X)
    scrolly.config(command=treeview.yview)
    scrollx.config(command=treeview.xview)
    treeview.pack(fill=BOTH,expand=1)
    treeview.heading('invoice_no',text='Invoice No')
    treeview.heading('name', text='Name')
    treeview.heading('contact', text='Contact')
    treeview.heading('description', text='Description')

    treeview.column('invoice_no',width=80)
    treeview.column('name', width=160)
    treeview.column('contact', width=120)
    treeview.column('description', width=300)

    treeview_data(treeview)
    treeview.bind('<ButtonRelease-1>',lambda event:select_data(event,invoice_entry,name_entry,contact_entry,description_entry,treeview))

    return supplier_frame