

import identibooru, fnmatch, itertools
from flask import send_from_directory
from identibooru.models.tags import Tags, render_tag_list

@identibooru.app.route("/")
def index():
    tags = Tags.query.all()
    tag_list = render_tag_list(html=True, tags=tags, is_profile=False, is_map=False)
    return identibooru.render_template('home.html', title='home', tags=tag_list)

@identibooru.app.route("/info")
def info():
    return identibooru.render_template('info.html', title='info')

@identibooru.app.route("/info/terms")
def info_terms():
    return identibooru.render_template('info-terms.html', title='terms of service')

@identibooru.app.route("/info/privacy")
def info_privacy():
    return identibooru.render_template('info-privacy.html', title='privacy policy')

@identibooru.app.route("/info/uploads")
def info_uploads():
    return identibooru.render_template('info-uploads.html', title='upload rules')

@identibooru.app.route("/info/users")
def info_profile():
    return identibooru.render_template('info-users.html', title='user accounts')

@identibooru.app.route("/info/donate")
def info_donate():
    return identibooru.render_template('donate.html', title='donate')

@identibooru.app.route('/robots.txt')
def robotstxt():
    return send_from_directory(identibooru.app.static_folder, identibooru.request.path[1:])

@identibooru.app.route('/humans.txt')
def humanstxt():
    return send_from_directory(identibooru.app.static_folder, identibooru.request.path[1:])

@identibooru.app.route('/info.txt')
def infotxt():
    return send_from_directory(identibooru.app.static_folder, identibooru.request.path[1:])

@identibooru.app.route('/favicon.ico')
def faviconico():
    return send_from_directory(identibooru.app.static_folder, identibooru.request.path[1:])

@identibooru.app.errorhandler(404)
def page_not_found(e):
    return "Not Found"