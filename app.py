from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
import calendar
from werkzeug.utils import secure_filename
from flask import send_from_directory


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey' # Needed for flash messages
db = SQLAlchemy(app)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship to versions
    versions = db.relationship('ProjectVersion', backref='project', lazy=True, cascade="all, delete-orphan")
    
    # Custom fields can be global to the project or per version? 
    # Usually custom fields are project-level metadata, but user said "diff in fields".
    # Let's keep custom fields on Project for now to avoid over-complication, 
    # or move them to Version if they change often. 
    # Given the request "see differences in fields", let's put them on Version or keep them simple.
    # For now, I'll keep CustomField linked to Project, but maybe we need to version them too?
    # Let's stick to the requested fields for versioning first.
    
    @property
    def latest_version(self):
        return ProjectVersion.query.filter_by(project_id=self.id).order_by(ProjectVersion.created_at.desc()).first()

    # Proxy properties to the latest version for backward compatibility in templates
    @property
    def status(self): return self.latest_version.status if self.latest_version else 'Not started'
    @property
    def progress(self): return self.latest_version.progress if self.latest_version else 0
    @property
    def deadline(self): return self.latest_version.deadline if self.latest_version else None
    @property
    def deadline_str(self): return self.latest_version.deadline_str if self.latest_version else "Non définie"
    @property
    def current_phase(self): return self.latest_version.phase if self.latest_version else 'Intake'
    @property
    def team(self): return self.latest_version.team if self.latest_version else []
    @property
    def description(self): return self.latest_version.description if self.latest_version else ""
    
    # Time proxy
    @property
    def theoretical_end_date(self): return self.latest_version.theoretical_end_date if self.latest_version else None

class ProjectVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    version_number = db.Column(db.String(20), nullable=False) # e.g. V1.1.0
    created_at = db.Column(db.DateTime, default=datetime.now)
    parent_id = db.Column(db.Integer, db.ForeignKey('project_version.id'), nullable=True)
    
    # Core Fields
    phase = db.Column(db.String(50)) # Intake, Qualification, ...
    status = db.Column(db.String(50)) # Done, Stopped, ...
    app_status = db.Column(db.String(50)) # Working, Not Working, ...
    integration_level = db.Column(db.String(50)) # Local, Prod, ...
    hosting = db.Column(db.String(50)) # Cloud, Services
    accessibility = db.Column(db.String(50)) # Online, Offline
    
    # New Fields
    cost = db.Column(db.Float, default=0.0)
    cost_type = db.Column(db.String(20), default='Monthly') # Monthly, Annual
    objective = db.Column(db.Text, nullable=True)
    target_audience = db.Column(db.Text, nullable=True)
    features = db.Column(db.Text, nullable=True)
    whats_new = db.Column(db.Text, nullable=True)
    
    # Time Management
    start_date = db.Column(db.Date, nullable=True)
    duration_days = db.Column(db.Integer, default=0)
    pause_start = db.Column(db.Date, nullable=True)
    pause_end = db.Column(db.Date, nullable=True)
    
    # Future Upgrade / Planning Fields
    request_description = db.Column(db.Text, nullable=True) # New: Description of the request
    requester = db.Column(db.String(100), nullable=True) # New: Who requested it
    user_request_type = db.Column(db.String(50), nullable=True) # Add feature, Modify...
    tech_request_type = db.Column(db.String(50), nullable=True) # Refactor, Migration...
    planned_improvement = db.Column(db.String(20), default='Not decided') # Yes, No, Not decided
    improvement_type = db.Column(db.String(20), default='Not decided') # Patch, Minor, Major
    difficulty_level = db.Column(db.String(20), default='Not decided') # Easy, Medium, Hard
    priority_level = db.Column(db.String(20), default='Medium') # Low, Medium, High, Urgent

    # Legacy/Standard Fields
    progress = db.Column(db.Integer, default=0)
    deadline = db.Column(db.Date)
    team_members = db.Column(db.String(100))
    budget_consumed = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    
    children = db.relationship('ProjectVersion', backref=db.backref('parent', remote_side=[id]))

    @property
    def theoretical_end_date(self):
        if not self.start_date or not self.duration_days:
            return None
            
        current = self.start_date
        needed = self.duration_days
        
        # Safety limit
        max_days = 365 * 5
        count = 0
        
        while needed > 0 and count < max_days:
            is_weekend = current.weekday() >= 5
            is_pause = False
            if self.pause_start and self.pause_end:
                if self.pause_start <= current <= self.pause_end:
                    is_pause = True
            
            if not is_weekend and not is_pause:
                needed -= 1
            
            if needed > 0:
                current += timedelta(days=1)
            count += 1
                
        return current

    @property
    def team(self):
        if self.team_members:
            # Return list of strings (names or IDs)
            return [x.strip() for x in self.team_members.split(',')]
        return []
    
    @property
    def deadline_str(self):
        if self.deadline:
            return self.deadline.strftime('%d %b %Y')
        return "Non définie"
    
    @property
    def theoretical_end_date_str(self):
        if self.theoretical_end_date:
            return self.theoretical_end_date.strftime('%d %b %Y')
        return "Non calculée"

class CustomField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(200))
    
    project = db.relationship('Project', backref=db.backref('custom_fields', lazy=True, cascade="all, delete-orphan"))

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    
    project = db.relationship('Project', backref=db.backref('documents', lazy=True, cascade="all, delete-orphan"))

class ContextRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    version_id = db.Column(db.Integer, db.ForeignKey('project_version.id'), nullable=False)
    requester = db.Column(db.String(100))
    requester_role = db.Column(db.String(50))  # New: Client, Manager, Developer, etc.
    description = db.Column(db.Text)
    
    # Request types (comma-separated for multi-select)
    user_request_type = db.Column(db.String(200))
    tech_request_type = db.Column(db.String(200))
    
    # Planning fields
    planned_improvement = db.Column(db.String(20), default='Not decided')
    improvement_type = db.Column(db.String(20), default='Not decided')
    
    # Assessment fields
    difficulty_level = db.Column(db.String(20), default='Not decided')
    priority_level = db.Column(db.String(20), default='Medium')
    
    # Approval status
    approved = db.Column(db.String(20), default='En attente')  # En attente, Approuvé, Rejeté
    
    version = db.relationship('ProjectVersion', backref=db.backref('requests', lazy=True, cascade="all, delete-orphan"))


def get_calendar_data():
    now = datetime.now()
    year = now.year
    month = now.month
    
    # French month names
    months_fr = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    
    cal = calendar.monthcalendar(year, month)
    
    return {
        'year': year,
        'month': month,
        'month_name': months_fr[month],
        'calendar_matrix': cal,
        'today': now.day
    }

def init_db():
    with app.app_context():
        db.create_all()
        if Project.query.count() == 0:
            # Seed data
            now = datetime.now()
            
            p1 = Project(name='Refonte Site Web', category='Développement Web', created_at=now)
            db.session.add(p1)
            db.session.commit()
            
            v1 = ProjectVersion(
                project_id=p1.id,
                version_number='V1.0.0',
                phase='Build',
                status='In progress',
                app_status='Building',
                integration_level='Local',
                hosting='Cloud',
                accessibility='Offline',
                progress=65,
                deadline=now + timedelta(days=45),
                team_members='1,2,3',
                description='Refonte complète du frontend.',
                cost=1500.0,
                cost_type='Monthly',
                objective='Moderniser l\'interface utilisateur',
                target_audience='Clients existants',
                features='Nouvelle page d\'accueil, Dashboard interactif',
                whats_new='Initial release',
                start_date=now.date(),
                duration_days=45
            )
            db.session.add(v1)
            
            p2 = Project(name='Migration Cloud', category='Infrastructure', created_at=now)
            db.session.add(p2)
            db.session.commit()
            
            v2 = ProjectVersion(
                project_id=p2.id,
                version_number='V0.1.0',
                phase='Planning',
                status='Not started',
                app_status='Not Working',
                integration_level='Incoming',
                hosting='Services',
                accessibility='Offline',
                progress=15,
                deadline=now + timedelta(days=90),
                team_members='4,5',
                description='Planification de la migration.',
                cost=5000.0,
                cost_type='Annual',
                objective='Réduire les coûts d\'infrastructure',
                target_audience='Équipe IT',
                features='Migration AWS, Dockerisation',
                whats_new='Initial planning',
                start_date=now.date() + timedelta(days=10),
                duration_days=60
            )
            db.session.add(v2)
            
            db.session.commit()

@app.route('/')
def dashboard():
    # Calendar Navigation
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    now = datetime.now()
    if not year: year = now.year
    if not month: month = now.month
    
    # Adjust month if out of bounds (though calendar module handles it, navigation logic needs it)
    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1
        
    projects = Project.query.all()
    
    # Calculate stats based on latest versions
    total_projects = len(projects)
    active_projects = 0
    completed_projects = 0
    overdue_projects = 0
    total_budget = 0
    total_cost = 0
    
    # Data for Chart
    status_counts = {
        'En cours': 0,
        'Terminé': 0,
        'En attente': 0,
        'Autre': 0
    }
    
    for p in projects:
        v = p.latest_version
        if v:
            if v.status in ['In progress', 'Review']:
                active_projects += 1
                status_counts['En cours'] += 1
            elif v.status == 'Done':
                completed_projects += 1
                status_counts['Terminé'] += 1
            elif v.status == 'Not started':
                status_counts['En attente'] += 1
            else:
                status_counts['Autre'] += 1
                
            if v.status not in ['Done', 'Stopped', 'Gel'] and v.deadline and v.deadline < datetime.now().date():
                overdue_projects += 1
            total_budget += v.budget_consumed
            total_cost += v.cost

    avg_budget = int(total_budget / total_projects) if total_projects > 0 else 0

    stats = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'overdue_projects': overdue_projects,
        'budget_consumed': avg_budget,
        'total_cost': total_cost
    }
    
    # Calendar Data (Removed for Dashboard, moved to Gantt page)
    # Use the requested year/month for header display only if needed, but we removed the widget.
    # We still need 'calendar' object for the "Welcome" message (today's date)
    
    months_fr = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    
    cal_data = {
        'year': now.year,
        'month': now.month,
        'month_name': months_fr[now.month],
        'today': now.day
    }
            
    # Get upcoming deliverables (Only Review and Done status)
    upcoming_deliverables = []
    for p in projects:
        v = p.latest_version
        if v:
            # User request: Only display if current status is Review or Done
            if v.status in ['Review', 'Done']:
                upcoming_deliverables.append(p)
    
    # Sort by deadline (Review projects without deadline go to end or handle as needed)
    # Prioritize projects in 'Review' status, then by deadline
    def sort_key(p):
        v = p.latest_version
        # Prioritize Review (0) over Done (1)
        status_priority = 0 if v.status == 'Review' else 1
        deadline = v.deadline if v.deadline else datetime.max.date()
        return (status_priority, deadline)

    upcoming_deliverables.sort(key=sort_key)
    # Increase limit to ensure all Review projects are likely seen, or at least more of them
    upcoming_deliverables = upcoming_deliverables[:10]
    
    response = make_response(render_template('dashboard.html', stats=stats, projects=projects, 
                           calendar=cal_data,
                           upcoming_deliverables=upcoming_deliverables,
                           status_counts=status_counts))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/projects')
def projects_list():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects, now=datetime.now().date())

@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        
        # Version fields
        version_number = request.form.get('version_number', 'V1.0.0')
        phase = request.form.get('phase')
        status = request.form.get('status')
        app_status = request.form.get('app_status')
        integration_level = request.form.get('integration_level')
        hosting = request.form.get('hosting')
        accessibility = request.form.get('accessibility')
        description = request.form.get('description')
        progress = int(request.form.get('progress', 0))
        
        # New fields
        cost = float(request.form.get('cost', 0.0))
        cost_type = request.form.get('cost_type', 'Monthly')
        objective = request.form.get('objective')
        target_audience = request.form.get('target_audience')
        features = request.form.get('features')
        whats_new = request.form.get('whats_new')
        
        # Time Management
        start_date_str = request.form.get('start_date')
        duration_days_str = request.form.get('duration_days')
        pause_start_str = request.form.get('pause_start')
        pause_end_str = request.form.get('pause_end')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        duration_days = int(duration_days_str) if duration_days_str else 0
        pause_start = datetime.strptime(pause_start_str, '%Y-%m-%d').date() if pause_start_str else None
        pause_end = datetime.strptime(pause_end_str, '%Y-%m-%d').date() if pause_end_str else None
        
        deadline_str = request.form.get('deadline')
        deadline = None
        if deadline_str:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            
        new_project = Project(name=name, category=category)
        db.session.add(new_project)
        db.session.commit()
        
        new_version = ProjectVersion(
            project_id=new_project.id,
            version_number=version_number,
            phase=phase,
            status=status,
            app_status=app_status,
            integration_level=integration_level,
            hosting=hosting,
            accessibility=accessibility,
            description=description,
            progress=progress,
            deadline=deadline,
            cost=cost,
            cost_type=cost_type,
            objective=objective,
            target_audience=target_audience,
            features=features,
            whats_new=whats_new,
            start_date=start_date,
            duration_days=duration_days,
            pause_start=pause_start,
            pause_end=pause_end
        )
        db.session.add(new_version)
        db.session.commit()
        
        # Handle initial custom fields
        custom_field_names = request.form.getlist('custom_field_name[]')
        custom_field_values = request.form.getlist('custom_field_value[]')
        
        for name, value in zip(custom_field_names, custom_field_values):
            if name and value:
                cf = CustomField(project_id=new_project.id, name=name, value=value)
                db.session.add(cf)
        
        db.session.commit()
        
        flash('Projet créé avec succès!', 'success')
        return redirect(url_for('projects_list'))
        
    return render_template('project_form.html', project=None)

@app.route('/projects/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    # Get all versions ordered by date
    versions = ProjectVersion.query.filter_by(project_id=id).order_by(ProjectVersion.created_at.desc()).all()
    
    version_id = request.args.get('version_id', type=int)
    selected_version = None
    
    if version_id:
        selected_version = ProjectVersion.query.get(version_id)
        # Ensure it belongs to this project
        if selected_version and selected_version.project_id != id:
            selected_version = None
            
    if not selected_version and versions:
        selected_version = versions[0]
        
    # Calculate suggested next version based on the latest version's planning
    suggested_version = "V1.0.0"
    if versions:
        latest = versions[0]
        suggested_version = calculate_next_version(latest.version_number, latest.improvement_type)
        
    return render_template('project_detail.html', project=project, versions=versions, selected_version=selected_version, suggested_version=suggested_version)

def calculate_next_version(current_version_str, improvement_type):
    if not current_version_str.startswith('V'):
        return current_version_str
    
    try:
        # Remove 'V' and split
        parts = [int(x) for x in current_version_str[1:].split('.')]
        if len(parts) != 3:
            return current_version_str
            
        major, minor, patch = parts
        
        if improvement_type == 'Major':
            major += 1
            minor = 0
            patch = 0
        elif improvement_type == 'Minor':
            minor += 1
            patch = 0
        elif improvement_type == 'Patch':
            patch += 1
            
        return f"V{major}.{minor}.{patch}"
    except:
        return current_version_str

@app.route('/requests')
def requests_list():
    # Filter params
    project_id_filter = request.args.get('project_id', type=int)
    sort_filter = request.args.get('sort', 'newest')
    difficulty_filter = request.args.get('difficulty')
    priority_filter = request.args.get('priority')
    approved_filter = request.args.get('approved')
    type_filter = request.args.get('type')
    version_id_filter = request.args.get('version_id', type=int)
    role_filter = request.args.get('role')

    # Base query
    query = db.session.query(ContextRequest, ProjectVersion, Project).join(
        ProjectVersion, ContextRequest.version_id == ProjectVersion.id
    ).join(
        Project, ProjectVersion.project_id == Project.id
    )

    # Apply filters
    if project_id_filter:
        query = query.filter(Project.id == project_id_filter)
        filter_project = Project.query.get(project_id_filter)
    else:
        filter_project = None

    if version_id_filter:
        query = query.filter(ProjectVersion.id == version_id_filter)
    
    if difficulty_filter and difficulty_filter != 'all':
        query = query.filter(ContextRequest.difficulty_level == difficulty_filter)
    
    if priority_filter and priority_filter != 'all':
        query = query.filter(ContextRequest.priority_level == priority_filter)
        
    if approved_filter and approved_filter != 'all':
        query = query.filter(ContextRequest.approved == approved_filter)
        
    if role_filter and role_filter != 'all':
        query = query.filter(ContextRequest.requester_role == role_filter)

    if type_filter and type_filter != 'all':
        # Filter in both type fields (contains string)
        query = query.filter(db.or_(
            ContextRequest.user_request_type.contains(type_filter),
            ContextRequest.tech_request_type.contains(type_filter)
        ))

    # Apply sorting
    if sort_filter == 'oldest':
        query = query.order_by(ContextRequest.created_at.asc())
    else: # newest
        query = query.order_by(ContextRequest.created_at.desc())

    requests_query = query.all()
    
    # Calculate statistics (based on filtered results or total? Usually total context is better for global stats, 
    # but the request implies filtering the view. Let's keep stats on the filtered view for relevance 
    # OR keep stats global? The existing code calculated stats on the query result.
    # We will stick to calculating stats on the RESULT set.)
    total_requests = len(requests_query)
    
    # Priority stats
    priority_stats = {'Low': 0, 'Medium': 0, 'High': 0, 'Urgent': 0}
    difficulty_stats = {'Easy': 0, 'Medium': 0, 'Hard': 0, 'Not decided': 0}
    improvement_stats = {'Yes': 0, 'No': 0, 'Not decided': 0}
    approval_stats = {'En attente': 0, 'Approuvé': 0, 'Rejeté': 0}
    
    for req, version, project in requests_query:
        if req.priority_level in priority_stats:
            priority_stats[req.priority_level] += 1
        if req.difficulty_level in difficulty_stats:
            difficulty_stats[req.difficulty_level] += 1
        if req.planned_improvement in improvement_stats:
            improvement_stats[req.planned_improvement] += 1
        if req.approved in approval_stats:
            approval_stats[req.approved] += 1
    
    # Get lists for dropdowns
    all_projects = Project.query.all()
    all_versions = ProjectVersion.query.all() # Optimization: Filter by project if project selected?
    if project_id_filter:
        all_versions = ProjectVersion.query.filter_by(project_id=project_id_filter).all()

    return render_template('requests.html',
                         requests_data=requests_query,
                         total_requests=total_requests,
                         priority_stats=priority_stats,
                         difficulty_stats=difficulty_stats,
                         improvement_stats=improvement_stats,
                         approval_stats=approval_stats,
                         all_projects=all_projects,
                         all_versions=all_versions,
                         filter_project=filter_project,
                         filters={
                             'sort': sort_filter,
                             'difficulty': difficulty_filter,
                             'priority': priority_filter,
                             'approved': approved_filter,
                             'type': type_filter,
                             'version_id': version_id_filter,
                             'role': role_filter,
                             'project_id': project_id_filter
                         })

@app.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    project = Project.query.get_or_404(id)
    latest_version = project.latest_version
    
    if request.method == 'POST':
        # Check if we are creating a new version or updating the current one
        # For simplicity, let's say "Edit" updates the current latest version details
        # UNLESS the user explicitly changes the version number, then we fork?
        # Let's keep it simple: Edit updates the current latest version.
        # We will add a separate "New Version" route later if needed, or handle it here.
        
        project.name = request.form.get('name')
        project.category = request.form.get('category')
        
        # Update latest version fields
        latest_version.version_number = request.form.get('version_number')
        latest_version.phase = request.form.get('phase')
        latest_version.status = request.form.get('status')
        latest_version.app_status = request.form.get('app_status')
        latest_version.integration_level = request.form.get('integration_level')
        latest_version.hosting = request.form.get('hosting')
        latest_version.accessibility = request.form.get('accessibility')
        latest_version.progress = int(request.form.get('progress', 0))
        latest_version.description = request.form.get('description')
        
        # Update new fields
        latest_version.cost = float(request.form.get('cost', 0.0))
        latest_version.cost_type = request.form.get('cost_type')
        latest_version.objective = request.form.get('objective')
        latest_version.target_audience = request.form.get('target_audience')
        latest_version.features = request.form.get('features')
        latest_version.whats_new = request.form.get('whats_new')
        
        # Time Management
        start_date_str = request.form.get('start_date')
        duration_days_str = request.form.get('duration_days')
        pause_start_str = request.form.get('pause_start')
        pause_end_str = request.form.get('pause_end')
        
        latest_version.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        latest_version.duration_days = int(duration_days_str) if duration_days_str else 0
        latest_version.pause_start = datetime.strptime(pause_start_str, '%Y-%m-%d').date() if pause_start_str else None
        latest_version.pause_end = datetime.strptime(pause_end_str, '%Y-%m-%d').date() if pause_end_str else None
        
        deadline_str = request.form.get('deadline')
        if deadline_str:
            latest_version.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            
        db.session.commit()
        flash('Projet mis à jour!', 'success')
        return redirect(url_for('project_detail', id=project.id))
        
    return render_template('project_form.html', project=project, version=latest_version)

@app.route('/projects/<int:id>/new_version', methods=['POST'])
def new_project_version(id):
    project = Project.query.get_or_404(id)
    latest = project.latest_version
    
    # Create a copy of the latest version as a base
    new_v = ProjectVersion(
        project_id=project.id,
        version_number=request.form.get('version_number'),
        phase=latest.phase,
        status=latest.status,
        app_status=latest.app_status,
        integration_level=latest.integration_level,
        hosting=latest.hosting,
        accessibility=latest.accessibility,
        progress=latest.progress,
        deadline=latest.deadline,
        description=latest.description,
        team_members=latest.team_members,
        parent_id=latest.id,
        cost=latest.cost,
        cost_type=latest.cost_type,
        objective=latest.objective,
        target_audience=latest.target_audience,
        features=latest.features,
        whats_new="", # Reset what's new for new version
        start_date=latest.start_date,
        duration_days=latest.duration_days,
        pause_start=latest.pause_start,
        pause_end=latest.pause_end,
        # Copy future planning fields? Maybe reset them? 
        # Usually planning fields are for the *next* version, so if we create a new version, 
        # these might become the "current" state or be reset.
        # Let's reset them as they apply to the specific version planning.
        user_request_type=latest.user_request_type, # Copy request type? Maybe
        tech_request_type=latest.tech_request_type,
        request_description=latest.request_description,
        requester=latest.requester,
        planned_improvement='Not decided',
        improvement_type='Not decided',
        difficulty_level='Not decided',
        priority_level='Medium'
    )
    
    db.session.add(new_v)
    db.session.commit()
    flash('Nouvelle version créée!', 'success')
    return redirect(url_for('edit_project', id=project.id))

@app.route('/projects/<int:id>/version/<int:version_id>/delete', methods=['POST'])
def delete_project_version(id, version_id):
    project = Project.query.get_or_404(id)
    version = ProjectVersion.query.get_or_404(version_id)
    
    # Ensure version belongs to project
    if version.project_id != project.id:
        return {'success': False, 'message': 'Version mismatch'}, 400
        
    # Prevent deleting the only version? Or allow it and delete project?
    # Let's just delete the version. If it's the last one, project remains but empty?
    # Or maybe we shouldn't allow deleting the last version.
    if ProjectVersion.query.filter_by(project_id=id).count() <= 1:
        flash('Impossible de supprimer la dernière version. Supprimez le projet entier.', 'error')
        return redirect(url_for('project_detail', id=id))

    db.session.delete(version)
    db.session.commit()
    flash('Version supprimée.', 'success')
    return redirect(url_for('project_detail', id=id))

@app.route('/projects/<int:id>/delete', methods=['POST'])
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Projet supprimé.', 'info')
    return redirect(url_for('projects_list'))

@app.route('/projects/<int:id>/update_status', methods=['POST'])
def update_project_status(id):
    project = Project.query.get_or_404(id)
    latest = project.latest_version
    if not latest:
        return {'success': False, 'message': 'No version found'}, 404
        
    data = request.get_json()
    new_status = data.get('status')
    
    # Validate against the new status list
    valid_statuses = ['Done', 'Stopped', 'In progress', 'Not started', 'Review', 'Gel']
    
    if new_status in valid_statuses:
        latest.status = new_status
        db.session.commit()
        return {'success': True, 'message': 'Statut mis à jour'}
    
    return {'success': False, 'message': 'Statut invalide'}, 400

@app.route('/projects/<int:id>/update_phase', methods=['POST'])
def update_project_phase(id):
    project = Project.query.get_or_404(id)
    latest = project.latest_version
    if not latest:
        return {'success': False, 'message': 'No version found'}, 404
        
    data = request.get_json()
    new_phase = data.get('phase')
    
    # Validate against known phases
    valid_phases = ['Intake', 'Qualification', 'Scoping', 'Planning', 'Build', 'Test & QA', 'Staging', 'Release', 'Operate', 'Retro', 'Closed']
    
    if new_phase in valid_phases:
        latest.phase = new_phase
        db.session.commit()
        return {'success': True, 'message': 'Phase mise à jour'}
    
    return {'success': False, 'message': 'Phase invalide'}, 400

@app.route('/projects/<int:id>/add_custom_field', methods=['POST'])
def add_custom_field(id):
    project = Project.query.get_or_404(id)
    name = request.form.get('name')
    value = request.form.get('value')
    
    if name and value:
        cf = CustomField(project_id=project.id, name=name, value=value)
        db.session.add(cf)
        db.session.commit()
        flash('Champ personnalisé ajouté.', 'success')
    
    return redirect(url_for('project_detail', id=project.id))

@app.route('/custom_field/<int:id>/delete', methods=['POST'])
def delete_custom_field(id):
    cf = CustomField.query.get_or_404(id)
    project_id = cf.project_id
    db.session.delete(cf)
    db.session.commit()
    flash('Champ supprimé.', 'info')
    return redirect(url_for('project_detail', id=project_id))

@app.route('/projects/<int:id>/upload_document', methods=['POST'])
def upload_document(id):
    project = Project.query.get_or_404(id)
    
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('project_detail', id=id))
        
    file = request.files['file']
    name = request.form.get('name') or file.filename
    
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('project_detail', id=id))
        
    if file:
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid collisions
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        upload_folder = os.path.join(app.root_path, 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file.save(os.path.join(upload_folder, filename))
        
        doc = Document(project_id=project.id, name=name, filename=filename)
        db.session.add(doc)
        db.session.commit()
        
        flash('Document ajouté avec succès', 'success')
        
    return redirect(url_for('project_detail', id=id))

@app.route('/documents/<int:id>/view')
def view_document(id):
    doc = Document.query.get_or_404(id)
    upload_folder = os.path.join(app.root_path, 'uploads')
    return send_from_directory(upload_folder, doc.filename)

@app.route('/documents/<int:id>/delete', methods=['POST'])
def delete_document(id):
    doc = Document.query.get_or_404(id)
    project_id = doc.project_id
    
    # Remove file from disk
    upload_folder = os.path.join(app.root_path, 'uploads')
    file_path = os.path.join(upload_folder, doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    db.session.delete(doc)
    db.session.commit()
    
    flash('Document supprimé', 'success')
    return redirect(url_for('project_detail', id=project_id))

# API to get project versions
@app.route('/api/projects/<int:project_id>/versions')
def get_project_versions(project_id):
    versions = ProjectVersion.query.filter_by(project_id=project_id).order_by(ProjectVersion.created_at.desc()).all()
    return jsonify([{
        'id': v.id,
        'version_number': v.version_number
    } for v in versions])

# Context Request API routes
@app.route('/api/version/<int:version_id>/context_requests', methods=['POST'])
def add_context_request(version_id):
    version = ProjectVersion.query.get_or_404(version_id)
    data = request.json
    
    context_request = ContextRequest(
        version_id=version_id,
        requester=data.get('requester', ''),
        requester_role=data.get('requester_role', ''),
        description=data.get('description', ''),
        user_request_type=data.get('user_request_type', ''),
        tech_request_type=data.get('tech_request_type', ''),
        planned_improvement=data.get('planned_improvement', 'Not decided'),
        improvement_type=data.get('improvement_type', 'Not decided'),
        difficulty_level=data.get('difficulty_level', 'Not decided'),
        priority_level=data.get('priority_level', 'Medium'),
        approved=data.get('approved', 'En attente')
    )
    
    db.session.add(context_request)
    db.session.commit()
    
    return jsonify({'success': True, 'id': context_request.id})

@app.route('/api/context_request/<int:request_id>', methods=['GET'])
def get_context_request(request_id):
    context_request = ContextRequest.query.get_or_404(request_id)
    return jsonify({
        'id': context_request.id,
        'requester': context_request.requester,
        'requester_role': context_request.requester_role,
        'description': context_request.description,
        'user_request_type': context_request.user_request_type,
        'tech_request_type': context_request.tech_request_type,
        'planned_improvement': context_request.planned_improvement,
        'improvement_type': context_request.improvement_type,
        'difficulty_level': context_request.difficulty_level,
        'priority_level': context_request.priority_level,
        'approved': context_request.approved,
        'created_at': context_request.created_at.isoformat() if context_request.created_at else None
    })

@app.route('/api/context_request/<int:request_id>', methods=['PUT'])
def update_context_request(request_id):
    context_request = ContextRequest.query.get_or_404(request_id)
    data = request.json
    
    # Check if it's a single field update or full object update
    if 'field' in data and 'value' in data:
        # Single field update (for inline editing)
        field = data.get('field')
        value = data.get('value')
        
        if field == 'requester':
            context_request.requester = value
        elif field == 'requester_role':
            context_request.requester_role = value
        elif field == 'description':
            context_request.description = value
        elif field == 'user_request_type':
            context_request.user_request_type = value
        elif field == 'tech_request_type':
            context_request.tech_request_type = value
        elif field == 'planned_improvement':
            context_request.planned_improvement = value
        elif field == 'improvement_type':
            context_request.improvement_type = value
        elif field == 'difficulty_level':
            context_request.difficulty_level = value
        elif field == 'priority_level':
            context_request.priority_level = value
        elif field == 'approved':
            context_request.approved = value
    else:
        # Full object update (from edit panel)
        context_request.requester = data.get('requester', context_request.requester)
        context_request.requester_role = data.get('requester_role', context_request.requester_role)
        context_request.description = data.get('description', context_request.description)
        context_request.user_request_type = data.get('user_request_type', context_request.user_request_type)
        context_request.tech_request_type = data.get('tech_request_type', context_request.tech_request_type)
        context_request.planned_improvement = data.get('planned_improvement', context_request.planned_improvement)
        context_request.improvement_type = data.get('improvement_type', context_request.improvement_type)
        context_request.difficulty_level = data.get('difficulty_level', context_request.difficulty_level)
        context_request.priority_level = data.get('priority_level', context_request.priority_level)
        context_request.approved = data.get('approved', context_request.approved)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/context_request/<int:request_id>', methods=['DELETE'])
def delete_context_request(request_id):
    context_request = ContextRequest.query.get_or_404(request_id)
    db.session.delete(context_request)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/version/<int:id>/update_field', methods=['POST'])
def update_version_field(id):
    version = ProjectVersion.query.get_or_404(id)
    data = request.get_json()
    field = data.get('field')
    value = data.get('value')
    
    if not field:
        return {'success': False, 'message': 'Field missing'}, 400
        
    # Allow list of editable fields
    editable_fields = [
        'phase', 'status', 'app_status', 'integration_level', 'hosting', 'accessibility',
        'description', 'objective', 'target_audience', 'features', 'whats_new',
        'cost', 'cost_type', 'progress', 'user_request_type', 'tech_request_type',
        'planned_improvement', 'improvement_type', 'difficulty_level', 'priority_level',
        'duration_days'
    ]
    
    # Date fields need special handling
    date_fields = ['deadline', 'start_date', 'pause_start', 'pause_end']
    
    if field in date_fields:
        try:
            date_val = datetime.strptime(value, '%Y-%m-%d').date() if value else None
            setattr(version, field, date_val)
        except ValueError:
            return {'success': False, 'message': 'Invalid date format'}, 400
    elif field in editable_fields:
        # Handle numeric types
        if field in ['cost']:
            try:
                value = float(value)
            except:
                value = 0.0
        elif field in ['progress', 'duration_days']:
            try:
                value = int(value)
            except:
                value = 0
                
        setattr(version, field, value)
    else:
        return {'success': False, 'message': f'Field {field} not editable'}, 400
        
    db.session.commit()
    
    # Return formatted value if needed, or just success
    return {'success': True, 'message': 'Updated'}

@app.route('/api/version/<int:id>/update_fields', methods=['POST'])
def update_version_fields_batch(id):
    version = ProjectVersion.query.get_or_404(id)
    data = request.get_json()
    updates = data.get('updates', [])
    
    if not updates:
        return {'success': False, 'message': 'No updates provided'}, 400
        
    # Allow list of editable fields
    editable_fields = [
        'phase', 'status', 'app_status', 'integration_level', 'hosting', 'accessibility',
        'description', 'objective', 'target_audience', 'features', 'whats_new',
        'cost', 'cost_type', 'progress', 'user_request_type', 'tech_request_type',
        'planned_improvement', 'improvement_type', 'difficulty_level', 'priority_level',
        'duration_days', 'deadline', 'start_date', 'pause_start', 'pause_end',
        'request_description', 'requester'
    ]
    
    date_fields = ['deadline', 'start_date', 'pause_start', 'pause_end']
    
    for update in updates:
        field = update.get('field')
        value = update.get('value')
        
        if field not in editable_fields:
            continue
            
        if field in date_fields:
            try:
                date_val = datetime.strptime(value, '%Y-%m-%d').date() if value else None
                setattr(version, field, date_val)
            except ValueError:
                pass # Skip invalid dates
        else:
            # Handle numeric types
            if field in ['cost']:
                try:
                    value = float(value)
                except:
                    value = 0.0
            elif field in ['progress', 'duration_days']:
                try:
                    value = int(value)
                except:
                    value = 0
                    
            setattr(version, field, value)
            
    db.session.commit()
    return {'success': True, 'message': 'Batch update successful'}

@app.route('/stats')
def stats_page():
    projects = Project.query.all()
    
    # Aggregations
    by_category = {}
    by_phase = {}
    by_status = {}
    cost_by_category = {}
    progress_distribution = {'0-25%': 0, '26-50%': 0, '51-75%': 0, '76-100%': 0}
    
    total_cost = 0
    total_projects = len(projects)
    active_count = 0
    
    for p in projects:
        # Category
        cat = p.category or "Non classé"
        by_category[cat] = by_category.get(cat, 0) + 1
        
        v = p.latest_version
        if v:
            # Phase
            phase = v.phase or "Non définie"
            by_phase[phase] = by_phase.get(phase, 0) + 1
            
            # Status
            status = v.status or "Non défini"
            by_status[status] = by_status.get(status, 0) + 1
            
            if status in ['In progress', 'Review', 'En cours']:
                active_count += 1
            
            # Cost
            cost = v.cost or 0
            total_cost += cost
            cost_by_category[cat] = cost_by_category.get(cat, 0) + cost
            
            # Progress
            prog = v.progress or 0
            if prog <= 25: progress_distribution['0-25%'] += 1
            elif prog <= 50: progress_distribution['26-50%'] += 1
            elif prog <= 75: progress_distribution['51-75%'] += 1
            else: progress_distribution['76-100%'] += 1

    return render_template('stats.html', 
                           by_category=by_category, 
                           by_phase=by_phase, 
                           by_status=by_status, 
                           cost_by_category=cost_by_category,
                           progress_distribution=progress_distribution,
                           total_cost=total_cost,
                           total_projects=total_projects,
                           active_count=active_count)

@app.route('/gantt')
def gantt_chart():
    projects = Project.query.all()
    tasks = []
    
    for p in projects:
        v = p.latest_version
        if not v: continue
        
        # Determine Start Date
        start = v.start_date if v.start_date else v.created_at.date()
        
        # Determine End Date
        end = v.theoretical_end_date
        if not end:
            end = v.deadline if v.deadline else (start + timedelta(days=30))
            
        # Ensure End > Start
        if end < start:
             end = max(datetime.now().date(), start + timedelta(days=1))
             
        # Determine Progress
        progress = v.progress if v.progress is not None else 0
        
        # Map status to custom class for coloring
        custom_class = 'bar-todo'
        if v.status in ['In progress', 'En cours']: custom_class = 'bar-progress'
        elif v.status == 'Review': custom_class = 'bar-review'
        elif v.status == 'Done': custom_class = 'bar-done'
        elif v.status == 'Overdue': custom_class = 'bar-overdue'

        tasks.append({
            'id': str(p.id),
            'name': p.name,
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'progress': progress,
            'custom_class': custom_class
        })
        
    return render_template('gantt.html', tasks=tasks)

if __name__ == '__main__':
    if not os.path.exists('projects.db'):
        init_db()
    app.run(debug=True)
