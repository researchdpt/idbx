import identibooru
from identibooru.models.users import Users, UserOpts, get_user_options

@identibooru.app.route("/function/change-options", methods=['POST'])
def function_change_options():
    username = identibooru.request.form['username']

    if (username == identibooru.current_user.get_username()) or (get_user_options(identibooru.current_user.get_username())['rank'] == 99):
        user = Users.query.filter_by(username=username).first()
        opts = UserOpts.query.filter_by(uid=user.uid).first()

        if identibooru.request.form.get('options'):
            options = identibooru.request.form.getlist('options')
            if "toggleSharing" in options:
                opts.sharing = 1
            else:
                opts.sharing = 0
            if "toggleTracking" in options:
                opts.tracking = 1
            else:
                opts.tracking = 0
            if "toggleAvatar" in options:
                opts.avatar = 1
            else:
                opts.avatar = 0
            if "toggleMap" in options:
                opts.map = 1
            else:
                opts.map = 0
            if "toggleAdult" in options:
                opts.adult = 1
            else:
                opts.adult = 0
        else:
            opts.sharing = 0
            opts.tracking = 0
            opts.avatar = 0
            opts.map = 0
            opts.adult = 0

        identibooru.db.session.commit()
        identibooru.cache.delete_memoized(identibooru.models.users.get_user_options)
        identibooru.cache.delete_memoized(identibooru.models.users.user_is_checked)
        identibooru.flash("settings changed", "success")
        return identibooru.redirect("/" + username + "/settings")
    identibooru.flash("authentication failed", "danger")
    return identibooru.redirect("/")