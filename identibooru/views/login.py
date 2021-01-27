import identibooru
from identibooru.models.users import Users, get_user_options
from werkzeug.security import check_password_hash

@identibooru.app.route("/account/login")
def account_login():
    if get_user_options(identibooru.current_user.get_username())['rank'] != 0:
        return identibooru.redirect(identibooru.url_for('index'))
    return identibooru.render_template('account-login.html', title='log in')

@identibooru.app.route("/function/login", methods=['GET', 'POST'])
def function_login():
    if get_user_options(identibooru.current_user.get_username())['rank'] != 0:
        return identibooru.redirect(identibooru.url_for('index'))
    email = identibooru.request.form['email']

    # this might stop automated requests
    if email != "":
        identibooru.app.logger.info(f'potential bot: %s entered an email address when email addresses aren\'t used', email)
        return "error: email address entered"

    username = identibooru.request.form['username']
    password = identibooru.request.form['password']

    user = Users.query.filter_by(username=username).first()
    if user:
        validity = check_password_hash(user.password, password)
        if validity:
            user.is_authenticated = True
            identibooru.login_user(user)
            if identibooru.current_user.is_authenticated:
                return identibooru.redirect("/" + user.username + "/edit")
    identibooru.flash("authentication failed", "danger")
    return identibooru.redirect(identibooru.url_for('account_login'))
