from flask import Flask, render_template, request, redirect, session, flash,url_for
import mysql.connector
from datetime import datetime
from mysql.connector.errors import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="hotel_db"
)

cursor = db.cursor(dictionary=True)

# --------- AUTH ---------
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    if user:
        session['user'] = user['username']
        return redirect('/dashboard')
    flash("Invalid login")
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# --------- DASHBOARD ---------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    cursor.execute("SELECT COUNT(*) AS total FROM rooms")
    room_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM guests")
    guest_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM bookings")
    booking_count = cursor.fetchone()['total']

    return render_template('dashboard.html', room_count=room_count, guest_count=guest_count, booking_count=booking_count)

# ---------- ROOMS ----------
@app.route('/rooms')
def rooms():
    if 'user' not in session:
        return redirect('/')
    cursor.execute("""
        SELECT rooms.id, rooms.room_number, room_types.type_name, rooms.status, rooms.price_per_night
        FROM rooms
        JOIN room_types ON rooms.room_type_id = room_types.id
    """)
    rooms = cursor.fetchall()

    cursor.execute("SELECT * FROM room_types")
    room_types = cursor.fetchall()

    return render_template('rooms.html', rooms=rooms, room_types=room_types)


@app.route('/add_room', methods=['POST'])
def add_room():
    room_number = request.form['room_number']
    room_type_id = request.form['room_type_id']
    price = request.form['price']
    cursor.execute(
        "INSERT INTO rooms (room_number, room_type_id, price_per_night) VALUES (%s, %s, %s)",
        (room_number, room_type_id, price)
    )
    db.commit()
    flash("Room added successfully!")
    return redirect('/rooms')


@app.route('/update_room/<int:id>', methods=['POST'])
def update_room(id):
    room_number = request.form['room_number']
    room_type_id = request.form['room_type_id']
    price = request.form['price']
    cursor.execute(
        "UPDATE rooms SET room_number=%s, room_type_id=%s, price_per_night=%s WHERE id=%s",
        (room_number, room_type_id, price, id)
    )
    db.commit()
    flash("Room updated successfully!")
    return redirect('/rooms')


@app.route('/delete-room/<int:id>')
def delete_room(id):
    if 'user' not in session:
        return redirect('/')

    try:
        cursor.execute("DELETE FROM rooms WHERE id = %s", (id,))
        db.commit()
        flash("Room deleted successfully!")
    except IntegrityError as e:
        db.rollback()
        if e.errno == 1451:
            flash("Cannot delete room: It is linked to existing bookings.")
        else:
            flash(f"An error occurred: {str(e)}")

    return redirect('/rooms')

# --------- GUESTS ---------
@app.route('/guests')
def guests():
    if 'user' not in session:
        return redirect('/')
    cursor.execute("SELECT * FROM guests")
    guests = cursor.fetchall()
    return render_template('guests.html', guests=guests)

@app.route('/add_guest', methods=['POST'])
def add_guest():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    cursor.execute("INSERT INTO guests (name, email, phone, address) VALUES (%s, %s, %s, %s)", (name, email, phone, address))
    db.commit()
    flash("Guest added")
    return redirect('/guests')

@app.route('/delete-guest/<int:id>')
def delete_guest(id):
    if 'user' not in session:
        return redirect('/')
    
    try:
        cursor.execute("DELETE FROM guests WHERE id = %s", (id,))
        db.commit()
        flash("Guest deleted successfully!", "success")
    
    except IntegrityError as e:
        if "foreign key constraint fails" in str(e):
            flash("Cannot delete guest as they have active bookings or related records. Please remove those first.", "danger")
        else:
            flash(f"An unexpected database error occurred: {str(e)}", "danger")
    
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")

    return redirect('/guests')


@app.route('/update_guest/<int:id>', methods=['POST'])
def update_guest(id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    cursor.execute("UPDATE guests SET name=%s, email=%s, phone=%s, address=%s WHERE id=%s", (name, email, phone, address, id))
    flash("Guest updated")
    db.commit()
    return redirect('/guests')

# @app.route('/edit-guest/<int:id>')
# def edit_guest(id):
#     if 'user' not in session:
#         return redirect('/')
#     cursor.execute("SELECT * FROM guests WHERE id = %s", (id,))
#     guest = cursor.fetchone()
#     return render_template('edit_guest.html', guest=guest)

# --------- BOOKINGS ---------
@app.route('/bookings')
def bookings():
    if 'user' not in session:
        return redirect('/')
    
    query = """
    SELECT bookings.*, guests.name AS guest_name, rooms.room_number
    FROM bookings
    JOIN guests ON bookings.guest_id = guests.id
    JOIN rooms ON bookings.room_id = rooms.id
    """
    cursor.execute(query)
    bookings = cursor.fetchall()

    cursor.execute("SELECT id, name FROM guests")
    guests = cursor.fetchall()

    cursor.execute("SELECT id, room_number FROM rooms")
    rooms = cursor.fetchall()

    return render_template('bookings.html', bookings=bookings, guests=guests, rooms=rooms)

@app.route('/add_booking', methods=['POST'])
def add_booking():
    if 'user' not in session:
        return redirect('/')

    guest_id = request.form['guest_id']
    room_id = request.form['room_id']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    
    cursor.execute("""
        SELECT * FROM bookings 
        WHERE room_id = %s AND (
            (check_in <= %s AND check_out > %s) OR
            (check_in < %s AND check_out >= %s) OR
            (check_in >= %s AND check_out <= %s)
        )
    """, (room_id, check_in, check_in, check_out, check_out, check_in, check_out))
    
    conflict = cursor.fetchone()
    if conflict:
        flash("Room is already booked for the selected dates.")
        return redirect('/bookings')


    cursor.execute("""
        INSERT INTO bookings (guest_id, room_id, check_in, check_out)
        VALUES (%s, %s, %s, %s)
    """, (guest_id, room_id, check_in, check_out))
    booking_id = cursor.lastrowid


    cursor.execute("SELECT price_per_night FROM rooms WHERE id = %s", (room_id,))
    room = cursor.fetchone()
    if not room:
        flash("Invalid room.")
        return redirect('/bookings')

    price = room['price_per_night']
    nights = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days

    if nights <= 0:
        flash("Invalid date range. Check-out must be after check-in.")
        return redirect('/bookings')

    total_amount = price * nights


    cursor.execute("""
        INSERT INTO payments (booking_id, amount, payment_date, payment_method)
        VALUES (%s, %s, %s, %s)
    """, (booking_id, total_amount, datetime.today().date(), 'Cash'))


    cursor.execute("UPDATE rooms SET status = 'booked' WHERE id = %s", (room_id,))

    db.commit()
    flash("Booking and payment recorded successfully!")
    return redirect('/bookings')

@app.route('/update_booking/<int:id>', methods=['POST'])
def update_booking(id):
    if 'user' not in session:
        return redirect('/')

    guest_id = request.form['guest_id']
    new_room_id = request.form['room_id']
    check_in = request.form['check_in']
    check_out = request.form['check_out']

    # Get the original booking info
    cursor.execute("SELECT room_id FROM bookings WHERE id = %s", (id,))
    original_booking = cursor.fetchone()
    if not original_booking:
        flash("Original booking not found.")
        return redirect('/bookings')

    old_room_id = original_booking['room_id']

    # Check for overlapping bookings for the new room
    cursor.execute("""
        SELECT * FROM bookings 
        WHERE room_id = %s AND id != %s
        AND (
            (check_in <= %s AND check_out > %s) OR
            (check_in < %s AND check_out >= %s) OR
            (check_in >= %s AND check_out <= %s)
        )
    """, (new_room_id, id, check_in, check_in, check_out, check_out, check_in, check_out))
    
    conflict = cursor.fetchone()
    if conflict:
        flash("Error: Room is already booked for these dates!")
        return redirect('/bookings')

    # Update booking
    cursor.execute("""
        UPDATE bookings 
        SET guest_id=%s, room_id=%s, check_in=%s, check_out=%s
        WHERE id=%s
    """, (guest_id, new_room_id, check_in, check_out, id))

    # Update room statuses if the room was changed
    if old_room_id != new_room_id:
        # Check if old room still has active bookings
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM bookings 
            WHERE room_id = %s AND id != %s AND check_out >= CURDATE()
        """, (old_room_id, id))
        old_active = cursor.fetchone()['cnt']
        if old_active == 0:
            cursor.execute("UPDATE rooms SET status = 'available' WHERE id = %s", (old_room_id,))

        # Mark new room as booked
        cursor.execute("UPDATE rooms SET status = 'booked' WHERE id = %s", (new_room_id,))

    db.commit()
    flash("Booking updated successfully!")
    return redirect('/bookings')


@app.route('/edit-booking/<int:id>')
def edit_booking(id):
    if 'user' not in session:
        return redirect('/')
    
    cursor.execute("SELECT * FROM bookings WHERE id = %s", (id,))
    booking = cursor.fetchone()

    booking['check_in'] = booking['check_in'].strftime('%Y-%m-%d')
    booking['check_out'] = booking['check_out'].strftime('%Y-%m-%d')

    cursor.execute("SELECT id, name FROM guests")
    guests = cursor.fetchall()

    cursor.execute("SELECT id, room_number FROM rooms")
    rooms = cursor.fetchall()

    return render_template('edit_booking.html', booking=booking, guests=guests, rooms=rooms)


@app.route('/cancel-booking/<int:booking_id>')
def cancel_booking(booking_id):
    try:
        # Get room_id before deleting the booking
        cursor.execute("SELECT room_id FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            flash("Booking not found.", "danger")
            return redirect(url_for('bookings'))

        room_id = booking['room_id']

        # Delete the booking
        cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
        db.commit()

        # Check if the room still has any future bookings
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM bookings 
            WHERE room_id = %s AND check_out >= CURDATE()
        """, (room_id,))
        active = cursor.fetchone()['cnt']

        # If no active bookings, mark it available
        if active == 0:
            cursor.execute("UPDATE rooms SET status = 'available' WHERE id = %s", (room_id,))
            db.commit()

        flash('Booking cancelled successfully!', 'success')

    except Exception as e:
        if "foreign key constraint fails" in str(e):
            flash("Cannot cancel this booking as it is linked to one or more services. Please remove the associated services first.", "danger")
        else:
            flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('bookings'))


# --------- PAYMENTS ---------
@app.route('/payments')
def payments():
    if 'user' not in session:
        return redirect('/')
    query = """
    SELECT payments.*, guests.name AS guest_name
    FROM payments
    JOIN bookings ON payments.booking_id = bookings.id
    JOIN guests ON bookings.guest_id = guests.id
    """
    cursor.execute(query)
    payments = cursor.fetchall()
    return render_template('payments.html', payments=payments)

# --------- FEEDBACK ---------
@app.route('/feedback')
def feedback():
    if 'user' not in session:
        return redirect('/')
    query = """
    SELECT feedbacks.*, guests.name AS guest_name
    FROM feedbacks
    JOIN guests ON feedbacks.guest_id = guests.id
    """
    cursor.execute(query)
    feedbacks = cursor.fetchall()
    return render_template('feedback.html', feedbacks=feedbacks)

# --------- RUN APP ---------
if __name__ == '__main__':
    app.run(debug=True, port=5003)
