from flask import Flask,request,render_template,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date
import urllib.parse
from flask_migrate import Migrate
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from forms import AdminForm,LoginForm,CourseForm,SearchForm
from werkzeug.utils import secure_filename
import uuid as uuid
import os


app=Flask(__name__)
app.config['SECRET_KEY']='kirrrra'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
db=SQLAlchemy(app)
migrate=Migrate(app, db)

UPLOAD_FOLDER='static/images/'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
#login things
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'


#navbar Searching feature
@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

#database models
class Admin(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(255),nullable=False)
    last_name=db.Column(db.String(255),nullable=False)
    user_name=db.Column(db.String(255),nullable=False,unique=True)
    email=db.Column(db.String(255),nullable=False,unique=True)
    password_hash=db.Column(db.String(255))
    
    @property
    def password(self):
        raise AttributeError("Password is needed.")
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)    
    
    def __repr__(self):
        return '<user_name %r>' % self.user_name
    
#database for adding course
class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    course_name=db.Column(db.String(255),nullable=False)
    course_title=db.Column(db.String(255),nullable=False)
    content=db.Column(db.String(255),nullable=False)
    date_posted=db.Column(db.DateTime,default=datetime.utcnow)    
    course_pic=db.Column(db.String(),nullable=True)
    streams = db.relationship('Stream', backref='course', lazy=True,cascade="all, delete-orphan")
    
    def __repr__(self):
            return '<course_name %r>' % self.course_name
        
        
#database model for adding stream
class Stream(db.Model):
    stream_id=db.Column(db.Integer,primary_key=True)
    stream_name=db.Column(db.String(255),nullable=False)
    course_id=db.Column(db.Integer,db.ForeignKey('course.course_id'),nullable=False)  
     #create a string
    colleges = db.relationship('College', backref='stream', lazy=True,cascade="all, delete-orphan")
     
    def __repr__(self):
        return '<stream_name %r>' % self.stream_name
    
#database model for adding colleges
class College(db.Model):
    college_id=db.Column(db.Integer,primary_key=True)
    college_name=db.Column(db.String(255),nullable=False)
    college_address=db.Column(db.String(255),nullable=True)
    college_web=db.Column(db.String(255),nullable=True)
    stream_id=db.Column(db.Integer,db.ForeignKey('stream.stream_id'),nullable=False)
     #create a string
    def __repr__(self):
        return '<college_name %r>' % self.college_name

class HomeImage(db.Model):
    home_id=db.Column(db.Integer,primary_key=True)
    home_img=db.Column(db.String(),nullable=True)    
    def __repr__(self):
            return '<college_name %r>' % self.home_img                     

@app.route('/')
def home():
    courses=Course.query.all()
    home_img=HomeImage.query.all()
    
    print(courses)
    print(home_img)
    if courses and home_img:
     return render_template('home.html',courses=courses,home_img=home_img)
    elif courses:
     return render_template('home.html',courses=courses)
    else:
     return render_template('home.html',courses=courses)
        
         

@app.route('/signin',methods=['POST','GET'])
def signin():
    user_name=None
    form=AdminForm()
    if form.validate_on_submit():
        admin=Admin.query.filter_by(user_name=form.user_name.data).first()
        print(admin)
        if admin is None:
            hashed_pass=generate_password_hash(form.password_hash.data,method='scrypt')
            print(hashed_pass)
            admin=Admin(first_name=form.first_name.data,last_name=form.last_name.data,user_name=form.user_name.data,email=form.email.data,password_hash=hashed_pass)
            db.session.add(admin)
            db.session.commit()
            flash("You have successfully signed In.")
            return render_template("signinsuccess.html")
        else:
            form.first_name.data=''
            flash("User already exists.")
            return render_template("signin.html",form=form) 
        
    form.first_name.data=''
    form.last_name.data=''
    form.user_name.data=''
    form.email.data=''   
   # form.password_hash.errors=''            
    return render_template("signin.html",form=form)  
    
@app.route('/login',methods=['POST','GET'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        admin=Admin.query.filter_by(user_name=form.user_name.data).first()
        print(admin)
        print(admin)
        if admin:
            if check_password_hash(admin.password_hash,form.password.data):  
                print("uee")
                login_user(admin)
                flash("Login successfully.")
                return redirect(url_for('dashboard'))
            else:
                   flash("Wrong password!!")
        else:
            flash("User doesnt exist.")
    form.user_name.data=''
    form.password.data=''                
    return render_template("login.html",form=form)
    
@app.route('/dashboard')
@login_required
def dashboard():
    courses=Course.query.all()
    print(courses)
    if courses:
       return render_template('dashboard.html',courses=courses)
    else:
       return render_template('dashboard.html',courses=courses)
       

#logout  page
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for('home'))


@app.route('/addcourse',methods=['POST','GET'])
@login_required
def add_course():
    form=CourseForm()
    if form.validate_on_submit():
        print(form.course_name.data)   
        course_pic=form.course_pic.data
        print(course_pic)
        #saving image

        #making image name
        pic_filename=secure_filename(course_pic.filename)
        #set uuid
        pic_name=str(uuid.uuid1())+ "_" + pic_filename
        course_pic.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
        course=Course(course_name=form.course_name.data,course_title=form.course_title.data,content=form.content.data,course_pic=pic_name)
        db.session.add(course) 
        db.session.commit()
        counter=1
        while True:
            stream_key = f'stream{counter}'
            print(stream_key)
            if stream_key in request.form:
                stream = request.form[stream_key]
                #college = request.form[college_key]
                course=Course.query.filter_by(course_name=form.course_name.data).first()  
                stream=Stream(stream_name=stream,course_id=course.course_id)
                db.session.add(stream)
                db.session.commit()
                print(stream)
                counter+=1
            else:
                break    
        flash("Course Added successfully.")    
    return render_template('addcourse.html',form=form)

@app.route('/view_admin',methods=['POST','GET'])
@login_required
def view_course():
    courses=Course.query.all()
    print(courses)
    if courses:
       return render_template('view_course.html',courses=courses)
    else:
       return render_template('view_course.html',courses=courses)
        

@app.route('/view_ind/<int:id>',methods=['POST','GET'])
def view_ind(id):
    print(id)
    courses=Course.query.filter_by(course_id=id).first()
    print(courses.course_pic)
    streams = courses.streams
 
    print(streams)
    return render_template('view_ind.html',courses=courses,streams=streams)
    
@app.route('/delete/<int:id>',methods=['POST','GET'])
@login_required
def delete(id):
    course_to_delete=Course.query.get_or_404(id)
    try:
        db.session.delete(course_to_delete)
        db.session.commit()
        flash('Deleted successfully.')
        courses=Course.query.all()
        return render_template('view_course.html',courses=courses)
    except:
            flash('Whoops error in deleting the post.')
            courses=Course.query.all()
            return render_template("posts.html",courses=courses)
    
@app.route('/view_to_add',methods=['POST','GET'])
@login_required
def view_to_add():
      courses=Course.query.all()
      print(courses)
      return render_template('view_to_add.html',courses=courses)
  
    
@app.route('/add_college/<int:id>',methods=['POST','GET'])
def add_college(id):
    courses=Course.query.filter_by(course_id=id).first()
    print(courses)
    streams = courses.streams
    print(streams)
    return render_template('view_to_addsss.html',courses=courses,streams=streams)

    
@app.route('/add_clg/<int:id>',methods=['POST','GET'])
@login_required
def add_clg(id):
    streams=Stream.query.filter_by(stream_id=id).first()
    print(streams)
    course_id = streams.course_id
    courses=Course.query.filter_by(course_id=course_id).first()
    if request.method=='POST':
        counter=1
        while True:
            college_name = f'college{counter}'
            college_address=f'address{counter}'
            college_link=f'link{counter}'
            if college_name in request.form and college_address in request.form and college_link in request.form:
                clg_name = request.form[college_name]
                clg_address=request.form[college_address]
                clg_link=request.form[college_link]
                college=College(college_name=clg_name,college_address=clg_address,college_web=clg_link,stream_id=streams.stream_id)
                db.session.add(college)
                db.session.commit()
                counter+=1
            else:
                break;
        flash("SuccessFully Added College Details.")
    return render_template('addclg.html',streams=streams,courses=courses)

@app.route('/v_college/<int:id>',methods=['POST','GET'])
def v_college(id):
        print(id)
        colleges=College.query.filter_by(stream_id=id).all()
        print(colleges)
        if colleges:
            for college in colleges:
                stream_id = college.stream_id
                print(stream_id)
                stream=Stream.query.filter_by(stream_id=stream_id).first()
                print(stream.stream_name)
            course_name = stream.course.course_name.upper()
            print(course_name)      
            return render_template('view_college.html',colleges=colleges,streams=stream,course_name=course_name)
        else:
            streams=Stream.query.filter_by(stream_id=id).first()
            flash('Cannot find Colleges for this particular course.')
            return render_template('view_college.html',colleges=colleges,streams=streams.stream_name.upper(),stream_id=streams.stream_id)
            
@app.route('/search',methods=['POST'])
def search():
     form=SearchForm()
     courses=Course.query
     if form.validate_on_submit:
         #Getting data from form submitted
         searched=form.searched.data
         #Quering database
         courses=courses.filter(Course.course_name.like('%' + searched + '%'))
         courses=courses.order_by(Course.course_title).all()
         return render_template("search.html",form=form,searched=searched,courses=courses)
    
@app.route('/delete_clg/<int:id>',methods=['POST','GET'])
@login_required
def delete_college(id):
    college_to_delete=College.query.get_or_404(id)
    print(college_to_delete)
    stream_id=college_to_delete.stream_id
    print(stream_id)
    try:
        db.session.delete(college_to_delete)
        db.session.commit()
        flash('Deleted successfully.')
        colleges=College.query.filter_by(stream_id=stream_id).all()
        if colleges:
            for college in colleges:
                stream_id = college.stream_id
                print(stream_id)
                stream=Stream.query.filter_by(stream_id=stream_id).first()
                print(stream.stream_name)
            course_name = stream.course.course_name.upper()
            print(course_name)      
            return render_template('view_college.html',colleges=colleges,streams=stream,course_name=course_name)
        else:
            streams=Stream.query.filter_by(stream_id=id).first()
            flash('Cannot find Colleges for this particular course.')
            return render_template('view_college.html',colleges=colleges,streams=streams,course_name=streams.stream_id)
    except:
            flash('Whoops error in deleting the post.')
            courses=Course.query.all()
            return render_template("view_college.html",courses=courses)
        
        
@app.route('/add_more_stream/<int:id>',methods=['POST','GET'])
@login_required
def add_more_stream(id):
    print(id)
    if request.method == 'POST':
        counter=1
        while True:
            stream_key = f'stream{counter}'
            print(stream_key)
            if stream_key in request.form:
                    stream = request.form[stream_key]
                    stream=Stream(stream_name=stream,course_id=id)
                    db.session.add(stream)
                    db.session.commit()
                    print(stream)
                    counter+=1
            else:
                break
        stream=Stream.query.filter_by(course_id=id).all()
        course=Course.query.filter_by(course_id=id).first()
        print(course)        
        flash("Course Added successfully.")   
        return render_template('view_ind.html',streams=stream,courses=course)
        

@app.route('/delete_stream/<int:id>',methods=['POST','GET'])
@login_required
def delete_stream(id):
        print(id)
        stream_to_delete=Stream.query.get_or_404(id)
        print(stream_to_delete)
        try:
            db.session.delete(stream_to_delete)
            db.session.commit()
            flash('We deleted a Stream.')
            course=Course.query.filter_by(course_id=stream_to_delete.stream_id).first()
            stream=Stream.query.filter_by(course_id=course.course_id).all()
            return render_template('view_ind.html',streams=stream,courses=course)
        except:
               flash('Whoops error in deleting the post.')
               course=Course.query.filter_by(course_id=stream_to_delete.course_id).first()
               stream=Stream.query.filter_by(course_id=course.course_id).all()
               return render_template('view_ind.html',streams=stream,courses=course)
               
@app.route('/add_more_clg/<int:id>',methods=['POST','GET'])
@login_required
def add_more_clg(id):
    print(id)
    if request.method == 'POST':
        counter=1
        while True:
            college_name = f'college{counter}'
            college_address=f'address{counter}'
            college_link=f'link{counter}'
            print(college_link)
            print(college_name)
            print(college_address)
            
            if college_name in request.form and college_address in request.form and college_link in request.form:
                clg_name = request.form[college_name]
                clg_address=request.form[college_address]
                clg_link=request.form[college_link]
                print(clg_name)
                print(clg_address)
                print(clg_link)
                
                college=College(college_name=clg_name,college_address=clg_address,college_web=clg_link,stream_id=id)
                db.session.add(college)
                db.session.commit()
                counter+=1
            else:
                print("jiiii")
                break;
        
        colleges=College.query.filter_by(stream_id=id).all()
        print(colleges)
        stream=Stream.query.filter_by(stream_id=id).first()
        print(stream)
        course=Course.query.filter_by(course_id=stream.course_id).first()
        print(course)
        flash("College Added successfully.")   
        return render_template('view_college.html',colleges=colleges,streams=stream,course_name=course.course_name)

@app.route('/home_img',methods=['GET','POST'])        
def home_img():
        if request.method=='POST':
            home_img=request.files['image']
            print(home_img)
            pic_filename=secure_filename(home_img.filename)
        #set uuid
            pic_name=str(uuid.uuid1())+ "_" + pic_filename
            home_img.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
            homeimg=HomeImage(home_img=pic_name)
            db.session.add(homeimg) 
            db.session.commit()   
            flash("Successfully Added Image")   
            imgs=HomeImage.query.all()
            print(imgs)
            return render_template('home_img.html',imgs=imgs)
        else:   
            imgs=HomeImage.query.all()
            return render_template('home_img.html',imgs=imgs)   
        
@app.route('/delete_home_img/<int:id>',methods=['POST','GET'])        
def delete_home_img(id):
        print(id)
        home_img=HomeImage.query.get_or_404(id)
        print(home_img)
        try:
            db.session.delete(home_img)
            db.session.commit()
            flash('Image deleted Successfully.')
            imgs=HomeImage.query.all()
            print(imgs)
            return render_template('home_img.html',imgs=imgs)
        except:
               flash('Whoops error in deleting the post.')
               imgs=HomeImage.query.all()
               return render_template('home_img.html',imgs=imgs)
               
@app.route('/update/<int:id>',methods=['POST','GET'])
@login_required
def update(id):             
    form=CourseForm()
    course_to_update=Course.query.get_or_404(id)  
    if request.method=='POST':
         course_to_update.course_name=request.form['course_name']
         course_to_update.course_title=request.form['course_title']
         course_to_update.content=request.form['content']
         course_to_update.course_pic=request.files['course_pic']
         pic_filename=secure_filename(course_to_update.course_pic.filename)
         print(pic_filename)
            #set uuid
         pic_name=str(uuid.uuid1())+ "_" + pic_filename
         request.files['course_pic'].save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
         print(form.course_name.data)
         print(pic_name)
         course_to_update.course_pic=pic_name
         try:
             db.session.commit()
             flash('Updated successfully!')
             return render_template('update_course.html',form=form,course_to_update=course_to_update)
         except:
            #  db.session.rollback()
             flash('Error!')
             return render_template('update_course.html',form=form,course_to_update=course_to_update)
    else:
             return render_template('update_course.html',form=form,course_to_update=course_to_update,id=id)
             
if __name__=='__main__':
    app.run(debug=True)