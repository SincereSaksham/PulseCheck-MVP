from collections import defaultdict

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Team, Mood, Activity
from forms import RegisterForm, LoginForm, TeamForm, TrackerForm, InviteForm
from collections import Counter
from datetime import timedelta, time, datetime, date
from utils import seed_mock_activities, generate_invite, creator_required

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'pulsecheck.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash("Email already exists.")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(form.password.data)
        user = User(name=form.name.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('onboarding'))
    return render_template('register.html', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            session.permanent = True
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.")
    return render_template('login.html', form=form)




@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if current_user.team_id:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        choice = request.form.get('choice')
        team_name = request.form.get('team_name')
        invite_code = request.form.get('invite_code')

        if choice == 'create':
            new_team = Team(
                name=team_name,
                invite_code=generate_invite(),
                creator_id=current_user.id
            )
            db.session.add(new_team)
            db.session.commit()
            current_user.team_id = new_team.id
            db.session.commit()
            flash(f"Team '{team_name}' created! Share your invite code: {new_team.invite_code}", "success")
            return redirect(url_for('dashboard'))

        elif choice == 'join':
            team = Team.query.filter_by(invite_code=invite_code).first()
            if team:
                current_user.team_id = team.id
                db.session.commit()
                flash(f"Joined team '{team.name}'", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid invite code!", "danger")

    return render_template('onboarding.html')





@app.route('/invite', methods=['GET', 'POST'])
@login_required
def invite():
    form = InviteForm()
    invite_code = current_user.team.invite_code

    if form.validate_on_submit():
        email = form.email.data
        # Simulate sending invite
        flash(f"Mock invite sent to {email} with team code: {invite_code}", "info")
        return redirect(url_for('invite'))

    return render_template('invite.html', form=form, invite_code=invite_code)




@app.route('/select-team', methods=['GET', 'POST'])
@login_required
def select_team():
    form = TeamForm()
    if form.validate_on_submit():
        if form.team_name.data:
            team = Team(name=form.team_name.data, creator_id=current_user.id)
            db.session.add(team)
            db.session.commit()
            current_user.team_id = team.id
        elif form.invite_code.data:
            team = Team.query.filter_by(invite_code=form.invite_code.data).first()
            if not team:
                flash("Invalid invite code.")
                return redirect(url_for('select_team'))
            current_user.team_id = team.id
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('team_select.html', form=form)






from collections import defaultdict, Counter
from datetime import datetime, timedelta, time
from flask import flash

@app.route('/dashboard')
@login_required
def dashboard():
    team = current_user.team

    if not team :
        return render_template("no_team.html")

    # Seed mock activities if none exist for team
    if not team.activities or len(team.activities) == 0:
        seed_mock_activities(team)

    # Query all activities for team, ordered by latest
    activities = Activity.query.filter_by(team_id=team.id).order_by(Activity.timestamp.desc()).all()

    now = datetime.utcnow()
    today = now.date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]  # last 7 days in order

    # Initialize counters per day
    commits_per_day = defaultdict(int)
    messages_per_day = defaultdict(int)
    blockers_per_day = defaultdict(int)
    moods_per_day = defaultdict(list)

    # Count activities per category per day
    for act in activities:
        act_date = act.timestamp.date()
        if act_date in dates:
            if act.category == "Commit":
                commits_per_day[act_date] += 1
            elif act.category == "Message":
                messages_per_day[act_date] += 1
            elif act.category == 'Blocker':
                blockers_per_day[act_date] += 1

    # Date range for mood query
    start_of_oldest = datetime.combine(dates[0], time.min)
    end_of_latest = datetime.combine(dates[-1], time.max)

    # Query moods in range for the team
    mood_entries = Mood.query.filter(
        Mood.team_id == team.id,
        Mood.timestamp >= start_of_oldest,
        Mood.timestamp <= end_of_latest
    ).all()

    for mood in mood_entries:
        mood_date = mood.timestamp.date()
        if mood_date in dates:
            moods_per_day[mood_date].append(mood.mood_value)

    # Calculate average mood per day (None if no data)
    avg_moods = []
    for d in dates:
        day_moods = moods_per_day.get(d, [])
        if day_moods:
            avg = round(sum(day_moods) / len(day_moods), 2)
        else:
            avg = None
        avg_moods.append(avg)

    # Prepare data lists for charts
    commits_data = [commits_per_day.get(d, 0) for d in dates]
    messages_data = [messages_per_day.get(d, 0) for d in dates]
    blockers_data = [blockers_per_day.get(d, 0) for d in dates]
    date_labels = [d.strftime("%m-%d") for d in dates]

    # Team members and stats for each member (last 7 days)
    team_members = User.query.filter_by(team_id=team.id).all()
    member_stats = []

    for member in team_members:
        stats = Counter()
        for act in member.activities:
            act_date = act.timestamp.date()
            if act_date in dates:
                stats[act.category] += 1

        total_activity = sum(stats.values())
        participation_score = min(round((total_activity / 20) * 100), 100)  # cap at 100%

        member_stats.append({
            "user": member,  # ← include the model object
            "name" : member.name,
            "initial": member.name[0],
            "commits": stats.get("Commit", 0),
            "messages": stats.get("Message", 0),
            "prs": stats.get("Pull Request", 0),
            "blockers": stats.get("Blocker", 0),
            "score": participation_score
        })



    # Prepare heatmap data: dict with member names as keys, values are list of activity counts per day
    heatmap_data = {}

    for member in team_members:
        daily_counts = []
        for d in dates:
            count = sum(1 for act in member.activities if act.timestamp.date() == d)
            daily_counts.append(count)
        heatmap_data[member.name] = daily_counts

    # Blocker spike alert if 3+ blockers in last 24h
    blockers_last_24h = Activity.query.filter(
        Activity.team_id == team.id,
        Activity.category == 'Blocker',
        Activity.timestamp >= now - timedelta(hours=24)
    ).count()

    if blockers_last_24h >= 3:
        flash(f"Alert: {blockers_last_24h} blockers reported in last 24 hours!", "danger")

    return render_template('dashboard.html',
                           activities=activities,
                           commits_data=commits_data,
                           messages_data=messages_data,
                           blockers_data=blockers_data,
                           date_labels=date_labels,
                           member_stats=member_stats,
                           avg_moods=avg_moods,
                           heatmap_data = heatmap_data
                          )







@app.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    form = TrackerForm()
    if form.validate_on_submit():
        # Save Blocker to Activity
        blocker = Activity(
            user_id=current_user.id,
            team_id=current_user.team_id,
            category="Blocker",
            description=form.blocker.data
        )
        db.session.add(blocker)

        # Save Mood to Mood model
        mood_entry = Mood(
            user_id=current_user.id,
            team_id=current_user.team_id,
            mood_value=int(form.mood.data),
            timestamp=datetime.utcnow()
        )
        db.session.add(mood_entry)

        db.session.commit()
        flash("Tracker submitted successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('tracker.html', form=form)





@app.route('/team-summary')
@login_required
def team_summary():
    team = current_user.team
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    # Total members
    total_members = User.query.filter_by(team_id=team.id).count()

    # Fetch all team activities in the last 7 days
    week_activities = Activity.query.filter(
        Activity.team_id == team.id,
        Activity.timestamp >= datetime.combine(dates[0], time.min),
        Activity.timestamp <= datetime.combine(dates[-1], time.max)
    ).all()

    # Count activities per day
    activity_count_by_day = defaultdict(int)
    activity_by_user = defaultdict(int)

    for act in week_activities:
        activity_count_by_day[act.timestamp.date()] += 1
        activity_by_user[act.user.name] += 1

    active_days = len([d for d in dates if activity_count_by_day[d] > 0])
    peak_day = max(activity_count_by_day.items(), key=lambda x: x[1], default=(None, 0))[0]
    if isinstance(peak_day, date):
        formatted_peak_day = peak_day.strftime('%A, %d %b')
    else:
        formatted_peak_day = "N/A"


    most_active_member = max(activity_by_user.items(), key=lambda x: x[1], default=(None, 0))[0]

    return render_template("team_summary.html",
                           total_members=total_members,
                           active_days=active_days,
                           peak_day=peak_day.strftime('%A, %d %b') if peak_day else "N/A",
                           most_active_member=most_active_member or "N/A")



@app.route('/rename_team', methods=['POST'])
@login_required
@creator_required
def rename_team():
    new_name = request.form.get('new_name')
    if new_name:
        current_user.team.name = new_name
        db.session.commit()
        flash("Team name updated successfully.", "success")
    else:
        flash("Invalid team name.", "danger")
    return redirect(url_for('dashboard'))



@app.route('/remove_member/<int:user_id>', methods=['POST'])
@login_required
@creator_required
def remove_member(user_id):
    member = User.query.get_or_404(user_id)
    team = current_user.team
    if member.team_id == team.id and member.id != team.creator_id:
        member.team_id = None
        db.session.commit()
        flash(f"Removed {member.name} from the team.", "warning")
    else:
        flash("You cannot remove this member.", "danger")
    return redirect(url_for('dashboard'))



@app.route('/join_team', methods=['POST'])
@login_required
def join_team():
    invite_code = request.form.get('invite_code')
    team = Team.query.filter_by(invite_code=invite_code).first()

    if team:
        current_user.team_id = team.id
        db.session.commit()
        flash("Successfully joined the team!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid invite code.", "danger")
        return redirect(url_for('dashboard'))







@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))




@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
