

from flask import request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask.views import MethodView
from flask import Flask

from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, current_user, login_user, login_required, logout_user

import uuid, time, os, time, re, signal, json
import pkg_resources, platform
from datetime import datetime, timedelta
from flask_hcaptcha import hCaptcha
import humanize


# class Config(object):
#     def __init__(self, path):
#         try:
#             with open(path) as config_file:
#                 self.data = json.load(config_file)
#         except:
#             logging.error(f"Could not load the config from {path}.")
#         else:
#             logging.info(f"Successfully loaded the config from {path}.")

# # Configuration
# config_path = "config.xml"
# logging.info(f'Loading config from {config_path}.')

# config = Config(config_path)

# Configuration Variables
db = os.environ.get('identibooru_DB')
secret = os.environ.get('identibooru_Secret')

branding = os.environ.get('identibooru_Branding')
email = os.environ.get('identibooru_Email')
disable_search = True if os.environ.get('identibooru_Disable_Search') == "true" else False
disable_registration = True if os.environ.get('identibooru_Disable_Registration') == "true" else False

hcaptcha_site_key = os.environ.get('identibooru_hCaptcha_Sitekey')
hcaptcha_secret_key = os.environ.get('identibooru_hCaptcha_Secret')
hcaptcha_enabled = os.environ.get('identibooru_hCaptcha_Enabled')

image_maxwidth = os.environ.get('identibooru_Image_MaxWidth')
image_maxheight = os.environ.get('identibooru_Image_MaxHeight')

thumb_maxwidth = os.environ.get('identibooru_Thumb_MaxWidth')
thumb_maxheight = os.environ.get('identibooru_Thumb_MaxHeight')

image_filesize = os.environ.get('identibooru_Image_FileSize')

profile_tag_limit = 500 if not os.environ.get('identibooru_Profile_Tag_Limit') else int(os.environ.get('identibooru_Profile_Tag_Limit'))

software = os.environ.get('identibooru_Software')
version = os.environ.get('identibooru_Version')

if db == None or secret == None:
    print(" * Improper configuration! Exiting...")
    os.kill(os.getpid(), signal.SIGTERM)
if db == "mysql://<user>:<password>@<host>/<database>":
    print(" * Database not configured properly! Exiting...")
    os.kill(os.getpid(), signal.SIGTERM)

app = Flask(__name__)

if app.debug:
     print(" * Cache: Nulltype")
     cache = Cache(app,config={'CACHE_TYPE': 'null'})
else:
     print(" * Cache: Redis")
     cache = Cache(app, config={
          'CACHE_TYPE': 'redis',
          'CACHE_KEY_PREFIX': 'fcache',
          'CACHE_REDIS_HOST': 'localhost',
          'CACHE_REDIS_PORT': '6379',
          'CACHE_REDIS_URL': 'redis://localhost:6379'
     })

app.config.update(dict(
    SQLALCHEMY_DATABASE_URI=db,
    SQLALCHEMY_TRACK_MODIFICATIONS="false",
    SQLALCHEMY_ECHO=True if app.debug else False,
    HCAPTCHA_SITE_KEY=hcaptcha_site_key,
    HCAPTCHA_SECRET_KEY=hcaptcha_secret_key,
    HCAPTCHA_ENABLED=True if hcaptcha_enabled == "true" else False,
    SECRET_KEY=secret,
    MAX_CONTENT_LENGTH=int(image_filesize)
))
app.jinja_env.cache = {}

db = SQLAlchemy(app)
login = LoginManager(app)
hcaptcha = hCaptcha(app)

print(" * Initializing...")

questionable_tag_file = open(os.path.dirname(app.instance_path) + "/data/ratings_questionable.txt", "r")
explicit_tag_file = open(os.path.dirname(app.instance_path) + "/data/ratings_explicit.txt", "r")
questionable_tag_list = questionable_tag_file.read().splitlines()
explicit_tag_list = explicit_tag_file.read().splitlines()
     
import identibooru.initialize