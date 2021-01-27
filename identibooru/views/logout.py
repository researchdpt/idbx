import identibooru

@identibooru.app.route("/function/logout")
def function_logout():
    identibooru.logout_user()
    identibooru.flash("logged out", "danger")
    return identibooru.redirect(identibooru.url_for('index'))
