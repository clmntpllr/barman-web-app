""" Flask application config """

# Flask settings
SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

# Flask-SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///barman_app.sqlite'    # File-based SQL database
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

# Flask-User settings
USER_APP_NAME = "Barman Web App"      # Shown in and email templates and page footers
USER_ENABLE_EMAIL = False             # Disable email authentication
USER_ENABLE_USERNAME = True           # Enable username authentication
USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form
USER_ENABLE_REGISTER = False          # No register possible
USER_COPYRIGHT_YEAR = "2021"
USER_CORPORATION_NAME = "Clément Paillier"
USER_APP_VERSION = "1.2"

#Flask-Caching config
CACHE_TYPE = "SimpleCache"  # Flask-Caching related configs
CACHE_DEFAULT_TIMEOUT = 300

# App config
APP_CONF_ADMIN_USERNAME = "admin"
APP_CONF_ADMIN_PASSWORD = "MyPassword"
APP_CONF_USE_PREFIX_COMMAND = False
APP_CONF_PREFIX_COMMAND = ("sudo","-u","barman")
# More Examples
#APP_CONF_PREFIX_COMMAND = ("ssh","barman@barmanhost")
#APP_CONF_PREFIX_COMMAND = ("sudo","-u","postgres","ssh","barman@barmanhost")