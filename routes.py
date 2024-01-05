from main import app, db
from flask import render_template, redirect, url_for, flash, send_from_directory, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import numpy as np
from flask_login import login_user, current_user, login_required, login_manager, logout_user
from models import *
from flask_login import LoginManager
import os
import time
import secrets

# Inisialisasi LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'signin'

@login_manager.user_loader
def load_user(user_id):
    # Implementasikan cara memuat pengguna berdasarkan ID
    # Misalnya, ambil dari basis data atau sumber data lainnya
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        # Hash the password before saving it to the database
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        new_user = User(name=form.name.data, username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! You will now be redirected to the sign-in page.', 'success')
        return redirect(url_for('signin'))

    return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SignInForm()

    if form.validate_on_submit():
        # Ambil informasi pengguna dari database berdasarkan a pengguna
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            # Login pengguna menggunakan Flask-Login
            login_user(user)

            flash('Login successful! You will now be redirected to the home page.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
        return redirect(url_for('home')) 
        
    return render_template('signin.html', form=form)

@app.route('/logout')
@login_required
def logout():
    # Logout user menggunakan Flask-Login
    logout_user()

    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/watermark' , methods=['GET', 'POST'])
@login_required
def watermark():
    # Cek apakah pengguna sudah memiliki data sign up (User model)
    if not current_user.has_signed_up():
        flash('You need to sign up first before creating a watermark.', 'info')
        return redirect(url_for('signup'))
    
    form = WatermarkForm()

    if current_user.is_authenticated:
        show_signup_button = False  # User is logged in, hide the "Sign Up" button
    else:
        show_signup_button = True   # User is not logged in, show the "Sign Up" button

    if form.validate_on_submit():
        # Get uploaded files
        original_file = request.files['original']
        watermark_file = request.files['watermark']

        # Save the files to a temporary directory
        original_filename = secure_filename(original_file.filename)
        watermark_filename = secure_filename(watermark_file.filename)

        original_path = f'tmp/{original_filename}'
        watermark_path = f'tmp/{watermark_filename}'

        original_file.save(original_path)
        watermark_file.save(watermark_path)

        # Save the images to the database
        original_model = MyImage(filename=original_filename, user_id=current_user.id)
        watermark_model = Watermark(filename=watermark_filename, user_id=current_user.id)
        db.session.add(original_model)
        db.session.add(watermark_model)
        db.session.commit()

        # Replace LSB of the original image with LSB of the watermark
        watermarked_image_file = User.create_watermark_image(original_path, watermark_path)

        # Generate a unique filename for the watermarked image
        timestamp = int(time.time())
        random_string = secrets.token_hex(8)
        watermarked_filename = secure_filename(f"watermarked_{timestamp}_{random_string}.jpg")
        watermarked_image_path = f'tmp/{watermarked_filename}'
        watermarked_image_file.save(watermarked_image_path)

        # Save the watermarked image to the database
        watermarked_model = WatermarkedImage(
            filename=watermarked_filename,
            original_image=original_model,
            watermark=watermark_model,
            user_id=current_user.id
        )
        db.session.add(watermarked_model)
        db.session.commit()

        # Redirect to a page to show the result or download the watermarked image
        return redirect(url_for('result', filename=watermarked_filename))
    return render_template('watermark.html', form=form)

@app.route('/result/<filename>')
def result(filename):
    # Get the WatermarkedImage model from the database based on the filename
    watermarkedImage = WatermarkedImage.query.filter_by(filename=filename).first()

    if watermarkedImage:
        return render_template('result.html', watermarkedImage=watermarkedImage, filename=watermarkedImage.filename)
    else:
        # Handle the case where the watermarked image is not found
        return render_template('result_not_found.html')
        

@app.route('/tmp/<path:filename>')
def serve_watermarkedImg(filename):
    return send_from_directory('tmp', filename)

@app.route('/assets/<path:filename>')
def serve_img(filename):
    return send_from_directory('assets', filename)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)