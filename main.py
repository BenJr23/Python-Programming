import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import font
import sqlite3
import bcrypt
import requests
import base64
from datetime import datetime
import os
from tkcalendar import DateEntry
logged_in_user_id = None
logged_in_user_name = None
logged_in_user_password = None
test = None
reservation_id = None


def setup_database():
    conn = sqlite3.connect('vehicle_rental.db')
    cursor = conn.cursor()

    # Define the schema
    schema = """
    CREATE TABLE IF NOT EXISTS VEHICLE(
        VehicleID INTEGER PRIMARY KEY AUTOINCREMENT,
        Make TEXT NOT NULL,
        Model TEXT NOT NULL,
        Year INTEGER NOT NULL,
        FuelType TEXT NOT NULL,
        DailyRentalPrice REAL NOT NULL,
        VehicleType TEXT NOT NULL,
        AvailabilityStatus TEXT NOT NULL,
        IsDeleted BOOLEAN NOT NULL DEFAULT 0,
        CreatedBy INTEGER,
        FOREIGN KEY (CreatedBy) REFERENCES EMPLOYEE(EmployeeID)
    );

    CREATE TABLE IF NOT EXISTS CAR(
        VehicleID INTEGER PRIMARY KEY,
        BodyStyle TEXT NOT NULL,
        TransmissionType TEXT NOT NULL,
        NumberOfDoors INTEGER NOT NULL,
        IsDeleted BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (VehicleID) REFERENCES VEHICLE(VehicleID)
    );

    CREATE TABLE IF NOT EXISTS TRUCK(
        VehicleID INTEGER PRIMARY KEY,
        PayLoadCapacity REAL NOT NULL,
        TruckBedSize TEXT NOT NULL,
        NumberOfAxles INTEGER NOT NULL,
        IsDeleted BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (VehicleID) REFERENCES VEHICLE(VehicleID)
    );

    CREATE TABLE IF NOT EXISTS MOTORCYCLE(
        VehicleID INTEGER PRIMARY KEY,
        EngineDisplacement REAL NOT NULL,
        Type TEXT NOT NULL,
        IsDeleted BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (VehicleID) REFERENCES VEHICLE(VehicleID)
    );

    CREATE TABLE IF NOT EXISTS EMPLOYEE(
        EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmpEmail TEXT UNIQUE NOT NULL,
        EmpUserName TEXT UNIQUE NOT NULL,
        EmpHashPassword TEXT NOT NULL,
        EmpPasswordSalt TEXT NOT NULL,
        EmpFirstName TEXT NOT NULL,
        EmpMiddleName TEXT,
        EmpLastName TEXT NOT NULL,
        EmpSuffix TEXT,
        EmpPhoneNumber TEXT NOT NULL,
        EmployeeType TEXT NOT NULL,
        IsDeleted BOOLEAN NOT NULL DEFAULT 0,
        CreatedBy INTEGER,
        Photo BLOB,
        FOREIGN KEY (CreatedBy) REFERENCES EMPLOYEE(EmployeeID)
    );

    CREATE TABLE IF NOT EXISTS RESERVATION(
        ReservationID INTEGER PRIMARY KEY AUTOINCREMENT,
        VehicleID INTEGER NOT NULL,
        EmployeeID INTEGER NOT NULL,
        CustomerFirstName TEXT NOT NULL,
        CustomerMiddleName TEXT,
        CustomerLastName TEXT NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        PhoneNumber TEXT NOT NULL,
        StreetAddress TEXT NOT NULL,
        Brgy TEXT NOT NULL,
        City TEXT NOT NULL,
        Zipcode TEXT NOT NULL,
        ReservationDate DATE NOT NULL,
        RentalStartDate DATE NOT NULL,
        RentalEndDate DATE NOT NULL,
        TotalCost REAL NOT NULL,
        Status TEXT NOT NULL,
        IsDeleted BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (VehicleID) REFERENCES VEHICLE(VehicleID),
        FOREIGN KEY (EmployeeID) REFERENCES EMPLOYEE(EmployeeID)
    );


    CREATE TABLE IF NOT EXISTS PAYMENT(
        PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
        ReservationID INTEGER NOT NULL,
        PaymentAmount REAL NOT NULL,
        PaymentMethod TEXT NOT NULL,
        PaymentStatus TEXT NOT NULL,
        IsDeleted BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (ReservationID) REFERENCES RESERVATION(ReservationID)
    );
    """

    # Execute the schema
    cursor.executescript(schema)
    conn.commit()
    conn.close()


def create_admin_employee():
    conn = sqlite3.connect('vehicle_rental.db')
    cursor = conn.cursor()

    # Check if the admin account already exists
    cursor.execute("SELECT * FROM EMPLOYEE WHERE EmpUserName = 'RubenAdmin'")
    admin_exists = cursor.fetchone()

    if admin_exists:
        conn.close()
        return
    password = "benjr23"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    # Hashing the password
    hashed = bcrypt.hashpw(password_bytes, salt)

    admin_employee = {
        'EmpEmail': 'rubenjrtbertuso@gmail.com',
        'EmpUserName': 'RubenAdmin',
        'EmpHashPassword': hashed,  # Ideally, use a secure hash
        'EmpPasswordSalt': salt,
        'EmpFirstName': 'Ruben Jr',
        'EmpMiddleName': 'Tapiod',
        'EmpLastName': 'Bertuso',
        'EmpSuffix': None,
        'EmpPhoneNumber': '09272914369',
        'EmployeeType': 'Admin',
        'IsDeleted': 0,
        'CreatedBy': None
    }

    cursor.execute("""
    INSERT INTO EMPLOYEE (EmpEmail, EmpUserName, EmpHashPassword, EmpPasswordSalt, EmpFirstName, EmpMiddleName, EmpLastName, EmpSuffix, EmpPhoneNumber, EmployeeType, IsDeleted, CreatedBy)
    VALUES (:EmpEmail, :EmpUserName, :EmpHashPassword, :EmpPasswordSalt, :EmpFirstName, :EmpMiddleName, :EmpLastName, :EmpSuffix, :EmpPhoneNumber, :EmployeeType, :IsDeleted, :CreatedBy)
    """, admin_employee)

    conn.commit()
    conn.close()


def main():
    global logged_in_user_id
    global logged_in_user_name
    global logged_in_user_password
    global test

    def log_in():
        global logged_in_user_id
        global logged_in_user_name
        global logged_in_user_password
        global test
        window2.withdraw()
        window1.deiconify()
        logged_in_user_id = None
        logged_in_user_name = None
        logged_in_user_password = None

    def admin_window():
        window1.withdraw()
        window2.deiconify()


    def clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()


    def check_login():
        global logged_in_user_id
        global logged_in_user_name
        global logged_in_user_password
        global test
        username = username_entry.get()

        conn = sqlite3.connect('vehicle_rental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EMPLOYEE WHERE EmpUserName=?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result is None:
            messagebox.showerror("Login Failed", "Invalid username or password")
            return

        password = password_entry.get()
        salt = result[4]
        password_bytes = password.encode('utf-8')
        emp_hash_password = bcrypt.hashpw(password_bytes, salt)
        retrieved_password = result[3]

        if emp_hash_password == retrieved_password:
            logged_in_user_id = result[0]  # Store the logged-in user's ID
            logged_in_user_name = username
            logged_in_user_password = password
            employee_type = result[10] # column of employee type
            if employee_type == 'Admin':
                test = 1
                admin_window()

            elif employee_type == 'Staff':
                window1.destroy()
                test = 1
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def account_management_panel():
        def create_employee():
            def submit_employee():
                password = emp_password_entry.get()
                password_bytes = password.encode('utf-8')
                salt = bcrypt.gensalt()
                emp_email = emp_email_entry.get()
                emp_username = emp_username_entry.get()
                emp_hash_password = bcrypt.hashpw(password_bytes, salt)
                emp_password_salt = salt
                emp_first_name = emp_first_name_entry.get()
                emp_middle_name = emp_middle_name_entry.get()
                emp_last_name = emp_last_name_entry.get()
                emp_suffix = emp_suffix_entry.get()
                emp_phone_number = emp_phone_number_entry.get()
                employee_type = employee_type_combobox.get()
                emp_isdeleted = 0

                if not employee_type:
                    messagebox.showerror("Error", "Please select an employee type")
                    return

                if not emp_email:
                    messagebox.showerror("Error", "Email cannot be empty")
                    return

                if not emp_username:
                    messagebox.showerror("Error", "User name cannot be empty")
                    return

                if not password:
                    messagebox.showerror("Error", "Password cannot be empty")
                    return

                if not emp_first_name:
                    messagebox.showerror("Error", "Field cannot be empty")
                    return

                if not emp_last_name:
                    messagebox.showerror("Error", "Field cannot be empty")
                    return

                if not emp_phone_number:
                    messagebox.showerror("Error", "Contact number cannot be empty")
                    return

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                new_employee = {
                    'EmpEmail': emp_email,
                    'EmpUserName': emp_username,
                    'EmpHashPassword': emp_hash_password,
                    'EmpPasswordSalt': emp_password_salt,
                    'EmpFirstName': emp_first_name,
                    'EmpMiddleName': emp_middle_name,
                    'EmpLastName': emp_last_name,
                    'EmpSuffix': emp_suffix,
                    'EmpPhoneNumber': emp_phone_number,
                    'EmployeeType': employee_type,
                    'IsDeleted': emp_isdeleted,
                    'CreatedBy': logged_in_user_id  # Use the global variable for CreatedBy
                }

                cursor.execute("""
                    INSERT INTO EMPLOYEE (EmpEmail, EmpUserName, EmpHashPassword, EmpPasswordSalt, EmpFirstName, EmpMiddleName, EmpLastName, EmpSuffix, EmpPhoneNumber, EmployeeType, IsDeleted, CreatedBy)
                    VALUES (:EmpEmail, :EmpUserName, :EmpHashPassword, :EmpPasswordSalt, :EmpFirstName, :EmpMiddleName, :EmpLastName, :EmpSuffix, :EmpPhoneNumber, :EmployeeType, :IsDeleted, :CreatedBy)
                    """, new_employee)

                conn.commit()
                conn.close()
                load_employees()
                create_employee_window.destroy()

            create_employee_window = tk.Toplevel(window2)
            create_employee_window.title("Create Employee")
            create_employee_window.geometry("1080x800")

            # Load the background image
            bg_image_path = r"C:\Users\Styvn\VRMS\resources\images\2.png"  # Update with the correct path
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((1920, 1080))
            bg_image_tk = ImageTk.PhotoImage(bg_image)

            # Load the logo image
            logo_image_path = r"C:\Users\Styvn\VRMS\resources\images\1.png"  # Update with the correct path
            logo_image = Image.open(logo_image_path)
            logo_image = logo_image.resize((100, 60))
            logo_image_tk = ImageTk.PhotoImage(logo_image)

            # Create a canvas to hold the background image
            canvas = tk.Canvas(create_employee_window, width=1080, height=720)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(0, 0, image=bg_image_tk, anchor="nw")

            # Create the form frame on top of the canvas
            form_frame = tk.Frame(canvas, bg="#f0f0f0", bd=5, relief="groove")
            form_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=450)

            # Create form fields
            tk.Label(form_frame, text="Create Account", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(1, 20))

            emp_email_label = tk.Label(form_frame, text="Email", bg="#f0f0f0")
            emp_email_label.place(relx=0.5, rely=0.2, anchor='center', width=200, height=30)
            emp_email_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            emp_email_entry.place(relx=0.5, rely=0.25, anchor='center', width=341, height=30)

            emp_username_label = tk.Label(form_frame, text="Username", bg="#f0f0f0")
            emp_username_label.place(relx=0.5, rely=0.3, anchor='center', width=200, height=30)
            emp_username_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            emp_username_entry.place(relx=0.5, rely=0.35, anchor='center', width=341, height=30)

            emp_password_label = tk.Label(form_frame, text="Password", bg="#f0f0f0")
            emp_password_label.place(relx=0.5, rely=0.4, anchor='center', width=200, height=30)
            emp_password_entry = tk.Entry(form_frame, show="*", bg='#f0f0f0', fg='black', font=title_font)
            emp_password_entry.place(relx=0.5, rely=0.45, anchor='center', width=341, height=30)

            emp_first_name_label = tk.Label(form_frame, text="First Name", bg="#f0f0f0")
            emp_first_name_label.place(relx=0.25, rely=0.5, anchor='center', width=200, height=30)
            emp_first_name_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            emp_first_name_entry.place(relx=0.25, rely=0.55, anchor='center', width=150, height=30)

            emp_middle_name_label = tk.Label(form_frame, text="Middle Name", bg="#f0f0f0")
            emp_middle_name_label.place(relx=0.75, rely=0.5, anchor='center', width=200, height=30)
            emp_middle_name_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            emp_middle_name_entry.place(relx=0.75, rely=0.55, anchor='center', width=150, height=30)

            emp_last_name_label = tk.Label(form_frame, text="Last Name", bg="#f0f0f0")
            emp_last_name_label.place(relx=0.25, rely=0.6, anchor='center', width=200, height=30)
            emp_last_name_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            emp_last_name_entry.place(relx=0.25, rely=0.65, anchor='center', width=150, height=30)

            emp_suffix_label = tk.Label(form_frame, text="Suffix", bg="#f0f0f0")
            emp_suffix_label.place(relx=0.75, rely=0.6, anchor='center', width=200, height=30)
            emp_suffix_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            emp_suffix_entry.place(relx=0.75, rely=0.65, anchor='center', width=100, height=30)

            emp_phone_number_label = tk.Label(form_frame, text="Phone Number", bg="#f0f0f0")
            emp_phone_number_label.place(relx=0.5, rely=0.7, anchor='center', width=200, height=30)
            emp_phone_number_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            emp_phone_number_entry.place(relx=0.5, rely=0.75, anchor='center', width=200, height=30)

            employee_type_label = tk.Label(form_frame, text="Employee Type", bg="#f0f0f0")
            employee_type_label.place(relx=0.5, rely=0.8, anchor='center', width=200, height=30)
            employee_type_combobox = ttk.Combobox(form_frame, values=["Admin", "Staff"], state="readonly")
            employee_type_combobox.place(relx=0.5, rely=0.85, anchor='center', width=200, height=30)

            # Submit button
            submit_button = tk.Button(form_frame, text="Submit", command=submit_employee)
            submit_button.place(relx=0.5, rely=.95, anchor='center', width=200, height=40)

            # Keep a reference to the background and logo images
            create_employee_window.bg_image_tk = bg_image_tk

        def edit_employee():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "No account is selected")
                return

            item = tree.item(selected_item)
            employee_id = item['values'][0]
            emp_email = item['values'][1]
            emp_username = item['values'][2]
            emp_first_name = item['values'][3]
            emp_middle_name = item['values'][4]
            emp_last_name = item['values'][5]
            emp_suffix = item['values'][6]
            emp_phone_number = item['values'][7]
            employee_type = item['values'][8]

            def submit_employee_changes():
                new_emp_email = emp_email_entry.get()
                new_emp_username = emp_username_entry.get()
                new_emp_first_name = emp_first_name_entry.get()
                new_emp_middle_name = emp_middle_name_entry.get()
                new_emp_last_name = emp_last_name_entry.get()
                new_emp_suffix = emp_suffix_entry.get()
                new_emp_phone_number = emp_phone_number_entry.get()
                new_employee_type = employee_type_combobox.get()

                if not new_employee_type:
                    messagebox.showerror("Error", "Please select an employee type")
                    return

                if not new_emp_email:
                    messagebox.showerror("Error", "Email cannot be empty")
                    return

                if not new_emp_username:
                    messagebox.showerror("Error", "User name cannot be empty")
                    return

                if not new_emp_first_name:
                    messagebox.showerror("Error", "Field cannot be empty")
                    return

                if not new_emp_last_name:
                    messagebox.showerror("Error", "Field cannot be empty")
                    return

                if not new_emp_phone_number:
                    messagebox.showerror("Error", "Contact number cannot be empty")
                    return

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                cursor.execute("""
                UPDATE EMPLOYEE
                SET EmpEmail = ?, EmpUserName = ?, EmpFirstName = ?, EmpMiddleName = ?, EmpLastName = ?, EmpSuffix = ?, EmpPhoneNumber = ?, EmployeeType = ?
                WHERE EmployeeID = ?
                """, (new_emp_email, new_emp_username, new_emp_first_name, new_emp_middle_name,
                      new_emp_last_name, new_emp_suffix, new_emp_phone_number, new_employee_type, employee_id))

                conn.commit()
                conn.close()
                load_employees()
                edit_employee_window.destroy()

            edit_employee_window = tk.Toplevel(window2)
            edit_employee_window.title("Edit Employee")
            edit_employee_window.geometry("600x600")

            # Load and set the background image
            background_image = Image.open(r"C:\Users\Styvn\VRMS\resources\images\2.png")
            background_image = background_image.resize((1900, 800))
            bg_image = ImageTk.PhotoImage(background_image)

            canvas = tk.Canvas(edit_employee_window, width=600, height=600)
            canvas.pack(fill='both', expand=True)
            canvas.create_image(0, 0, image=bg_image, anchor='nw')

            # Create a frame for the form with a specific background color
            form_frame = tk.Frame(edit_employee_window, bg='#1E5A2A', bd=5)
            form_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=700)

            # Create and add form fields
            def add_form_field(parent, label_text, default_value):
                label = tk.Label(parent, text=label_text, bg='#1E5A2A', fg='white', font=('Helvetica', 12, 'bold'))
                label.pack(pady=5, anchor='w')
                entry = tk.Entry(parent, font=('Helvetica', 12))
                entry.insert(0, default_value)
                entry.pack(pady=5, fill='x', padx=20)
                return entry

            emp_email_entry = add_form_field(form_frame, "Email", emp_email)
            emp_username_entry = add_form_field(form_frame, "Username", emp_username)
            emp_password_entry = add_form_field(form_frame, "Password", "")
            emp_password_entry.config(show='*')  # Configure it to show asterisks for password masking
            emp_first_name_entry = add_form_field(form_frame, "First Name", emp_first_name)
            emp_middle_name_entry = add_form_field(form_frame, "Middle Name", emp_middle_name)
            emp_last_name_entry = add_form_field(form_frame, "Last Name", emp_last_name)
            emp_suffix_entry = add_form_field(form_frame, "Suffix", emp_suffix)
            emp_phone_number_entry = add_form_field(form_frame, "Phone Number", emp_phone_number)

            employee_type_label = tk.Label(form_frame, text="Employee Type", bg='#1E5A2A', fg='white',
                                           font=('Helvetica', 12, 'bold'))
            employee_type_label.pack(pady=5, anchor='w')
            employee_type_combobox = ttk.Combobox(form_frame, values=["Admin", "Staff"], state="readonly",
                                                  font=('Helvetica', 12))
            employee_type_combobox.set(employee_type)
            employee_type_combobox.pack(pady=5, fill='x', padx=20)

            # Create a frame for the buttons
            button_frame = tk.Frame(form_frame, bg='#1E5A2A')
            button_frame.pack(pady=20)

            # Submit button
            submit_button = tk.Button(button_frame, text="Save Changes", command=submit_employee_changes, bg='#FFC107',
                                      fg='black', font=('Helvetica', 12, 'bold'))
            submit_button.pack(side='left', padx=10)

            # Cancel button
            cancel_button = tk.Button(button_frame, text="Cancel", command=edit_employee_window.destroy, bg='#D32F2F',
                                      fg='white', font=('Helvetica', 12, 'bold'))
            cancel_button.pack(side='left', padx=10)

            # Keep a reference to the image to prevent it from being garbage collected
            edit_employee_window.bg_image = bg_image



        def delete_employee():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "No account is selected")
                return

            item = tree.item(selected_item)
            employee_id = item['values'][0]

            if employee_id == logged_in_user_id:
                messagebox.showerror("Error", "Cannot delete the account currently in use")
                return

            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected account?")
            if not confirm:
                return

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE EMPLOYEE SET IsDeleted = 1 WHERE EmployeeID = ?", (employee_id,))
            conn.commit()
            load_employees()
            conn.close()

        def load_employees():
            for row in tree.get_children():
                tree.delete(row)
            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT EmployeeID, EmpEmail, EmpUserName, EmpFirstName, EmpMiddleName, EmpLastName, EmpSuffix, EmpPhoneNumber, EmployeeType, CreatedBy"
                " FROM EMPLOYEE"
                " WHERE IsDeleted = 0")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            conn.close()

        clear_frame(content_frame_main)
        columns = (
            "EmployeeID", "EmpEmail", "EmpUserName",
            "EmpFirstName", "EmpMiddleName", "EmpLastName", "EmpSuffix", "EmpPhoneNumber",
            "EmployeeType", "CreatedBy"
        )
        tree = ttk.Treeview(content_frame_main, columns=columns, show='headings')
        tree.heading("EmployeeID", text="ID")
        tree.column("EmployeeID", width=10)
        tree.heading("EmpEmail", text="Email")
        tree.column("EmpEmail", width=150)
        tree.heading("EmpUserName", text="Username")
        tree.column("EmpUserName", width=50)
        tree.heading("EmpFirstName", text="First Name")
        tree.column("EmpFirstName", width=50)
        tree.heading("EmpMiddleName", text="Middle Name")
        tree.column("EmpMiddleName", width=50)
        tree.heading("EmpLastName", text="Last Name")
        tree.column("EmpLastName", width=50)
        tree.heading("EmpSuffix", text="Suffix")
        tree.column("EmpSuffix", width=20)
        tree.heading("EmpPhoneNumber", text="Phone Number")
        tree.column("EmpPhoneNumber", width=70)
        tree.heading("EmployeeType", text="Type")
        tree.column("EmployeeType", width=50)
        tree.heading("CreatedBy", text="Created By")
        tree.column("CreatedBy", width=30)

        tree.pack(expand=True, fill='both')

        # Create buttons for CRUD operations
        button_frame = tk.Frame(content_frame_main)
        button_frame.pack(fill='x', pady=10)

        create_button = tk.Button(button_frame, text="CREATE", command=create_employee, bg="yellow")
        create_button.pack(side='left', padx=5)

        read_button = tk.Button(button_frame, text="EDIT", command=edit_employee, bg="lightblue")
        read_button.pack(side='left', padx=5)

        delete_button = tk.Button(button_frame, text="DELETE", command=delete_employee, bg="red", fg="white")
        delete_button.pack(side='left', padx=5)

        load_employees()



    def vehicle_management_panel():
        def create_car():
            def submit_car():
                make = make_entry.get()
                model = model_entry.get()
                year = year_entry.get()
                fuel_type = fuel_type_combobox.get()
                daily_rental_price = daily_rental_price_entry.get()
                body_style = body_style_entry.get()
                transmission_type = transmission_type_entry.get()
                number_of_doors = number_of_doors_entry.get()
                availability_status = availability_status_combobox.get()
                is_deleted = 0
                created_by = logged_in_user_id

                if not make or not model or not year or not fuel_type or not daily_rental_price or not body_style or not transmission_type or not number_of_doors or not availability_status:
                    messagebox.showerror("Error", "Please fill in all fields")
                    return

                # Insert into VEHICLE and CAR tables
                vehicle_data = {
                    'Make': make,
                    'Model': model,
                    'Year': year,
                    'FuelType': fuel_type,
                    'DailyRentalPrice': daily_rental_price,
                    'VehicleType': 'Car',
                    'AvailabilityStatus': availability_status,
                    'IsDeleted': is_deleted,
                    'CreatedBy': created_by
                }

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO VEHICLE (Make, Model, Year, FuelType, DailyRentalPrice, VehicleType, AvailabilityStatus, IsDeleted, CreatedBy)
                    VALUES (:Make, :Model, :Year, :FuelType, :DailyRentalPrice, :VehicleType, :AvailabilityStatus, :IsDeleted, :CreatedBy)
                """, vehicle_data)

                # Retrieve the last inserted VehicleID
                vehicle_id = cursor.lastrowid

                car_data = {
                    'VehicleID': vehicle_id,
                    'BodyStyle': body_style,
                    'TransmissionType': transmission_type,
                    'NumberOfDoors': number_of_doors,
                    'IsDeleted': is_deleted
                }

                cursor.execute("""
                    INSERT INTO CAR (VehicleID, BodyStyle, TransmissionType, NumberOfDoors, IsDeleted)
                    VALUES (:VehicleID, :BodyStyle, :TransmissionType, :NumberOfDoors, :IsDeleted)
                """, car_data)

                conn.commit()
                conn.close()

                # Optional: Display confirmation message or navigate to another view
                vehicle_car_window_admin()
                messagebox.showinfo("Success", "Car created successfully")
                create_car_window.destroy()

            # Create the car creation window
            create_car_window = tk.Toplevel(window2)
            create_car_window.title("Create Car")
            create_car_window.geometry("1080x800")

            # Load the background image
            bg_image_path = r"C:\Users\Styvn\VRMS\resources\images\2.png"  # Update with the correct path
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((1920, 1080))
            bg_image_tk = ImageTk.PhotoImage(bg_image)

            # Load the logo image
            logo_image_path = r"C:\Users\Styvn\VRMS\resources\images\1.png"  # Update with the correct path
            logo_image = Image.open(logo_image_path)
            logo_image = logo_image.resize((100, 60))
            logo_image_tk = ImageTk.PhotoImage(logo_image)

            # Create a canvas to hold the background image
            canvas = tk.Canvas(create_car_window, width=1080, height=720)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(0, 0, image=bg_image_tk, anchor="nw")

            # Create the form frame on top of the canvas
            form_frame = tk.Frame(canvas, bg="#f0f0f0", bd=5, relief="groove")
            form_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=700)

            # Create form fields
            tk.Label(form_frame, text="Create Car", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(1, 20))

            # Form Fields
            make_label = tk.Label(form_frame, text="Make", bg="#f0f0f0")
            make_label.place(relx=0.5, rely=0.05, anchor='center', width=200, height=30)
            make_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            make_entry.place(relx=0.5, rely=0.1, anchor='center', width=341, height=30)

            model_label = tk.Label(form_frame, text="Model", bg="#f0f0f0")
            model_label.place(relx=0.5, rely=0.15, anchor='center', width=200, height=30)
            model_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            model_entry.place(relx=0.5, rely=0.2, anchor='center', width=341, height=30)

            year_label = tk.Label(form_frame, text="Year", bg="#f0f0f0")
            year_label.place(relx=0.5, rely=0.25, anchor='center', width=200, height=30)
            year_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            year_entry.place(relx=0.5, rely=0.3, anchor='center', width=341, height=30)

            fuel_type_label = tk.Label(form_frame, text="Fuel Type", bg="#f0f0f0")
            fuel_type_label.place(relx=0.5, rely=0.35, anchor='center', width=200, height=30)
            fuel_type_combobox = ttk.Combobox(form_frame, values=["Gasoline", "Diesel", "Electric", "Hybrid"],
                                              state="readonly")
            fuel_type_combobox.place(relx=0.5, rely=0.4, anchor='center', width=341, height=30)

            daily_rental_price_label = tk.Label(form_frame, text="Daily Rental Price", bg="#f0f0f0")
            daily_rental_price_label.place(relx=0.5, rely=0.45, anchor='center', width=200, height=30)
            daily_rental_price_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            daily_rental_price_entry.place(relx=0.5, rely=0.5, anchor='center', width=341, height=30)

            body_style_label = tk.Label(form_frame, text="Body Style", bg="#f0f0f0")
            body_style_label.place(relx=0.5, rely=0.55, anchor='center', width=200, height=30)
            body_style_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            body_style_entry.place(relx=0.5, rely=0.6, anchor='center', width=341, height=30)

            transmission_type_label = tk.Label(form_frame, text="Transmission Type", bg="#f0f0f0")
            transmission_type_label.place(relx=0.5, rely=0.65, anchor='center', width=200, height=30)
            transmission_type_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            transmission_type_entry.place(relx=0.5, rely=0.7, anchor='center', width=341, height=30)

            number_of_doors_label = tk.Label(form_frame, text="Number of Doors", bg="#f0f0f0")
            number_of_doors_label.place(relx=0.5, rely=0.75, anchor='center', width=200, height=30)
            number_of_doors_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            number_of_doors_entry.place(relx=0.5, rely=0.8, anchor='center', width=341, height=30)

            availability_status_label = tk.Label(form_frame, text="Availability Status", bg="#f0f0f0")
            availability_status_label.place(relx=0.5, rely=0.85, anchor='center', width=200, height=30)
            availability_status_combobox = ttk.Combobox(form_frame, values=["Available", "Unavailable", "Leased"],
                                                        state="readonly")
            availability_status_combobox.place(relx=0.5, rely=0.9, anchor='center', width=341, height=30)

            # Submit button
            submit_button = tk.Button(form_frame, text="Submit", command=submit_car)
            submit_button.place(relx=0.5, rely=0.97, anchor='center', width=200, height=40)

            # Keep a reference to the background and logo images
            create_car_window.bg_image_tk = bg_image_tk

        def create_truck():
            def submit_truck():
                make = make_entry.get()
                model = model_entry.get()
                year = year_entry.get()
                fuel_type = fuel_type_combobox.get()
                daily_rental_price = daily_rental_price_entry.get()
                payload_capacity = payload_capacity_entry.get()
                truck_bed_size = truck_bed_size_entry.get()
                number_of_axles = number_of_axles_entry.get()
                availability_status = availability_status_combobox.get()
                is_deleted = 0
                created_by = logged_in_user_id

                if not make or not model or not year or not fuel_type or not daily_rental_price or not payload_capacity or not truck_bed_size or not number_of_axles or not availability_status:
                    messagebox.showerror("Error", "Please fill in all fields")
                    return

                # Insert into VEHICLE table
                vehicle_data = {
                    'Make': make,
                    'Model': model,
                    'Year': year,
                    'FuelType': fuel_type,
                    'DailyRentalPrice': daily_rental_price,
                    'VehicleType': 'Truck',
                    'AvailabilityStatus': availability_status,
                    'IsDeleted': is_deleted,
                    'CreatedBy': created_by
                }

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO VEHICLE (Make, Model, Year, FuelType, DailyRentalPrice, VehicleType, AvailabilityStatus, IsDeleted, CreatedBy)
                    VALUES (:Make, :Model, :Year, :FuelType, :DailyRentalPrice, :VehicleType, :AvailabilityStatus, :IsDeleted, :CreatedBy)
                """, vehicle_data)

                # Retrieve the last inserted VehicleID
                vehicle_id = cursor.lastrowid

                # Insert into TRUCK table
                truck_data = {
                    'VehicleID': vehicle_id,
                    'PayloadCapacity': payload_capacity,
                    'TruckBedSize': truck_bed_size,
                    'NumberOfAxles': number_of_axles,
                    'IsDeleted': is_deleted
                }

                cursor.execute("""
                    INSERT INTO TRUCK (VehicleID, PayloadCapacity, TruckBedSize, NumberOfAxles, IsDeleted)
                    VALUES (:VehicleID, :PayloadCapacity, :TruckBedSize, :NumberOfAxles, :IsDeleted)
                """, truck_data)

                conn.commit()
                conn.close()

                # Optional: Display confirmation message or navigate to another view
                vehicle_truck_window_admin()
                messagebox.showinfo("Success", "Truck created successfully")
                create_truck_window.destroy()

            # Create the truck creation window
            create_truck_window = tk.Toplevel(window2)
            create_truck_window.title("Create Truck")
            create_truck_window.geometry("1080x800")

            # Load the background image
            bg_image_path = r"C:\Users\Styvn\VRMS\resources\images\2.png" # Update with the correct path
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((1920, 1080))
            bg_image_tk = ImageTk.PhotoImage(bg_image)

            # Create a canvas to hold the background image
            canvas = tk.Canvas(create_truck_window, width=1080, height=720)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(0, 0, image=bg_image_tk, anchor="nw")

            # Create the form frame on top of the canvas
            form_frame = tk.Frame(canvas, bg="#f0f0f0", bd=5, relief="groove")
            form_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=700)

            # Create form fields
            tk.Label(form_frame, text="Create Truck", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(1, 20))

            # Form Fields
            make_label = tk.Label(form_frame, text="Make", bg="#f0f0f0")
            make_label.place(relx=0.5, rely=0.05, anchor='center', width=200, height=30)
            make_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            make_entry.place(relx=0.5, rely=0.1, anchor='center', width=341, height=30)

            model_label = tk.Label(form_frame, text="Model", bg="#f0f0f0")
            model_label.place(relx=0.5, rely=0.15, anchor='center', width=200, height=30)
            model_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            model_entry.place(relx=0.5, rely=0.2, anchor='center', width=341, height=30)

            year_label = tk.Label(form_frame, text="Year", bg="#f0f0f0")
            year_label.place(relx=0.5, rely=0.25, anchor='center', width=200, height=30)
            year_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            year_entry.place(relx=0.5, rely=0.3, anchor='center', width=341, height=30)

            fuel_type_label = tk.Label(form_frame, text="Fuel Type", bg="#f0f0f0")
            fuel_type_label.place(relx=0.5, rely=0.35, anchor='center', width=200, height=30)
            fuel_type_combobox = ttk.Combobox(form_frame, values=["Gasoline", "Diesel", "Electric", "Hybrid"],
                                              state="readonly")
            fuel_type_combobox.place(relx=0.5, rely=0.4, anchor='center', width=341, height=30)

            daily_rental_price_label = tk.Label(form_frame, text="Daily Rental Price", bg="#f0f0f0")
            daily_rental_price_label.place(relx=0.5, rely=0.45, anchor='center', width=200, height=30)
            daily_rental_price_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            daily_rental_price_entry.place(relx=0.5, rely=0.5, anchor='center', width=341, height=30)

            payload_capacity_label = tk.Label(form_frame, text="Payload Capacity", bg="#f0f0f0")
            payload_capacity_label.place(relx=0.5, rely=0.55, anchor='center', width=200, height=30)
            payload_capacity_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            payload_capacity_entry.place(relx=0.5, rely=0.6, anchor='center', width=341, height=30)

            truck_bed_size_label = tk.Label(form_frame, text="Truck Bed Size", bg="#f0f0f0")
            truck_bed_size_label.place(relx=0.5, rely=0.65, anchor='center', width=200, height=30)
            truck_bed_size_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            truck_bed_size_entry.place(relx=0.5, rely=0.7, anchor='center', width=341, height=30)

            number_of_axles_label = tk.Label(form_frame, text="Number of Axles", bg="#f0f0f0")
            number_of_axles_label.place(relx=0.5, rely=0.75, anchor='center', width=200, height=30)
            number_of_axles_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            number_of_axles_entry.place(relx=0.5, rely=0.8, anchor='center', width=341, height=30)

            availability_status_label = tk.Label(form_frame, text="Availability Status", bg="#f0f0f0")
            availability_status_label.place(relx=0.5, rely=0.85, anchor='center', width=200, height=30)
            availability_status_combobox = ttk.Combobox(form_frame, values=["Available", "Unavailable", "Leased"],
                                                        state="readonly")
            availability_status_combobox.place(relx=0.5, rely=0.9, anchor='center', width=341, height=30)

            # Submit button
            submit_button = tk.Button(form_frame, text="Submit", command=submit_truck)
            submit_button.place(relx=0.5, rely=0.97, anchor='center', width=200, height=40)

            # Keep a reference to the background and logo images
            create_truck_window.bg_image_tk = bg_image_tk

        def create_motorcycle():
            def submit_motorcycle():
                make = make_entry.get()
                model = model_entry.get()
                year = year_entry.get()
                fuel_type = fuel_type_combobox.get()
                daily_rental_price = daily_rental_price_entry.get()
                engine_displacement = engine_displacement_entry.get()
                type = type_entry.get()
                availability_status = availability_status_combobox.get()
                is_deleted = 0
                created_by = logged_in_user_id

                if not make or not model or not year or not fuel_type or not daily_rental_price or not engine_displacement or not type or not availability_status:
                    messagebox.showerror("Error", "Please fill in all fields")
                    return

                # Insert into VEHICLE table
                vehicle_data = {
                    'Make': make,
                    'Model': model,
                    'Year': year,
                    'FuelType': fuel_type,
                    'DailyRentalPrice': daily_rental_price,
                    'VehicleType': 'Motorcycle',
                    'AvailabilityStatus': availability_status,
                    'IsDeleted': is_deleted,
                    'CreatedBy': created_by
                }

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO VEHICLE (Make, Model, Year, FuelType, DailyRentalPrice, VehicleType, AvailabilityStatus, IsDeleted, CreatedBy)
                    VALUES (:Make, :Model, :Year, :FuelType, :DailyRentalPrice, :VehicleType, :AvailabilityStatus, :IsDeleted, :CreatedBy)
                """, vehicle_data)

                # Retrieve the last inserted VehicleID
                vehicle_id = cursor.lastrowid

                # Insert into MOTORCYCLE table
                motorcycle_data = {
                    'VehicleID': vehicle_id,
                    'EngineDisplacement': engine_displacement,
                    'Type': type,
                    'IsDeleted': is_deleted
                }

                cursor.execute("""
                    INSERT INTO MOTORCYCLE (VehicleID, EngineDisplacement, Type, IsDeleted)
                    VALUES (:VehicleID, :EngineDisplacement, :Type, :IsDeleted)
                """, motorcycle_data)

                conn.commit()
                conn.close()

                # Optional: Display confirmation message or navigate to another view
                vehicle_motorcycle_window_admin()
                messagebox.showinfo("Success", "Motorcycle created successfully")
                create_motorcycle_window.destroy()

            # Create the motorcycle creation window
            create_motorcycle_window = tk.Toplevel(window2)
            create_motorcycle_window.title("Create Motorcycle")
            create_motorcycle_window.geometry("1080x800")

            # Load the background image
            bg_image_path = r"C:\Users\Styvn\VRMS\resources\images\2.png"  # Update with the correct path
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((1920, 1080))
            bg_image_tk = ImageTk.PhotoImage(bg_image)

            # Create a canvas to hold the background image
            canvas = tk.Canvas(create_motorcycle_window, width=1080, height=720)
            canvas.pack(fill="both", expand=True)
            canvas.create_image(0, 0, image=bg_image_tk, anchor="nw")

            # Create the form frame on top of the canvas
            form_frame = tk.Frame(canvas, bg="#f0f0f0", bd=5, relief="groove")
            form_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=650)

            # Create form fields
            tk.Label(form_frame, text="Create Motorcycle", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(1, 20))

            # Form Fields
            make_label = tk.Label(form_frame, text="Make", bg="#f0f0f0")
            make_label.place(relx=0.5, rely=0.1, anchor='center', width=200, height=30)
            make_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            make_entry.place(relx=0.5, rely=0.15, anchor='center', width=341, height=30)

            model_label = tk.Label(form_frame, text="Model", bg="#f0f0f0")
            model_label.place(relx=0.5, rely=0.2, anchor='center', width=200, height=30)
            model_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            model_entry.place(relx=0.5, rely=0.25, anchor='center', width=341, height=30)

            year_label = tk.Label(form_frame, text="Year", bg="#f0f0f0")
            year_label.place(relx=0.5, rely=0.3, anchor='center', width=200, height=30)
            year_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            year_entry.place(relx=0.5, rely=0.35, anchor='center', width=341, height=30)

            fuel_type_label = tk.Label(form_frame, text="Fuel Type", bg="#f0f0f0")
            fuel_type_label.place(relx=0.5, rely=0.4, anchor='center', width=200, height=30)
            fuel_type_combobox = ttk.Combobox(form_frame, values=["Gasoline", "Diesel", "Electric", "Hybrid"],
                                              state="readonly")
            fuel_type_combobox.place(relx=0.5, rely=0.45, anchor='center', width=341, height=30)

            daily_rental_price_label = tk.Label(form_frame, text="Daily Rental Price", bg="#f0f0f0")
            daily_rental_price_label.place(relx=0.5, rely=0.5, anchor='center', width=200, height=30)
            daily_rental_price_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            daily_rental_price_entry.place(relx=0.5, rely=0.55, anchor='center', width=341, height=30)

            engine_displacement_label = tk.Label(form_frame, text="Engine Displacement", bg="#f0f0f0")
            engine_displacement_label.place(relx=0.5, rely=0.6, anchor='center', width=200, height=30)
            engine_displacement_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            engine_displacement_entry.place(relx=0.5, rely=0.65, anchor='center', width=341, height=30)

            type_label = tk.Label(form_frame, text="Type", bg="#f0f0f0")
            type_label.place(relx=0.5, rely=0.7, anchor='center', width=200, height=30)
            type_entry = tk.Entry(form_frame, bg='#f0f0f0', fg='black', font=title_font)
            type_entry.place(relx=0.5, rely=0.75, anchor='center', width=341, height=30)

            availability_status_label = tk.Label(form_frame, text="Availability Status", bg="#f0f0f0")
            availability_status_label.place(relx=0.5, rely=0.8, anchor='center', width=200, height=30)
            availability_status_combobox = ttk.Combobox(form_frame, values=["Available", "Unavailable", "Leased"],
                                                        state="readonly")
            availability_status_combobox.place(relx=0.5, rely=0.85, anchor='center', width=341, height=30)

            # Submit button
            submit_button = tk.Button(form_frame, text="Submit", command=submit_motorcycle)
            submit_button.place(relx=0.5, rely=0.95, anchor='center', width=200, height=40)

            # Keep a reference to the background and logo images
            create_motorcycle_window.bg_image_tk = bg_image_tk

        def vehicle_car_window_admin():
            def edit_car():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a car to edit.")
                    return

                item_values = tree.item(selected_item, 'values')
                vehicle_id = item_values[0]  # Assuming VehicleID is the first column

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                # Retrieve car details for editing
                cursor.execute("""
                    SELECT VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.AvailabilityStatus,
                           CAR.BodyStyle, CAR.TransmissionType, CAR.NumberOfDoors
                    FROM VEHICLE 
                    INNER JOIN CAR ON VEHICLE.VehicleID = CAR.VehicleID
                    WHERE VEHICLE.VehicleID = ?
                """, (vehicle_id,))

                car_details = cursor.fetchone()
                conn.close()

                if not car_details:
                    messagebox.showerror("Error", "Failed to fetch car details for editing.")
                    return

                def submit_edit():
                    # Get updated values from entry fields
                    updated_make = make_entry.get()
                    updated_model = model_entry.get()
                    updated_year = year_entry.get()
                    updated_fuel_type = fuel_type_combobox.get()
                    updated_daily_rental_price = daily_rental_price_entry.get()
                    updated_body_style = body_style_entry.get()
                    updated_transmission_type = transmission_type_entry.get()
                    updated_number_of_doors = number_of_doors_entry.get()
                    updated_availability_status = availability_status_combobox.get()

                    if not (
                            updated_make and updated_model and updated_year and updated_fuel_type and updated_daily_rental_price and
                            updated_body_style and updated_transmission_type and updated_number_of_doors and updated_availability_status):
                        messagebox.showerror("Error", "Please fill in all fields")
                        return

                    # Update the database with the new values
                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("""
                        UPDATE VEHICLE
                        SET Make = ?, Model = ?, Year = ?, FuelType = ?, DailyRentalPrice = ?, AvailabilityStatus = ?
                        WHERE VehicleID = ?
                    """, (updated_make, updated_model, updated_year, updated_fuel_type, updated_daily_rental_price,
                          updated_availability_status, vehicle_id))

                    cursor.execute("""
                        UPDATE CAR
                        SET BodyStyle = ?, TransmissionType = ?, NumberOfDoors = ?
                        WHERE VehicleID = ?
                    """, (updated_body_style, updated_transmission_type, updated_number_of_doors, vehicle_id))

                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Success", "Car details updated successfully.")
                    edit_car_window.destroy()

                # Create the edit car window
                edit_car_window = tk.Toplevel(window2)
                edit_car_window.title("Edit Car")
                edit_car_window.geometry("600x600")

                # Load and set the background image
                background_image = Image.open(r"C:\Users\Styvn\VRMS\resources\images\2.png")
                background_image = background_image.resize((1900, 800))
                bg_image = ImageTk.PhotoImage(background_image)

                canvas = tk.Canvas(edit_car_window, width=600, height=600)
                canvas.pack(fill='both', expand=True)
                canvas.create_image(0, 0, image=bg_image, anchor='nw')

                # Create a frame for the form with a specific background color
                form_frame = tk.Frame(edit_car_window, bg='#1E5A2A', bd=5)
                form_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=680)

                # Create and add form fields
                def add_form_field(parent, label_text, default_value):
                    label = tk.Label(parent, text=label_text, bg='#1E5A2A', fg='white', font=('Helvetica', 12, 'bold'))
                    label.pack(pady=5, anchor='w')
                    entry = tk.Entry(parent, font=('Helvetica', 12))
                    entry.insert(0, default_value)
                    entry.pack(pady=5, fill='x', padx=20)
                    return entry

                make_entry = add_form_field(form_frame, "Make", car_details[0])
                model_entry = add_form_field(form_frame, "Model", car_details[1])
                year_entry = add_form_field(form_frame, "Year", car_details[2])
                daily_rental_price_entry = add_form_field(form_frame, "Daily Rental Price", car_details[4])
                body_style_entry = add_form_field(form_frame, "Body Style", car_details[6])
                transmission_type_entry = add_form_field(form_frame, "Transmission Type", car_details[7])
                number_of_doors_entry = add_form_field(form_frame, "Number of Doors", car_details[8])

                fuel_type_label = tk.Label(form_frame, text="Fuel Type", bg='#1E5A2A', fg='white',
                                           font=('Helvetica', 12, 'bold'))
                fuel_type_label.pack(pady=5, anchor='w')
                fuel_type_combobox = ttk.Combobox(form_frame, values=["Gasoline", "Diesel", "Electric", "Hybrid"],
                                                  state="readonly",
                                                  font=('Helvetica', 12))
                fuel_type_combobox.set(car_details[3])
                fuel_type_combobox.pack(pady=5, fill='x', padx=20)

                availability_status_label = tk.Label(form_frame, text="Availability Status", bg='#1E5A2A', fg='white',
                                                     font=('Helvetica', 12, 'bold'))
                availability_status_label.pack(pady=5, anchor='w')
                availability_status_combobox = ttk.Combobox(form_frame, values=["Available", "Unavailable", "Leased"],
                                                            state="readonly",
                                                            font=('Helvetica', 12))
                availability_status_combobox.set(car_details[5])
                availability_status_combobox.pack(pady=5, fill='x', padx=20)

                # Create a frame for the buttons
                button_frame = tk.Frame(form_frame, bg='#1E5A2A')
                button_frame.pack(pady=20)

                # Submit button
                submit_button = tk.Button(button_frame, text="Save Changes", command=submit_edit, bg='#FFC107',
                                          fg='black',
                                          font=('Helvetica', 12, 'bold'))
                submit_button.pack(side='left', padx=10)

                # Cancel button
                cancel_button = tk.Button(button_frame, text="Cancel", command=edit_car_window.destroy, bg='#D32F2F',
                                          fg='white',
                                          font=('Helvetica', 12, 'bold'))
                cancel_button.pack(side='left', padx=10)

                # Keep a reference to the image to prevent it from being garbage collected
                edit_car_window.bg_image = bg_image

            def delete_car():
                selected_item = tree.focus()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a car to delete")
                    return

                confirm_delete = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this car?")
                if confirm_delete:
                    item_values = tree.item(selected_item, 'values')
                    vehicle_id = item_values[0]  # Assuming VehicleID is the first column

                    # Delete from CAR table
                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("UPDATE VEHICLE SET IsDeleted = 1 WHERE VehicleID = ?", (vehicle_id,))
                    conn.commit()

                    conn.close()

                    messagebox.showinfo("Success", "Car deleted successfully")
                    vehicle_car_window_admin()  # Refresh the car list after delete

            clear_frame(content_frame)
            columns = (
                "VehicleID", "Make", "Model", "Year", "FuelType", "DailyRentalPrice", "VehicleType",
                "AvailabilityStatus",
                "BodyStyle", "TransmissionType", "NumberOfDoors", "CreatedBy"
            )
            tree = ttk.Treeview(content_frame, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            tree.pack(expand=True, fill='both')

            for row in tree.get_children():
                tree.delete(row)

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("""
            SELECT VEHICLE.VehicleID, VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.VehicleType, VEHICLE.AvailabilityStatus, 
            CAR.BodyStyle, CAR.TransmissionType, CAR.NumberOfDoors, VEHICLE.CreatedBy 
            FROM VEHICLE 
            INNER JOIN CAR ON VEHICLE.VehicleID = CAR.VehicleID
            WHERE VEHICLE.IsDeleted = 0
            """)

            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

            conn.close()

            global button_frame
            button_frame = tk.Frame(content_frame)
            button_frame.pack(fill='x', pady=10)
            tk.Button(button_frame, text="CREATE", command=create_car, bg="yellow").pack(side='left', padx=5)
            tk.Button(button_frame, text="EDIT", command=edit_car, bg="lightblue").pack(side='left', padx=5)
            tk.Button(button_frame, text="DELETE", command=delete_car, bg="red", fg="white").pack(side='left', padx=5)

        def vehicle_truck_window_admin():
            def edit_truck():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a truck to edit.")
                    return

                item_values = tree.item(selected_item, 'values')
                vehicle_id = item_values[0]  # Assuming VehicleID is the first column

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                # Retrieve truck details for editing
                cursor.execute("""
                    SELECT VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.AvailabilityStatus,
                           TRUCK.PayLoadCapacity, TRUCK.TruckBedSize, TRUCK.NumberOfAxles
                    FROM VEHICLE 
                    INNER JOIN TRUCK ON VEHICLE.VehicleID = TRUCK.VehicleID
                    WHERE VEHICLE.VehicleID = ?
                """, (vehicle_id,))

                truck_details = cursor.fetchone()
                conn.close()

                if not truck_details:
                    messagebox.showerror("Error", "Failed to fetch truck details for editing.")
                    return

                def submit_edit():
                    # Get updated values from entry fields
                    updated_make = make_entry.get()
                    updated_model = model_entry.get()
                    updated_year = year_entry.get()
                    updated_fuel_type = fuel_type_combobox.get()
                    updated_daily_rental_price = daily_rental_price_entry.get()
                    updated_payload_capacity = payload_capacity_entry.get()
                    updated_truck_bed_size = truck_bed_size_entry.get()
                    updated_number_of_axles = number_of_axles_entry.get()
                    updated_availability_status = availability_status_combobox.get()

                    if not (
                            updated_make and updated_model and updated_year and updated_fuel_type and updated_daily_rental_price and
                            updated_payload_capacity and updated_truck_bed_size and updated_number_of_axles and updated_availability_status):
                        messagebox.showerror("Error", "Please fill in all fields")
                        return

                    # Update the database with the new values
                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("""
                        UPDATE VEHICLE
                        SET Make = ?, Model = ?, Year = ?, FuelType = ?, DailyRentalPrice = ?, AvailabilityStatus = ?
                        WHERE VehicleID = ?
                    """, (updated_make, updated_model, updated_year, updated_fuel_type, updated_daily_rental_price,
                          updated_availability_status, vehicle_id))

                    cursor.execute("""
                        UPDATE TRUCK
                        SET PayLoadCapacity = ?, TruckBedSize = ?, NumberOfAxles = ?
                        WHERE VehicleID = ?
                    """, (updated_payload_capacity, updated_truck_bed_size, updated_number_of_axles, vehicle_id))

                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Success", "Truck details updated successfully.")
                    edit_truck_window.destroy()

                # Create the edit truck window
                edit_truck_window = tk.Toplevel(window2)
                edit_truck_window.title("Edit Truck")
                edit_truck_window.geometry("600x600")

                # Load and set the background image
                background_image = Image.open(r"C:\Users\Styvn\VRMS\resources\images\2.png")
                background_image = background_image.resize((1900, 800))
                bg_image = ImageTk.PhotoImage(background_image)

                canvas = tk.Canvas(edit_truck_window, width=600, height=600)
                canvas.pack(fill='both', expand=True)
                canvas.create_image(0, 0, image=bg_image, anchor='nw')

                # Create a frame for the form with a specific background color
                form_frame = tk.Frame(edit_truck_window, bg='#1E5A2A', bd=5)
                form_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=680)

                # Create and add form fields
                def add_form_field(parent, label_text, default_value):
                    label = tk.Label(parent, text=label_text, bg='#1E5A2A', fg='white', font=('Helvetica', 12, 'bold'))
                    label.pack(pady=5, anchor='w')
                    entry = tk.Entry(parent, font=('Helvetica', 12))
                    entry.insert(0, default_value)
                    entry.pack(pady=5, fill='x', padx=20)
                    return entry

                make_entry = add_form_field(form_frame, "Make", truck_details[0])
                model_entry = add_form_field(form_frame, "Model", truck_details[1])
                year_entry = add_form_field(form_frame, "Year", truck_details[2])
                daily_rental_price_entry = add_form_field(form_frame, "Daily Rental Price", truck_details[4])
                payload_capacity_entry = add_form_field(form_frame, "Payload Capacity", truck_details[5])
                truck_bed_size_entry = add_form_field(form_frame, "Truck Bed Size", truck_details[6])
                number_of_axles_entry = add_form_field(form_frame, "Number of Axles", truck_details[7])

                fuel_type_label = tk.Label(form_frame, text="Fuel Type", bg='#1E5A2A', fg='white',
                                           font=('Helvetica', 12, 'bold'))
                fuel_type_label.pack(pady=5, anchor='w')
                fuel_type_combobox = ttk.Combobox(form_frame, values=["Gasoline", "Diesel", "Electric", "Hybrid"],
                                                  state="readonly",
                                                  font=('Helvetica', 12))
                fuel_type_combobox.set(truck_details[3])
                fuel_type_combobox.pack(pady=5, fill='x', padx=20)

                availability_status_label = tk.Label(form_frame, text="Availability Status", bg='#1E5A2A', fg='white',
                                                     font=('Helvetica', 12, 'bold'))
                availability_status_label.pack(pady=5, anchor='w')
                availability_status_combobox = ttk.Combobox(form_frame, values=["Available", "Unavailable", "Leased"],
                                                            state="readonly",
                                                            font=('Helvetica', 12))
                availability_status_combobox.set(truck_details[8])
                availability_status_combobox.pack(pady=5, fill='x', padx=20)

                # Create a frame for the buttons
                button_frame = tk.Frame(form_frame, bg='#1E5A2A')
                button_frame.pack(pady=20)

                # Submit button
                submit_button = tk.Button(button_frame, text="Save Changes", command=submit_edit, bg='#FFC107',
                                          fg='black',
                                          font=('Helvetica', 12, 'bold'))
                submit_button.pack(side='left', padx=10)

                # Cancel button
                cancel_button = tk.Button(button_frame, text="Cancel", command=edit_truck_window.destroy, bg='#D32F2F',
                                          fg='white',
                                          font=('Helvetica', 12, 'bold'))
                cancel_button.pack(side='left', padx=10)

                # Keep a reference to the image to prevent it from being garbage collected
                edit_truck_window.bg_image = bg_image

            def delete_truck():
                selected_item = tree.focus()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a truck to delete")
                    return

                confirm_delete = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this car?")
                if confirm_delete:
                    item_values = tree.item(selected_item, 'values')
                    vehicle_id = item_values[0]  # Assuming VehicleID is the first column

                    # Delete from CAR table
                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("UPDATE VEHICLE SET IsDeleted = 1 WHERE VehicleID = ?", (vehicle_id,))
                    conn.commit()

                    conn.close()

                    messagebox.showinfo("Success", "Car deleted successfully")
                    vehicle_car_window_admin()  # Refresh the car list after delete

            clear_frame(content_frame)
            columns = (
                "VehicleID", "Make", "Model", "Year", "FuelType", "DailyRentalPrice", "VehicleType",
                "AvailabilityStatus",
                "PayloadCapacity", "TruckBedSize", "NumberOfAxles", "CreatedBy"
            )
            tree = ttk.Treeview(content_frame, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            tree.pack(expand=True, fill='both')

            # Clear existing rows
            for row in tree.get_children():
                tree.delete(row)

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("""
                    SELECT VEHICLE.VehicleID, VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.VehicleType, VEHICLE.AvailabilityStatus, 
                    TRUCK.PayLoadCapacity, TRUCK.TruckBedSize, TRUCK.NumberOfAxles, VEHICLE.CreatedBy 
                    FROM VEHICLE 
                    INNER JOIN TRUCK ON VEHICLE.VehicleID = TRUCK.VehicleID
                    WHERE VEHICLE.IsDeleted = 0
                    """)
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            conn.close()

            # Create buttons for CRUD operations
            global button_frame
            button_frame = tk.Frame(content_frame)
            button_frame.pack(fill='x', pady=10)
            tk.Button(button_frame, text="CREATE", command=create_truck, bg="yellow").pack(side='left', padx=5)
            tk.Button(button_frame, text="EDIT", command=edit_truck, bg="lightblue").pack(side='left', padx=5)
            tk.Button(button_frame, text="DELETE", command=delete_truck, bg="red", fg="white").pack(side='left', padx=5)

        def vehicle_motorcycle_window_admin():
            def edit_motorcycle():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a motorcycle to edit.")
                    return

                item_values = tree.item(selected_item, 'values')
                vehicle_id = item_values[0]  # Assuming VehicleID is the first column

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                # Retrieve motorcycle details for editing
                cursor.execute("""
                    SELECT VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.AvailabilityStatus,
                           MOTORCYCLE.EngineDisplacement, MOTORCYCLE.Type
                    FROM VEHICLE 
                    INNER JOIN MOTORCYCLE ON VEHICLE.VehicleID = MOTORCYCLE.VehicleID
                    WHERE VEHICLE.VehicleID = ?
                """, (vehicle_id,))

                motorcycle_details = cursor.fetchone()
                conn.close()

                if not motorcycle_details:
                    messagebox.showerror("Error", "Failed to fetch motorcycle details for editing.")
                    return

                def submit_edit():
                    # Get updated values from entry fields
                    updated_make = make_entry.get()
                    updated_model = model_entry.get()
                    updated_year = year_entry.get()
                    updated_fuel_type = fuel_type_combobox.get()
                    updated_daily_rental_price = daily_rental_price_entry.get()
                    updated_engine_displacement = engine_displacement_entry.get()
                    updated_type = type_entry.get()
                    updated_availability_status = availability_status_combobox.get()

                    if not (
                            updated_make and updated_model and updated_year and updated_fuel_type and updated_daily_rental_price and
                            updated_engine_displacement and updated_type and updated_availability_status):
                        messagebox.showerror("Error", "Please fill in all fields")
                        return

                    # Update the database with the new values
                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("""
                        UPDATE VEHICLE
                        SET Make = ?, Model = ?, Year = ?, FuelType = ?, DailyRentalPrice = ?, AvailabilityStatus = ?
                        WHERE VehicleID = ?
                    """, (updated_make, updated_model, updated_year, updated_fuel_type, updated_daily_rental_price,
                          updated_availability_status, vehicle_id))

                    cursor.execute("""
                        UPDATE MOTORCYCLE
                        SET EngineDisplacement = ?, Type = ?
                        WHERE VehicleID = ?
                    """, (updated_engine_displacement, updated_type, vehicle_id))

                    conn.commit()
                    conn.close()

                    messagebox.showinfo("Success", "Motorcycle details updated successfully.")
                    edit_motorcycle_window.destroy()

                # Create the edit motorcycle window
                edit_motorcycle_window = tk.Toplevel(window2)
                edit_motorcycle_window.title("Edit Motorcycle")
                edit_motorcycle_window.geometry("600x600")

                # Load and set the background image
                background_image = Image.open(r"C:\Users\Styvn\VRMS\resources\images\2.png")
                background_image = background_image.resize((1900, 800))
                bg_image = ImageTk.PhotoImage(background_image)

                canvas = tk.Canvas(edit_motorcycle_window, width=600, height=600)
                canvas.pack(fill='both', expand=True)
                canvas.create_image(0, 0, image=bg_image, anchor='nw')

                # Create a frame for the form with a specific background color
                form_frame = tk.Frame(edit_motorcycle_window, bg='#1E5A2A', bd=5)
                form_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=630)

                # Create and add form fields
                def add_form_field(parent, label_text, default_value):
                    label = tk.Label(parent, text=label_text, bg='#1E5A2A', fg='white', font=('Helvetica', 12, 'bold'))
                    label.pack(pady=5, anchor='w')
                    entry = tk.Entry(parent, font=('Helvetica', 12))
                    entry.insert(0, default_value)
                    entry.pack(pady=5, fill='x', padx=20)
                    return entry

                make_entry = add_form_field(form_frame, "Make", motorcycle_details[0])
                model_entry = add_form_field(form_frame, "Model", motorcycle_details[1])
                year_entry = add_form_field(form_frame, "Year", motorcycle_details[2])
                daily_rental_price_entry = add_form_field(form_frame, "Daily Rental Price", motorcycle_details[4])
                engine_displacement_entry = add_form_field(form_frame, "Engine Displacement", motorcycle_details[5])
                type_entry = add_form_field(form_frame, "Type", motorcycle_details[6])

                fuel_type_label = tk.Label(form_frame, text="Fuel Type", bg='#1E5A2A', fg='white',
                                           font=('Helvetica', 12, 'bold'))
                fuel_type_label.pack(pady=5, anchor='w')
                fuel_type_combobox = ttk.Combobox(form_frame, values=["Gasoline", "Diesel", "Electric", "Hybrid"],
                                                  state="readonly",
                                                  font=('Helvetica', 12))
                fuel_type_combobox.set(motorcycle_details[3])
                fuel_type_combobox.pack(pady=5, fill='x', padx=20)

                availability_status_label = tk.Label(form_frame, text="Availability Status", bg='#1E5A2A', fg='white',
                                                     font=('Helvetica', 12, 'bold'))
                availability_status_label.pack(pady=5, anchor='w')
                availability_status_combobox = ttk.Combobox(form_frame, values=["Available", "Unavailable", "Leased"],
                                                            state="readonly",
                                                            font=('Helvetica', 12))
                availability_status_combobox.set(motorcycle_details[7])
                availability_status_combobox.pack(pady=5, fill='x', padx=20)

                # Create a frame for the buttons
                button_frame = tk.Frame(form_frame, bg='#1E5A2A')
                button_frame.pack(pady=20)

                # Submit button
                submit_button = tk.Button(button_frame, text="Save Changes", command=submit_edit, bg='#FFC107',
                                          fg='black',
                                          font=('Helvetica', 12, 'bold'))
                submit_button.pack(side='left', padx=10)

                # Cancel button
                cancel_button = tk.Button(button_frame, text="Cancel", command=edit_motorcycle_window.destroy,
                                          bg='#D32F2F', fg='white',
                                          font=('Helvetica', 12, 'bold'))
                cancel_button.pack(side='left', padx=10)

                # Keep a reference to the image to prevent it from being garbage collected
                edit_motorcycle_window.bg_image = bg_image

            def delete_motorcycle():
                selected_item = tree.focus()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a motorcycle to delete")
                    return

                confirm_delete = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this car?")
                if confirm_delete:
                    item_values = tree.item(selected_item, 'values')
                    vehicle_id = item_values[0]  # Assuming VehicleID is the first column

                    # Delete from CAR table
                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("UPDATE VEHICLE SET IsDeleted = 1 WHERE VehicleID = ?", (vehicle_id,))
                    conn.commit()

                    conn.close()

                    messagebox.showinfo("Success", "Car deleted successfully")
                    vehicle_car_window_admin()  # Refresh the car list after delete

            clear_frame(content_frame)
            columns = (
                "VehicleID", "Make", "Model", "Year", "FuelType", "DailyRentalPrice", "VehicleType",
                "AvailabilityStatus",
                "EngineDisplacement", "Type", "CreatedBy"
            )
            tree = ttk.Treeview(content_frame, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            tree.pack(expand=True, fill='both')
            # Clear existing rows
            for row in tree.get_children():
                tree.delete(row)

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("""
                    SELECT VEHICLE.VehicleID, VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.VehicleType, VEHICLE.AvailabilityStatus, 
                    MOTORCYCLE.EngineDisplacement, MOTORCYCLE.Type, VEHICLE.CreatedBy 
                    FROM VEHICLE 
                    INNER JOIN MOTORCYCLE ON VEHICLE.VehicleID = MOTORCYCLE.VehicleID
                    WHERE VEHICLE.IsDeleted = 0
                    """)
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)
            conn.close()
            # Create buttons for CRUD operations
            global button_frame
            button_frame = tk.Frame(content_frame)
            button_frame.pack(fill='x', pady=10)
            tk.Button(button_frame, text="CREATE", command=create_motorcycle, bg="yellow").pack(side='left', padx=5)
            tk.Button(button_frame, text="EDIT", command=edit_motorcycle, bg="lightblue").pack(side='left', padx=5)
            tk.Button(button_frame, text="DELETE", command=delete_motorcycle, bg="red", fg="white").pack(side='left',
                                                                                                         padx=5)

        def vehicle_type_change(event):
            vehicle_type = vehicle_type_combobox.get()
            if vehicle_type == "Cars":
                vehicle_car_window_admin()
            elif vehicle_type == "Truck":
                vehicle_truck_window_admin()
            elif vehicle_type == "Motorcycle":
                vehicle_motorcycle_window_admin()

        clear_frame(content_frame_main)
        content_frame1 = tk.Frame(content_frame_main)
        content_frame1.pack(fill="x", pady=10)
        content_frame = tk.Frame(content_frame_main)
        content_frame.pack(side="top", fill="both", expand=True)
        vehicle_type_label = tk.Label(content_frame1, text="Vehicle Type")
        vehicle_type_label.pack(pady=5)
        vehicle_type_combobox = ttk.Combobox(content_frame1, values=["Cars", "Truck", "Motorcycle"], state="readonly")
        vehicle_type_combobox.set("Truck")
        vehicle_type_combobox.pack(pady=5)
        vehicle_type_combobox.bind("<<ComboboxSelected>>", vehicle_type_change)

        # Load the default content
        vehicle_type_change(None)



    # Create the main application window 1
    window1 = tk.Tk()
    window1.title("Login")
    window1.geometry("900x600")
    test = 0
    #Background
    background_image = Image.open(r"C:\Users\Styvn\VRMS\resources\images\2.png")  # Path to background image
    background_image = background_image.resize((1920, 1080))
    background_photo = ImageTk.PhotoImage(background_image)

    background_label = tk.Label(window1, image=background_photo)
    background_label.place(relwidth=1, relheight=1)

    # Create a Frame for the login box
    login_frame = tk.Frame(window1, bg='#f0f0f0', bd=5)
    login_frame.place(relx=0.5, rely=0.5, anchor='center', width=300, height=350)

    # Logo
    logo = Image.open(r"C:\Users\Styvn\VRMS\resources\images\1.png")  # Path to logo image
    logo = logo.resize((160, 110))
    logo_photo = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(login_frame, image=logo_photo, bg='#f0f0f0')
    logo_label.place(relx=0.5, rely=0.15, anchor='center')

    # Title
    title_font = font.Font(family='Helvetica', size=10, weight='bold')
    title_label = tk.Label(login_frame, text="Enter your Login Credentials", bg='#f0f0f0', font=title_font)
    title_label.place(relx=0.5, rely=0.35, anchor='center')

    # Username Entry
    username_entry = tk.Entry(window1, bg='#f0f0f0', fg='black', font=title_font)
    username_entry.insert(0, 'Enter Username')
    username_entry.bind("<FocusIn>", lambda event: username_entry.delete(0, 'end'))
    username_entry.place(relx=0.5, rely=0.50, anchor='center', width=200, height=30)

    # Password Entry
    password_entry = tk.Entry(window1, show='*', bg='#f0f0f0', fg='black', font=title_font)
    password_entry.insert(0, 'Enter Password')
    password_entry.bind("<FocusIn>", lambda event: password_entry.delete(0, 'end'))
    password_entry.place(relx=0.5, rely=0.59, anchor='center', width=200, height=30)

    # Add a Login button
    login_button = tk.Button(window1, text="LOGIN", bg='#28a745', fg='white', bd=0, command=check_login)
    login_button.place(relx=0.5, rely=0.67, anchor='center', width=100, height=40)

    # Create the second window (admin dashboard)
    window2 = tk.Toplevel(window1)
    window2.title("Admin Dashboard")
    window2.geometry("1900x800")
    window2.withdraw()

    # Add a frame for the sidebar
    sidebar = tk.Frame(window2, bg='#1E5A2A', width=200)
    sidebar.pack(side='left', fill='y')

    title_label = tk.Label(sidebar, text="TARA BYAHE!", bg='#1E5A2A', font=('Helvetica', 12, 'bold'), fg='black')
    title_label.place(relx=0.5, rely=0.05, anchor='center')
    title_label = tk.Label(sidebar, text="VEHICLE RENTING", bg='#1E5A2A', font=('Helvetica', 12, 'bold'), fg='black')
    title_label.place(relx=0.5, rely=0.08, anchor='center')



    # Add a frame for the main content area
    content_frame_main = tk.Frame(window2, bg='white')
    content_frame_main.pack(side='right', fill='both', expand=True)

    # Add sidebar buttons

    account_management_button = tk.Button(sidebar, text="Manage Account", width=40, height=3, bg='#1E5A2A',
                                          relief="flat", command=account_management_panel)
    account_management_button.place(relx=0.5, rely=0.3, anchor='center')

    vehicle_management_button = tk.Button(sidebar, text="Manage Vehicle", width=40, height=3, bg='#1E5A2A',
                                          relief="flat", command=vehicle_management_panel)
    vehicle_management_button.place(relx=0.5, rely=0.4, anchor='center')

    # Add the logout button
    logout_button = tk.Button(sidebar, text="Logout", width=20, height=2, bg='#1E5A2A', relief="flat", command=log_in)
    logout_button.pack(side='bottom', fill="x")

    # Load and set the background image for the main content area
    background_image = Image.open(r"C:\Users\Styvn\VRMS\resources\images\2.png")
    background_image = background_image.resize((1900, 800))
    bg_image = ImageTk.PhotoImage(background_image)

    canvas = tk.Canvas(content_frame_main, width=880, height=800)
    canvas.pack(fill='both', expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor='nw')

    # Keep a reference to the image to prevent it from being garbage collected
    content_frame_main.bg_image = bg_image



    # Start the Tkinter event loop with the main window
    window1.mainloop()


class PayMongoClient:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.base_url = "https://api.paymongo.com/v1"

    def create_payment_intent(self, amount, currency, description):
        url = f"{self.base_url}/payment_intents"
        headers = {
            "Authorization": f"Basic {base64.b64encode(self.secret_key.encode()).decode()}",
            "Content-Type": "application/json",
        }
        data = {
            "data": {
                "attributes": {
                    "amount": amount,
                    "payment_method_allowed": ["card"],
                    "currency": currency,
                    "description": description,
                }
            }
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def attach_payment_method(self, intent_id, payment_method_id):
        url = f"{self.base_url}/payment_intents/{intent_id}/attach"
        headers = {
            "Authorization": f"Basic {base64.b64encode(self.secret_key.encode()).decode()}",
            "Content-Type": "application/json",
        }
        data = {
            "data": {
                "attributes": {
                    "payment_method": payment_method_id,
                }
            }
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def create_payment_method(self, card_number, exp_month, exp_year, cvc):
        url = f"{self.base_url}/payment_methods"
        headers = {
            "Authorization": f"Basic {base64.b64encode(self.secret_key.encode()).decode()}",
            "Content-Type": "application/json",
        }
        data = {
            "data": {
                "attributes": {
                    "type": "card",
                    "details": {
                        "card_number": card_number,
                        "exp_month": int(exp_month),
                        "exp_year": int(exp_year),
                        "cvc": cvc,
                    },
                }
            }
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()



class VehicleRentingApp(tk.Tk):


    def __init__(self):
        super().__init__()
        self.title("Vehicle Renting")
        self.geometry("800x600")
        self.configure(bg='#FFFFFF')
        self.resizable(False, False)
        self.selected_tile = None
        self.create_widgets()



    def create_widgets(self):
        sidebar = tk.Frame(self, bg='#2C5F2D', width=200, height=600)
        sidebar.pack(side='left', fill='y')

        logo = tk.Label(sidebar, text="TARA BYAHEI\nVEHICLE RENTING", bg='#2C5F2D', fg='white',
                        font=('Helvetica', 12, 'bold'))
        logo.pack(pady=20)

        self.create_sidebar_tile(sidebar, "Reservation", '#3F704D')
        self.create_sidebar_tile(sidebar, "Payment", '#2C5F2D')

        user_logout_frame = tk.Frame(sidebar, bg='#2C5F2D')
        user_logout_frame.pack(side='bottom', pady=20, padx=20, fill='x')

        conn = sqlite3.connect('vehicle_rental.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EMPLOYEE WHERE EmpUserName=?", (logged_in_user_name,))
        result = cursor.fetchone()
        conn.close()
        name = result[2]
        role = result[10]
        user_info = tk.Label(user_logout_frame, text=f"{name}\n{role}", bg='#2C5F2D', fg='white', font=('Helvetica', 10))
        user_info.pack(side='left')

        logout_button = tk.Label(user_logout_frame, text="Logout", bg='#2C5F2D', fg='white',
                                 font=('Helvetica', 10, 'bold'))
        logout_button.pack(side='right')
        logout_button.bind("<Button-1>", lambda e: self.destroy())

        self.main_frame = tk.Frame(self, bg='#FFFFFF')
        self.main_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)

        self.frames = {}
        for frame_name in ['reservation', 'payment']:
            frame = tk.Frame(self.main_frame, bg='#FFFFFF')
            frame.grid(row=0, column=0, sticky='nsew')
            self.frames[frame_name] = frame

        self.create_reservation_frame(self.frames['reservation'])
        self.create_payment_frame(self.frames['payment'])

        self.show_frame('reservation')

    def create_sidebar_tile(self, parent, text, bg_color):
        tile = tk.Frame(parent, bg=bg_color, height=40)
        tile.pack(fill='x', padx=20, pady=10)
        label = tk.Label(tile, text=text, bg=bg_color, fg='white', font=('Helvetica', 10, 'bold'))
        label.pack(anchor='center', expand=True)

        label.bind("<Button-1>", lambda e, tile=tile, label=label, text=text, bg_color=bg_color: self.on_tile_click(tile, label, text, bg_color))

    def on_tile_click(self, tile, label, tile_name, bg_color):
        if self.selected_tile:
            self.selected_tile.config(bg='#2C5F2D')
            self.selected_tile.children['!label'].config(bg='#2C5F2D')

        self.selected_tile = tile
        self.selected_tile.config(bg='gray')
        label.config(bg='gray')

        self.on_tile_select(tile_name)

    def on_tile_select(self, tile_name):
        if tile_name == "Reservation":
            self.show_frame('reservation')
        elif tile_name == "Payment":
            self.show_frame('payment')
        print(f"{tile_name} tile clicked")

    def logout(self):
        print("Logout clicked")
        self.destroy()

    def create_reservation_frame(self, frame):
        def clear_frame(frame):
            for widget in frame.winfo_children():
                widget.destroy()

        def load_reservation():
            for row in tree.get_children():
                tree.delete(row)
            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            query = """
            SELECT r.ReservationID, r.CustomerFirstName || ' ' || r.CustomerLastName AS GuestName, v.VehicleType, v.Make || ' ' || v.Model AS VehicleName, r.Status
            FROM RESERVATION r
            JOIN VEHICLE v ON r.VehicleID = v.VehicleID
            WHERE r.IsDeleted == 0
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                tree.insert('', 'end', values=row)

        def soft_delete_reservation():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a reservation to delete.")
                return

            item_values = tree.item(selected_item, 'values')
            reservation_id = item_values[0]

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("SELECT VehicleID FROM RESERVATION WHERE ReservationID = ?", (reservation_id,))
            vehicle_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE RESERVATION SET IsDeleted = 1 WHERE ReservationID = ?", (reservation_id,))
            conn.commit()
            conn.close()

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE VEHICLE SET AvailabilityStatus = 'Available' WHERE VehicleID = ?", (vehicle_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Reservation deleted successfully")
            load_reservation()

        def edit_reservation():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Please select a reservation to edit.")
                return

            item_values = tree.item(selected_item, 'values')
            reservation_id = item_values[0]

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM RESERVATION WHERE ReservationID = ?", (reservation_id,))
            reservation_data = cursor.fetchone()
            conn.close()

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("SELECT VehicleID FROM RESERVATION WHERE ReservationID = ?", (reservation_id,))
            vehicle_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("SELECT DailyRentalPrice FROM VEHICLE WHERE VehicleID = ?", (vehicle_id,))
            save_vehicle_rental_price = cursor.fetchone()[0]
            conn.commit()
            conn.close()

            if not reservation_data:
                messagebox.showerror("Error", "Failed to fetch reservation details.")
                return

            def submit_reservation_edit():
                customer_first_name = customer_first_name_entry.get()
                customer_middle_name = customer_middle_name_entry.get()
                customer_last_name = customer_last_name_entry.get()
                email = email_entry.get()
                phone_number = phone_number_entry.get()
                street_address = street_address_entry.get()
                brgy = brgy_entry.get()
                city = city_entry.get()
                zipcode = zipcode_entry.get()
                reservation_date = reservation_date_entry.get()
                rental_start_date = rental_start_date_entry.get()
                rental_end_date = rental_end_date_entry.get()
                total_cost = total_cost_entry.get()
                status = status_combobox.get()

                if not all([customer_first_name, customer_last_name, email, phone_number, street_address, brgy,
                            city, zipcode, reservation_date, rental_start_date, rental_end_date, total_cost,
                            status]):
                    messagebox.showerror("Error", "Please fill in all required fields")
                    return
                if rental_start_date_entry.get() != current_rental_start or rental_end_date_entry.get() != current_rental_end:
                    messagebox.showwarning("Invalid", "Calculate to specify the changes")
                    return


                reservation_data = {
                    'CustomerFirstName': customer_first_name,
                    'CustomerMiddleName': customer_middle_name,
                    'CustomerLastName': customer_last_name,
                    'Email': email,
                    'PhoneNumber': phone_number,
                    'StreetAddress': street_address,
                    'Brgy': brgy,
                    'City': city,
                    'Zipcode': zipcode,
                    'ReservationDate': reservation_date,
                    'RentalStartDate': rental_start_date,
                    'RentalEndDate': rental_end_date,
                    'TotalCost': total_cost,
                    'Status': status,
                    'ReservationID': reservation_id
                }

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE RESERVATION
                    SET CustomerFirstName = :CustomerFirstName,
                        CustomerMiddleName = :CustomerMiddleName,
                        CustomerLastName = :CustomerLastName,
                        Email = :Email,
                        PhoneNumber = :PhoneNumber,
                        StreetAddress = :StreetAddress,
                        Brgy = :Brgy,
                        City = :City,
                        Zipcode = :Zipcode,
                        ReservationDate = :ReservationDate,
                        RentalStartDate = :RentalStartDate,
                        RentalEndDate = :RentalEndDate,
                        TotalCost = :TotalCost,
                        Status = :Status
                    WHERE ReservationID = :ReservationID
                """, reservation_data)

                conn.commit()
                conn.close()

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()
                cursor.execute("SELECT VehicleID FROM RESERVATION WHERE ReservationID = ?", (reservation_id,))
                vehicle_id = cursor.fetchone()[0]
                conn.commit()
                conn.close()
                if status == "COMPLETED" or status == "CANCELLED" or status =="UNPAID/CANCELLED" or status == "PAID/CANCELLED":
                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("""
                                                            UPDATE VEHICLE
                                                            SET AvailabilityStatus = ?
                                                            WHERE VehicleID = ?
                                                            """, ('Available', vehicle_id))
                    conn.commit()
                    conn.close()


                messagebox.showinfo("Success", "Reservation updated successfully")
                load_reservation()
                edit_reservation_window.destroy()

            def calculate():
                rental_start_date = rental_start_date_entry.get()
                rental_end_date = rental_end_date_entry.get()
                rental_start_date1 = datetime.strptime(rental_start_date, '%Y-%m-%d')
                rental_end_date1 = datetime.strptime(rental_end_date, '%Y-%m-%d')
                difference = (rental_end_date1 - rental_start_date1).days
                total_cost = float(difference) * float(save_vehicle_rental_price)
                total_cost_entry.config(state='normal')
                total_cost_entry.delete(0, "end")
                total_cost_entry.insert(0, str(total_cost))
                total_cost_entry.config(state='readonly')

            edit_reservation_window = tk.Toplevel(app)
            edit_reservation_window.title("Edit Reservation")
            edit_reservation_window.geometry("1080x800")

            current_rental_start = reservation_data[13]
            current_rental_end = reservation_data[14]
            form_frame = tk.Frame(edit_reservation_window, bg="#f0f0f0", bd=5, relief="groove")
            form_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=900)

            tk.Label(form_frame, text="Edit Reservation", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=(10, 20))

            customer_first_name_label = tk.Label(form_frame, text="Customer First Name", bg="#f0f0f0")
            customer_first_name_label.pack(pady=(5, 0))
            customer_first_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
            customer_first_name_entry.insert(0, reservation_data[3])
            customer_first_name_entry.pack()

            customer_middle_name_label = tk.Label(form_frame, text="Customer Middle Name", bg="#f0f0f0")
            customer_middle_name_label.pack(pady=(5, 0))
            customer_middle_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
            customer_middle_name_entry.insert(0, reservation_data[4])
            customer_middle_name_entry.pack()

            customer_last_name_label = tk.Label(form_frame, text="Customer Last Name", bg="#f0f0f0")
            customer_last_name_label.pack(pady=(5, 0))
            customer_last_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
            customer_last_name_entry.insert(0, reservation_data[5])
            customer_last_name_entry.pack()

            email_label = tk.Label(form_frame, text="Email", bg="#f0f0f0")
            email_label.pack(pady=(5, 0))
            email_entry = tk.Entry(form_frame, bg='#f0f0f0')
            email_entry.insert(0, reservation_data[6])
            email_entry.pack()

            phone_number_label = tk.Label(form_frame, text="Phone Number", bg="#f0f0f0")
            phone_number_label.pack(pady=(5, 0))
            phone_number_entry = tk.Entry(form_frame, bg='#f0f0f0')
            phone_number_entry.insert(0, reservation_data[7])
            phone_number_entry.pack()

            street_address_label = tk.Label(form_frame, text="Street Address", bg="#f0f0f0")
            street_address_label.pack(pady=(5, 0))
            street_address_entry = tk.Entry(form_frame, bg='#f0f0f0')
            street_address_entry.insert(0, reservation_data[8])
            street_address_entry.pack()

            brgy_label = tk.Label(form_frame, text="Brgy", bg="#f0f0f0")
            brgy_label.pack(pady=(5, 0))
            brgy_entry = tk.Entry(form_frame, bg='#f0f0f0')
            brgy_entry.insert(0, reservation_data[9])
            brgy_entry.pack()

            city_label = tk.Label(form_frame, text="City", bg="#f0f0f0")
            city_label.pack(pady=(5, 0))
            city_entry = tk.Entry(form_frame, bg='#f0f0f0')
            city_entry.insert(0, reservation_data[10])
            city_entry.pack()

            zipcode_label = tk.Label(form_frame, text="Zipcode", bg="#f0f0f0")
            zipcode_label.pack(pady=(5, 0))
            zipcode_entry = tk.Entry(form_frame, bg='#f0f0f0')
            zipcode_entry.insert(0, reservation_data[11])
            zipcode_entry.pack()

            reservation_date_label = tk.Label(form_frame, text="Reservation Date (YYYY-MM-DD)", bg="#f0f0f0")
            reservation_date_label.pack(pady=(5, 0))
            reservation_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                       date_pattern='yyyy-mm-dd')

            reservation_date_entry.pack()
            reservation_date_entry.delete(0, tk.END)
            reservation_date_entry.insert(0, reservation_data[12])

            rental_start_date_label = tk.Label(form_frame, text="Rental Start Date (YYYY-MM-DD)", bg="#f0f0f0")
            rental_start_date_label.pack(pady=(5, 0))
            rental_start_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                       date_pattern='yyyy-mm-dd')

            rental_start_date_entry.pack()
            rental_start_date_entry.delete(0, tk.END)
            rental_start_date_entry.insert(0, reservation_data[13])

            rental_end_date_label = tk.Label(form_frame, text="Rental End Date (YYYY-MM-DD)", bg="#f0f0f0")
            rental_end_date_label.pack(pady=(5, 0))
            rental_end_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                       date_pattern='yyyy-mm-dd')

            rental_end_date_entry.pack()
            rental_end_date_entry.delete(0, tk.END)
            rental_end_date_entry.insert(0, reservation_data[14])

            total_cost_label = tk.Label(form_frame, text="Total Cost", bg="#f0f0f0")
            total_cost_label.pack(pady=(5, 0))
            total_cost_entry = tk.Entry(form_frame, bg='#f0f0f0')
            total_cost_entry.insert(0, reservation_data[15])
            total_cost_entry.pack()

            status_label = tk.Label(form_frame, text="Status", bg="#f0f0f0")
            status_label.pack(pady=(5, 0))
            status_combobox = ttk.Combobox(form_frame, values=["PENDING/PAYMENT", "CANCELLED", "UNPAID/CANCELLED", "PAID/CONFIRMED", "PAID/CANCELLED", "IN-PROGRESS", "COMPLETED"], state="readonly")
            status_combobox.set(reservation_data[16])
            status_combobox.pack()

            if reservation_data[16] == "PAID/CONFIRMED":
                reservation_date_entry.config(state='disabled')
                rental_start_date_entry.config(state='disabled')
                rental_end_date_entry.config(state='disabled')

            submit_button = tk.Button(form_frame, text="CALCULATE", command=calculate)
            submit_button.pack(pady=(20, 0))

            submit_button = tk.Button(form_frame, text="Submit", command=submit_reservation_edit)
            submit_button.pack(pady=(20, 0))



        def load_vehicle_new_window():
            def vehicle_car_window_admin():
                def create_reservation():
                    selected_item = tree.selection()
                    if not selected_item:
                        messagebox.showerror("Error", "Please select a car to edit.")
                        return

                    item_values = tree.item(selected_item, 'values')
                    save_vehicle_id = item_values[0]  # Assuming VehicleID is the first column
                    save_vehicle_availability = item_values[7]
                    save_vehicle_rental_price = item_values[5]
                    if save_vehicle_availability == 'Leased':
                        messagebox.showinfo("Invalid", "The selected car is leased.")
                        return

                    window2.withdraw()

                    def submit_reservation():


                        customer_first_name = customer_first_name_entry.get()
                        customer_middle_name = customer_middle_name_entry.get()
                        customer_last_name = customer_last_name_entry.get()
                        email = email_entry.get()
                        phone_number = phone_number_entry.get()
                        street_address = street_address_entry.get()
                        brgy = brgy_entry.get()
                        city = city_entry.get()
                        zipcode = zipcode_entry.get()
                        reservation_date = reservation_date_entry.get()
                        rental_start_date1 = rental_start_date_entry.get()
                        rental_end_date1 = rental_end_date_entry.get()
                        rental_start_date = datetime.strptime(rental_start_date1, '%Y-%m-%d')
                        rental_end_date = datetime.strptime(rental_end_date1, '%Y-%m-%d')
                        total_cost = total_cost_entry.get()


                        status = status_combobox.get()
                        is_deleted = 0
                        employee_id = 1
                        vehicle_id = save_vehicle_id

                        if not all([customer_first_name, customer_last_name, email, phone_number, street_address, brgy,
                                    city, zipcode, reservation_date, rental_start_date, rental_end_date,
                                    status]):
                            messagebox.showerror("Error", "Please fill in all required fields")
                            return
                        if not total_cost:
                            messagebox.showerror("Error", "Calculate first before submitting")
                            return

                        reservation_data = {
                            'VehicleID': vehicle_id,
                            'EmployeeID': employee_id,
                            'CustomerFirstName': customer_first_name,
                            'CustomerMiddleName': customer_middle_name,
                            'CustomerLastName': customer_last_name,
                            'Email': email,
                            'PhoneNumber': phone_number,
                            'StreetAddress': street_address,
                            'Brgy': brgy,
                            'City': city,
                            'Zipcode': zipcode,
                            'ReservationDate': reservation_date,
                            'RentalStartDate': rental_start_date,
                            'RentalEndDate': rental_end_date,
                            'TotalCost': total_cost,
                            'Status': status,
                            'IsDeleted': is_deleted
                        }

                        conn = sqlite3.connect('vehicle_rental.db')
                        cursor = conn.cursor()

                        cursor.execute("""
                            INSERT INTO RESERVATION (VehicleID, EmployeeID, CustomerFirstName, CustomerMiddleName, CustomerLastName, Email, PhoneNumber, StreetAddress, Brgy, City, Zipcode, ReservationDate, RentalStartDate, RentalEndDate, TotalCost, Status, IsDeleted)
                            VALUES (:VehicleID, :EmployeeID, :CustomerFirstName, :CustomerMiddleName, :CustomerLastName, :Email, :PhoneNumber, :StreetAddress, :Brgy, :City, :Zipcode, :ReservationDate, :RentalStartDate, :RentalEndDate, :TotalCost, :Status, :IsDeleted)
                        """, reservation_data)

                        conn.commit()
                        conn.close()

                        conn = sqlite3.connect('vehicle_rental.db')
                        cursor = conn.cursor()

                        cursor.execute("""
                                        UPDATE VEHICLE
                                        SET AvailabilityStatus = ?
                                        WHERE VehicleID = ?
                                        """, ('Leased', vehicle_id))

                        conn.commit()
                        conn.close()

                        # Optional: Display confirmation message or navigate to another view
                        messagebox.showinfo("Success", "Reservation created successfully")
                        load_reservation()
                        create_reservation_window.destroy()

                    def calculate():
                        rental_start_date = rental_start_date_entry.get()
                        rental_end_date = rental_end_date_entry.get()
                        rental_start_date1 = datetime.strptime(rental_start_date, '%Y-%m-%d')
                        rental_end_date1 = datetime.strptime(rental_end_date, '%Y-%m-%d')
                        difference = (rental_end_date1 - rental_start_date1).days
                        total_cost = float(difference) * float(save_vehicle_rental_price)
                        total_cost_entry.config(state='normal')
                        total_cost_entry.delete(0, "end")
                        total_cost_entry.insert(0, str(total_cost))
                        total_cost_entry.config(state='readonly')


                    # Create the reservation creation window
                    create_reservation_window = tk.Toplevel(window2)
                    create_reservation_window.title("Create Reservation")
                    create_reservation_window.geometry("1080x800")

                    # Create the form frame
                    form_frame = tk.Frame(create_reservation_window, bg="#f0f0f0", bd=5, relief="groove")
                    form_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=900)

                    # Create form fields
                    tk.Label(form_frame, text="Create Reservation", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(
                        pady=(10, 20))

                    customer_first_name_label = tk.Label(form_frame, text="Customer First Name", bg="#f0f0f0")
                    customer_first_name_label.pack(pady=(5, 0))
                    customer_first_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_first_name_entry.pack()

                    customer_middle_name_label = tk.Label(form_frame, text="Customer Middle Name", bg="#f0f0f0")
                    customer_middle_name_label.pack(pady=(5, 0))
                    customer_middle_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_middle_name_entry.pack()

                    customer_last_name_label = tk.Label(form_frame, text="Customer Last Name", bg="#f0f0f0")
                    customer_last_name_label.pack(pady=(5, 0))
                    customer_last_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_last_name_entry.pack()

                    email_label = tk.Label(form_frame, text="Email", bg="#f0f0f0")
                    email_label.pack(pady=(5, 0))
                    email_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    email_entry.pack()

                    phone_number_label = tk.Label(form_frame, text="Phone Number", bg="#f0f0f0")
                    phone_number_label.pack(pady=(5, 0))
                    phone_number_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    phone_number_entry.pack()

                    street_address_label = tk.Label(form_frame, text="Street Address", bg="#f0f0f0")
                    street_address_label.pack(pady=(5, 0))
                    street_address_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    street_address_entry.pack()

                    brgy_label = tk.Label(form_frame, text="Brgy", bg="#f0f0f0")
                    brgy_label.pack(pady=(5, 0))
                    brgy_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    brgy_entry.pack()

                    city_label = tk.Label(form_frame, text="City", bg="#f0f0f0")
                    city_label.pack(pady=(5, 0))
                    city_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    city_entry.pack()

                    zipcode_label = tk.Label(form_frame, text="Zipcode", bg="#f0f0f0")
                    zipcode_label.pack(pady=(5, 0))
                    zipcode_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    zipcode_entry.pack()

                    reservation_date_label = tk.Label(form_frame, text="Reservation Date (YYYY-MM-DD)", bg="#f0f0f0")
                    reservation_date_label.pack(pady=(5, 0))
                    reservation_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                    reservation_date_entry.pack()

                    rental_start_date_label = tk.Label(form_frame, text="Rental Start Date (YYYY-MM-DD)", bg="#f0f0f0")
                    rental_start_date_label.pack(pady=(5, 0))
                    rental_start_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                    rental_start_date_entry.pack()

                    rental_end_date_label = tk.Label(form_frame, text="Rental End Date (YYYY-MM-DD)", bg="#f0f0f0")
                    rental_end_date_label.pack(pady=(5, 0))
                    rental_end_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                    rental_end_date_entry.pack()

                    total_cost_label = tk.Label(form_frame, text="Total Cost", bg="#f0f0f0")
                    total_cost_label.pack(pady=(5, 0))
                    total_cost_entry = tk.Entry(form_frame, bg='#f0f0f0',state='readonly')
                    total_cost_entry.pack()

                    status_label = tk.Label(form_frame, text="Status", bg="#f0f0f0")
                    status_label.pack(pady=(5, 0))
                    status_combobox = ttk.Combobox(form_frame, values=["PENDING/PAYMENT", "CANCELLED", "UNPAID/CANCELLED", "PAID/CONFIRMED", "PAID/CANCELLED", "IN-PROGRESS", "COMPLETED"],
                                                   state="readonly")
                    status_combobox.pack()

                    # Submit button
                    submit_button = tk.Button(form_frame, text="CALCULATE", command=calculate)
                    submit_button.pack(pady=(20, 0))

                    submit_button = tk.Button(form_frame, text="SUBMIT", command=submit_reservation)
                    submit_button.pack(pady=(20, 0))

                clear_frame(content_frame)

                columns = (
                    "VehicleID", "Make", "Model", "Year", "FuelType", "DailyRentalPrice", "VehicleType",
                    "AvailabilityStatus",
                    "BodyStyle", "TransmissionType", "NumberOfDoors", "CreatedBy"
                )
                tree = ttk.Treeview(content_frame, columns=columns, show='headings')
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)
                tree.pack(expand=True, fill='both')
                for row in tree.get_children():
                    tree.delete(row)
                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()
                cursor.execute("""
                SELECT VEHICLE.VehicleID, VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.VehicleType, VEHICLE.AvailabilityStatus, 
                CAR.BodyStyle, CAR.TransmissionType, CAR.NumberOfDoors, VEHICLE.CreatedBy 
                FROM VEHICLE 
                INNER JOIN CAR ON VEHICLE.VehicleID = CAR.VehicleID
                """)

                for row in cursor.fetchall():
                    tree.insert("", "end", values=row)

                conn.close()

                global button_frame
                button_frame = tk.Frame(content_frame)
                button_frame.pack(fill='x', pady=10)

                tk.Button(button_frame, text="SELECT", command=create_reservation, bg="lightblue").pack(side='left', padx=5)

            def vehicle_truck_window_admin():
                def create_reservation():
                    selected_item = tree.selection()
                    if not selected_item:
                        messagebox.showerror("Error", "Please select a car to edit.")
                        return

                    item_values = tree.item(selected_item, 'values')
                    save_vehicle_id = item_values[0]  # Assuming VehicleID is the first column
                    save_vehicle_availability = item_values[7]
                    save_vehicle_rental_price = item_values[5]
                    if save_vehicle_availability == 'Leased':
                        messagebox.showinfo("Invalid", "The selected car is leased.")
                        return

                    window2.withdraw()

                    def submit_reservation():
                        customer_first_name = customer_first_name_entry.get()
                        customer_middle_name = customer_middle_name_entry.get()
                        customer_last_name = customer_last_name_entry.get()
                        email = email_entry.get()
                        phone_number = phone_number_entry.get()
                        street_address = street_address_entry.get()
                        brgy = brgy_entry.get()
                        city = city_entry.get()
                        zipcode = zipcode_entry.get()
                        reservation_date = reservation_date_entry.get()
                        rental_start_date = rental_start_date_entry.get()
                        rental_end_date = rental_end_date_entry.get()
                        rental_start_date = datetime.strptime(rental_start_date, '%Y-%m-%d')
                        rental_end_date = datetime.strptime(rental_end_date, '%Y-%m-%d')
                        total_cost = total_cost_entry.get()
                        status = status_combobox.get()
                        is_deleted = 0
                        employee_id = 1
                        vehicle_id = save_vehicle_id

                        if not all([customer_first_name, customer_last_name, email, phone_number, street_address, brgy,
                                    city, zipcode, reservation_date, rental_start_date, rental_end_date, total_cost,
                                    status]):
                            messagebox.showerror("Error", "Please fill in all required fields")
                            return

                        reservation_data = {
                            'VehicleID': vehicle_id,
                            'EmployeeID': employee_id,
                            'CustomerFirstName': customer_first_name,
                            'CustomerMiddleName': customer_middle_name,
                            'CustomerLastName': customer_last_name,
                            'Email': email,
                            'PhoneNumber': phone_number,
                            'StreetAddress': street_address,
                            'Brgy': brgy,
                            'City': city,
                            'Zipcode': zipcode,
                            'ReservationDate': reservation_date,
                            'RentalStartDate': rental_start_date,
                            'RentalEndDate': rental_end_date,
                            'TotalCost': total_cost,
                            'Status': status,
                            'IsDeleted': is_deleted
                        }

                        conn = sqlite3.connect('vehicle_rental.db')
                        cursor = conn.cursor()

                        cursor.execute("""
                            INSERT INTO RESERVATION (VehicleID, EmployeeID, CustomerFirstName, CustomerMiddleName, CustomerLastName, Email, PhoneNumber, StreetAddress, Brgy, City, Zipcode, ReservationDate, RentalStartDate, RentalEndDate, TotalCost, Status, IsDeleted)
                            VALUES (:VehicleID, :EmployeeID, :CustomerFirstName, :CustomerMiddleName, :CustomerLastName, :Email, :PhoneNumber, :StreetAddress, :Brgy, :City, :Zipcode, :ReservationDate, :RentalStartDate, :RentalEndDate, :TotalCost, :Status, :IsDeleted)
                        """, reservation_data)

                        conn.commit()
                        conn.close()

                        conn = sqlite3.connect('vehicle_rental.db')
                        cursor = conn.cursor()

                        cursor.execute("""
                                        UPDATE VEHICLE
                                        SET AvailabilityStatus = ?
                                        WHERE VehicleID = ?
                                        """, ('Leased', vehicle_id))

                        conn.commit()
                        conn.close()

                        # Optional: Display confirmation message or navigate to another view
                        messagebox.showinfo("Success", "Reservation created successfully")
                        load_reservation()
                        create_reservation_window.destroy()

                    def calculate():
                        rental_start_date = rental_start_date_entry.get()
                        rental_end_date = rental_end_date_entry.get()
                        rental_start_date1 = datetime.strptime(rental_start_date, '%Y-%m-%d')
                        rental_end_date1 = datetime.strptime(rental_end_date, '%Y-%m-%d')
                        difference = (rental_end_date1 - rental_start_date1).days
                        total_cost = float(difference) * float(save_vehicle_rental_price)
                        total_cost_entry.config(state='normal')
                        total_cost_entry.delete(0, "end")
                        total_cost_entry.insert(0, str(total_cost))
                        total_cost_entry.config(state='readonly')

                    # Create the reservation creation window
                    create_reservation_window = tk.Toplevel(window2)
                    create_reservation_window.title("Create Reservation")
                    create_reservation_window.geometry("1080x800")

                    # Create the form frame
                    form_frame = tk.Frame(create_reservation_window, bg="#f0f0f0", bd=5, relief="groove")
                    form_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=900)

                    # Create form fields
                    tk.Label(form_frame, text="Create Reservation", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(
                        pady=(10, 20))

                    customer_first_name_label = tk.Label(form_frame, text="Customer First Name", bg="#f0f0f0")
                    customer_first_name_label.pack(pady=(5, 0))
                    customer_first_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_first_name_entry.pack()

                    customer_middle_name_label = tk.Label(form_frame, text="Customer Middle Name", bg="#f0f0f0")
                    customer_middle_name_label.pack(pady=(5, 0))
                    customer_middle_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_middle_name_entry.pack()

                    customer_last_name_label = tk.Label(form_frame, text="Customer Last Name", bg="#f0f0f0")
                    customer_last_name_label.pack(pady=(5, 0))
                    customer_last_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_last_name_entry.pack()

                    email_label = tk.Label(form_frame, text="Email", bg="#f0f0f0")
                    email_label.pack(pady=(5, 0))
                    email_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    email_entry.pack()

                    phone_number_label = tk.Label(form_frame, text="Phone Number", bg="#f0f0f0")
                    phone_number_label.pack(pady=(5, 0))
                    phone_number_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    phone_number_entry.pack()

                    street_address_label = tk.Label(form_frame, text="Street Address", bg="#f0f0f0")
                    street_address_label.pack(pady=(5, 0))
                    street_address_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    street_address_entry.pack()

                    brgy_label = tk.Label(form_frame, text="Brgy", bg="#f0f0f0")
                    brgy_label.pack(pady=(5, 0))
                    brgy_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    brgy_entry.pack()

                    city_label = tk.Label(form_frame, text="City", bg="#f0f0f0")
                    city_label.pack(pady=(5, 0))
                    city_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    city_entry.pack()

                    zipcode_label = tk.Label(form_frame, text="Zipcode", bg="#f0f0f0")
                    zipcode_label.pack(pady=(5, 0))
                    zipcode_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    zipcode_entry.pack()

                    reservation_date_label = tk.Label(form_frame, text="Reservation Date (YYYY-MM-DD)", bg="#f0f0f0")
                    reservation_date_label.pack(pady=(5, 0))
                    reservation_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white',
                                                       borderwidth=2,
                                                       date_pattern='yyyy-mm-dd')
                    reservation_date_entry.pack()

                    rental_start_date_label = tk.Label(form_frame, text="Rental Start Date (YYYY-MM-DD)", bg="#f0f0f0")
                    rental_start_date_label.pack(pady=(5, 0))
                    rental_start_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white',
                                                        borderwidth=2,
                                                        date_pattern='yyyy-mm-dd')
                    rental_start_date_entry.pack()

                    rental_end_date_label = tk.Label(form_frame, text="Rental End Date (YYYY-MM-DD)", bg="#f0f0f0")
                    rental_end_date_label.pack(pady=(5, 0))
                    rental_end_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white',
                                                      borderwidth=2,
                                                      date_pattern='yyyy-mm-dd')
                    rental_end_date_entry.pack()

                    total_cost_label = tk.Label(form_frame, text="Total Cost", bg="#f0f0f0")
                    total_cost_label.pack(pady=(5, 0))
                    total_cost_entry = tk.Entry(form_frame, bg='#f0f0f0', state='readonly')
                    total_cost_entry.pack()

                    status_label = tk.Label(form_frame, text="Status", bg="#f0f0f0")
                    status_label.pack(pady=(5, 0))
                    status_combobox = ttk.Combobox(form_frame,
                                                   values=["PENDING/PAYMENT", "CANCELLED", "UNPAID/CANCELLED",
                                                           "PAID/CONFIRMED",
                                                           "PAID/CANCELLED", "IN-PROGRESS", "COMPLETED"],
                                                   state="readonly")
                    status_combobox.pack()

                    # Submit button
                    submit_button = tk.Button(form_frame, text="CALCULATE", command=calculate)
                    submit_button.pack(pady=(20, 0))

                    submit_button = tk.Button(form_frame, text="SUBMIT", command=submit_reservation)
                    submit_button.pack(pady=(20, 0))

                clear_frame(content_frame)
                columns = (
                    "VehicleID", "Make", "Model", "Year", "FuelType", "DailyRentalPrice", "VehicleType",
                    "AvailabilityStatus",
                    "PayloadCapacity", "TruckBedSize", "NumberOfAxles", "CreatedBy"
                )
                tree = ttk.Treeview(content_frame, columns=columns, show='headings')
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)
                tree.pack(expand=True, fill='both')

                # Clear existing rows
                for row in tree.get_children():
                    tree.delete(row)

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()
                cursor.execute("""
                        SELECT VEHICLE.VehicleID, VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.VehicleType, VEHICLE.AvailabilityStatus, 
                        TRUCK.PayLoadCapacity, TRUCK.TruckBedSize, TRUCK.NumberOfAxles, VEHICLE.CreatedBy 
                        FROM VEHICLE 
                        INNER JOIN TRUCK ON VEHICLE.VehicleID = TRUCK.VehicleID
                        """)
                for row in cursor.fetchall():
                    tree.insert("", "end", values=row)
                conn.close()

                # Create buttons for CRUD operations
                global button_frame
                button_frame = tk.Frame(content_frame)
                button_frame.pack(fill='x', pady=10)

                tk.Button(button_frame, text="SELECT", command=create_reservation, bg="lightblue").pack(side='left', padx=5)

            def vehicle_motorcycle_window_admin():
                def create_reservation():
                    selected_item = tree.selection()
                    if not selected_item:
                        messagebox.showerror("Error", "Please select a car to edit.")
                        return

                    item_values = tree.item(selected_item, 'values')
                    save_vehicle_id = item_values[0]  # Assuming VehicleID is the first column
                    save_vehicle_availability = item_values[7]
                    save_vehicle_rental_price = item_values[5]
                    if save_vehicle_availability == 'Leased':
                        messagebox.showinfo("Invalid", "The selected car is leased.")
                        return

                    window2.withdraw()

                    def submit_reservation():
                        customer_first_name = customer_first_name_entry.get()
                        customer_middle_name = customer_middle_name_entry.get()
                        customer_last_name = customer_last_name_entry.get()
                        email = email_entry.get()
                        phone_number = phone_number_entry.get()
                        street_address = street_address_entry.get()
                        brgy = brgy_entry.get()
                        city = city_entry.get()
                        zipcode = zipcode_entry.get()
                        reservation_date = reservation_date_entry.get()
                        rental_start_date = rental_start_date_entry.get()
                        rental_end_date = rental_end_date_entry.get()
                        rental_start_date = datetime.strptime(rental_start_date, '%Y-%m-%d')
                        rental_end_date = datetime.strptime(rental_end_date, '%Y-%m-%d')
                        total_cost = total_cost_entry.get()
                        status = status_combobox.get()
                        is_deleted = 0
                        employee_id = 1
                        vehicle_id = save_vehicle_id

                        if not all([customer_first_name, customer_last_name, email, phone_number, street_address, brgy,
                                    city, zipcode, reservation_date, rental_start_date, rental_end_date, total_cost,
                                    status]):
                            messagebox.showerror("Error", "Please fill in all required fields")
                            return

                        reservation_data = {
                            'VehicleID': vehicle_id,
                            'EmployeeID': employee_id,
                            'CustomerFirstName': customer_first_name,
                            'CustomerMiddleName': customer_middle_name,
                            'CustomerLastName': customer_last_name,
                            'Email': email,
                            'PhoneNumber': phone_number,
                            'StreetAddress': street_address,
                            'Brgy': brgy,
                            'City': city,
                            'Zipcode': zipcode,
                            'ReservationDate': reservation_date,
                            'RentalStartDate': rental_start_date,
                            'RentalEndDate': rental_end_date,
                            'TotalCost': total_cost,
                            'Status': status,
                            'IsDeleted': is_deleted
                        }

                        conn = sqlite3.connect('vehicle_rental.db')
                        cursor = conn.cursor()

                        cursor.execute("""
                            INSERT INTO RESERVATION (VehicleID, EmployeeID, CustomerFirstName, CustomerMiddleName, CustomerLastName, Email, PhoneNumber, StreetAddress, Brgy, City, Zipcode, ReservationDate, RentalStartDate, RentalEndDate, TotalCost, Status, IsDeleted)
                            VALUES (:VehicleID, :EmployeeID, :CustomerFirstName, :CustomerMiddleName, :CustomerLastName, :Email, :PhoneNumber, :StreetAddress, :Brgy, :City, :Zipcode, :ReservationDate, :RentalStartDate, :RentalEndDate, :TotalCost, :Status, :IsDeleted)
                        """, reservation_data)

                        conn.commit()
                        conn.close()

                        conn = sqlite3.connect('vehicle_rental.db')
                        cursor = conn.cursor()

                        cursor.execute("""
                                        UPDATE VEHICLE
                                        SET AvailabilityStatus = ?
                                        WHERE VehicleID = ?
                                        """, ('Leased', vehicle_id))

                        conn.commit()
                        conn.close()

                        # Optional: Display confirmation message or navigate to another view
                        messagebox.showinfo("Success", "Reservation created successfully")
                        load_reservation()
                        create_reservation_window.destroy()

                    def calculate():
                        rental_start_date = rental_start_date_entry.get()
                        rental_end_date = rental_end_date_entry.get()
                        rental_start_date1 = datetime.strptime(rental_start_date, '%Y-%m-%d')
                        rental_end_date1 = datetime.strptime(rental_end_date, '%Y-%m-%d')
                        difference = (rental_end_date1 - rental_start_date1).days
                        total_cost = float(difference) * float(save_vehicle_rental_price)
                        total_cost_entry.config(state='normal')
                        total_cost_entry.delete(0, "end")
                        total_cost_entry.insert(0, str(total_cost))
                        total_cost_entry.config(state='readonly')

                    # Create the reservation creation window
                    create_reservation_window = tk.Toplevel(window2)
                    create_reservation_window.title("Create Reservation")
                    create_reservation_window.geometry("1080x800")

                    # Create the form frame
                    form_frame = tk.Frame(create_reservation_window, bg="#f0f0f0", bd=5, relief="groove")
                    form_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=900)

                    # Create form fields
                    tk.Label(form_frame, text="Create Reservation", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(
                        pady=(10, 20))

                    customer_first_name_label = tk.Label(form_frame, text="Customer First Name", bg="#f0f0f0")
                    customer_first_name_label.pack(pady=(5, 0))
                    customer_first_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_first_name_entry.pack()

                    customer_middle_name_label = tk.Label(form_frame, text="Customer Middle Name", bg="#f0f0f0")
                    customer_middle_name_label.pack(pady=(5, 0))
                    customer_middle_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_middle_name_entry.pack()

                    customer_last_name_label = tk.Label(form_frame, text="Customer Last Name", bg="#f0f0f0")
                    customer_last_name_label.pack(pady=(5, 0))
                    customer_last_name_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    customer_last_name_entry.pack()

                    email_label = tk.Label(form_frame, text="Email", bg="#f0f0f0")
                    email_label.pack(pady=(5, 0))
                    email_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    email_entry.pack()

                    phone_number_label = tk.Label(form_frame, text="Phone Number", bg="#f0f0f0")
                    phone_number_label.pack(pady=(5, 0))
                    phone_number_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    phone_number_entry.pack()

                    street_address_label = tk.Label(form_frame, text="Street Address", bg="#f0f0f0")
                    street_address_label.pack(pady=(5, 0))
                    street_address_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    street_address_entry.pack()

                    brgy_label = tk.Label(form_frame, text="Brgy", bg="#f0f0f0")
                    brgy_label.pack(pady=(5, 0))
                    brgy_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    brgy_entry.pack()

                    city_label = tk.Label(form_frame, text="City", bg="#f0f0f0")
                    city_label.pack(pady=(5, 0))
                    city_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    city_entry.pack()

                    zipcode_label = tk.Label(form_frame, text="Zipcode", bg="#f0f0f0")
                    zipcode_label.pack(pady=(5, 0))
                    zipcode_entry = tk.Entry(form_frame, bg='#f0f0f0')
                    zipcode_entry.pack()

                    reservation_date_label = tk.Label(form_frame, text="Reservation Date (YYYY-MM-DD)", bg="#f0f0f0")
                    reservation_date_label.pack(pady=(5, 0))
                    reservation_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white',
                                                       borderwidth=2,
                                                       date_pattern='yyyy-mm-dd')
                    reservation_date_entry.pack()

                    rental_start_date_label = tk.Label(form_frame, text="Rental Start Date (YYYY-MM-DD)", bg="#f0f0f0")
                    rental_start_date_label.pack(pady=(5, 0))
                    rental_start_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white',
                                                        borderwidth=2,
                                                        date_pattern='yyyy-mm-dd')
                    rental_start_date_entry.pack()

                    rental_end_date_label = tk.Label(form_frame, text="Rental End Date (YYYY-MM-DD)", bg="#f0f0f0")
                    rental_end_date_label.pack(pady=(5, 0))
                    rental_end_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white',
                                                      borderwidth=2,
                                                      date_pattern='yyyy-mm-dd')
                    rental_end_date_entry.pack()

                    total_cost_label = tk.Label(form_frame, text="Total Cost", bg="#f0f0f0")
                    total_cost_label.pack(pady=(5, 0))
                    total_cost_entry = tk.Entry(form_frame, bg='#f0f0f0', state='readonly')
                    total_cost_entry.pack()

                    status_label = tk.Label(form_frame, text="Status", bg="#f0f0f0")
                    status_label.pack(pady=(5, 0))
                    status_combobox = ttk.Combobox(form_frame,
                                                   values=["PENDING/PAYMENT", "CANCELLED", "UNPAID/CANCELLED",
                                                           "PAID/CONFIRMED",
                                                           "PAID/CANCELLED", "IN-PROGRESS", "COMPLETED"],
                                                   state="readonly")
                    status_combobox.pack()

                    # Submit button
                    submit_button = tk.Button(form_frame, text="CALCULATE", command=calculate)
                    submit_button.pack(pady=(20, 0))

                    submit_button = tk.Button(form_frame, text="SUBMIT", command=submit_reservation)
                    submit_button.pack(pady=(20, 0))

                clear_frame(content_frame)
                columns = (
                    "VehicleID", "Make", "Model", "Year", "FuelType", "DailyRentalPrice", "VehicleType",
                    "AvailabilityStatus",
                    "EngineDisplacement", "Type", "CreatedBy"
                )
                tree = ttk.Treeview(content_frame, columns=columns, show='headings')
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)
                tree.pack(expand=True, fill='both')
                # Clear existing rows
                for row in tree.get_children():
                    tree.delete(row)

                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()
                cursor.execute("""
                        SELECT VEHICLE.VehicleID, VEHICLE.Make, VEHICLE.Model, VEHICLE.Year, VEHICLE.FuelType, VEHICLE.DailyRentalPrice, VEHICLE.VehicleType, VEHICLE.AvailabilityStatus, 
                        MOTORCYCLE.EngineDisplacement, MOTORCYCLE.Type, VEHICLE.CreatedBy 
                        FROM VEHICLE 
                        INNER JOIN MOTORCYCLE ON VEHICLE.VehicleID = MOTORCYCLE.VehicleID
                        """)
                for row in cursor.fetchall():
                    tree.insert("", "end", values=row)
                conn.close()
                # Create buttons for CRUD operations
                global button_frame
                button_frame = tk.Frame(content_frame)
                button_frame.pack(fill='x', pady=10)

                tk.Button(button_frame, text="SELECT", command=create_reservation, bg="lightblue").pack(side='left', padx=5)


            def vehicle_type_change(event):
                vehicle_type = vehicle_type_combobox.get()
                if vehicle_type == "Cars":
                    vehicle_car_window_admin()
                elif vehicle_type == "Truck":
                    vehicle_truck_window_admin()
                elif vehicle_type == "Motorcycle":
                    vehicle_motorcycle_window_admin()

            window2 = tk.Toplevel(app)
            window2.title("Vehicle Selection")
            window2.geometry("1080x800")
            content_frame1 = tk.Frame(window2)
            content_frame1.pack(fill="x", pady=10)
            content_frame = tk.Frame(window2)
            content_frame.pack(side="top", fill="both", expand=True)
            vehicle_type_label = tk.Label(content_frame1, text="Vehicle Type")
            vehicle_type_label.pack(pady=5)
            vehicle_type_combobox = ttk.Combobox(content_frame1, values=["Cars", "Truck", "Motorcycle"],
                                                 state="readonly")
            vehicle_type_combobox.set("Truck")
            vehicle_type_combobox.pack(pady=5)
            vehicle_type_combobox.bind("<<ComboboxSelected>>", vehicle_type_change)

            # Load the default content
            vehicle_type_change(None)

        label = tk.Label(frame, text="Reservation Frame", bg='#FFFFFF', font=('Helvetica', 14, 'bold'))
        label.pack(pady=20)

        button_frame = tk.Frame(frame, bg='white')
        button_frame.pack(side='bottom', fill='x', pady=10)

        create_button = tk.Button(button_frame, text="CREATE", command=load_vehicle_new_window, bg="yellow")
        create_button.pack(side='left', padx=5)

        read_button = tk.Button(button_frame, text="EDIT", command=edit_reservation, bg="lightblue")
        read_button.pack(side='left', padx=5)

        delete_button = tk.Button(button_frame, text="DELETE", command=soft_delete_reservation, bg="red", fg="white")
        delete_button.pack(side='left', padx=5)

        tree = ttk.Treeview(frame, columns=('GuestNo', 'GuestName', 'VehicleType', 'VehicleName', 'Status'), show='headings')
        for row in tree.get_children():
            tree.delete(row)
        tree.heading('GuestNo', text='Guest No.')
        tree.heading('GuestName', text='Guest Name')
        tree.heading('VehicleType', text='Vehicle Type')
        tree.heading('VehicleName', text='Vehicle Name')
        tree.heading('Status', text='Status')
        tree.pack(fill='both', expand=True)
        load_reservation()
        tree.column('GuestNo', width=100)
        tree.column('GuestName', width=150)
        tree.column('VehicleType', width=100)
        tree.column('VehicleName', width=150)
        tree.column('Status', width=100)



    def create_payment_frame(self, frame):


        def load_reservation_select():
            def select_reservation():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showerror("Error", "Please select a reservation to delete.")
                    return

                item_values = tree.item(selected_item, 'values')
                global reservation_id
                reservation_id = item_values[0]
                conn = sqlite3.connect('vehicle_rental.db')
                cursor = conn.cursor()
                cursor.execute("SELECT TotalCost FROM RESERVATION WHERE ReservationID=?", (reservation_id,))
                global result
                result = cursor.fetchone()
                conn.close()
                paymongo()

            root = tk.Toplevel(app)
            root.title("Select Reservation")
            tree = ttk.Treeview(root, columns=('GuestNo', 'GuestName', 'VehicleType', 'VehicleName', 'Status'),
                                show='headings')
            for row in tree.get_children():
                tree.delete(row)
            tree.heading('GuestNo', text='Guest No.')
            tree.heading('GuestName', text='Guest Name')
            tree.heading('VehicleType', text='Vehicle Type')
            tree.heading('VehicleName', text='Vehicle Name')
            tree.heading('Status', text='Status')
            tree.pack(fill='both', expand=True)
            tree.column('GuestNo', width=100)
            tree.column('GuestName', width=150)
            tree.column('VehicleType', width=100)
            tree.column('VehicleName', width=150)
            tree.column('Status', width=100)
            for row in tree.get_children():
                tree.delete(row)
            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            query = """
            SELECT r.ReservationID, r.CustomerFirstName || ' ' || r.CustomerLastName AS GuestName, v.VehicleType, v.Make || ' ' || v.Model AS VehicleName, r.Status
            FROM RESERVATION r
            JOIN VEHICLE v ON r.VehicleID = v.VehicleID
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                tree.insert('', 'end', values=row)
            button_frame = tk.Frame(root, bg='white')
            button_frame.pack(side='bottom', fill='x', pady=10)

            create_button = tk.Button(button_frame, text="SELECT", command=select_reservation, bg="yellow")
            create_button.pack(side='left', padx=5)

        def paymongo():
            def submit_payment():
                card_number = card_number_entry.get()
                exp_month = exp_month_entry.get()
                exp_year = exp_year_entry.get()
                cvc = cvc_entry.get()
                amount = amount_entry.get()

                if not all([card_number, exp_month, exp_year, cvc, amount]):
                    messagebox.showerror("Error", "All fields are required")
                    return

                try:
                    amount = int(amount)
                except ValueError:
                    messagebox.showerror("Error", "Amount must be an integer")
                    return

                payment_method = paymongo.create_payment_method(card_number, exp_month, exp_year, cvc)
                if 'errors' in payment_method:
                    messagebox.showerror("Error", payment_method['errors'][0]['detail'])
                    return

                payment_method_id = payment_method['data']['id']
                payment_intent = paymongo.create_payment_intent(amount, 'PHP', 'Test Payment')
                if 'errors' in payment_intent:
                    messagebox.showerror("Error", payment_intent['errors'][0]['detail'])
                    return

                intent_id = payment_intent['data']['id']
                attachment = paymongo.attach_payment_method(intent_id, payment_method_id)
                if 'errors' in attachment:
                    messagebox.showerror("Error", attachment['errors'][0]['detail'])
                    return
                else:
                    payment_data = {
                        'ReservationID': reservation_id,
                        'PaymentAmount': amount_entry.get()[:-2],
                        'PaymentMethod': 'Credit Card',
                        'PaymentStatus': 'Paid',
                        'IsDeleted': 0
                    }

                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("""
                                                                                    INSERT INTO PAYMENT (ReservationID, PaymentAmount, PaymentMethod, PaymentStatus, IsDeleted)
                                                                                    VALUES (:ReservationID, :PaymentAmount, :PaymentMethod, :PaymentStatus, :IsDeleted)
                                                                                """, payment_data)
                    conn.commit()
                    conn.close()

                    status = "PAID/CONFIRMED"

                    conn = sqlite3.connect('vehicle_rental.db')
                    cursor = conn.cursor()

                    cursor.execute("""
                                                    UPDATE RESERVATION
                                                    SET Status = ?
                                                    WHERE ReservationID = ?
                                                    """, (status,
                                                          reservation_id))

                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Payment Successful")

                load_payment_all()
                root.destroy()


            paymongo = PayMongoClient("sk_test_4iw88FL6V5hTMfNfvZzBGjUP")
            root = tk.Toplevel(app)
            root.title("PayMongo Payment")

            tk.Label(root, text="Card Number").grid(row=0, column=0)
            card_number_entry = tk.Entry(root)
            card_number_entry.grid(row=0, column=1)

            tk.Label(root, text="Exp Month").grid(row=1, column=0)
            exp_month_entry = tk.Entry(root)
            exp_month_entry.grid(row=1, column=1)

            tk.Label(root, text="Exp Year").grid(row=2, column=0)
            exp_year_entry = tk.Entry(root)
            exp_year_entry.grid(row=2, column=1)

            tk.Label(root, text="CVC").grid(row=3, column=0)
            cvc_entry = tk.Entry(root)
            cvc_entry.grid(row=3, column=1)

            tk.Label(root, text="Amount (in PHP)").grid(row=4, column=0)
            amount_entry = tk.Entry(root)
            amount_entry.grid(row=4, column=1)
            amount_entry.insert(0, str(result)[1:-4]+'00')
            amount_entry.config(state='readonly')

            submit_button = tk.Button(root, text="Submit Payment", command=submit_payment)
            submit_button.grid(row=5, columnspan=2)

        def payment_type_change(event):
            payment_method = selected_method.get()
            print(f"Payment method selected: {payment_method}")  # Debugging print statement
            if payment_method == "All":
                load_payment_all()
            else:
                load_payment(payment_method)

        def load_payment_all():
            for row in payment_tree.get_children():
                payment_tree.delete(row)

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            query = """
            SELECT p.PaymentID, r.CustomerFirstName || ' ' || r.CustomerLastName AS GuestName, v.VehicleType, v.Make || ' ' || v.Model AS VehicleName, p.PaymentMethod
            FROM PAYMENT p
            JOIN RESERVATION r ON r.ReservationID = p.ReservationID
            JOIN VEHICLE v ON r.VehicleID = v.VehicleID
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                payment_tree.insert('', 'end', values=row)

        def load_payment(payment_method):
            for row in payment_tree.get_children():
                payment_tree.delete(row)

            conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            query = """
            SELECT p.PaymentID, r.CustomerFirstName || ' ' || r.CustomerLastName AS GuestName, v.VehicleType, v.Make || ' ' || v.Model AS VehicleName, p.PaymentMethod
            FROM PAYMENT p
            JOIN RESERVATION r ON r.ReservationID = p.ReservationID
            JOIN VEHICLE v ON r.VehicleID = v.VehicleID
            WHERE p.PaymentMethod = ?
            """
            cursor.execute(query, (payment_method,))
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                payment_tree.insert('', 'end', values=row)

        label = tk.Label(frame, text="Payment Frame", bg='#FFFFFF', font=('Helvetica', 14, 'bold'))
        label.pack(pady=20)

        button_frame = tk.Frame(frame, bg='white')
        button_frame.pack(side='bottom', fill='x', pady=10)

        create_button = tk.Button(button_frame, text="CREATE", bg="yellow", command=load_reservation_select)
        create_button.pack(side='left', padx=5)

        payment_methods = ["All", "Cash", "Credit Card"]
        selected_method = tk.StringVar()
        selected_method.set(payment_methods[0])
        dropdown = tk.OptionMenu(frame, selected_method, *payment_methods, command=lambda event=None: payment_type_change(event))
        dropdown.pack(pady=10)


        payment_tree = ttk.Treeview(frame,
                                    columns=('PaymentID', 'ClientName', 'VehicleType', 'VehicleName', 'PaymentMethod'),
                                    show='headings')
        payment_tree.heading('PaymentID', text='Payment ID')
        payment_tree.heading('ClientName', text='Client Name')
        payment_tree.heading('VehicleType', text='Vehicle Type')
        payment_tree.heading('VehicleName', text='Vehicle Name')
        payment_tree.heading('PaymentMethod', text='Payment Method')
        payment_tree.pack(fill='both', expand=True)

        payment_tree.column('PaymentID', width=100)
        payment_tree.column('ClientName', width=150)
        payment_tree.column('VehicleType', width=100)
        payment_tree.column('VehicleName', width=150)
        payment_tree.column('PaymentMethod', width=100)

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

if __name__ == "__main__":
    setup_database()
    create_admin_employee()
    test = 1
    while test == 1:
        main()
        if test == 0:
            break
        app = VehicleRentingApp()
        app.mainloop()

        #new testing to push