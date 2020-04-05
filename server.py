"""FamilyCube"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User,Profile,Member,Event,Image
from datetime import datetime
from sqlalchemy import extract
import os

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def indexpage():
    """Indexpage."""
    app.logger.info("Hello World")
    if session.get("user_id") is not None:
        return redirect("/homepage")
    else:
        return render_template("index.html")


@app.route('/register')
def register_form():
#     """Show form for user signup."""

    return render_template("register_form.html")

@app.route('/register', methods=['POST'])
def register_process():
#     """Process registration."""

#     # Get form variables
    first_name = request.form.get("Firstname")
    last_name = request.form.get("Lastname")
    email = request.form.get("Email")
    password = request.form.get("Password")
    

    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    
    session["first_name"] = new_user.first_name
    db.session.add(new_user)
    db.session.commit()

    flash(f"User {email} added.")
    return redirect("/login")


@app.route('/login')
def login_form():
#     """Show login form."""

    return render_template("login_form.html")



@app.route('/validatelogin', methods=['POST'])
def validate_login():
#     """Validate login."""

#     # Get form variables
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()
    if user is not None and user.password == password:
        session["user_id"] = user.user_id
        session["first_name"] = user.first_name
        response = ''
    else:
        response = 'Invalid userid and password combination'

    return response



@app.route('/homepage')
def homepage():

    first_name = session["first_name"]
    first3_events = latest_events()
    app.logger.info(os.path.join(os.environ['HOME'], 'static'))
    app.logger.info(os.path.dirname(app.instance_path))
    return render_template("home_page.html",first_name=first_name, events=first3_events)

@app.route('/profile')
def profile_page():
    """Show form for user to update profile."""
    if has_profile_exists():
        return redirect("/profile_display")
    else:
        return render_template("profile.html")


@app.route('/profile', methods=['POST'])
def profile_update():
    """Profile updation process"""

    first_name= request.form.get("Firstname")
    last_name = request.form.get("Lastname")
    display_name = request.form.get("Displayname")
    email = request.form.get("Email")
    phonenumber = request.form.get("Phonenumber")
    date_of_birth_str = request.form.get("Birthday")
    date_of_birth = datetime.strptime(date_of_birth_str,'%Y-%m-%d')
    address_1 = request.form.get("Address1")
    address_2 = request.form.get("Address2")
    city = request.form.get("City")
    state = request.form.get("State")
    zipcode = request.form.get("Zipcode")
    country = request.form.get("Country")
    married = request.form.get("Marital_Status")
    marriage_date_str = request.form.get("Marriage_Anniversary")
    marriage_date = datetime.strptime(marriage_date_str,'%Y-%m-%d')
    kids = int(request.form.get("Kids"))
    userid = session["user_id"]
    

    user_profile = Profile(display_name=display_name, user_id=userid, email=email,phonenumber=phonenumber,date_of_birth=date_of_birth,
                          address_1=address_1, address_2=address_2, city=city, state=state, zipcode=zipcode, 
                          country=country, married=married, marriage_date=marriage_date, kids=kids)
    db.session.add(user_profile)
    db.session.commit()
    text = f"Birthday for {first_name} {last_name}"
    user_event = Event(profile_id=user_profile.profile_id,event_type='Birthday',event_date=date_of_birth,event_text=text)
    db.session.add(user_event)
    db.session.commit()

    return redirect("/homepage")

def get_profile():
    """return profile for the user"""
    user_id = session["user_id"]
    if user_id is not None:
        return Profile.query.filter_by(user_id=user_id).first()
    else:
        return None


def has_profile_exists():
    """return True if profile exists in database"""
    profile = get_profile()
    return profile is not None


@app.route('/profile_display')
def profile_view():
    """Profile display"""
    
    profile = get_profile()    
    return render_template("profile_display.html",user=profile.users, profile=profile)

@app.route('/member')
def add_member():
    """Update Member"""

    return render_template("member.html")

@app.route('/member_display')
def member_view():
    """Member display"""
    
    userid = session.get("user_id")
    if userid is not None:
        members = db.session.query(Member).join(Profile).filter(Profile.user_id==userid).all()
        return render_template("member_display.html",members=members)

@app.route('/member',methods=['POST'])
def member_update():
    """Member updation process"""

    first_name= request.form.get("Member_Firstname")
    last_name = request.form.get("Member_Lastname")
    email = request.form.get("Member_Email")
    phonenumber = request.form.get("Member_Phonenumber")
    date_of_birth_str = request.form.get("Member_Birthday")
    date_of_birth = datetime.strptime(date_of_birth_str,'%Y-%m-%d')
    marriage_date_str = request.form.get("Member_Marriage_Anniversary")
    if marriage_date_str != '':
        marriage_date = datetime.strptime(marriage_date_str,'%Y-%m-%d')
    else:
        marriage_date = None

    relation = request.form.get("Member_Relation")

    user_profile = get_profile()

    member_profile = Member(profile_id=user_profile.profile_id,first_name=first_name, last_name=last_name,email=email,
                            phonenumber=phonenumber, date_of_birth=date_of_birth, marriage_date=marriage_date,
                            relation=relation)
    db.session.add(member_profile)
    db.session.commit()

    #Add birthday and marriage anniversary to events
    text = f"Birthday for {first_name} {last_name}"
    member_db_event = Event(profile_id=user_profile.profile_id,member_id=member_profile.member_id,event_type='Birthday',event_date=date_of_birth,event_text=text)
    db.session.add(member_db_event)
    if marriage_date is not None:
        text = f"Marriage Anniversary for {first_name} {last_name} and {user_profile.fullname()}"
        marriage_event = Event(profile_id=user_profile.profile_id,member_id=member_profile.member_id,event_type='Marriage_Anniversary',event_date=marriage_date,event_text=text)
        db.session.add(marriage_event)
    db.session.commit()
    return redirect("/member")
    


@app.route('/events')
def show_events():
#     """Show events."""

    userid = session.get("user_id")
    app.logger.info(userid)
    if userid is not None:
        events = db.session.query(Event).join(Profile)\
                    .filter(Profile.user_id == userid)\
                    .filter(Profile.profile_id == Event.profile_id)\
                    .order_by(extract('month', Event.event_date)).all()
        app.logger.info(events)
        return render_template("events.html",events=events)

@app.route('/events', methods=['POST'])
def add_event():
    
    event_type = request.form.get("event_type")
    event_text = request.form.get("event_text")
    event_date_str = request.form.get("event_date")
    event_date = datetime.strptime(event_date_str,'%Y-%m-%d')
    event_location = request.form.get("event_location")
    user_id = session["user_id"]
    profile = Profile.query.filter_by(user_id=user_id).first()
    db_event = Event(profile_id=profile.profile_id,event_type=event_type,event_date=event_date,event_text=event_text)
    db.session.add(db_event)
    db.session.commit()
    return redirect("/homepage")

@app.route('/photos')
def add_photos():
    """add photos"""

    return render_template("photos.html")

@app.route('/photos', methods=['POST'])
def add_album_process():
    """add album"""
    album_name = request.form.get("Albumname")
    image = request.form.get("Photolink")
    user_id = session["user_id"]
    
    profile = Profile.query.filter_by(user_id=user_id).first()
    new_album = Image(album_name=album_name, image=image, profile_id=profile.profile_id, image_type="photo")
    db.session.add(new_album)
    db.session.commit()

    return redirect("/photos")

@app.route('/viewphotos')
def view_photos():
    """view uploaded pictures"""

    userid = session.get("user_id")
    app.logger.info(userid)
    if userid is not None:
        images = db.session.query(Image).join(Profile).filter(Profile.user_id==userid,Image.image_type=="photo").all()
        app.logger.info(images)
        return render_template("viewphotos.html",images=images)


@app.route('/videos')
def upload_videos():
    """Add Video link"""

    return render_template("videos.html")

@app.route('/videos', methods=['POST'])
def add_video_process():
    """add video link"""
    album_name = request.form.get("Videoname")
    image = request.form.get("Videolink")
    profile = get_profile()
    new_video = Image(album_name=album_name, image=image, profile_id=profile.profile_id, image_type="video")
    db.session.add(new_video)
    db.session.commit()

    return redirect("/videos")



@app.route('/viewvideos')
def view_videos():
    """view uploaded videos"""

    userid = session.get("user_id")
    app.logger.info(userid)
    if userid is not None:
        images = db.session.query(Image).join(Profile).filter(Profile.user_id==userid,Image.image_type=="video").all()
        app.logger.info(images)
        return render_template("viewvideos.html",videos=images)

@app.route('/calendar')
def calendar_event():
    """ View and update calendar for events"""

    return render_template("calendar.html")



@app.route('/logout')
def logout():
    """Log out."""
    if session["user_id"] is not None:
        del session["user_id"]
    return redirect("/")


def latest_events():
    """Get latest 3 events."""

    userid = session.get("user_id")
    if userid is not None:
        events = db.session.query(Event).join(Profile)\
                    .filter(Profile.user_id == userid)\
                    .filter(Profile.profile_id == Event.profile_id)\
                    .filter(extract('month', Event.event_date) >= datetime.today().month)\
                    .order_by(extract('month', Event.event_date)).limit(3).all()
        app.logger.info(events)
        return events
    else:
        return None


    

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = False

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0")