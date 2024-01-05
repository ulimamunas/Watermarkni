from main import db
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired, Length
from werkzeug.security import check_password_hash
from PIL import Image
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    original_images = relationship('MyImage', backref='user_image', lazy=True)
    watermarks = relationship('Watermark', backref='user_watermark', lazy=True)
    watermarked_images = relationship('WatermarkedImage', backref='user_watermarked_images', lazy=True)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def has_signed_up(self):
        # Implementasi metode ini sesuai kebutuhan
        # Misalnya, cek apakah ada data pengguna berdasarkan ID atau kondisi lain
        return True if self.id else False
    
    def create_watermark_image(original, watermark):
        originalImage = Image.open(original)
        watermarkImage = Image.open(watermark)

        # Pastikan kedua gambar memiliki mode dan ukuran yang sama
        watermarkImage = watermarkImage.convert('RGBA')
        originalImage = originalImage.convert('RGBA')

        # Buat gambar RGBA kosong untuk watermark
        watermarkedImage = Image.new('RGBA', originalImage.size)

        # Gabungkan gambar asli dan watermark
        watermarkedImage.paste(originalImage, (0, 0))
        watermarkedImage.paste(watermarkImage, (0, 0), mask=watermarkImage)

        # Hapus saluran alpha untuk mengembalikan ke mode RGB
        watermarkedImage = watermarkedImage.convert('RGB')
        
        return watermarkedImage         
        
    
class MyImage(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  

    watermarked_image = relationship('WatermarkedImage', backref='image_watermarked_images', uselist=False)

class Watermark(db.Model):
    __tablename__ = 'watermarks'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  

    watermarked_image = relationship('WatermarkedImage', backref='watermark_watermarked_images', uselist=False)

class WatermarkedImage(db.Model):
    __tablename__ = 'watermarkedimages'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    original_image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    watermark_id = db.Column(db.Integer, db.ForeignKey('watermarks.id'), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  
        
    original_image = relationship("MyImage", uselist=False)
    watermark = relationship("Watermark", uselist=False)
    user = relationship("User", uselist=False)

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=80)])
    submit = SubmitField('Sign In')

class WatermarkForm(FlaskForm):
    original = FileField(validators=[InputRequired()])
    watermark = FileField(validators=[InputRequired()])
    submit = SubmitField('Generate')