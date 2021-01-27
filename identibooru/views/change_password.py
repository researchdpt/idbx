import identibooru
from identibooru.models.users import Users
from werkzeug.security import generate_password_hash

@identibooru.app.route("/function/change-password", methods=['POST'])
def function_change_password():
    username = identibooru.request.form['username']
    password = identibooru.request.form['password']

    if (username == identibooru.current_user.get_username()) or (get_user_options(identibooru.current_user.get_username())['rank'] == 99):
        user = Users.query.filter_by(username=username).first()
        if user:
            hash = generate_password_hash(password)
            user.password = hash
            identibooru.db.session.commit()
            identibooru.flash("password changed", "success")
            identibooru.cache.delete_memoized(identibooru.models.users.get_user_options)
            return identibooru.redirect("/" + user.username + "/settings")
    identibooru.flash("authentication failed", "danger")
    return identibooru.redirect("/" + user.username + "/settings")
