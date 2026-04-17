from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gyanpustak_secret_2025')

# ─────────────────────────────────────────────
# DB Connection
# ─────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database='gyanpustak'
    )

def query(sql, args=(), one=False, commit=False):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, args)
    if commit:
        conn.commit()
        conn.close()
        return cur.lastrowid
    rv = cur.fetchone() if one else cur.fetchall()
    conn.close()
    return rv

# ─────────────────────────────────────────────
# Auth decorators
# ─────────────────────────────────────────────
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('landing'))
            if role and session.get('role') != role:
                flash('Unauthorized access.', 'danger')
                return redirect(url_for('landing'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ─────────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────────
@app.route('/')
def landing():
    return render_template('landing.html')

# ─────────────────────────────────────────────
# STUDENT LOGIN / REGISTER
# ─────────────────────────────────────────────
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        sid = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        if not sid or not name:
            flash('Please fill in all fields.', 'danger')
            return render_template('student_login.html')
        row = query(
            "SELECT * FROM student WHERE student_id=%s AND CONCAT(fname,' ',lname)=%s",
            (sid, name), one=True
        )
        if row:
            session['user_id'] = row['student_id']
            session['role'] = 'student'
            session['name'] = f"{row['fname']} {row['lname']}"
            # ensure cart exists
            cart = query("SELECT cart_id FROM cart WHERE student_id=%s", (row['student_id'],), one=True)
            if not cart:
                query("INSERT INTO cart (student_id) VALUES (%s)", (row['student_id'],), commit=True)
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid Student ID or Name.', 'danger')
    return render_template('student_login.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    universities = query("SELECT * FROM university")
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        dob = request.form.get('dob', None) or None
        major = request.form.get('major', '')
        status = request.form.get('status', 'Undergraduate')
        year_of_study = request.form.get('year_of_study', 1)
        university_id = request.form.get('university_id') or None
        password = request.form['password']
        try:
            sid = query(
                "INSERT INTO student (fname,lname,email,address,phone,dob,major,status,year_of_study,university_id,password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (fname,lname,email,address,phone,dob,major,status,year_of_study,university_id,password), commit=True
            )
            query("INSERT INTO cart (student_id) VALUES (%s)", (sid,), commit=True)
            flash(f'Registration successful! Your Student ID is {sid}. Use your full name to login.', 'success')
            return redirect(url_for('student_login'))
        except mysql.connector.IntegrityError:
            flash('Email already registered.', 'danger')
    return render_template('student_register.html', universities=universities)

# ─────────────────────────────────────────────
# EMPLOYEE LOGIN (CS / Admin / Super Admin)
# ─────────────────────────────────────────────
@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    role_hint = request.args.get('role', '')
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('employee_login.html', role_hint=role_hint)
        emp = query("SELECT * FROM employee WHERE email=%s AND password=%s", (email, password), one=True)
        if not emp:
            flash('Invalid credentials.', 'danger')
            return render_template('employee_login.html', role_hint=role_hint)
        # Determine role
        admin_row = query("SELECT * FROM administrator WHERE employee_id=%s", (emp['employee_id'],), one=True)
        cs_row = query("SELECT * FROM customer_support WHERE employee_id=%s", (emp['employee_id'],), one=True)
        if admin_row:
            session['user_id'] = emp['employee_id']
            session['admin_id'] = admin_row['admin_id']
            session['name'] = f"{emp['fname']} {emp['lname']}"
            if admin_row['is_super_admin']:
                session['role'] = 'super_admin'
                return redirect(url_for('super_admin_dashboard'))
            else:
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
        elif cs_row:
            session['user_id'] = emp['employee_id']
            session['cs_id'] = cs_row['cs_id']
            session['name'] = f"{emp['fname']} {emp['lname']}"
            session['role'] = 'cs'
            return redirect(url_for('cs_dashboard'))
        else:
            flash('Employee role not found.', 'danger')
    return render_template('employee_login.html', role_hint=role_hint)

# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

# ═════════════════════════════════════════════
# STUDENT ROUTES
# ═════════════════════════════════════════════
@app.route('/student/dashboard')
@login_required('student')
def student_dashboard():
    search = request.args.get('q', '')
    category_id = request.args.get('category', '')
    categories = query("SELECT * FROM category")
    if search and category_id:
        books = query("""
            SELECT b.*, c.name as cat_name,
                   GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors
            FROM book b
            LEFT JOIN category c ON b.category_id=c.category_id
            LEFT JOIN book_author ba ON b.book_id=ba.book_id
            LEFT JOIN author a ON ba.author_id=a.author_id
            WHERE b.title LIKE %s AND b.category_id=%s
            GROUP BY b.book_id
        """, (f'%{search}%', category_id))
    elif search:
        books = query("""
            SELECT b.*, c.name as cat_name,
                   GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors
            FROM book b
            LEFT JOIN category c ON b.category_id=c.category_id
            LEFT JOIN book_author ba ON b.book_id=ba.book_id
            LEFT JOIN author a ON ba.author_id=a.author_id
            WHERE b.title LIKE %s OR a.name LIKE %s
            GROUP BY b.book_id
        """, (f'%{search}%', f'%{search}%'))
    elif category_id:
        books = query("""
            SELECT b.*, c.name as cat_name,
                   GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors
            FROM book b
            LEFT JOIN category c ON b.category_id=c.category_id
            LEFT JOIN book_author ba ON b.book_id=ba.book_id
            LEFT JOIN author a ON ba.author_id=a.author_id
            WHERE b.category_id=%s
            GROUP BY b.book_id
        """, (category_id,))
    else:
        books = query("""
            SELECT b.*, c.name as cat_name,
                   GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors
            FROM book b
            LEFT JOIN category c ON b.category_id=c.category_id
            LEFT JOIN book_author ba ON b.book_id=ba.book_id
            LEFT JOIN author a ON ba.author_id=a.author_id
            GROUP BY b.book_id
        """)
    return render_template('student_dashboard.html', books=books, categories=categories, search=search, selected_cat=category_id)

@app.route('/student/book/<int:book_id>')
@login_required('student')
def book_detail(book_id):
    book = query("""
        SELECT b.*, c.name as cat_name, p.name as pub_name,
               GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') as authors
        FROM book b
        LEFT JOIN category c ON b.category_id=c.category_id
        LEFT JOIN publisher p ON b.publisher_id=p.publisher_id
        LEFT JOIN book_author ba ON b.book_id=ba.book_id
        LEFT JOIN author a ON ba.author_id=a.author_id
        WHERE b.book_id=%s GROUP BY b.book_id
    """, (book_id,), one=True)
    reviews = query("""
        SELECT r.*, CONCAT(s.fname,' ',s.lname) as student_name
        FROM review r JOIN student s ON r.student_id=s.student_id
        WHERE r.book_id=%s ORDER BY r.date_written DESC
    """, (book_id,))
    return render_template('book_detail.html', book=book, reviews=reviews)

@app.route('/student/cart')
@login_required('student')
def student_cart():
    cart = query("SELECT * FROM cart WHERE student_id=%s", (session['user_id'],), one=True)
    items = []
    total = 0
    if cart:
        items = query("""
            SELECT ci.*, b.title, b.price, b.format, b.type
            FROM cart_item ci JOIN book b ON ci.book_id=b.book_id
            WHERE ci.cart_id=%s
        """, (cart['cart_id'],))
        total = sum(i['price'] * i['quantity'] for i in items)
    return render_template('student_cart.html', items=items, total=total, cart=cart)

@app.route('/student/cart/add', methods=['POST'])
@login_required('student')
def cart_add():
    book_id = request.form['book_id']
    qty = int(request.form.get('quantity', 1))
    txn = request.form.get('transaction_type', 'Buy')
    cart = query("SELECT cart_id FROM cart WHERE student_id=%s", (session['user_id'],), one=True)
    if not cart:
        cid = query("INSERT INTO cart (student_id) VALUES (%s)", (session['user_id'],), commit=True)
    else:
        cid = cart['cart_id']
    existing = query("SELECT * FROM cart_item WHERE cart_id=%s AND book_id=%s AND transaction_type=%s", (cid, book_id, txn), one=True)
    if existing:
        query("UPDATE cart_item SET quantity=quantity+%s WHERE item_id=%s", (qty, existing['item_id']), commit=True)
    else:
        query("INSERT INTO cart_item (cart_id, book_id, quantity, transaction_type) VALUES (%s,%s,%s,%s)", (cid, book_id, qty, txn), commit=True)
    query("UPDATE cart SET date_updated=CURDATE() WHERE cart_id=%s", (cid,), commit=True)
    flash('Book added to cart!', 'success')
    return redirect(url_for('student_cart'))

@app.route('/student/cart/remove/<int:item_id>', methods=['POST'])
@login_required('student')
def cart_remove(item_id):
    query("DELETE FROM cart_item WHERE item_id=%s", (item_id,), commit=True)
    flash('Item removed from cart.', 'info')
    return redirect(url_for('student_cart'))

@app.route('/student/checkout', methods=['GET', 'POST'])
@login_required('student')
def checkout():
    cart = query("SELECT * FROM cart WHERE student_id=%s", (session['user_id'],), one=True)
    items = []
    total = 0
    if cart:
        items = query("""
            SELECT ci.*, b.title, b.price, b.format
            FROM cart_item ci JOIN book b ON ci.book_id=b.book_id
            WHERE ci.cart_id=%s
        """, (cart['cart_id'],))
        total = sum(i['price'] * i['quantity'] for i in items)
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('student_cart'))
    if request.method == 'POST':
        shipping = request.form['shipping_type']
        cc_num = request.form['cc_number']
        cc_exp = request.form['cc_expiry']
        cc_holder = request.form['cc_holder']
        cc_type = request.form['cc_type']
        oid = query(
            "INSERT INTO `order` (student_id, shipping_type, cc_number, cc_expiry, cc_holder, cc_type, status) VALUES (%s,%s,%s,%s,%s,%s,'New')",
            (session['user_id'], shipping, cc_num, cc_exp, cc_holder, cc_type), commit=True
        )
        for item in items:
            query(
                "INSERT INTO order_item (order_id, book_id, quantity, price, transaction_type) VALUES (%s,%s,%s,%s,%s)",
                (oid, item['book_id'], item['quantity'], item['price'], item['transaction_type']), commit=True
            )
            query("UPDATE book SET quantity=quantity-%s WHERE book_id=%s", (item['quantity'], item['book_id']), commit=True)
        query("DELETE FROM cart_item WHERE cart_id=%s", (cart['cart_id'],), commit=True)
        flash(f'Order #{oid} placed successfully!', 'success')
        return redirect(url_for('student_orders'))
    return render_template('checkout.html', items=items, total=total)

@app.route('/student/orders')
@login_required('student')
def student_orders():
    orders = query("""
        SELECT o.*, GROUP_CONCAT(b.title SEPARATOR '; ') as titles
        FROM `order` o
        LEFT JOIN order_item oi ON o.order_id=oi.order_id
        LEFT JOIN book b ON oi.book_id=b.book_id
        WHERE o.student_id=%s
        GROUP BY o.order_id ORDER BY o.date_created DESC
    """, (session['user_id'],))
    return render_template('student_orders.html', orders=orders)

@app.route('/student/orders/<int:order_id>')
@login_required('student')
def order_detail(order_id):
    order = query("SELECT * FROM `order` WHERE order_id=%s AND student_id=%s", (order_id, session['user_id']), one=True)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('student_orders'))
    items = query("""
        SELECT oi.*, b.title, b.format FROM order_item oi
        JOIN book b ON oi.book_id=b.book_id WHERE oi.order_id=%s
    """, (order_id,))
    return render_template('order_detail.html', order=order, items=items)

@app.route('/student/reviews', methods=['GET', 'POST'])
@login_required('student')
def student_reviews():
    purchased_books = query("""
        SELECT DISTINCT b.book_id, b.title FROM order_item oi
        JOIN `order` o ON oi.order_id=o.order_id
        JOIN book b ON oi.book_id=b.book_id
        WHERE o.student_id=%s
    """, (session['user_id'],))
    my_reviews = query("""
        SELECT r.*, b.title FROM review r JOIN book b ON r.book_id=b.book_id
        WHERE r.student_id=%s ORDER BY r.date_written DESC
    """, (session['user_id'],))
    if request.method == 'POST':
        book_id = request.form['book_id']
        rating = request.form['rating']
        review_text = request.form['review_text']
        existing = query("SELECT review_id FROM review WHERE student_id=%s AND book_id=%s", (session['user_id'], book_id), one=True)
        if existing:
            query("UPDATE review SET rating=%s, review_text=%s, date_written=CURDATE() WHERE review_id=%s",
                  (rating, review_text, existing['review_id']), commit=True)
        else:
            query("INSERT INTO review (student_id, book_id, rating, review_text) VALUES (%s,%s,%s,%s)",
                  (session['user_id'], book_id, rating, review_text), commit=True)
        # update avg rating
        query("""UPDATE book SET avg_rating=(SELECT AVG(rating) FROM review WHERE book_id=%s) WHERE book_id=%s""",
              (book_id, book_id), commit=True)
        flash('Review submitted!', 'success')
        return redirect(url_for('student_reviews'))
    return render_template('student_reviews.html', books=purchased_books, reviews=my_reviews)

@app.route('/student/tickets', methods=['GET', 'POST'])
@login_required('student')
def student_tickets():
    if request.method == 'POST':
        title = request.form['title']
        problem = request.form['problem_desc']
        category = request.form['category']
        query("INSERT INTO trouble_ticket (title, problem_desc, category, created_by_student, status) VALUES (%s,%s,%s,%s,'New')",
              (title, problem, category, session['user_id']), commit=True)
        flash('Support ticket submitted!', 'success')
        return redirect(url_for('student_tickets'))
    tickets = query("""
        SELECT * FROM trouble_ticket WHERE created_by_student=%s ORDER BY date_logged DESC
    """, (session['user_id'],))
    return render_template('student_tickets.html', tickets=tickets)

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required('student')
def student_profile():
    student = query("SELECT s.*, u.name as uni_name FROM student s LEFT JOIN university u ON s.university_id=u.university_id WHERE s.student_id=%s", (session['user_id'],), one=True)
    universities = query("SELECT * FROM university")
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        address = request.form['address']
        major = request.form['major']
        query("UPDATE student SET fname=%s, lname=%s, phone=%s, address=%s, major=%s WHERE student_id=%s",
              (fname, lname, phone, address, major, session['user_id']), commit=True)
        session['name'] = f"{fname} {lname}"
        flash('Profile updated!', 'success')
        return redirect(url_for('student_profile'))
    return render_template('student_profile.html', student=student, universities=universities)

# ═════════════════════════════════════════════
# CUSTOMER SUPPORT ROUTES
# ═════════════════════════════════════════════
@app.route('/cs/dashboard')
@login_required('cs')
def cs_dashboard():
    tickets = query("""
        SELECT t.*,
               CONCAT(s.fname,' ',s.lname) as student_name,
               e2.fname as cs_fname, e2.lname as cs_lname
        FROM trouble_ticket t
        LEFT JOIN student s ON t.created_by_student=s.student_id
        LEFT JOIN customer_support cs ON t.created_by_cs=cs.cs_id
        LEFT JOIN employee e2 ON cs.employee_id=e2.employee_id
        ORDER BY t.date_logged DESC
    """)
    return render_template('cs_dashboard.html', tickets=tickets)

@app.route('/cs/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required('cs')
def cs_ticket_detail(ticket_id):
    ticket = query("SELECT * FROM trouble_ticket WHERE ticket_id=%s", (ticket_id,), one=True)
    admins = query("""
        SELECT a.admin_id, CONCAT(e.fname,' ',e.lname) as name
        FROM administrator a JOIN employee e ON a.employee_id=e.employee_id
        WHERE a.is_super_admin=0
    """)
    history = query("""
        SELECT h.*, e.fname, e.lname FROM ticket_status_history h
        LEFT JOIN employee e ON h.changed_by_employee=e.employee_id
        WHERE h.ticket_id=%s ORDER BY h.changed_at
    """, (ticket_id,))
    if request.method == 'POST':
        action = request.form.get('action')
        if ticket['status'] != 'New':
            flash('You can only modify tickets with status New.', 'warning')
            return redirect(url_for('cs_ticket_detail', ticket_id=ticket_id))
        if action == 'assign':
            admin_id = request.form['admin_id']
            old_status = ticket['status']
            query("UPDATE trouble_ticket SET status='Assigned', assigned_to_admin=%s WHERE ticket_id=%s",
                  (admin_id, ticket_id), commit=True)
            query("INSERT INTO ticket_status_history (ticket_id, old_status, new_status, changed_by_employee) VALUES (%s,%s,'Assigned',%s)",
                  (ticket_id, old_status, session['user_id']), commit=True)
            flash('Ticket assigned to administrator.', 'success')
        elif action == 'create_order_cancel':
            order_id = request.form.get('order_id')
            if order_id:
                query("UPDATE `order` SET status='Canceled', cancelled_by_cs=%s WHERE order_id=%s",
                      (session.get('cs_id'), order_id), commit=True)
                flash(f'Order #{order_id} cancelled.', 'success')
        return redirect(url_for('cs_ticket_detail', ticket_id=ticket_id))
    return render_template('cs_ticket_detail.html', ticket=ticket, admins=admins, history=history)

@app.route('/cs/ticket/new', methods=['GET', 'POST'])
@login_required('cs')
def cs_create_ticket():
    if request.method == 'POST':
        title = request.form['title']
        problem = request.form['problem_desc']
        category = request.form['category']
        query("INSERT INTO trouble_ticket (title, problem_desc, category, created_by_cs, status) VALUES (%s,%s,%s,%s,'New')",
              (title, problem, category, session.get('cs_id')), commit=True)
        flash('Ticket created.', 'success')
        return redirect(url_for('cs_dashboard'))
    return render_template('cs_create_ticket.html')

@app.route('/cs/orders')
@login_required('cs')
def cs_orders():
    orders = query("""
        SELECT o.*, CONCAT(s.fname,' ',s.lname) as student_name
        FROM `order` o JOIN student s ON o.student_id=s.student_id
        ORDER BY o.date_created DESC
    """)
    return render_template('cs_orders.html', orders=orders)

@app.route('/cs/orders/cancel/<int:order_id>', methods=['POST'])
@login_required('cs')
def cs_cancel_order(order_id):
    order = query("SELECT * FROM `order` WHERE order_id=%s", (order_id,), one=True)
    if order and order['status'] not in ('Shipped', 'Canceled'):
        query("UPDATE `order` SET status='Canceled', cancelled_by_cs=%s WHERE order_id=%s",
              (session.get('cs_id'), order_id), commit=True)
        flash(f'Order #{order_id} cancelled.', 'success')
    else:
        flash('Cannot cancel this order.', 'warning')
    return redirect(url_for('cs_orders'))

# ═════════════════════════════════════════════
# ADMIN ROUTES
# ═════════════════════════════════════════════
@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    tickets = query("""
        SELECT t.*, CONCAT(s.fname,' ',s.lname) as student_name
        FROM trouble_ticket t
        LEFT JOIN student s ON t.created_by_student=s.student_id
        WHERE t.status IN ('Assigned','In-Process','Completed')
        ORDER BY t.date_logged DESC
    """)
    books = query("""
        SELECT b.*, c.name as cat_name FROM book b
        LEFT JOIN category c ON b.category_id=c.category_id
        ORDER BY b.book_id
    """)
    return render_template('admin_dashboard.html', tickets=tickets, books=books)

@app.route('/admin/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_ticket_detail(ticket_id):
    ticket = query("SELECT * FROM trouble_ticket WHERE ticket_id=%s", (ticket_id,), one=True)
    history = query("""
        SELECT h.*, e.fname, e.lname FROM ticket_status_history h
        LEFT JOIN employee e ON h.changed_by_employee=e.employee_id
        WHERE h.ticket_id=%s ORDER BY h.changed_at
    """, (ticket_id,))
    if request.method == 'POST':
        if ticket['status'] == 'New':
            flash('Admins cannot edit tickets with status New.', 'warning')
            return redirect(url_for('admin_ticket_detail', ticket_id=ticket_id))
        new_status = request.form.get('status')
        solution = request.form.get('solution_desc', '')
        old_status = ticket['status']
        resolved_by = session.get('admin_id') if new_status == 'Completed' else ticket['resolved_by_admin']
        completion_date = 'CURDATE()' if new_status == 'Completed' else 'NULL'
        query("""UPDATE trouble_ticket SET status=%s, solution_desc=%s, resolved_by_admin=%s
                 WHERE ticket_id=%s""",
              (new_status, solution, resolved_by, ticket_id), commit=True)
        if new_status == 'Completed':
            query("UPDATE trouble_ticket SET completion_date=CURDATE() WHERE ticket_id=%s", (ticket_id,), commit=True)
        query("INSERT INTO ticket_status_history (ticket_id, old_status, new_status, changed_by_employee) VALUES (%s,%s,%s,%s)",
              (ticket_id, old_status, new_status, session['user_id']), commit=True)
        flash('Ticket updated.', 'success')
        return redirect(url_for('admin_ticket_detail', ticket_id=ticket_id))
    return render_template('admin_ticket_detail.html', ticket=ticket, history=history)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_book():
    publishers = query("SELECT * FROM publisher")
    categories = query("SELECT * FROM category")
    authors_all = query("SELECT * FROM author")
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        btype = request.form['type']
        purchase_option = request.form['purchase_option']
        price = request.form['price']
        quantity = request.form['quantity']
        language = request.form['language']
        bformat = request.form['format']
        edition = request.form['edition']
        pub_date = request.form['publication_date'] or None
        publisher_id = request.form['publisher_id'] or None
        category_id = request.form['category_id'] or None
        bid = query("""INSERT INTO book (title,isbn,type,purchase_option,price,quantity,language,format,edition,publication_date,publisher_id,category_id,last_updated_by)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (title,isbn,btype,purchase_option,price,quantity,language,bformat,edition,pub_date,publisher_id,category_id,session.get('admin_id')), commit=True)
        author_ids = request.form.getlist('author_ids')
        for aid in author_ids:
            query("INSERT IGNORE INTO book_author (book_id, author_id) VALUES (%s,%s)", (bid, aid), commit=True)
        flash('Book added!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_add_book.html', publishers=publishers, categories=categories, authors=authors_all)

@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_book(book_id):
    book = query("SELECT * FROM book WHERE book_id=%s", (book_id,), one=True)
    publishers = query("SELECT * FROM publisher")
    categories = query("SELECT * FROM category")
    if request.method == 'POST':
        price = request.form['price']
        quantity = request.form['quantity']
        btype = request.form['type']
        query("UPDATE book SET price=%s, quantity=%s, type=%s, last_updated_by=%s WHERE book_id=%s",
              (price, quantity, btype, session.get('admin_id'), book_id), commit=True)
        flash('Book updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit_book.html', book=book, publishers=publishers, categories=categories)

@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@login_required('admin')
def admin_delete_book(book_id):
    query("DELETE FROM book_author WHERE book_id=%s", (book_id,), commit=True)
    query("DELETE FROM book_keyword WHERE book_id=%s", (book_id,), commit=True)
    query("DELETE FROM book_subcategory WHERE book_id=%s", (book_id,), commit=True)
    query("DELETE FROM book WHERE book_id=%s", (book_id,), commit=True)
    flash('Book deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/course-books', methods=['GET', 'POST'])
@login_required('admin')
def admin_course_books():
    courses = query("SELECT c.*, u.name as uni_name FROM course c JOIN university u ON c.university_id=u.university_id")
    books = query("SELECT book_id, title FROM book")
    instructors = query("SELECT i.*, CONCAT(i.fname,' ',i.lname) as fullname FROM instructor i")
    course_books = query("""
        SELECT cb.*, c.name as course_name, b.title as book_title,
               CONCAT(i.fname,' ',i.lname) as instructor_name
        FROM course_book cb
        JOIN course c ON cb.course_id=c.course_id
        JOIN book b ON cb.book_id=b.book_id
        LEFT JOIN instructor i ON cb.instructor_id=i.instructor_id
    """)
    if request.method == 'POST':
        course_id = request.form['course_id']
        book_id = request.form['book_id']
        instructor_id = request.form.get('instructor_id') or None
        req_type = request.form['requirement_type']
        query("INSERT INTO course_book (course_id, book_id, instructor_id, requirement_type, added_by_admin) VALUES (%s,%s,%s,%s,%s)",
              (course_id, book_id, instructor_id, req_type, session.get('admin_id')), commit=True)
        flash('Course-book link added!', 'success')
        return redirect(url_for('admin_course_books'))
    return render_template('admin_course_books.html', courses=courses, books=books, instructors=instructors, course_books=course_books)

# ═════════════════════════════════════════════
# SUPER ADMIN ROUTES
# ═════════════════════════════════════════════
@app.route('/superadmin/dashboard')
@login_required('super_admin')
def super_admin_dashboard():
    admins = query("""
        SELECT e.*, a.admin_id, a.is_super_admin FROM administrator a
        JOIN employee e ON a.employee_id=e.employee_id WHERE a.is_super_admin=0
    """)
    cs_list = query("""
        SELECT e.*, c.cs_id FROM customer_support c
        JOIN employee e ON c.employee_id=e.employee_id
    """)
    return render_template('superadmin_dashboard.html', admins=admins, cs_list=cs_list)

@app.route('/superadmin/add-employee', methods=['GET', 'POST'])
@login_required('super_admin')
def superadmin_add_employee():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        gender = request.form['gender']
        salary = request.form['salary']
        aadhaar = request.form['aadhaar']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        emp_role = request.form['emp_role']
        try:
            emp_id = query(
                "INSERT INTO employee (fname,lname,gender,salary,aadhaar,email,phone,address,password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (fname,lname,gender,salary,aadhaar,email,phone,address,password), commit=True
            )
            if emp_role == 'admin':
                query("INSERT INTO administrator (employee_id, is_super_admin, added_by) VALUES (%s,0,%s)",
                      (emp_id, session.get('admin_id')), commit=True)
            else:
                query("INSERT INTO customer_support (employee_id, added_by) VALUES (%s,%s)",
                      (emp_id, session.get('admin_id')), commit=True)
            flash(f'Employee added successfully! Employee ID: {emp_id}', 'success')
            return redirect(url_for('super_admin_dashboard'))
        except mysql.connector.IntegrityError as e:
            flash(f'Error: {str(e)}', 'danger')
    return render_template('superadmin_add_employee.html')

@app.route('/superadmin/delete-employee/<string:role>/<int:emp_id>', methods=['POST'])
@login_required('super_admin')
def superadmin_delete_employee(role, emp_id):
    if role == 'admin':
        admin = query("SELECT * FROM administrator WHERE employee_id=%s", (emp_id,), one=True)
        if admin:
            query("DELETE FROM administrator WHERE employee_id=%s", (emp_id,), commit=True)
    elif role == 'cs':
        query("DELETE FROM customer_support WHERE employee_id=%s", (emp_id,), commit=True)
    query("DELETE FROM employee WHERE employee_id=%s", (emp_id,), commit=True)
    flash('Employee removed.', 'info')
    return redirect(url_for('super_admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
