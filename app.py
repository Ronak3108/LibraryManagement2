import csv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "ronak123455566"



@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
def loginPage():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('_flashes', None)
    if request.method == 'POST':
        login_id = request.form['login_id']
        password = request.form['password']

        users = {}
        with open('./db/admins.csv', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row.get('login_id', '').strip()
                user_pass = row.get('password', '').strip()
                if not user_id:
                    continue
                users[user_id] = user_pass

        if login_id in users and users[login_id] == password:
            session['user'] = login_id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid login ID or password. Try again.', 'danger')

    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    else:
        flash('You must log in first.', 'warning')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/transactions')
def transactions():
    if 'user' in session:
        return render_template('transactions.html', user=session['user'])
    else:
        flash('You must log in first.', 'warning')
        return redirect(url_for('login'))
    
    
    
@app.route('/members', methods=['GET', 'POST'])
def members():
    if 'user' not in session:
        flash('You must log in first.', 'warning')
        return redirect(url_for('login'))

    session.pop('_flashes', None)
    with open('./db/members.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)

    if request.method == 'POST':
        query = request.form.get('search_query', '').upper()
        
        search_list = []
        for row in csv_data:
            member_id = row.get('member_id', '').strip().upper()
            member_name = row.get('member_name', '').strip().title()
            book_id = row.get('book_id', '').strip()
            issue_date = row.get('issue_date', '').strip()
            return_date = row.get('return_date', '').strip()
            email = row.get('email', '').strip(),
            phone = row.get('phone', '').strip()

            if query in member_id:
                row_data = {
                    'member_id': member_id,
                    'member_name': member_name,
                    'book_id': book_id,
                    'issue_date': issue_date,
                    'return_date': return_date,
                    'email': email,
                    'phone': phone,
                }
                search_list.append(row_data)

        return render_template('members.html', user=session['user'], search_list=search_list)

    return render_template('members.html', user=session['user'], search_list=csv_data)


    

@app.route('/books', methods=['GET', 'POST'])
def books():
    if 'user' not in session:
        flash('You must log in first.', 'warning')
        return redirect(url_for('login'))

    session.pop('_flashes', None)
    with open('./db/books.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)

    if request.method == 'POST':
        query = request.form.get('search_query', '').upper()
            
        search_list = []
        for row in csv_data:
            book_id = row.get('book_id', '').strip().upper()
            book_name_raw = row.get('book_name', '').strip()
            book_name = book_name_raw.title()
            genre = row.get('genre', '').strip()
            author = row.get('author', '').strip()
            price = row.get('price', '').strip()
            quantity = row.get('quantity', '').strip()

            # search by NAME
            if query in book_name_raw.upper():
                row_data = {
                    'book_id': book_id,
                    'book_name': book_name,
                    'genre': genre,
                    'author': author,
                    'price': price,
                    'quantity': quantity,
                }
                search_list.append(row_data)

        return render_template('books.html', user=session['user'], search_list=search_list)
    
    return render_template('books.html', user=session['user'], search_list=csv_data)


@app.route('/delete/<member_ID>', methods=['POST'])
def deleteMember(member_ID):
    filename = './db/members.csv'
    rows=[]
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['member_id'] != member_ID:
                rows.append(row)

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return redirect(url_for("members"))



@app.route('/deleteBook/<book_ID>', methods=['POST'])
def deleteBook(book_ID):
    filename = './db/books.csv'
    rows=[]
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['book_id'] != book_ID:
                rows.append(row)

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return redirect(url_for("books"))

@app.route('/edit/<member_ID>', methods=['POST'])
def editMember(member_ID):
    filename = './db/members.csv'
    rows=[]
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            rows.append(row)

        for row in rows:
            if row['member_id'] == member_ID:
                new_name = request.form.get('member_name')
                new_phone = request.form.get('phone')
                new_email = request.form.get('email')
                row['member_name'] = new_name
                row['phone'] = new_phone
                row['email'] = new_email

    fieldnames = ['member_id', 'member_name', 'phone', 'email', 'book_id', 'issue_date', 'return_date']
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return redirect(url_for("members"))



@app.route('/editBook/<book_ID>', methods=['POST'])
def editBook(book_ID):
    filename = './db/books.csv'
    rows=[]
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            rows.append(row)

        for row in rows:
            if row['book_id'] == book_ID:
                new_name = request.form.get('book_name')
                new_quantity = request.form.get('quantity')
                new_author = request.form.get('author')
                new_price = request.form.get('price')
                new_genre = request.form.get('genre')

                row['book_name'] = new_name
                row['quantity'] = new_quantity
                row['author'] = new_author
                row['price'] = new_price
                row['genre'] = new_genre

    fieldnames = ['book_id', 'book_name', 'genre', 'author', 'price', 'quantity']
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return redirect(url_for("books"))



@app.route('/add-book', methods=['POST'])
def addBook():
    bookID = request.form.get('book_id')
    book_name = request.form.get('book_name')
    author = request.form.get('author')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    genre = request.form.get('genre')

    filename = './db/books.csv'
    rows=[]
    id_list = []

    message = "Error"

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            rows.append(row)
            id_list.append(row['book_id'])
    
    if bookID in id_list:
        message = "Book ID already exists. Please change it."
    elif int(quantity) <= 0 or int(quantity)%1 != 0  or book_name.trim() == "":
        message = "Invalid Details Entered."
    else:
        new_book_data = {
            'book_id': bookID,
            'book_name': book_name,
            'genre': genre,
            'author': author,
            'price': price,
            'quantity': quantity
        }
        rows.append(new_book_data)
        fieldnames = ['book_id', 'book_name', 'genre', 'author', 'price', 'quantity']
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        message = "Book Added Successfully"
        flash(message, "success")
        return redirect(url_for("books"))
    
    
    flash(message, "error")
    return redirect(url_for("books"))

    


@app.route('/add-member', methods=['POST'])
def addMember():
    memberID = request.form.get('member_id')
    member_name = request.form.get('member_name')
    phone = request.form.get('phone')
    email = request.form.get('email')

    filename = './db/members.csv'
    rows=[]
    id_list = []

    message = "Error"

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            rows.append(row)
            id_list.append(row['member_id'])
    
    if memberID in id_list:
        message = "Member ID already exists. Please change it."
    else:
        new_book_data = {
            'member_id': memberID,
            'member_name': member_name,
            'phone': phone,
            'email': email,
            'book_id': None,
            'issue_date': None,
            'return_date': None
        }
        rows.append(new_book_data)
        fieldnames = ['member_id', 'member_name', 'phone', 'email', 'book_id', 'issue_date', 'return_date']
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        message = "Member Added Successfully"
        flash(message, "success")
        return redirect(url_for("members"))
    
    flash(message, "error")
    return redirect(url_for("books"))



@app.route('/book_action', methods=['POST'])
def handleTransactions():
    session.pop('_flashes', None)
    memberID = request.form.get("member_id").upper()
    bookID = request.form.get("book_id").upper()
    action_type = request.form.get("action")

    member_data = None
    book_data = None

    with open('./db/members.csv', newline='') as f:
        reader = csv.DictReader(f)
        member_rows = list(reader)

    with open('./db/books.csv', newline='') as file:
        reader = csv.DictReader(file)
        book_rows = list(reader)


    for row in member_rows:
        if row['member_id'] == memberID:
            member_data = row
            break
    
    for row in book_rows:
        if row['book_id'] == bookID:
            book_data = row
            break

    if member_data:
        if book_data:
            if action_type == 'issue':
                if member_data.get('book_id') or member_data.get('issue_date') or member_data.get('return_date'):
                    flash("Member Cannot Issue another Book. Return previous one first", 'error')
                    return redirect(url_for("transactions"))
                elif int(book_data['quantity']) <= 0:
                    flash("Book issued by someone else", 'error')
                    return redirect(url_for("transactions"))
                else:
                    member_data['book_id'] = bookID
                    issue_datetime_obj = datetime.now()
                    return_datetime_obj = issue_datetime_obj + timedelta(days=7)

                    member_data['issue_date'] = issue_datetime_obj.strftime("%Y-%m-%d")
                    member_data['return_date'] = return_datetime_obj.strftime("%Y-%m-%d")

                    book_data['quantity'] = f"{int(book_data['quantity'])-1}"

                    for row in member_rows:
                        if row['member_id'] == member_data['member_id']:
                            row['book_id'] = member_data['book_id']
                            row['issue_date'] = member_data['issue_date']
                            row['return_date'] = member_data['return_date']
                    
                    for row in book_rows:
                        if row['book_id'] == book_data['book_id']:
                            row['quantity'] = book_data['quantity']
                    
                    fieldnames_members = ['member_id', 'member_name', 'phone', 'email', 'book_id', 'issue_date', 'return_date']
                    with open('./db/members.csv', mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames_members)
                        writer.writeheader()
                        writer.writerows(member_rows)

                    fieldnames_books = ['book_id', 'book_name', 'genre', 'author', 'price', 'quantity']
                    with open('./db/books.csv', mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames_books)
                        writer.writeheader()
                        writer.writerows(book_rows)

                    flash("Book Issued Successfully. Return it before 7 days", 'success')
                    return redirect(url_for("transactions"))
                
            elif action_type == 'return':
                if member_data.get('book_id') == bookID or member_data.get('issue_date') or member_data.get('return_date'):
                    member_data['book_id'] = None
                    member_data['issue_date'] = None
                    member_data['return_date'] = None
                    book_data['quantity'] = f"{int(book_data['quantity'])+1}"

                    for row in member_rows:
                        if row['member_id'] == member_data['member_id']:
                            row['book_id'] = member_data['book_id']
                            row['issue_date'] = member_data['issue_date']
                            row['return_date'] = member_data['return_date']
                    
                    for row in book_rows:
                        if row['book_id'] == book_data['book_id']:
                            row['quantity'] = book_data['quantity']
                    
                    fieldnames_members = ['member_id', 'member_name', 'phone', 'email', 'book_id', 'issue_date', 'return_date']
                    with open('./db/members.csv', mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames_members)
                        writer.writeheader()
                        writer.writerows(member_rows)

                    fieldnames_books = ['book_id', 'book_name', 'genre', 'author', 'price', 'quantity']
                    with open('./db/books.csv', mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames_books)
                        writer.writeheader()
                        writer.writerows(book_rows)
                        
                    flash("Book Returned Successfully", 'success')
                    return redirect(url_for("transactions"))
                else:
                    flash("Book Not Issued by the Member", 'error') # Added 'error' category
                    return redirect(url_for("transactions"))
            else:
                flash("Fill Form Properly", 'error')
                return redirect(url_for("transactions"))
        else:
            flash("Book Not Found", 'error')
            return redirect(url_for("transactions"))
    else:
        flash("Member Not Found", 'error')
        return redirect(url_for("transactions"))




if __name__ == '__main__':
    app.run()
