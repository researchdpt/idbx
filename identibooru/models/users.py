

import identibooru
from identibooru.models.conversions import isint, sanitize_html
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.utils import secure_filename
from identibooru.models.tags import Tags, render_tag_list, validate_tag
import hashlib

@identibooru.app.template_filter('get_branding')
@identibooru.cache.memoize(timeout=86400) # get_branding
def get_branding():
    return "my unconfigured website" if not identibooru.branding else identibooru.branding
identibooru.app.jinja_env.globals.update(get_branding=get_branding)

@identibooru.app.template_filter('get_contact')
@identibooru.cache.memoize(timeout=86400) # get_contact
def get_contact():
    return "webmaster@example.org" if not identibooru.email else identibooru.email
identibooru.app.jinja_env.globals.update(get_contact=get_contact)

@identibooru.app.template_filter('is_search_disabled')
@identibooru.cache.memoize(timeout=60) # is_search_disabled
def is_search_disabled():
    return identibooru.disable_search
identibooru.app.jinja_env.globals.update(is_search_disabled=is_search_disabled)

@identibooru.app.template_filter('get_request')
def get_request():
    if identibooru.request:
        return identibooru.request
    else:
        return ""
identibooru.app.jinja_env.globals.update(get_request=get_request)

@identibooru.app.template_filter('get_stats')
@identibooru.cache.memoize(timeout=86400) # get_stats
def get_stats():
    users = Users.query.count()
    tags = Tags.query.count()
    statistics = {}
    statistics['software'] = identibooru.software
    statistics['version'] = identibooru.version
    statistics['users'] = users
    statistics['tags'] = tags
    return statistics
identibooru.app.jinja_env.globals.update(get_stats=get_stats)

#Get user avatar by ID
@identibooru.app.template_filter('get_avatar')
@identibooru.cache.memoize(timeout=86400) # get_avatar
def get_avatar(username, thumbnail):
    default_avatar = '/files/default.png'
    user = Users.query.filter_by(username=username).first()
    if user:
        if thumbnail == 256:
            avatar_path = '/files/{}-avatar-thumb.png'.format(user.username)
        else:
            avatar_path = '/files/{}-avatar-full.png'.format(user.username)
        if identibooru.os.path.isfile(identibooru.app.static_folder+avatar_path):
            filetime = int(identibooru.os.stat(identibooru.app.static_folder+avatar_path).st_mtime)
            if filetime:
                return "/static" + avatar_path + "?v=" + str(filetime)
            return "/static" + avatar_path
        else:
            return ""
    else:
        return ""
identibooru.app.jinja_env.globals.update(get_avatar=get_avatar)


#Get user avatar by ID
@identibooru.app.template_filter('get_qr')
@identibooru.cache.memoize(timeout=86400) # get_qr
def get_qr(username):
    user = Users.query.filter_by(username=username).first()
    if user:
        qr_img_path = '/files/{}-qr.png'.format(user.username)
        if identibooru.os.path.isfile(identibooru.app.static_folder+qr_img_path):
            filetime = int(identibooru.os.stat(identibooru.app.static_folder+qr_img_path).st_mtime)
            if filetime:
                return "/static" + qr_img_path + "?v=" + str(filetime)
            return "/static" + qr_img_path
        else:
            return ""
    else:
        return ""
identibooru.app.jinja_env.globals.update(get_qr=get_qr)

@identibooru.app.template_filter('user_is_checked')
@identibooru.cache.memoize(timeout=86400)
def user_is_checked(username, option):
    user = Users.query.filter_by(username=username).first()
    if user:
        if option == "toggleSharing":
            opts = UserOpts.query.filter_by(uid=user.uid,sharing=1).first()
            if opts:
                return "checked"
            else:
                return ""
        if option == "toggleTracking":
            opts = UserOpts.query.filter_by(uid=user.uid,tracking=1).first()
            if opts:
                return "checked"
            else:
                return ""
        if option == "toggleAvatar":
            opts = UserOpts.query.filter_by(uid=user.uid,avatar=1).first()
            if opts:
                return "checked"
            else:
                return ""
        if option == "toggleMap":
            opts = UserOpts.query.filter_by(uid=user.uid,map=1).first()
            if opts:
                return "checked"
            else:
                return ""
        if option == "toggleAdult":
            opts = UserOpts.query.filter_by(uid=user.uid,adult=1).first()
            if opts:
                return "checked"
            else:
                return ""
identibooru.app.jinja_env.globals.update(user_is_checked=user_is_checked)

@identibooru.app.template_filter('get_user_options')
@identibooru.cache.memoize(timeout=86400) # get_user_options
def get_user_options(username):
    user_option = {}
    user_option['api'] = ""
    user_option['rank'] = 0
    user_option['views'] = 0

    user_option['sharing'] = 0
    user_option['tracking'] = 0
    user_option['avatar_sidebar'] = 0
    user_option['map_sidebar'] = 0
    user_option['adult'] = 0

    user_option['lat'] = 0
    user_option['lon'] = 0

    user_option['bio_summary'] = "Profile for " + username
    user_option['bio_parsed'] = ""
    user_option['bio'] = ""

    user = Users.query.filter_by(username=username).first()
    if user:
        opts = UserOpts.query.filter_by(uid=user.uid).first()
        parsed_bio = ""

        #get main options
        user_option['api'] = hashlib.sha224(user.password.encode()+user.username.encode()+str(user.uid).encode()).hexdigest()
        user_option['rank'] = opts.rank
        user_option['views'] = opts.views

        user_option['sharing'] = opts.sharing        
        user_option['tracking'] = opts.tracking
        user_option['avatar_sidebar'] = opts.avatar
        user_option['map_sidebar'] = opts.map
        user_option['adult'] = opts.adult

        # get lat lon
        location_types = ["lat", "lon"]
        lat_lon = []
        tags = Tags.query.filter_by(uid=user.uid).all()
        for tag in tags:
            groups = tag.tag.split(":")
            if len(groups) > 1:
                if groups[0] in location_types:
                    user_option[groups[0]] = identibooru.re.sub("[A-Z]+", "", groups[1]);

        # get bio
        if opts.bio:
            parsed_bio = opts.bio

            #convert newlines into html
            parsed_bio = parsed_bio.replace('\n\r', '<br />')

            #sanitize
            parsed_bio = sanitize_html(parsed_bio)

            #try environment variables
            vars = identibooru.re.findall(r'\{\{.*?\}\}', parsed_bio)
            for var in vars:
                if var == "{{image}}":
                    avatar_display = '''<img src="'''+get_avatar(user.username, 1024)+'''" alt="user:'''+user.username+'''" title="user:'''+user.username+'''" class="user-avatar large" style="margin: -3px;">'''
                    parsed_bio = parsed_bio.replace(var, avatar_display)

            #convert links to be clickable
            # url_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            # links = identibooru.re.findall(url_re, parsed_bio)
            # for link in links:
            #     if link in parsed_bio:
            #         parsed_bio = parsed_bio.replace(link, '<a href="/go/'+link+'">'+link+'</a>')
            
            bio_summary = opts.bio.splitlines()
            bio_summary = sanitize_html(bio_summary[0])

            user_option['bio_summary'] = bio_summary
            user_option['bio_parsed'] = parsed_bio
            user_option['bio'] = opts.bio
    return user_option
identibooru.app.jinja_env.globals.update(get_user_options=get_user_options)

class Anonymous(AnonymousUserMixin):
    uid = identibooru.db.Column(identibooru.db.Integer, primary_key=True)
    username = identibooru.db.Column(identibooru.db.String(length=50))
    password = identibooru.db.Column(identibooru.db.Text)

    def __init__(self):
        self.uid = 0
        self.username = False
        self.active = True

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.uid

    def get_username(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return ""

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True
        
    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return True

    def __repr__(self):
        return "<Users(uid='{0}', username='{1}', password='{2}')>".format(
                            self.uid, self.username, self.password)

class Users(UserMixin, identibooru.db.Model):
    __tablename__ = 'users'
 
    uid = identibooru.db.Column(identibooru.db.Integer, primary_key=True)
    username = identibooru.db.Column(identibooru.db.String(length=50))
    password = identibooru.db.Column(identibooru.db.Text)
    active = True

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.uid

    def get_username(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True
        
    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return "<Users(uid='{0}', username='{1}', password='{2}')>".format(
                            self.uid, self.username, self.password)

class UserOpts(identibooru.db.Model):
    __tablename__ = 'user_opts'
 
    uid = identibooru.db.Column(identibooru.db.Integer, primary_key=True)
    bio = identibooru.db.Column(identibooru.db.Text)
    views = identibooru.db.Column(identibooru.db.Integer)
    avatar = identibooru.db.Column(identibooru.db.Integer)
    map = identibooru.db.Column(identibooru.db.Integer)
    tracking = identibooru.db.Column(identibooru.db.Integer)
    sharing = identibooru.db.Column(identibooru.db.Integer)
    rank = identibooru.db.Column(identibooru.db.Integer)
    adult = identibooru.db.Column(identibooru.db.Integer)

    def __repr__(self):
        return "<Users(uid='{0}', bio='{1}', views='{2}', avatar='{3}', map='{4}', tracking='{5}', sharing='{6}', rank='{7}', adult='{8}')>".format(
                            self.uid, self.bio, self.views, self.avatar, self.map, self.tracking, self.sharing, self.rank, self.adult)

@identibooru.login.user_loader
def load_user(uid):
    try:
        return Users.query.filter_by(uid=uid).first()
    except:
        return None

identibooru.login.anonymous_user = Anonymous