from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,EqualTo,Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField,PasswordField,BooleanField,ValidationError,TextAreaField
from flask_wtf.file import FileField


#creating a form for Admin sign up
class AdminForm(FlaskForm):
    first_name=StringField("First name:",validators=[DataRequired()])
    last_name=StringField("Last name:",validators=[DataRequired()])
    user_name=StringField("User name:",validators=[DataRequired()])
    email=StringField("Email:",validators=[DataRequired()])
    password_hash=PasswordField("Password:",validators=[DataRequired(),EqualTo("confirm_password",message="Password does not match.")])
    confirm_password=PasswordField("Confirm password:",validators=[DataRequired()])
    
    submit=SubmitField("Submit")
    
#creating login form
class LoginForm(FlaskForm):
    user_name=StringField("User name:",validators=[DataRequired()])
    password=StringField("Password:",validators=[DataRequired()])
    
    submit=SubmitField("submit")
    
#creating form to add course details
class CourseForm(FlaskForm):
    course_name=StringField("Course name:",validators=[DataRequired()])
    course_title=StringField("Course title:",validators=[DataRequired()])
    content=StringField("Add content:",validators=[DataRequired()],widget=TextArea())
    
    submit=SubmitField("submit")    
    
#createing search form
class SearchForm(FlaskForm):
    searched=StringField("Searched:",validators=[DataRequired()])
    submit=SubmitField('Submit') 
        