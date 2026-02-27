from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/resumes'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "home"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------- MODELS ---------------- #

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    skills = db.Column(db.JSON)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer)
    project_id = db.Column(db.Integer)
    score = db.Column(db.Float)
    feedback = db.Column(db.String(300))

# ---------------- LOGIN MANAGER ---------------- #

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- HOME ---------------- #

@app.route('/')
def home():
    return render_template("login.html")

# ---------------- SIGNUP ---------------- #

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            role=request.form['role']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template("signup.html")

# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['POST'])
def login():
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]

    user = User.query.filter_by(
        email=email,
        password=password,
        role=role
    ).first()

    if user:
        login_user(user)

        if user.role == "admin":
            return redirect('/admin_dashboard')
        elif user.role == "company":
            return redirect('/company_dashboard')
        else:
            return redirect('/candidate_dashboard')

    return redirect('/')

# ---------------- LOGOUT ---------------- #

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# ---------------- ADMIN DASHBOARD ---------------- #

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect('/')
    projects = Project.query.all()
    return render_template("admin_dashboard.html", projects=projects)

# ---------------- COMPANY DASHBOARD ---------------- #

@app.route('/company_dashboard')
@login_required
def company_dashboard():
    if current_user.role != "company":
        return redirect('/')
    projects = Project.query.all()
    return render_template("company_dashboard.html", projects=projects)

# ---------------- CANDIDATE DASHBOARD ---------------- #

@app.route('/candidate_dashboard')
@login_required
def candidate_dashboard():
    if current_user.role != "candidate":
        return redirect('/')
    projects = Project.query.all()
    return render_template("dashboard.html", projects=projects)

# ---------------- CREATE PROJECT ---------------- #

@app.route('/create_project', methods=['GET','POST'])
@login_required
def create_project():

    if current_user.role not in ["admin", "company"]:
        return redirect('/')

    if request.method == 'POST':
        skills = request.form.getlist("skill_name")
        weights = request.form.getlist("skill_weight")

        skill_dict = {}

        for i in range(len(skills)):
            if skills[i] and weights[i]:
                skill_dict[skills[i]] = int(weights[i])

        project = Project(
            name=request.form['project_name'],
            skills=skill_dict
        )

        db.session.add(project)
        db.session.commit()

        return redirect('/admin_dashboard' if current_user.role=="admin" else '/company_dashboard')

    return render_template("create_project.html")

# ---------------- EDIT PROJECT ---------------- #

@app.route('/edit_project/<int:id>', methods=['GET','POST'])
@login_required
def edit_project(id):

    if current_user.role not in ["admin", "company"]:
        return redirect('/')

    project = Project.query.get_or_404(id)

    if request.method == 'POST':

        skills = request.form.getlist("skill_name")
        weights = request.form.getlist("skill_weight")

        skill_dict = {}

        for i in range(len(skills)):
            if skills[i] and weights[i]:
                skill_dict[skills[i]] = int(weights[i])

        project.name = request.form['project_name']
        project.skills = skill_dict

        db.session.commit()

        return redirect('/admin_dashboard' if current_user.role=="admin" else '/company_dashboard')

    return render_template("edit_project.html", project=project)

# ---------------- SKILL TEST + MATCH ENGINE ---------------- #

@app.route('/skill_test/<int:id>', methods=['GET','POST'])
@login_required
def skill_test(id):

    if current_user.role != "candidate":
        return redirect('/')

    project = Project.query.get_or_404(id)

    if request.method == 'POST':

        total_score = 0
        feedback_list = []

        for skill, weight in project.skills.items():

            self_rating = int(request.form.get(f"{skill}_self", 0))
            test_score = int(request.form.get(f"{skill}_test", 0))

            weighted_score = (test_score / 10) * weight
            total_score += weighted_score

            if test_score < 5:
                feedback_list.append(f"{skill} needs improvement")
            elif test_score < self_rating:
                feedback_list.append(f"{skill} performance below confidence")

        percentage = round(total_score, 2)

        feedback_text = ", ".join(feedback_list) if feedback_list else "Excellent Match"

        result = Result(
            candidate_id=current_user.id,
            project_id=id,
            score=percentage,
            feedback=feedback_text
        )

        db.session.add(result)
        db.session.commit()

        return redirect(url_for('results', id=id))

    return render_template("skill_test.html", project=project)

# ---------------- RESULTS (RANKING) ---------------- #

@app.route('/results/<int:id>')
@login_required
def results(id):

    results = Result.query.filter_by(project_id=id)\
                .order_by(Result.score.desc()).all()

    return render_template("results.html", results=results)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
