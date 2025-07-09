from flask import Flask, render_template, Blueprint, request, redirect, flash, url_for, session
import mysql.connector
import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import Error
import os
from werkzeug.utils import secure_filename
from flask import current_app
from flask import jsonify, session, request
from datetime import datetime, date

moon_routes = Blueprint('moon_routes', __name__)


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="hida system integrate"
)
cursor = db.cursor(dictionary=True)
#users routes

#dashboard for users
@moon_routes.route('/')
def index():
    is_logged_in = 'user_id' in session

    # Fetch rooms: one per type
    cursor.execute("""
        SELECT room_type, 
               MIN(description) AS description, 
               MIN(price) AS price, 
               MIN(image) AS image
        FROM rooms
        GROUP BY room_type
    """)
    rooms = cursor.fetchall()

    # Fetch recent accepted feedback with usernames and ratings
    cursor.execute("""
        SELECT f.message, f.submitted_at, u.username, f.rating
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        WHERE f.status = 'accepted'
        ORDER BY f.submitted_at DESC
    """)
    feedbacks = cursor.fetchall()

    return render_template('index.html', is_logged_in=is_logged_in, rooms=rooms, feedbacks=feedbacks)


#Logout
@moon_routes.route('/logout')
def logout():
    session.pop('user_id', None)  
    return redirect('/')

#Login
@moon_routes.route('/login')
def login():
    return render_template('login.html')

#Login Action
@moon_routes.route('/login_submit', methods=['POST'])
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    usernameError = None
    passwordError = None

    if not username:
        usernameError = "Username is required."
    if not password:
        passwordError = "Password is required."

    if username and password:
        try:
            # Check in the admins table
            cursor.execute("SELECT * FROM admins WHERE name = %s", (username,))
            admin = cursor.fetchone()

            if admin:
                if check_password_hash(admin['password_hash'], password):
                    session['admin_id'] = admin['id']
                    session['admin_name'] = admin['name']
                    return redirect(url_for('moon_routes.admin'))  
                else:
                    passwordError = "Incorrect password."
            else:
                
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user:
                    if check_password_hash(user['password_hash'], password):
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        return redirect(url_for('moon_routes.index'))  
                    else:
                        passwordError = "Incorrect password."
                else:
                    usernameError = "Username not found."

        except Error as e:
            flash(f"Database error: {e}")

    return render_template("login.html", usernameError=usernameError, passwordError=passwordError)

#Register for user
@moon_routes.route('/register')
def register():
    return render_template('register.html')

#Register action for users
@moon_routes.route('/register_submit', methods=['POST'])
def register_submit():
    username = request.form['username']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    phone = request.form['phone']
    address = request.form['address']
    age = request.form['age']

    print(f"Username: {username}, Name: {name}, Email: {email}, Phone: {phone}, Address: {address}, Age: {age}")

    if password != confirm_password:
        flash('Passwords do not match', 'password_error')
        return redirect(url_for('moon_routes.register'))

    if len(password) < 6:
        flash('Password must be at least 6 characters', 'password_length_error')
        return redirect(url_for('moon_routes.register'))

    if not age.isdigit() or int(age) <= 0:
        flash('Age must be a positive number', 'age_error')
        return redirect(url_for('moon_routes.register'))

    password_hash = generate_password_hash(password)

    try:
        # ✅ First, check if the username exists in the admins table
        cursor.execute("SELECT * FROM admins WHERE name = %s", (username,))
        if cursor.fetchone():
            flash('Username already exist', 'username_error')
            return redirect(url_for('moon_routes.register'))

        # ✅ Then check if the username exists in the users table
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash('Username already exist', 'username_error')
            return redirect(url_for('moon_routes.register'))

        # Check if email is already used in users table
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email already exists', 'email_error')
            return redirect(url_for('moon_routes.register'))

        # Insert new user into users table
        cursor.execute(
            "INSERT INTO users (username, name, email, password_hash, phone, address, age) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (username, name, email, password_hash, phone, address, int(age))
        )
        db.commit()
        print("✅ User inserted successfully!")

    except Error as e:
        print(f"❌ Database error: {e}")
        flash('Something went wrong with the database.', 'db_error')
        return redirect(url_for('moon_routes.register'))

    return redirect(url_for('moon_routes.login'))


#Forget Password
@moon_routes.route('/forget_password')
def forget_password():
    return render_template('forget_password.html')

#Reset Action for Password of User
@moon_routes.route('/reset_submit', methods=['POST'])
def reset_submit():
    username = request.form['username']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    # Error placeholders
    username_err = new_password_err = confirm_password_err = ''

    # Basic validations
    if not username:
        username_err = "Username is required."
    if not new_password:
        new_password_err = "New password is required."
    elif len(new_password) < 6:
        new_password_err = "Password must be at least 6 characters long."
    if new_password != confirm_password:
        confirm_password_err = "Passwords do not match."

    if username_err or new_password_err or confirm_password_err:
        return render_template('forget_password.html',
                               username=username,
                               username_err=username_err,
                               new_password_err=new_password_err,
                               confirm_password_err=confirm_password_err)

    # Check user existence
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user:
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s", (hashed_password, username))
        db.commit()
        flash('Password updated successfully. Please log in.', 'success')
        return redirect(url_for('moon_routes.login'))  # Adjust if your login route is different
    else:
        username_err = "Username not found."
        return render_template('forget_password.html',
                               username=username,
                               username_err=username_err)


#Rooms
@moon_routes.route('/rooms')
def rooms():
    is_logged_in = 'user_id' in session

    # Fetch only one room per room_type
    cursor.execute("""
        SELECT room_type, 
               MIN(description) AS description, 
               MIN(price) AS price, 
               MIN(image) AS image
        FROM rooms
        GROUP BY room_type
    """)
    available_rooms = cursor.fetchall()

    return render_template('rooms.html', is_logged_in=is_logged_in, available_rooms=available_rooms)


# Amenities 
@moon_routes.route('/amenities')
def amenities():
    is_logged_in = 'user_id' in session
    try:
        cursor.execute("SELECT * FROM amenities")
        amenities = cursor.fetchall()
        return render_template('amenities.html',is_logged_in=is_logged_in, amenities=amenities)
    except Error as e:
        flash(f"Error fetching amenities: {e}", "danger")
        return render_template('amenities.html',is_logged_in=is_logged_in, amenities=[])

#Book
# Book Room Page
@moon_routes.route('/bookroom')
def bookroom():
    if 'user_id' not in session:
        return redirect(url_for('moon_routes.login'))

    is_logged_in = True

    cursor.execute("SELECT * FROM rooms WHERE status = 'available'")
    available_rooms = cursor.fetchall()

    cursor.execute("SELECT * FROM amenities")
    amenities = cursor.fetchall()

    return render_template('bookroom.html', is_logged_in=is_logged_in,available_rooms=available_rooms, amenities=amenities)


@moon_routes.route('/payment_book', methods=['POST'])
def payment_bookroom():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to proceed.", "error")
        return redirect(url_for('auth.login'))

    room_id = request.form.get('room_id')
    room_type = request.form.get('room_type')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guest = request.form.get('guest')

    amenity_ids_str = request.form.get('amenity_ids')
    amenity_ids = amenity_ids_str.split(",") if amenity_ids_str else []

    # Date parsing and validation
    date_format = "%Y-%m-%d"
    try:
        d1 = datetime.strptime(check_in, date_format).date()
        d2 = datetime.strptime(check_out, date_format).date()
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "error")
        return redirect(url_for('moon_routes.bookroom'))

    today = date.today()

    if d1 < today:
        flash("Check-in date cannot be earlier than today.", "error")
        return redirect(url_for('moon_routes.bookroom'))

    if d2 <= d1:
        flash("Check-out date must be after check-in date.", "error")
        return redirect(url_for('moon_routes.bookroom'))

    # Fetch room details (price)
    cursor.execute("SELECT price FROM rooms WHERE id = %s", (room_id,))
    room = cursor.fetchone()
    if not room:
        flash("Selected room not found.", "error")
        return redirect(url_for('moon_routes.booking_page'))

    room_price = room['price']

    # Calculate number of nights
    nights = (d2 - d1).days

    # Fetch selected amenities and sum prices
    selected_amenities = []
    amenities_total = 0
    if amenity_ids:
        placeholders = ",".join(["%s"] * len(amenity_ids))
        query = f"SELECT * FROM amenities WHERE id IN ({placeholders})"
        cursor.execute(query, amenity_ids)
        selected_amenities = cursor.fetchall()
        amenities_total = sum(amenity['price'] for amenity in selected_amenities)

    # Calculate total price
    total_price = (room_price * nights) + amenities_total

    return render_template("payment_book.html",
                           room_id=room_id,
                           room_type=room_type,
                           check_in=check_in,
                           check_out=check_out,
                           guest=guest,
                           amenities=selected_amenities,
                           total_price=total_price,
                           nights=nights,
                           room_price=room_price,
                           amenities_total=amenities_total)

@moon_routes.route('/payment_confirm', methods=['POST'])
def payment_confirm():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to proceed.", "error")
        return redirect(url_for('auth.login'))

    try:
        # Get form data
        room_id = request.form['room_id']
        check_in = request.form['check_in']
        check_out = request.form['check_out']
        guest = request.form['guest']
        total_price = float(request.form['total_price'])
        amenity_ids_str = request.form.get('amenity_ids', '')

        # Validate required data
        if not all([room_id, check_in, check_out, guest, total_price]):
            flash("Missing booking information.", "error")
            return redirect(url_for('moon_routes.payment_bookroom'))

        # Insert booking
        insert_booking_query = """
            INSERT INTO bookings (user_id, room_id, check_in, check_out, guest, total_price, booking_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        cursor.execute(insert_booking_query, (user_id, room_id, check_in, check_out, guest, total_price, now))
        db.commit()

        # Get booking ID
        booking_id = cursor.lastrowid

        # Insert selected amenities (if any)
        if amenity_ids_str:
            amenity_ids = [aid.strip() for aid in amenity_ids_str.split(",") if aid.strip()]
            insert_amenity_query = "INSERT INTO booking_amenities (booking_id, amenity_id) VALUES (%s, %s)"
            for amenity_id in amenity_ids:
                cursor.execute(insert_amenity_query, (booking_id, amenity_id))
            db.commit()

        # ✅ Update room status to 'booked'
        update_status_query = "UPDATE rooms SET status = 'booked' WHERE id = %s"
        cursor.execute(update_status_query, (room_id,))
        db.commit()

        flash("Booking confirmed! Thank you for your payment.", "success")
        return redirect(url_for('moon_routes.booking_success_page'))

    except Exception as e:
        db.rollback()
        flash(f"An error occurred during booking: {str(e)}", "error")
        return redirect(url_for('moon_routes.payment_bookroom'))


@moon_routes.route('/booking_success_page')
def booking_success_page():
    return render_template('payment_success.html')





@moon_routes.route('/book_room', methods=['GET', 'POST'])
def book_room():
    if 'user_id' not in session:
        return redirect(url_for('moon_routes.login'))

    is_logged_in = True

    # Fetch available rooms and amenities
    cursor.execute("SELECT * FROM rooms WHERE status = 'available'")
    available_rooms = cursor.fetchall()

    cursor.execute("SELECT * FROM amenities")
    amenities = cursor.fetchall()

    return render_template('book_room.html', is_logged_in=is_logged_in, available_rooms=available_rooms, amenities=amenities)



#Payment
@moon_routes.route('/payment', methods=['POST'])
def payment():
    if 'user_id' not in session:
        return redirect(url_for('moon_routes.login'))

    # Get form data
    room_id = request.form.get('room_id')
    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')
    guest_count = int(request.form.get('guest'))  # Ensure it's treated as an integer
    amenity_ids_str = request.form.get('amenity_ids')

    # Input validation
    if not room_id or not check_in_str or not check_out_str or not guest_count or not amenity_ids_str:
        flash("All fields are required.", 'error')
        return redirect(url_for('moon_routes.book_room'))

    try:
        # Parse amenity IDs to list
        amenity_ids = [int(aid) for aid in amenity_ids_str.split(',') if aid]

        # Fetch room info
        cursor.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
        room = cursor.fetchone()
        if not room:
            flash("Room not found.", 'error')
            return redirect(url_for('moon_routes.book_room'))

        room_price_per_night = room['price']
        room_type = room['room_type']  # Fetch room type

        # Define guest limits based on room types
        guest_limits = {
            'Single Room': 1,
            'Double Room': 2,
            'Twin Room': 2,
            'Family Room': 4,
            'Accessible Room': 2,
            'Deluxe Room': 3,
            'Executive Suite': 4
        }

        # Validate guest count based on room type
        if guest_count > guest_limits.get(room_type, 0):
            flash(f"The number of guests exceeds the allowed limit for a {room_type}.", 'error_guest')
            return redirect(url_for('moon_routes.book_room'))

        # Parse check-in and check-out dates
        check_in = datetime.strptime(check_in_str, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_str, "%Y-%m-%d")

        # Date validation: Check if check-in is earlier than check-out
        if check_in >= check_out:
            flash("Check-out date must be after check-in date.", 'error_checkout')
            return redirect(url_for('moon_routes.book_room'))

        # Validate check-in date (must not be in the past)
        today = datetime.today()
        if check_in < today:
            flash("Check-in date cannot be in the past.", 'error_checkin')
            return redirect(url_for('moon_routes.book_room'))

        # Calculate number of nights
        number_of_nights = (check_out - check_in).days
        number_of_nights = max(number_of_nights, 1)  # Minimum of 1 night

        # Fetch selected amenities
        selected_amenities = []
        total_amenity_price = 0
        if amenity_ids:
            format_strings = ','.join(['%s'] * len(amenity_ids))
            cursor.execute(f"SELECT * FROM amenities WHERE id IN ({format_strings})", tuple(amenity_ids))
            selected_amenities = cursor.fetchall()
            total_amenity_price = sum(a['price'] for a in selected_amenities)

        # Calculate total price
        room_total = room_price_per_night * number_of_nights
        total_price = room_total + total_amenity_price

        # Pass data to the template
        return render_template(
            'payment.html',
            room=room,
            check_in=check_in_str,
            check_out=check_out_str,
            guest_count=guest_count,
            number_of_nights=number_of_nights,
            room_total=room_total,
            selected_amenities=selected_amenities,
            total_amenity_price=total_amenity_price,
            total_price=total_price
        )

    except Exception as e:
        flash("An error occurred: " + str(e), 'error')
        return redirect(url_for('moon_routes.book_room'))




#Book action
@moon_routes.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    is_logged_in = 'user_id' in session
    if 'user_id' not in session:
        return redirect(url_for('moon_routes.login'))

    # Get the form data
    user_id = session['user_id']
    room_id = request.form['room_id']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    guest = request.form['guest']
    total_price = float(request.form['total_price'])  # Assuming the total price is passed correctly

    # Validate input (consider adding more robust validation here)
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        number_of_nights = (check_out_date - check_in_date).days
        if number_of_nights <= 0:
            flash("Check-out date must be later than check-in date", "error")
            return redirect(url_for('moon_routes.book_room'))
    except ValueError:
        flash("Invalid date format", "error")
        return redirect(url_for('moon_routes.book_room'))

    # Insert the booking into the bookings table
    try:
        cursor.execute("""
            INSERT INTO bookings (user_id, room_id, check_in, check_out, guest, total_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, room_id, check_in, check_out, guest, total_price))
        booking_id = cursor.lastrowid  # Get the ID of the newly inserted booking

        # Insert amenities into the booking_amenities table
        amenity_ids = request.form.getlist('amenity_ids')  # Get the selected amenity IDs from the form
        for amenity_id in amenity_ids:
            cursor.execute("""
                INSERT INTO booking_amenities (booking_id, amenity_id)
                VALUES (%s, %s)
            """, (booking_id, amenity_id))

        # Commit the transaction
        db.commit()

        # Update the room's status to 'booked'
        cursor.execute("""
            UPDATE rooms SET status = 'booked' WHERE id = %s
        """, (room_id,))
        db.commit()

        # Render the confirmation page or payment success
        flash("Payment successful! Your booking is confirmed.", "success")
        return render_template('payment_success.html', is_logged_in=is_logged_in)
    except Error as e:
        db.rollback()  # Rollback in case of an error
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('moon_routes.book_room'))

#Profile 
@moon_routes.route('/profile') 
def profile():
    is_logged_in = 'user_id' in session
    if not is_logged_in:
        flash('You must be logged in to view your profile.', 'login_required')
        return redirect(url_for('moon_routes.login'))

    user_id = session['user_id']

    # Fetch user information
    cursor.execute("SELECT username, name, email, phone, address, age FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash('User not found.', 'user_not_found')
        return redirect(url_for('moon_routes.login'))

    # Fetch bookings with room number, floor, and amenities
    cursor.execute("""
    SELECT 
        b.id,  -- Include booking ID
        r.room_type, 
        b.check_in, 
        b.check_out, 
        b.guest, 
        b.total_price, 
        b.status, 
        r.room_number, 
        r.floor,
        GROUP_CONCAT(a.amenity ORDER BY a.amenity ASC) AS amenities
    FROM bookings b
    LEFT JOIN rooms r ON b.room_id = r.id
    LEFT JOIN booking_amenities ba ON b.id = ba.booking_id
    LEFT JOIN amenities a ON ba.amenity_id = a.id
    WHERE b.user_id = %s
    GROUP BY b.id, r.room_number, r.floor
""", (user_id,))

    bookings = cursor.fetchall()

    return render_template('profile.html', user=user, bookings=bookings, is_logged_in=is_logged_in)


@moon_routes.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to cancel bookings.', 'warning')
        return jsonify({'success': False, 'message': 'Not logged in'}), 403

    cursor.execute("SELECT id FROM bookings WHERE id = %s AND user_id = %s", (booking_id, user_id))
    booking = cursor.fetchone()
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found or unauthorized.'}), 404

    cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE id = %s", (booking_id,))
    db.commit()
    return jsonify({'success': True, 'message': 'Booking successfully cancelled.'}), 200



#Update action for Profile
@moon_routes.route('/update_profile', methods=['POST'])
def update_profile():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You must be logged in to update your profile.', 'login_required')
        return redirect(url_for('moon_routes.login'))

    user_id = session['user_id']
    username = request.form['username']  
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    age = request.form['age']

    try:
        
        cursor.execute("""
            UPDATE users
            SET username = %s, name = %s, email = %s, phone = %s, address = %s, age = %s
            WHERE id = %s
        """, (username, name, email, phone, address, age, user_id))  
        db.commit()

        flash('Profile updated successfully!', 'success')

        return redirect(url_for('moon_routes.profile'))

    except Error as e:
        print(f"❌ Database error: {e}")
        flash('An error occurred while updating the profile.', 'db_error')
        return redirect(url_for('moon_routes.profile'))

# Feedback route
@moon_routes.route('/feedback', methods=['GET', 'POST'])
def feedback():
    is_logged_in = 'user_id' in session
    if not is_logged_in:
        flash("You must be logged in to submit feedback.", "error")
        return redirect(url_for('moon_routes.login'))
    return render_template('feedback.html', is_logged_in=is_logged_in)

@moon_routes.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return redirect(url_for('moon_routes.login'))

    user_id = session['user_id']
    message = request.form.get('message')
    rating = request.form.get('rating')

    modal_type = None
    modal_message = ""

    if not message or not rating:
        modal_type = "error"
        modal_message = "Please complete all fields."
    else:
        try:
            cursor = db.cursor()
            insert_query = """
                INSERT INTO feedback (user_id, message, rating)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (user_id, message, int(rating)))
            db.commit()
            modal_type = "success"
            modal_message = "Thank you for your feedback!"
        except Error as e:
            print(f"Database Error: {e}")
            modal_type = "error"
            modal_message = "Something went wrong. Please try again later."
        finally:
            cursor.close()

    return render_template(
        'feedback.html',
        is_logged_in=True,
        show_modal=True,
        modal_type=modal_type,
        modal_message=modal_message
    )







#admins route

#Dashboard for Admin
@moon_routes.route('/admin')
def admin():
    
    # Total users
    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()['total_users']

    # Total booked rooms (assuming any booking with status not Cancelled counts)
    cursor.execute("SELECT COUNT(*) AS total_booked FROM bookings WHERE status != 'Cancelled'")
    total_booked = cursor.fetchone()['total_booked']

    # Total available rooms
    cursor.execute("SELECT COUNT(*) AS total_available FROM rooms WHERE status = 'available'")
    total_available = cursor.fetchone()['total_available']

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_booked=total_booked,
        total_available=total_available
    )


#Register for Admin
@moon_routes.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        print("Form Data Received:", name, password, confirm_password)

        
        if not name or not password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template('admin_register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('admin_register.html')

        try:
            
            cursor.execute("""
                SELECT name FROM admins WHERE name = %s 
                UNION 
                SELECT name FROM users WHERE name = %s
            """, (name, name))
            existing = cursor.fetchone()

            if existing:
                flash("Admin name already taken.", "error")
                return render_template('admin_register.html')

            
            password_hash = generate_password_hash(password)
            print("Generated Password Hash:", password_hash)

            cursor.execute(
                "INSERT INTO admins (name, password_hash) VALUES (%s, %s)",
                (name, password_hash)
            )
            db.commit()
            print("Row inserted:", cursor.rowcount)

            flash("Admin registered successfully!", "success")
            return redirect(url_for('moon_routes.login'))  

        except Error as e:
            print("Database Error:", e)
            flash(f"Database error: {e}", "error")

    return render_template('admin_register.html')

#Room Management for Admin
@moon_routes.route('/admin_rooms')
def admin_rooms():
    try:
        cursor.execute("SELECT * FROM rooms ORDER BY floor ASC")  
        rooms = cursor.fetchall()
        rooms_by_floor = {}
        for room in rooms:
            floor = room['floor']
            if floor not in rooms_by_floor:
                rooms_by_floor[floor] = []
            rooms_by_floor[floor].append(room)

        return render_template('admin_rooms.html', rooms_by_floor=rooms_by_floor)
    except Exception as e:
        print("Error fetching rooms:", e)
        return "Error loading rooms."


#Add action for Room
@moon_routes.route('/add_room', methods=['POST'])
def add_room():
    room_type = request.form['room_type']
    floor = request.form['floor']
    price = request.form.get('price', '').strip()
    description = request.form.get('description', '').strip()
    status = 'available'
    image = request.files.get('image')
    image_filename = None

    # Validate price
    if not price.replace('.', '', 1).isdigit() or float(price) <= 0:
        flash('Price must be a positive number', 'price_error')
        return redirect(url_for('moon_routes.admin_rooms'))

    # Handle image upload
    if image and image.filename != '':
        image_filename = secure_filename(image.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, image_filename)
        image.save(image_path)

    # Map floor name to prefix number
    floor_map = {
        '1st Floor': '1',
        '2nd Floor': '2',
        '3rd Floor': '3',
        '4th Floor': '4'
    }
    floor_prefix = floor_map.get(floor)
    if not floor_prefix:
        flash('Invalid floor selected', 'danger')
        return redirect(url_for('moon_routes.admin_rooms'))

    # Fetch existing room numbers for the selected floor
    cursor.execute("SELECT room_number FROM rooms WHERE floor = %s", (floor,))
    existing_numbers = [
        int(row['room_number']) for row in cursor.fetchall() 
        if row['room_number'] and row['room_number'].isdigit()
    ]

    # Find the lowest available room number
    next_suffix = 1
    while True:
        candidate = int(floor_prefix) * 100 + next_suffix
        if candidate not in existing_numbers:
            room_number = str(candidate)
            break
        next_suffix += 1

    # Insert room with generated room_number
    insert_query = '''
        INSERT INTO rooms (room_number, room_type, floor, price, description, image, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    data = (room_number, room_type, floor, price, description, image_filename, status)
    cursor.execute(insert_query, data)
    db.commit()

    flash(f'Room {room_number} added successfully!', 'success')
    return redirect('/admin_rooms')


#Delete action for Room
@moon_routes.route('/delete_room/<int:room_id>', methods=['GET'])
def delete_room(room_id):
    try:
        cursor.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
        db.commit()
        flash('Room deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting room: {e}', 'danger')
    return redirect('/admin_rooms')

# Edit action for Room
@moon_routes.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
def edit_room(room_id):
    cursor.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
    room = cursor.fetchone()

    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('moon_routes.admin_rooms'))

    # Check if the room status is booked
    if room['status'] == 'booked':
        flash('This room is currently booked and cannot be edited.', 'danger')
        return redirect(url_for('moon_routes.admin_rooms'))

    if request.method == 'POST':
        room_type = request.form['room_type']
        price = request.form['price']
        description = request.form['description']
        status = request.form['status']
        image = request.files.get('image')

        if image and image.filename != '':
            # Handle image upload
            image_filename = secure_filename(image.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_filename)
            image.save(image_path)

            cursor.execute(''' 
                UPDATE rooms 
                SET room_type = %s, price = %s, description = %s, status = %s, image = %s 
                WHERE id = %s
            ''', (room_type, price, description, status, image_filename, room_id))
        else:
            cursor.execute(''' 
                UPDATE rooms 
                SET room_type = %s, price = %s, description = %s, status = %s 
                WHERE id = %s
            ''', (room_type, price, description, status, room_id))

        db.commit()
        flash('Room updated successfully!', 'success')
        return redirect(url_for('moon_routes.admin_rooms'))

    return render_template('admin/edit_room.html', room=room)

#Amenities Management for Admin
@moon_routes.route('/admin_amenities')
def admin_amenities():
    try:
        cursor.execute("SELECT * FROM amenities")
        amenities = cursor.fetchall()
        return render_template('admin_amenities.html', amenities=amenities)
    except Error as e:
        flash(f"Error fetching amenities: {e}", "danger")
        return render_template('admin_amenities.html', amenities=[])

#Add action for Amenities
@moon_routes.route('/add_amenities', methods=['POST'])
def add_amenities():
    amenity = request.form['amenity']
    description = request.form['description']
    price = request.form['price']

    try:
        query = "INSERT INTO amenities (amenity, description, price) VALUES (%s, %s, %s)"
        values = (amenity, description, price)
        cursor.execute(query, values)
        db.commit()
    except Error as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for('moon_routes.admin_amenities'))  

#Edit action for Amenities
@moon_routes.route('/edit_amenity', methods=['POST'])
def edit_amenity():
    amenity_id = request.form['amenity_id']
    amenity = request.form['amenity']
    description = request.form['description']
    price = request.form['price']

    try:
        query = "UPDATE amenities SET amenity = %s, description = %s, price = %s WHERE id = %s"
        values = (amenity, description, price, amenity_id)
        cursor.execute(query, values)
        db.commit()
    except Error as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for('moon_routes.admin_amenities'))

#Delete action for Amenities
@moon_routes.route('/delete_amenity/<int:amenity_id>', methods=['GET'])
def delete_amenity(amenity_id):
    try:
        query = "DELETE FROM amenities WHERE id = %s"
        cursor.execute(query, (amenity_id,))
        db.commit()
    except Error as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for('moon_routes.admin_amenities'))

#Booking Management for admin
@moon_routes.route('/admin_booking', methods=['GET', 'POST']) 
def admin_booking():
    # Get page number from query params, default 1
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    # Count total bookings to calculate total pages
    count_query = 'SELECT COUNT(*) as total FROM bookings'
    cursor.execute(count_query)
    total = cursor.fetchone()['total']
    total_pages = (total + per_page - 1) // per_page  # ceil division

    # Main query with LIMIT and OFFSET for pagination
    query = f'''
        SELECT b.id, u.username AS username, r.room_type, r.room_number, 
               b.check_in, b.check_out, b.guest, b.total_price, b.booking_date, 
               b.status, GROUP_CONCAT(a.amenity ORDER BY a.amenity) AS amenities,
               r.id as room_id, u.id as user_id
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        LEFT JOIN booking_amenities ba ON b.id = ba.booking_id
        LEFT JOIN amenities a ON ba.amenity_id = a.id
        JOIN users u ON b.user_id = u.id
        GROUP BY b.id
        ORDER BY b.booking_date DESC
        LIMIT %s OFFSET %s
    '''
    cursor.execute(query, (per_page, offset))
    bookings = cursor.fetchall()

    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        action = request.form.get('action')

        if action in ['accept', 'reject', 'cancel']:
            # Fetch current status
            cursor.execute('SELECT status, room_id FROM bookings WHERE id = %s', (booking_id,))
            booking = cursor.fetchone()

            if not booking:
                flash('Booking not found.', 'danger')
                return redirect(url_for('moon_routes.admin_booking'))

            current_status = booking['status']
            room_id = booking['room_id']

            # Determine new status based on action
            if action == 'accept':
                if current_status in ['Cancelled', 'Rejected', 'Booked']:
                    flash('Cannot accept this booking. It is already processed.', 'warning')
                    return redirect(url_for('moon_routes.admin_booking'))
                status = 'Booked'
            elif action == 'reject':
                if current_status in ['Cancelled', 'Rejected']:
                    flash('Booking already cancelled or rejected.', 'warning')
                    return redirect(url_for('moon_routes.admin_booking'))
                status = 'Rejected'
            elif action == 'cancel':
                if current_status == 'Cancelled':
                    flash('Booking already cancelled.', 'warning')
                    return redirect(url_for('moon_routes.admin_booking'))
                status = 'Cancelled'

            # Update booking status
            cursor.execute('UPDATE bookings SET status = %s WHERE id = %s', (status, booking_id))

            # Update room status accordingly
            if status in ['Cancelled', 'Rejected']:
                cursor.execute('UPDATE rooms SET status = %s WHERE id = %s', ('available', room_id))
            elif status == 'Booked':
                cursor.execute('UPDATE rooms SET status = %s WHERE id = %s', ('booked', room_id))

            db.commit()
            flash(f'Booking {status} successfully!', 'success')
            return redirect(url_for('moon_routes.admin_booking'))



    cursor.execute("SELECT * FROM rooms WHERE status = 'available'")
    available_rooms = cursor.fetchall()

    cursor.execute("SELECT * FROM amenities")
    amenities = cursor.fetchall()

    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()

    return render_template('admin_booking.html', bookings=bookings, available_rooms=available_rooms, amenities=amenities, users=users, page=page, total_pages=total_pages)

@moon_routes.route('/add_booking', methods=['POST'])
def add_booking():
    user_id = request.form.get('user_id')  # Ensure user is logged in
    room_id = request.form.get('room_id')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guest = request.form.get('guest')
    total_price = request.form.get('totalPrice')
    amenities_str = request.form.get('amenity_ids')  # comma-separated

    if not user_id:
        flash("Please select a user for the booking.")
        return redirect(url_for('moon_routes.admin_booking'))

    if not all([room_id, check_in, check_out, guest, total_price]):
        flash("Please fill all required fields.")
        return redirect(url_for('moon_routes.admin_booking'))

    amenity_ids = []
    if amenities_str:
        amenity_ids = amenities_str.split(',')

    try:
        cursor = db.cursor()
        # Insert booking
        insert_booking_sql = """
            INSERT INTO bookings (user_id, room_id, check_in, check_out, guest, total_price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_booking_sql, (user_id, room_id, check_in, check_out, guest, total_price))
        booking_id = cursor.lastrowid

        # Insert booking amenities
        if amenity_ids:
            insert_amenities_sql = "INSERT INTO booking_amenities (booking_id, amenity_id) VALUES (%s, %s)"
            amenity_data = [(booking_id, int(aid)) for aid in amenity_ids]
            cursor.executemany(insert_amenities_sql, amenity_data)

        # Update room status to 'booked'
        update_room_status_sql = "UPDATE rooms SET status = 'booked' WHERE id = %s"
        cursor.execute(update_room_status_sql, (room_id,))

        db.commit()
        flash("Booking added successfully!")
    except mysql.connector.Error as err:
        db.rollback()
        flash(f"Database error: {err}")
    except Exception as e:
        db.rollback()
        flash(f"Unexpected error: {e}")
    finally:
        cursor.close()

    return redirect(url_for('moon_routes.admin_booking'))

@moon_routes.route('/admin_edit_booking', methods=['POST'])
def admin_edit_booking():
    booking_id = request.form.get('booking_id')
    user_id = request.form.get('user_id')
    room_id = request.form.get('room_id')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guest = request.form.get('guest')
    edit_amenity_ids = request.form.get('edit_amenity_ids')  # Comma-separated string

    try:
        # Get a cursor from the database connection
        cursor = db.cursor()

        # 1. Update the booking details
        update_query = '''
            UPDATE bookings 
            SET user_id = %s, room_id = %s, check_in = %s, check_out = %s, guest = %s
            WHERE id = %s
        '''
        cursor.execute(update_query, (user_id, room_id, check_in, check_out, guest, booking_id))

        # 2. Delete old amenities for this booking
        delete_amenities_query = "DELETE FROM booking_amenities WHERE booking_id = %s"
        cursor.execute(delete_amenities_query, (booking_id,))

        # 3. Insert new amenities if any
        if edit_amenity_ids:
            amenity_id_list = [int(aid) for aid in edit_amenity_ids.split(",") if aid.strip().isdigit()]
            insert_amenity_query = "INSERT INTO booking_amenities (booking_id, amenity_id) VALUES (%s, %s)"
            for aid in amenity_id_list:
                cursor.execute(insert_amenity_query, (booking_id, aid))

        # Commit all changes once after the operations
        db.commit()

        flash('Booking updated successfully!', 'success')

    except Exception as e:
        db.rollback()
        flash(f'Error updating booking: {e}', 'danger')

    finally:
        cursor.close()

    return redirect(url_for('moon_routes.admin_booking'))


#User Management for admin
@moon_routes.route('/admin_users')
def admin_users():
    try:
        # Get current page from query parameters (default to 1)
        page = request.args.get('page', default=1, type=int)
        per_page = 5  # Adjust how many users you want per page
        offset = (page - 1) * per_page

        # Get total number of users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        total_pages = (total_users + per_page - 1) // per_page

        # Get users for the current page
        cursor.execute("SELECT * FROM users LIMIT %s OFFSET %s", (per_page, offset))
        users = cursor.fetchall()

        return render_template('admin_users.html', users=users, page=page, total_pages=total_pages)
    except Error as e:
        flash(f"Error fetching users: {e}", "danger")
        return render_template('admin_users.html', users=[], page=1, total_pages=1)

    
#Add action for User Admin side
@moon_routes.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']
    address = request.form['address']
    age = request.form['age']

    # Validate inputs
    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'password_length_error')
        return redirect(url_for('moon_routes.admin_users'))

    if not age.isdigit() or int(age) <= 0:
        flash('Age must be a positive number.', 'age_error')
        return redirect(url_for('moon_routes.admin_users'))

    # Check admin table first
    cursor.execute("SELECT * FROM admins WHERE name = %s", (username,))
    if cursor.fetchone():
        flash('Username already exists in admin.', 'username_error')
        return redirect(url_for('moon_routes.admin_users'))

    # Then check users table
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        flash('Username already exists in users.', 'username_error')
        return redirect(url_for('moon_routes.admin_users'))

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        flash('Email already exists in users.', 'email_error')
        return redirect(url_for('moon_routes.admin_users'))

    # Insert user if all checks pass
    try:
        password_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (username, name, email, phone, address, age, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, name, email, phone, address, int(age), password_hash))
        db.commit()
        flash("User added successfully!", "success")
    except Error as e:
        print(f"❌ Error inserting user: {e}")
        flash("Database error while adding user.", "danger")

    return redirect(url_for('moon_routes.admin_users'))

@moon_routes.route('/update_user', methods=['POST'])
def update_user():
    user_id = request.form['id']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    age = request.form['age']

    try:
        cursor.execute("""
            UPDATE users
            SET name = %s,
                email = %s,
                phone = %s,
                address = %s,
                age = %s
            WHERE id = %s
        """, (name, email, phone, address, age, user_id))
        db.commit()
        flash('User updated successfully!', 'success')
    except Error as e:
        flash(f'Error updating user: {e}', 'danger')

    return redirect(url_for('moon_routes.admin_users'))

@moon_routes.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        flash('User deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting user: {e}', 'danger')

    return redirect(url_for('moon_routes.admin_users'))


# View feedback (admin)
@moon_routes.route('/admin_feedback')
def admin_feedback():
    try:
        cursor.execute("""
            SELECT feedback.id, users.username, feedback.message, feedback.submitted_at, feedback.status, feedback.rating
            FROM feedback
            JOIN users ON feedback.user_id = users.id
            ORDER BY feedback.submitted_at DESC
        """)
        feedback_list = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        flash("Failed to retrieve feedback.", "error")
        feedback_list = []

    return render_template('admin_feedback.html', feedback_list=feedback_list)




# Accept feedback
@moon_routes.route('/accept_feedback/<int:feedback_id>')
def accept_feedback(feedback_id):
    try:
        cursor.execute("UPDATE feedback SET status = 'accepted' WHERE id = %s", (feedback_id,))
        db.commit()  # ✅ FIXED: use db.commit(), not cursor.connection.commit()
        flash("Feedback accepted.", "success")
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        flash("Failed to accept feedback.", "error")
    return redirect(url_for('moon_routes.admin_feedback'))


# Reject feedback
@moon_routes.route('/reject_feedback/<int:feedback_id>')
def reject_feedback(feedback_id):
    try:
        cursor.execute("UPDATE feedback SET status = 'rejected' WHERE id = %s", (feedback_id,))
        db.commit()  # ✅ FIXED: use db.commit(), not cursor.connection.commit()
        flash("Feedback rejected.", "success")
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        flash("Failed to reject feedback.", "error")
    return redirect(url_for('moon_routes.admin_feedback'))
