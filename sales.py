from tkinter import *
from tkinter import ttk
import os

# You need to install tkPDFViewer first:
# pip install tkPDFViewer

from tkPDFViewer import tkPDFViewer as pdf

def sales_form(root):
    global back_image
    sales_frame = Frame(root, width=1070, height=567, bg='white')
    sales_frame.place(x=200, y=100)

    # Heading bar
    heading_label = Label(sales_frame, text='Sales Info',
                          font=('times new roman', 16, 'bold'),
                          bg='#434E78', fg='white')
    heading_label.place(x=0, y=0, relwidth=1)

    back_image = PhotoImage(file='images/back.png')
    back_button = Button(sales_frame, image=back_image, bd=0, cursor='hand2', bg='white',
                         command=lambda: sales_frame.place_forget())
    back_button.place(x=20, y=35)

    # ---------------- Left Frame ----------------
    left_frame = Frame(sales_frame, bg="white", padx=20, pady=20)
    left_frame.place(x=10, y=100, width=300, height=400)

    total_sales_label = Label(left_frame, text="Total Sales: 0",
                              font=('times new roman', 16, 'bold'),
                              bg='#009688', fg='white', pady=10)
    total_sales_label.pack(fill=X, pady=(0, 20))

    invoice_label = Label(left_frame, text='Invoice No.',
                          font=('times new roman', 14, 'bold'), bg='white')
    invoice_label.pack(anchor="w", pady=(10, 5))

    invoice_entry = Entry(left_frame, font=('times new roman', 14, 'bold'),
                          bg='lightyellow', relief=SOLID, bd=2)
    invoice_entry.pack(fill=X, pady=(0, 15))

    search_button = Button(left_frame, text='Search',
                        font=('times new roman', 14, 'bold'),
                        width=12, cursor='hand2',
                        fg='white', bg='#434E78', bd=3, relief=RAISED)
    search_button.pack(pady=10)

    show_button = Button(left_frame, text='Show All',
                        font=('times new roman', 14, 'bold'),
                        width=12, cursor='hand2',
                        fg='white', bg='#434E78', bd=3, relief=RAISED)
    show_button.pack(pady=10)

    # ---------------- Center Frame ----------------
    center_frame = Frame(sales_frame, padx=10, pady=10, bg='white')
    center_frame.place(x=350, y=120, width=200, height=260)

    list_frame = Frame(center_frame, bg='white')
    list_frame.pack(fill=BOTH, expand=True)

    scrolly = Scrollbar(list_frame, orient=VERTICAL)
    bill_listbox = Listbox(list_frame, font=('times new roman', 12),
                           yscrollcommand=scrolly.set,
                           bg='white', justify=LEFT)
    bill_listbox.grid(row=0, column=0, sticky="nsew")
    scrolly.grid(row=0, column=1, sticky="ns")
    scrolly.config(command=bill_listbox.yview)

    list_frame.rowconfigure(0, weight=1)
    list_frame.columnconfigure(0, weight=1)

    # ---------------- Right Frame ----------------
    right_frame = Frame(sales_frame, padx=5, pady=5, bg='#CAF0F8')
    right_frame.place(x=630, y=120, width=380, height=260)

    # Container for PDF viewer
    pdf_container = Frame(right_frame, bg="white")
    pdf_container.pack(fill=BOTH, expand=True)

    # Load all bills from folder
    def load_bills():
        bill_listbox.delete(0, END)
        bill_folder = "bill"
        if not os.path.exists(bill_folder):
            os.makedirs(bill_folder)
        files = os.listdir(bill_folder)
        pdf_files = [f for f in files if f.lower().endswith(".pdf")]
        for f in pdf_files:
            bill_listbox.insert(END, f)
        # Update total sales label with all bills
        total_sales_label.config(text=f"Total Sales: {len(pdf_files)}")
        # Clear the search entry when showing all
        invoice_entry.delete(0, END)

    # Search for a specific invoice number
    def search_bill():
        bill_listbox.delete(0, END)
        query = invoice_entry.get().strip()
        bill_folder = "bill"
        if not os.path.exists(bill_folder):
            os.makedirs(bill_folder)
        files = os.listdir(bill_folder)
        pdf_files = [f for f in files if f.lower().endswith(".pdf")]
        matched = [f for f in pdf_files if query.lower() in f.lower()]
        for f in matched:
            bill_listbox.insert(END, f)
        # Do NOT change total sales label here

    search_button.config(command=search_bill)
    show_button.config(command=load_bills)

    # Function to display selected PDF in right frame
    def show_selected_bill(event):
        selection = bill_listbox.curselection()
        if selection:
            filename = bill_listbox.get(selection[0]).strip()
            bill_folder = "bill"
            filepath = os.path.join(bill_folder, filename)

            # Clear previous viewer
            for widget in pdf_container.winfo_children():
                widget.destroy()

            # Reset tkPDFViewer image cache
            pdf.ShowPdf.img_object_li.clear()

            # Create PDF viewer widget with safe progress bar handling
            v1 = pdf.ShowPdf()
            v2 = v1.pdf_view(pdf_container, pdf_location=filepath,
                             width=50, height=30, bar=False)
            v2.pack(fill=BOTH, expand=True)

    bill_listbox.bind("<Double-Button-1>", show_selected_bill)

    # Load bills initially
    load_bills()

    return sales_frame
