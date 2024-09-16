from flask import *
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, Regexp
import bcrypt
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
db = mysql.connector.connect(
    host = 'localhost',
    user = 'username',    # replace with your username
    password = 'password',    # replace with your password
    database = 'database name'    # replace with your database name
)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Regexp(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$',
               message="Password must be at least 6 characters long, include atleast one uppercase letter, one digit, one special symbol")
               ])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError('Passwords must match.')

    def validate_email(self, field):
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email=%s', (field.data,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    login_input = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = db.cursor()
        cursor.execute('SELECT name FROM users WHERE id=%s', (user_id,))
        user = cursor.fetchone()
        
        if user:
            user_name = user[0]
            return render_template('index.html', user_name=user_name)
    
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # insert into the database
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, hashed_password))
        db.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.login_input.data
        password = form.password.data

        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email=%s OR name=%s', (login_input, login_input))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please chek your email and password")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))
        user = cursor.fetchone()

        if user:
            # notes
            if request.method == 'POST':
                if 'add_note' in request.form:
                    content = request.form.get('note_content')
                    if content:
                        cursor.execute('INSERT INTO notes (user_id, content) VALUES (%s, %s)', (user_id, content))
                        db.commit()
                        flash("Note added successfully")
                    return redirect(url_for('dashboard'))
                elif 'delete_note' in request.form:
                    note_id = request.form.get('note_id')
                    if note_id:
                        cursor.execute('DELETE FROM notes WHERE id=%s AND user_id=%s', (note_id, user_id))
                        db.commit()
                        flash("Note deleted successfully")
                    return redirect(url_for('dashboard'))

            # fetch the user's notes
            cursor.execute('SELECT * FROM notes WHERE user_id=%s ORDER BY created_at DESC', (user_id,))
            notes = cursor.fetchall()

            # Time-Based Greeting Logic
            current_hour = datetime.now().hour
            if current_hour < 12:
                greeting = "Good Morning"
            elif 12 <= current_hour < 18:
                greeting = "Good Afternoon"
            else:
                greeting = "Good Evening"

            return render_template('dashboard.html', user=user, greeting=greeting, notes=notes)

    return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = db.cursor()
        cursor.execute('DELETE FROM users WHERE id=%s', (user_id,))
        db.commit()
        cursor.close()

        session.pop('user_id', None)
        
        return jsonify({'success': True})

    return jsonify({'success': False})

if __name__=='__main__':
    app.run(debug=True)
