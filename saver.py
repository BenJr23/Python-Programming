
save_vehicle_rental_price = item_values[5]

rental_start_date = datetime.strptime(rental_start_date, '%Y-%m-%d')
rental_end_date = datetime.strptime(rental_end_date, '%Y-%m-%d')

conn = sqlite3.connect('vehicle_rental.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE RESERVATION SET IsDeleted = 1 WHERE ReservationID = ?", (reservation_id,))
            conn.commit()
            conn.close()
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

    reservation_date_label = tk.Label(form_frame, text="Reservation Date (YYYY-MM-DD)", bg="#f0f0f0")
    reservation_date_label.pack(pady=(5, 0))
    reservation_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                       date_pattern='yyyy-mm-dd')
    reservation_date_entry.pack()

    rental_start_date_label = tk.Label(form_frame, text="Rental Start Date (YYYY-MM-DD)", bg="#f0f0f0")
    rental_start_date_label.pack(pady=(5, 0))
    rental_start_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                        date_pattern='yyyy-mm-dd')
    rental_start_date_entry.pack()

    rental_end_date_label = tk.Label(form_frame, text="Rental End Date (YYYY-MM-DD)", bg="#f0f0f0")
    rental_end_date_label.pack(pady=(5, 0))
    rental_end_date_entry = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                      date_pattern='yyyy-mm-dd')
    rental_end_date_entry.pack()

    total_cost_label = tk.Label(form_frame, text="Total Cost", bg="#f0f0f0")
    total_cost_label.pack(pady=(5, 0))
    total_cost_entry = tk.Entry(form_frame, bg='#f0f0f0', state='readonly')
    total_cost_entry.pack()

    status_label = tk.Label(form_frame, text="Status", bg="#f0f0f0")
    status_label.pack(pady=(5, 0))
    status_combobox = ttk.Combobox(form_frame,
                                   values=["PENDING/PAYMENT", "CANCELLED", "UNPAID/CANCELLED", "PAID/CONFIRMED",
                                           "PAID/CANCELLED", "IN-PROGRESS", "COMPLETED"],
                                   state="readonly")
    status_combobox.pack()

    # Submit button
    submit_button = tk.Button(form_frame, text="CALCULATE", command=calculate)
    submit_button.pack(pady=(20, 0))

    submit_button = tk.Button(form_frame, text="SUBMIT", command=submit_reservation)
    submit_button.pack(pady=(20, 0))