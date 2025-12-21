from tkinter import *
from tkinter import messagebox
import random
from billing import billing
from dashboard import dashboard
from employees import connect_database

# --- Generate random CAPTCHA ---
def generate_captcha():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    captcha = "".join(random.choices(chars, k=6))
    return captcha

# --- Login check function ---
def check_login(root, username_entry, password_entry, captcha_entry, captcha_value,
                show_form, dashboard, billing):
    user_id = username_entry.get().strip()
    user_pass = password_entry.get().strip()
    user_captcha = captcha_entry.get().strip()

    # ✅ Empty field check
    if user_id == "" or user_pass == "" or user_captcha == "":
        messagebox.showerror("Error", "Please fill all fields including CAPTCHA")
        return

    # ✅ CAPTCHA check
    if user_captcha != captcha_value.get():
        messagebox.showerror("Error", "Invalid CAPTCHA")
        return

    cursor, conn = connect_database()
    if not cursor or not conn:
        return

    try:
        cursor.execute("USE inventory_system")
        cursor.execute("SELECT emp_id, password, usertype FROM employee_data WHERE emp_id=%s AND password=%s",
                       (user_id, user_pass))
        result = cursor.fetchone()

        if result:
            emp_id, pwd, usertype = result
            messagebox.showinfo("Success", f"Login successful! Welcome {usertype.capitalize()}")

            if usertype.lower() == "admin":
                show_form(dashboard, root)
            elif usertype.lower() == "employee":
                show_form(billing, root)
            else:
                messagebox.showerror("Error", f"Unknown usertype: {usertype}")
        else:
            messagebox.showerror("Error", "Invalid ID or Password")

    except Exception as e:
        messagebox.showerror("Database Error", f"Error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Frame switching ---
current_frame = None
def show_form(form_function, root):
    global current_frame
    if current_frame:
        current_frame.place_forget()
    current_frame = form_function(root)

# --- GUI ---
root = Tk()
root.title('Login')
root.geometry('1270x668+20+20')
root.resizable(0, 0)
root.config(bg='white')

titleLabel = Label(root, compound=LEFT, text='Inventory Management System',
                   font=('times new roman', 35, 'bold'), bg='#434E78', fg='white',
                   anchor='center', justify='center', padx=20)
titleLabel.place(x=0, y=0, relwidth=1)

leftFrame = Frame(root)
leftFrame.place(x=50, y=100, width=500, height=500)

logo = PhotoImage(file='images/login.png')
imageLabel = Label(leftFrame, image=logo, bg='white')
imageLabel.pack()

rightFrame = Frame(root, bg='#F7E396')
rightFrame.place(x=750, y=100, width=380, height=500)

loginImage = PhotoImage(file='images/account.png')
imageLabel = Label(rightFrame, image=loginImage, bg='#F7E396')
imageLabel.pack()

signinLabel = Label(rightFrame, text='Login', font=('times new roman', 20),
                    fg='#434E78', bg='#F7E396')
signinLabel.pack(fill=X)

usernameLabel = Label(rightFrame, text='ID', font=('times new roman', 15),
                      fg='#434E78', anchor='w', bg='#F7E396')
usernameLabel.pack(fill=X, padx=20, pady=(20,0))
username_entry = Entry(rightFrame, font=('times new roman', 20),
                       bg='lightyellow', bd=0)
username_entry.pack(fill=X, anchor='w', padx=20)

passwordLabel = Label(rightFrame, text='Password', font=('times new roman', 15),
                      fg='#434E78', anchor='w', bg='#F7E396')
passwordLabel.pack(fill=X, padx=20, pady=(20,0))
password_entry = Entry(rightFrame, font=('times new roman', 20),
                       bg='lightyellow', bd=0, show="*")
password_entry.pack(fill=X, anchor='w', padx=20)

# --- ICONS for show/hide ---
show_icon = PhotoImage(file="images/show.png")
hide_icon = PhotoImage(file="images/hide.png")

def toggle_password():
    if password_entry.cget('show') == '':
        password_entry.config(show='*')
        toggle_btn.config(image=show_icon)
    else:
        password_entry.config(show='')
        toggle_btn.config(image=hide_icon)

toggle_btn = Button(rightFrame, image=show_icon, bg='white', bd=0,
                    cursor="hand2", command=toggle_password)
toggle_btn.place(x=330, y=300)

# --- CAPTCHA ---
captcha_value = StringVar()
captcha_value.set(generate_captcha())

captchaFrame = Frame(rightFrame, bg='#F7E396')
captchaFrame.pack(pady=(30,0))

captchaLabel = Label(captchaFrame, textvariable=captcha_value,
                     font=('times new roman', 14, 'bold'),
                     fg='blue', bg='#F7E396', width=8)
captchaLabel.grid(row=0, column=0, padx=(0,10))

captcha_entry = Entry(captchaFrame, font=('times new roman', 14),
                      bg='lightyellow', bd=0, width=12)
captcha_entry.grid(row=0, column=1, padx=(0,10))

# --- Refresh icon instead of text button ---
refresh_icon = PhotoImage(file="images/refresh.png")  # place your refresh icon in images folder
def refresh_captcha():
    captcha_value.set(generate_captcha())

refresh_btn = Button(captchaFrame, image=refresh_icon, bg='#F7E396',
                     bd=0, cursor="hand2", command=refresh_captcha)
refresh_btn.grid(row=0, column=2)

# --- Login button ---
signinButton = Button(rightFrame, text='Login', font=('times new roman', 15, 'bold'),
                      fg='white', bg='#434E78', cursor='hand2', bd=2, width=10,
                      command=lambda: check_login(root, username_entry, password_entry,
                                                  captcha_entry, captcha_value,
                                                  show_form, dashboard, billing))
signinButton.place(x=125, y=420)

root.mainloop()
