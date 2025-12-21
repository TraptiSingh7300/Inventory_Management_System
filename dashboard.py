from tkinter import *
from tkinter import messagebox
import time
from employees import employee_form, connect_database
from supplier import supplier_form
from category import category_form
from product import product_form
from sales import sales_form
import os

# Logout function
def logout(root):
    result = messagebox.askyesno('Warning', 'Do you really want to logout?')
    if result:
        root.destroy()

def exit(root):
    result = messagebox.askyesno('Warning', 'Do you really want to exit?')
    if result:
        root.destroy()

# Frame switching
current_frame = None
def show_form(form_function, root):
    global current_frame
    if current_frame:
        current_frame.place_forget()
    current_frame = form_function(root)

# Time/date updater
def update_time_date(subtitleLabel):
    current_time = time.strftime("%I:%M:%S %p")
    current_date = time.strftime("%d-%m-%Y")
    subtitleLabel.config(text=f"Welcome Admin\t\t Date: {current_date}\t\t   Time: {current_time}")
    subtitleLabel.after(1000, lambda: update_time_date(subtitleLabel))

# Database count updater
def update_count(label, query):
    cursor, conn = connect_database()
    if not cursor or not conn:
        return
    try:
        cursor.execute("USE inventory_system")
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            label.config(text=str(result[0]))
    except Exception as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def refresh_dashboard(dash_frame):
    update_count(dash_frame.total_emp_label, "SELECT COUNT(*) FROM employee_data")
    update_count(dash_frame.total_supp_label, "SELECT COUNT(*) FROM supplier_data")
    update_count(dash_frame.total_catg_label, "SELECT COUNT(*) FROM category_data")
    update_count(dash_frame.total_prod_label, "SELECT COUNT(*) FROM product_data") # Count sales from bill folder
    bill_folder = "bill"
    if not os.path.exists(bill_folder):
        os.makedirs(bill_folder)
    files = os.listdir(bill_folder)
    pdf_files = [f for f in files if f.lower().endswith(".pdf")]
    dash_frame.total_sales_label.config(text=str(len(pdf_files)))


# Dashboard frame
def dashboard(root):
    dash_frame = Frame(root, bg="white")
    dash_frame.place(x=0, y=0, relwidth=1, relheight=1)

    dash_frame.images = {}  # persistent image references

    # Top bar
    dash_frame.images['bg'] = PhotoImage(file='images/inventory.png')
    titleLabel = Label(dash_frame, image=dash_frame.images['bg'], compound=LEFT,
                       text='                  Inventory Management System',
                       font=('times new roman', 35, 'bold'),
                       bg='#434E78', fg='white', anchor='w', padx=20)
    titleLabel.place(x=0, y=0, relwidth=1)

    logoutButton = Button(dash_frame, text='Logout', font=('times new roman', 15, 'bold'),
                          fg='#010c48', cursor='hand2', bd=2,
                          command=lambda: logout(root))
    logoutButton.place(x=1180, y=15)

    subtitleLabel = Label(dash_frame, text='Welcome Admin',
                          font=('times new roman', 15), bg='#4d636d', fg='white')
    subtitleLabel.place(x=0, y=70, relwidth=1)
    update_time_date(subtitleLabel)

    # Left menu
    leftFrame = Frame(dash_frame)
    leftFrame.place(x=0, y=102, width=200, height=555)

    Label(leftFrame, text='Dashboard', font=('times new roman', 30), bg='white', pady=10).pack(fill=X)

    dash_frame.images['logo'] = PhotoImage(file='images/logo.png')
    Label(leftFrame, image=dash_frame.images['logo']).pack()

    Label(leftFrame, text='Menu', font=('times new roman', 20), bg='#009688').pack(fill=X)

    dash_frame.images['employee'] = PhotoImage(file='images/employee.png')
    Button(leftFrame, image=dash_frame.images['employee'], compound=LEFT, text='   Employee',
           font=('times new roman', 20, 'bold'), anchor='w', padx=5, cursor='hand2',
           command=lambda: show_form(employee_form, root)).pack(fill=X)

    dash_frame.images['supplier'] = PhotoImage(file='images/supplier.png')
    Button(leftFrame, image=dash_frame.images['supplier'], compound=LEFT, text='   Supplier',
           font=('times new roman', 20, 'bold'), anchor='w', padx=5, cursor='hand2',
           command=lambda: show_form(supplier_form, root)).pack(fill=X)

    dash_frame.images['category'] = PhotoImage(file='images/category.png')
    Button(leftFrame, image=dash_frame.images['category'], compound=LEFT, text='   Category',
           font=('times new roman', 20, 'bold'), anchor='w', padx=5, cursor='hand2',
           command=lambda: show_form(category_form, root)).pack(fill=X)

    dash_frame.images['product'] = PhotoImage(file='images/product.png')
    Button(leftFrame, image=dash_frame.images['product'], compound=LEFT, text='   Product',
           font=('times new roman', 20, 'bold'), anchor='w', padx=5, cursor='hand2',
           command=lambda: show_form(product_form, root)).pack(fill=X)

    dash_frame.images['sales'] = PhotoImage(file='images/sales.png')
    Button(leftFrame, image=dash_frame.images['sales'], compound=LEFT, text='   Sales',
           font=('times new roman', 20, 'bold'), anchor='w', padx=5, cursor='hand2',
           command=lambda: show_form(sales_form, root)).pack(fill=X)

    dash_frame.images['exit'] = PhotoImage(file='images/exit.png')
    Button(leftFrame, image=dash_frame.images['exit'], compound=LEFT, text='   Exit',
           font=('times new roman', 20, 'bold'), anchor='w', padx=5, cursor='hand2',
           command=lambda: exit(root)).pack(fill=X)

    # Summary frames with dynamic counts
    # Employees
    emp_frame = Frame(dash_frame, bg='#2C3E50', bd=3, relief=RIDGE)
    emp_frame.place(x=400, y=125, height=150, width=280)
    dash_frame.images['total_emp'] = PhotoImage(file='images/total_emp.png')
    Label(emp_frame, image=dash_frame.images['total_emp'], bg='#2C3E50').pack()
    Label(emp_frame, text='Total Employees', bg='#2C3E50', fg='white',
          font=('times new roman', 15, 'bold')).pack()
    total_emp_count_label = Label(emp_frame, text='0', bg='#2C3E50', fg='white',
                                  font=('times new roman', 30, 'bold'))
    total_emp_count_label.pack()
    update_count(total_emp_count_label, "SELECT COUNT(*) FROM employee_data")
    dash_frame.total_emp_label = total_emp_count_label

    # Suppliers
    supp_frame = Frame(dash_frame, bg='#8E44AD', bd=3, relief=RIDGE)
    supp_frame.place(x=800, y=125, height=150, width=280)
    dash_frame.images['total_supp'] = PhotoImage(file='images/total_supplier.png')
    Label(supp_frame, image=dash_frame.images['total_supp'], bg='#8E44AD').pack()
    Label(supp_frame, text='Total Suppliers', bg='#8E44AD', fg='white',
          font=('times new roman', 15, 'bold')).pack()
    total_supp_count_label = Label(supp_frame, text='0', bg='#8E44AD', fg='white',
                                   font=('times new roman', 30, 'bold'))
    total_supp_count_label.pack()
    update_count(total_supp_count_label, "SELECT COUNT(*) FROM supplier_data")
    dash_frame.total_supp_label = total_supp_count_label

    # Categories
    catg_frame = Frame(dash_frame, bg='#27AE60', bd=3, relief=RIDGE)
    catg_frame.place(x=400, y=310, height=150, width=280)
    dash_frame.images['total_catg'] = PhotoImage(file='images/total_category.png')
    Label(catg_frame, image=dash_frame.images['total_catg'], bg='#27AE60').pack()
    Label(catg_frame, text='Total Categories', bg='#27AE60', fg='white',
          font=('times new roman', 15, 'bold')).pack()
    total_catg_count_label = Label(catg_frame, text='0', bg='#27AE60', fg='white',
                                   font=('times new roman', 30, 'bold'))
    total_catg_count_label.pack()
    update_count(total_catg_count_label, "SELECT COUNT(*) FROM category_data")
    dash_frame.total_catg_label = total_catg_count_label

    # Products
    prod_frame = Frame(dash_frame, bg='#E74C3C', bd=3, relief=RIDGE)
    prod_frame.place(x=800, y=310, height=150, width=280)
    dash_frame.images['total_prod'] = PhotoImage(file='images/total_product.png')
    Label(prod_frame, image=dash_frame.images['total_prod'], bg='#E74C3C').pack()
    Label(prod_frame, text='Total Products', bg='#E74C3C', fg='white',
          font=('times new roman', 15, 'bold')).pack()
    total_prod_count_label = Label(prod_frame, text='0', bg='#E74C3C', fg='white',
                                   font=('times new roman', 30, 'bold'))
    total_prod_count_label.pack()
    update_count(total_prod_count_label, "SELECT COUNT(*) FROM product_data")
    dash_frame.total_prod_label = total_prod_count_label

    sales_frame = Frame(dash_frame, bg='#3498DB', bd=3, relief=RIDGE)
    sales_frame.place(x=600, y=500, height=150, width=280)
    dash_frame.images['total_sales'] = PhotoImage(file='images/total_sales.png')
    Label(sales_frame, image=dash_frame.images['total_sales'], bg='#3498DB').pack()
    Label(sales_frame, text='Total Sales', bg='#3498DB', fg='white', font=('times new roman', 15, 'bold')).pack()
    total_sales_count_label = Label(sales_frame, text='0', bg='#3498DB', fg='white', font=('times new roman', 30, 'bold'))
    total_sales_count_label.pack()
    dash_frame.total_sales_label = total_sales_count_label

    def auto_refresh():
        refresh_dashboard(dash_frame)
        dash_frame.after(5000, auto_refresh)  # repeat every 5000 ms (5 seconds)

    auto_refresh()

    refresh_dashboard(dash_frame)
