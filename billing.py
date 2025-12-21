from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from employees import connect_database
import qrcode
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import subprocess
import os
import time
import random

# ------------------ Global (last invoice tracker) ------------------
last_invoice_no = None

# ------------------ Invoice Number Generator ------------------
def generate_invoice_number():
    return f"INV{random.randint(1000, 9999)}"

# ------------------ Calculator Functions ------------------
def calculator_click(var_cal_input, value):
    current = var_cal_input.get()
    var_cal_input.set(current + str(value))

def calculator_clear(var_cal_input):
    var_cal_input.set("")

def calculator_equal(var_cal_input):
    try:
        result = str(eval(var_cal_input.get()))
        var_cal_input.set(result)
    except Exception:
        var_cal_input.set("Error")

# ------------------ Clear All ------------------
def clear_all(name_entry, contact_entry, treeview1, bill_text, billFrame,
              amount_label, discount_label, pay_label):
    name_entry.delete(0, END)
    contact_entry.delete(0, END)
    treeview1.delete(*treeview1.get_children())
    bill_text.delete(1.0, END)
    amount_label.config(text="Bill Amount(Rs.)\n0")
    discount_label.config(text="Discount(5%)\n0")
    pay_label.config(text="Net Pay(Rs.)\n0")
    for widget in billFrame.winfo_children():
        if isinstance(widget, Label) and getattr(widget, "image", None) is not None:
            widget.destroy()

# ------------------ Print Bill (uses last invoice) ------------------
def print_bill():
    global last_invoice_no
    try:
        if not last_invoice_no:
            messagebox.showerror("Error", "No bill found to print. Please generate the bill first.")
            return

        filename = os.path.join("bill", f"{last_invoice_no}.pdf")
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"Bill file not found: {filename}")
            return

        adobe_reader = r"C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
        if os.path.exists(adobe_reader):
            subprocess.run([adobe_reader, "/p", "/h", filename], check=True)
            messagebox.showinfo("Success", "Bill sent to printer.")
        else:
            os.startfile(filename)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to print bill: {e}")

# ------------------ Generate Bill ------------------
def generate_bill(treeview1, amount_label, discount_label, pay_label, bill_text, billFrame, name_entry, contact_entry):
    global last_invoice_no
    try:
        customer_name = name_entry.get().strip()
        customer_contact = contact_entry.get().strip()

        # Validation
        if customer_name == "" or customer_contact == "":
            messagebox.showerror("Error", "Name and Contact are required")
            return

        # Generate short invoice number
        invoice_no = generate_invoice_number()
        last_invoice_no = invoice_no

        bill_text.delete(1.0, END)

        # Header with invoice + customer details
        bill_text.insert(END, "********** INVOICE **********\n\n")
        bill_text.insert(END, f"Invoice No: {invoice_no}\n")
        bill_text.insert(END, f"Customer Name: {customer_name}\n")
        bill_text.insert(END, f"Contact: {customer_contact}\n\n")

        bill_text.insert(END, f"{'ID':<5}{'Product':<15}{'Price':<10}{'Qty':<8}{'Total':<10}\n")
        bill_text.insert(END, "-"*50 + "\n")

        products = []
        for child in treeview1.get_children():
            values = treeview1.item(child, "values")
            pid, name, price, qty = values
            total = float(price) * int(qty)
            products.append((pid, name, price, qty, total))
            bill_text.insert(END, f"{pid:<5}{name:<15}{price:<10}{qty:<8}{total:<10.2f}\n")

        bill_text.insert(END, "-"*50 + "\n")
        bill_text.insert(END, amount_label.cget("text") + "\n")
        bill_text.insert(END, discount_label.cget("text") + "\n")
        bill_text.insert(END, pay_label.cget("text") + "\n")

        # QR code (includes invoice number)
        qr_data = f"Invoice: {invoice_no}, Customer: {customer_name}, Contact: {customer_contact}, {pay_label.cget('text')}"
        qr_img = qrcode.make(qr_data)
        qr_img.save("images/qr_temp.png")

        qr_open = Image.open("images/qr_temp.png").resize((100, 100))
        qr_photo = ImageTk.PhotoImage(qr_open)
        qr_label = Label(billFrame, image=qr_photo, bg="white")
        qr_label.image = qr_photo
        qr_label.place(x=150, y=300)

        # Ensure "bill" folder exists
        if not os.path.exists("bill"):
            os.makedirs("bill")

        # PDF export (filename uses invoice number)
        filename = os.path.join("bill", f"{invoice_no}.pdf")

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 20)
        c.drawString(200, height - 50, "INVOICE / BILL")

        # Invoice + customer details
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Invoice No: {invoice_no}")
        c.drawString(50, height - 100, f"Customer Name: {customer_name}")
        c.drawString(300, height - 100, f"Contact: {customer_contact}")

        # Table header
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 140, "ID")
        c.drawString(100, height - 140, "Product")
        c.drawString(250, height - 140, "Price")
        c.drawString(350, height - 140, "Qty")
        c.drawString(450, height - 140, "Total")

        y = height - 160
        for pid, name, price, qty, total in products:
            c.setFont("Helvetica", 12)
            c.drawString(50, y, str(pid))
            c.drawString(100, y, str(name))
            c.drawString(250, y, str(price))
            c.drawString(350, y, str(qty))
            c.drawString(450, y, f"{total:.2f}")
            y -= 20

        # Amount details
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y - 40, amount_label.cget("text"))
        c.drawString(50, y - 60, discount_label.cget("text"))
        c.drawString(50, y - 80, pay_label.cget("text"))

        # QR in PDF
        c.drawImage("images/qr_temp.png", 400, y - 120, width=100, height=100)

        c.save()

        messagebox.showinfo("Success", f"Bill generated successfully!\nSaved as {filename}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate bill: {e}")

# ------------------ Calculate Bill ------------------
def calculate_bill(treeview1, amount_label, discount_label, pay_label):
    total_amount = 0
    for child in treeview1.get_children():
        values = treeview1.item(child, "values")
        price = float(values[2])
        quantity = int(values[3])
        total_amount += price * quantity

    discount = total_amount * 0.05   # 5% discount
    net_pay = total_amount - discount

    amount_label.config(text=f"Bill Amount(Rs.)\n{total_amount:.2f}")
    discount_label.config(text=f"Discount(5%)\n{discount:.2f}")
    pay_label.config(text=f"Net Pay(Rs.)\n{net_pay:.2f}")

# ------------------ Cart Ops ------------------
def add_update_cart(product_name_entry, price_entry, quantity_entry,
                    treeview1, amount_label, discount_label, pay_label, stock_label):
    product_name = product_name_entry.get().strip()
    price = price_entry.get().strip()
    quantity = quantity_entry.get().strip()

    if product_name == "" or price == "" or quantity == "":
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror("Error", "Price must be a number and Quantity must be an integer")
        return

    # Extract stock value from stock_label (e.g. "In Stock: 10")
    stock_text = stock_label.cget("text")
    try:
        stock_value = int(stock_text.split(":")[1].strip())
    except:
        stock_value = 0

    if quantity > stock_value:
        messagebox.showerror("Error", f"Quantity entered ({quantity}) exceeds available stock ({stock_value})")
        return

    # Update if product exists, else insert
    for child in treeview1.get_children():
        values = treeview1.item(child, "values")
        if values[1] == product_name:
            treeview1.item(child, values=(values[0], product_name, price, quantity))
            break
    else:
        new_id = len(treeview1.get_children()) + 1
        treeview1.insert("", "end", values=(new_id, product_name, price, quantity))

    product_name_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)
    stock_label.config(text="In Stock:0")

    calculate_bill(treeview1, amount_label, discount_label, pay_label)

def select_data(event, product_name_entry, price_entry, quantity_entry, treeview, check, stock_label):
    index = treeview.selection()
    if not index:
        return
    content = treeview.item(index)
    row = content['values']

    product_name_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)
    product_name_entry.insert(0, row[1])
    price_entry.insert(0, row[2])
    quantity_entry.insert(0, row[3])

    stock_label.config(text=f"In Stock: {row[3]}")

    if check:
        treeview.selection_remove(treeview.selection())

def clear(product_name_entry,price_entry,quantity_entry,stock_label):
    product_name_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)
    stock_label.config(text="In Stock:0")

def show_all(treeview,search_entry):
    treeview_data(treeview)
    search_entry.delete(0,END)

def search_supplier(search_value,treeview):
    if search_value=='':
        messagebox.showerror('Error','Please enter product name')
    else:
        cursor,conn=connect_database()
        if not cursor or not conn:
            return
        try:
            cursor.execute('use inventory_system')
            cursor.execute('select id,name,price,quantity,status from product_data where name=%s', search_value)
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

def treeview_data(treeview):
    cursor, conn = connect_database()
    if not cursor or not conn:
        return
    try:
        cursor.execute('use inventory_system')
        cursor.execute('SELECT id,name,price,quantity,status FROM product_data')
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert('', END, values=record)
    except Exception as e:
        messagebox.showerror('Error',f'Error due to {e}')
    finally:
        cursor.close()
        conn.close()

# ------------------ Session UI ------------------
def logout(root):
    result = messagebox.askyesno('Warning', 'Do you really want to logout?')
    if result:
        root.destroy()

def update_time_date(subtitleLabel):
    current_time = time.strftime("%I:%M:%S %p")
    current_date = time.strftime("%d-%m-%Y")
    subtitleLabel.config(text=f"Welcome Employee\t\t Date: {current_date}\t\t   Time: {current_time}")
    subtitleLabel.after(1000, lambda: update_time_date(subtitleLabel))

def billing(root):
    billing_frame = Frame(root, bg="white")
    billing_frame.place(x=0, y=0, relwidth=1, relheight=1)

    billing_frame.images = {}

    billing_frame.images['bg'] = PhotoImage(file='images/inventory.png')
    titleLabel = Label(billing_frame, image=billing_frame.images['bg'], compound=LEFT,
                       text='                  Inventory Management System',
                       font=('times new roman', 35, 'bold'),
                       bg='#434E78', fg='white', anchor='w', padx=20)
    titleLabel.place(x=0, y=0, relwidth=1)

    logoutButton = Button(billing_frame, text='Logout', font=('times new roman', 15, 'bold'),
                          fg='#010c48', cursor='hand2', bd=2,
                          command=lambda: logout(root))
    logoutButton.place(x=1180, y=15)

    subtitleLabel = Label(billing_frame, text='Welcome Employee',
                          font=('times new roman', 15), bg='#4d636d', fg='white')
    subtitleLabel.place(x=0, y=70, relwidth=1)
    update_time_date(subtitleLabel)

    leftFrame = Frame(billing_frame,bg='white')
    leftFrame.place(x=10, y=102, width=350, height=540)

    firstFrame = Frame(leftFrame,bg='white', bd=5, relief=RIDGE)
    firstFrame.place(x=0, y=0, width=350, height=120)

    subtitleLabel = Label(firstFrame, text='All Products',
                          font=('times new roman', 15), bg='#434E78', fg='white')
    subtitleLabel.place(x=0, y=0, relwidth=1)

    search_label = Label(firstFrame, text='Product Name', font=('times new roman', 13, 'bold'), bg='white')
    search_label.place(x=10,y=40)
    search_entry = Entry(firstFrame, font=('times new roman', 13, 'bold'), bg='lightyellow')
    search_entry.place(x=140,y=40)

    show_button = Button(firstFrame, text='Search', font=('times new roman', 12), width=7, cursor='hand2',
                        fg='white', bg='#434E78',command=lambda:search_supplier(search_entry.get(),treeview))
    show_button.place(x=80,y=75)

    show_all_button = Button(firstFrame, text='Show All', font=('times new roman', 12), width=7, cursor='hand2',
                         fg='white', bg='#434E78',command=lambda:show_all(treeview,search_entry))
    show_all_button.place(x=190, y=75)

    secondFrame = Frame(leftFrame, bg='white', bd=5, relief=RIDGE)
    secondFrame.place(x=0, y=130, width=350, height=410)

    scrolly = Scrollbar(secondFrame, orient=VERTICAL)
    scrollx = Scrollbar(secondFrame, orient=HORIZONTAL)

    treeview = ttk.Treeview(secondFrame, columns=('id', 'name', 'price', 'quantity','status'), show='headings',
                            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrolly.config(command=treeview.yview)
    scrollx.config(command=treeview.xview)
    treeview.pack(fill=BOTH, expand=1)
    treeview.heading('id', text='ID')
    treeview.heading('name', text='Product Name')
    treeview.heading('price', text='Price')
    treeview.heading('quantity', text='Quantity')
    treeview.heading('status', text='Status')

    treeview.column('id', width=70)
    treeview.column('name', width=120)
    treeview.column('price', width=120)
    treeview.column('quantity', width=70)
    treeview.column('status', width=120)

    centerFrame = Frame(billing_frame,bg='white')
    centerFrame.place(x=370, y=102, width=480, height=540)

    upperFrame = Frame(centerFrame,bg='white', bd=5, relief=RIDGE)
    upperFrame.place(x=0, y=0, width=480, height=80)

    subtitleLabel = Label(upperFrame, text='Customer Details',
                          font=('times new roman', 15), bg='#434E78', fg='white')
    subtitleLabel.place(x=0, y=0, relwidth=1)

    name_label = Label(upperFrame, text='Name', font=('times new roman', 13, 'bold'), bg='white')
    name_label.place(x=30, y=40)
    name_entry = Entry(upperFrame, font=('times new roman', 13, 'bold'), bg='lightyellow', width=20)
    name_entry.place(x=90, y=40,width=120)

    contact_label = Label(upperFrame, text='Contact', font=('times new roman', 13, 'bold'), bg='white')
    contact_label.place(x=240, y=40)
    contact_entry = Entry(upperFrame, font=('times new roman', 13, 'bold'), bg='lightyellow', width=20)
    contact_entry.place(x=320, y=40, width=120)

    cal_label = Label(centerFrame, text='Calculator', font=('times new roman', 13, 'bold'), bg='white')
    cal_label.place(x=30, y=100)

    var_cal_input = StringVar()

    Cal_Frame = Frame(centerFrame, bd=5, relief=RIDGE, bg="white")
    Cal_Frame.place(x=0, y=130, width=155, height=195)

    txt_cal_input = Entry(
        Cal_Frame, textvariable=var_cal_input,
        font=('arial', 12, 'bold'), width=15,
        bd=5, relief=GROOVE, state='readonly', justify=RIGHT
    )
    txt_cal_input.grid(row=1, columnspan=4)

    Button(Cal_Frame, text='7', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '7')).grid(row=2, column=0)
    Button(Cal_Frame, text='8', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '8')).grid(row=2, column=1)
    Button(Cal_Frame, text='9', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '9')).grid(row=2, column=2)
    Button(Cal_Frame, text='+', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '+')).grid(row=2, column=3)

    Button(Cal_Frame, text='4', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '4')).grid(row=3, column=0)
    Button(Cal_Frame, text='5', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '5')).grid(row=3, column=1)
    Button(Cal_Frame, text='6', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '6')).grid(row=3, column=2)
    Button(Cal_Frame, text='-', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '-')).grid(row=3, column=3)

    Button(Cal_Frame, text='1', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '1')).grid(row=4, column=0)
    Button(Cal_Frame, text='2', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '2')).grid(row=4, column=1)
    Button(Cal_Frame, text='3', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '3')).grid(row=4, column=2)
    Button(Cal_Frame, text='*', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=5, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '*')).grid(row=4, column=3)

    Button(Cal_Frame, text='0', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=8, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '0')).grid(row=5, column=0)
    Button(Cal_Frame, text='C', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=8, cursor="hand2",
           command=lambda: calculator_clear(var_cal_input)).grid(row=5, column=1)
    Button(Cal_Frame, text='=', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=8, cursor="hand2",
           command=lambda: calculator_equal(var_cal_input)).grid(row=5, column=2)
    Button(Cal_Frame, text='/', font=('arial', 10, 'bold'),
           bd=3, width=3, pady=8, cursor="hand2",
           command=lambda: calculator_click(var_cal_input, '/')).grid(row=5, column=3)

    listFrame = Frame(centerFrame, bd=5, relief=RIDGE, bg="white")
    listFrame.place(x=170, y=100, width=310, height=225)

    scrolly = Scrollbar(listFrame, orient=VERTICAL)
    scrollx = Scrollbar(listFrame, orient=HORIZONTAL)

    treeview1 = ttk.Treeview(listFrame, columns=('id', 'name', 'price', 'quantity'), show='headings',
                            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrolly.config(command=treeview1.yview)
    scrollx.config(command=treeview1.xview)
    treeview1.pack(fill=BOTH, expand=1)
    treeview1.heading('id', text='ID')
    treeview1.heading('name', text='Product Name')
    treeview1.heading('price', text='Price')
    treeview1.heading('quantity', text='Quantity')

    treeview1.column('id', width=70)
    treeview1.column('name', width=120)
    treeview1.column('price', width=120)
    treeview1.column('quantity', width=70)

    bottomFrame = Frame(centerFrame, bd=5, relief=RIDGE,bg='white')
    bottomFrame.place(x=0, y=340, width=480, height=200)

    product_name_label = Label(bottomFrame, text='Product Name', font=('times new roman', 13, 'bold'), bg='white')
    product_name_label.grid(row=0,column=0,padx=(40,20),pady=(10,0),sticky='w')
    product_name_entry = Entry(bottomFrame, font=('times new roman', 13, 'bold'), bg='lightyellow', width=20)
    product_name_entry.grid(row=0,column=1,pady=(10,0))

    price_label = Label(bottomFrame, text='Price', font=('times new roman', 13, 'bold'), bg='white')
    price_label.grid(row=1,column=0,padx=(40,20),pady=20,sticky='w')
    price_entry = Entry(bottomFrame, font=('times new roman', 13, 'bold'), bg='lightyellow', width=20)
    price_entry.grid(row=1,column=1,pady=20)

    quantity_label = Label(bottomFrame, text='Quantity', font=('times new roman', 13, 'bold'), bg='white')
    quantity_label.grid(row=2,column=0,padx=(40,20),sticky='w')
    quantity_entry = Entry(bottomFrame, font=('times new roman', 13, 'bold'), bg='lightyellow', width=20)
    quantity_entry.grid(row=2,column=1)

    buttomFrame = Frame(bottomFrame,bg='white')
    buttomFrame.place(x=5, y=140, width=460, height=45)

    stock_label = Label(buttomFrame, text='In Stock:0', font=('times new roman', 13, 'bold'), bg='white',width=10)
    stock_label.grid(row=0, column=0,padx=(35,50),pady=5)

    clear_button = Button(buttomFrame, text='Clear', font=('times new roman', 12), width=7, cursor='hand2',
                         fg='white', bg='#434E78',command=lambda:clear(product_name_entry,price_entry,quantity_entry,stock_label))
    clear_button.grid(row=0, column=1,pady=5)

    add_button = Button(buttomFrame, text='Add/Update Cart', font=('times new roman', 12), width=12, cursor='hand2',
                          fg='white', bg='#434E78',
    command=lambda: add_update_cart(product_name_entry, price_entry, quantity_entry, treeview1,amount_label,discount_label,pay_label,stock_label))
    add_button.grid(row=0, column=2,padx=(30,10),pady=5)

    rightFrame = Frame(billing_frame,bg='white')
    rightFrame.place(x=860, y=102, width=400, height=540)

    billFrame = Frame(rightFrame, bg='white', bd=5, relief=RIDGE)
    billFrame.place(x=0, y=0, width=400, height=420)

    subtitleLabel = Label(billFrame, text='Bill',
                          font=('times new roman', 15), bg='#434E78', fg='white')
    subtitleLabel.place(x=0, y=0, relwidth=1)

    bill_text = Text(billFrame, font=('times new roman', 12), bg='lightyellow')
    bill_text.place(x=0, y=30, relwidth=1, relheight=0.9)

    btFrame = Frame(rightFrame, bg='white')
    btFrame.place(x=0, y=430, width=400, height=130)

    amount_label = Label(btFrame, text='Bill Amount(Rs.)\n0',
                          font=('times new roman', 12), bg='#4d636d', fg='white',width=12)
    amount_label.grid(row=0, column=0,padx=(15,0),pady=10)

    discount_label = Label(btFrame, text='Discount(5%)\n0',
                         font=('times new roman', 12), bg='#4d636d', fg='white', width=12)
    discount_label.grid(row=0, column=1,padx=(10,0),pady=10)

    pay_label = Label(btFrame, text='Net Pay(Rs.)\n0',
                         font=('times new roman', 12), bg='#4d636d', fg='white', width=12)
    pay_label.grid(row=0, column=2,padx=10,pady=10)

    generate_button = Button(btFrame, text='Generate Bill', font=('times new roman', 12), width=12, cursor='hand2',
                          fg='white', bg='#434E78',
                         command=lambda: generate_bill(treeview1, amount_label, discount_label, pay_label, bill_text, billFrame, name_entry, contact_entry))
    generate_button.grid(row=1, column=0,padx=(15,0))

    print_button = Button(btFrame, text='Print', font=('times new roman', 12), width=12, cursor='hand2',
                          fg='white', bg='#434E78',
                      command=print_bill)
    print_button.grid(row=1, column=1,padx=(10,0))

    clear_button = Button(btFrame, text='Clear All', font=('times new roman', 12), width=12, cursor='hand2',
                          fg='white', bg='#434E78',
                      command=lambda: clear_all(name_entry, contact_entry, treeview1, bill_text, billFrame,
              amount_label, discount_label, pay_label))
    clear_button.grid(row=1, column=2,padx=10)

    treeview_data(treeview)
    treeview.bind('<ButtonRelease-1>',
                  lambda event: select_data(event, product_name_entry, price_entry, quantity_entry,
                                            treeview,True,stock_label))

    return billing
