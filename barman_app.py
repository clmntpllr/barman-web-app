import json, datetime, subprocess
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin

""" Flask application factory """
def create_app():
    # Create Flask app load app.config
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    # Initialize Flask-SQLAlchemy
    db = SQLAlchemy(app)

    # Define the User data-model.
    # NB: Make sure to add flask_user UserMixin !!!
    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False, server_default='')
        email_confirmed_at = db.Column(db.DateTime())

        # User information
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        
        # Define the relationship to Role via UserRoles
        roles = db.relationship('Role', secondary='user_roles')

    # Define the Role data-model
    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # Define the UserRoles association table
    class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)

    # Create all database tables
    db.create_all()

    # Get app special conf
    appconf = app.config.get_namespace("APP_CONF_",False)

    # Create User admin with Role SuperAdmin
    if not User.query.filter(User.username == appconf["ADMIN_USERNAME"]).first():
        user = User(
            username=appconf["ADMIN_USERNAME"],
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password(appconf["ADMIN_PASSWORD"]),
        )
        user.roles.append(Role(name='SuperAdmin'))
        db.session.add(user)
        db.session.commit()

    def run_barman_command(*args):
        # Execute a barman command returning json output
        command_barman = ("barman","-f","json",*args)
        if appconf["USE_PREFIX_COMMAND"]:
            command_barman = appconf["PREFIX_COMMAND"] + command_barman
        result = json.loads(subprocess.run(list((command_barman)),stdout=subprocess.PIPE).stdout.decode("utf-8"))
        return result

    def get_servers_list():
        result_status = run_barman_command("list-server")
        return result_status

    # Get the server list at init
    tab_menu = get_servers_list()

    # Home Page
    @app.route('/')
    @login_required
    def home_page():
        return render_template("index_template.html", tab_menu=tab_menu)

    # Refresh Server List
    @app.route('/refreshlist')
    @roles_required('SuperAdmin')
    def refresh_list():
        global tab_menu 
        tab_menu = get_servers_list()
        return redirect(url_for('home_page'))

    # List Servers
    @app.route('/listservers')
    @roles_required('SuperAdmin')
    def barman_list_servers():
        result_status = run_barman_command("list-server")
        return render_template("list_servers.html", tab=result_status, tab_menu=tab_menu)

    # Status Server
    @app.route('/statusserver/<server>')
    @roles_required('SuperAdmin')
    def barman_status_server(server):
        result_status = run_barman_command("status", server)
        return render_template("status_server.html", tab=result_status, tab_menu=tab_menu)

    # Check Server
    @app.route('/checkserver/<server>')
    @roles_required('SuperAdmin')
    def barman_check_server(server):
        result_status = run_barman_command("check",server)
        return render_template("check_server.html", tab=result_status, tab_menu=tab_menu)

    # List Backup
    @app.route('/listbackupsserver/<server>')
    @roles_required('SuperAdmin')
    def barman_listbackup_server(server):
        result_status = run_barman_command("list-backup",server)
        datejour = datetime.date.today().strftime('%Y%m%d')
        return render_template("list_backup.html", tab=result_status, tab_menu=tab_menu,datejour=datejour)

    # Show Server
    @app.route('/showserver/<server>')
    @roles_required('SuperAdmin')
    def barman_show_server(server):
        result_status = run_barman_command("show-server",server)
        return render_template("show_server.html", tab=result_status, tab_menu=tab_menu)

    # Show Backup
    @app.route('/showbackup/<server>/<backupid>')
    @roles_required('SuperAdmin')
    def barman_show_backup(server,backupid):
        result_status = run_barman_command("show-backup",server,backupid)
        return render_template("show_backup.html", tab=result_status, tab_menu=tab_menu)

    # Delete Backup
    @app.route('/deletebackup/<server>/<backupid>')
    @roles_required('SuperAdmin')
    def barman_delete_backup(server,backupid):
        result_status = run_barman_command("delete",server,backupid)
        return render_template("delete_backup.html", tab=result_status, tab_menu=tab_menu, server=server)

    # Launch Backup Validation Page
    @app.route('/prelaunchbackup/<server>')
    @roles_required('SuperAdmin')
    def barman_prelaunch_backup(server):
        return render_template("pre_launch_backup.html", tab_menu=tab_menu, server=server)

    # Launch Backup
    @app.route('/launchbackup/<server>')
    @roles_required('SuperAdmin')
    def barman_launch_backup(server):
        result_status = run_barman_command("backup",server)
        return render_template("launch_backup.html", tab=result_status, tab_menu=tab_menu, server=server)

    return app

# Start development web server
if __name__=='__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5555, debug=True)
