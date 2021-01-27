import identibooru
import requests
from identibooru.models.users import Users, UserOpts, get_user_options, get_request
from identibooru.models.tags import Tags
from werkzeug.security import generate_password_hash
import qrcode

@identibooru.app.route("/account/register")
def account_register():
    if get_user_options(identibooru.current_user.get_username())['rank'] != 0:
        return identibooru.redirect(identibooru.url_for('index'))
    if identibooru.disable_registration:
        identibooru.flash("registration is currently disabled", "danger")
        return identibooru.redirect(identibooru.url_for('index'))
    return identibooru.render_template('account-register.html', title='register')

@identibooru.app.route("/function/register", methods=['POST'])
def function_register():
    if get_user_options(identibooru.current_user.get_username())['rank'] != 0:
        return identibooru.redirect(identibooru.url_for('index'))
        
    if identibooru.disable_registration:
        identibooru.flash("registration is currently disabled", "danger")
        return identibooru.redirect(identibooru.url_for('index'))

    email = identibooru.request.form['email']

    # this might stop automated requests
    if email != "":
        identibooru.app.logger.info(f'potential bot: %s entered an email address when email addresses aren\'t used', email)
        return "error: email address entered"

    if identibooru.hcaptcha:
        response = identibooru.request.form.get('g-recaptcha-response', False)
        data = {
            "secret": identibooru.hcaptcha_secret_key,
            "response": response,
            "remoteip": identibooru.request.environ.get('REMOTE_ADDR')
        }
        r = requests.post("https://hcaptcha.com/siteverify", data=data)
        is_valid = r.json()["success"] if r.status_code == 200 else False

        if not is_valid:
            identibooru.flash("invalid captcha", "danger")
            return identibooru.redirect(identibooru.url_for('account_register'))

    username = identibooru.request.form['username']
    password = identibooru.request.form['password']
    
    if not identibooru.re.search('^[a-z][a-z0-9-_]{2,32}$', username, identibooru.re.IGNORECASE):
        identibooru.flash("invalid username", "danger")
        return identibooru.redirect(identibooru.url_for('account_register'))

    user = Users.query.filter_by(username=username).first()
    if user:
        identibooru.flash("that username is taken", "danger")
        return identibooru.redirect(identibooru.url_for('account_register'))
    else:
        hash = generate_password_hash(password)
        create_user = Users(username=username, password=hash)
        identibooru.db.session.add(create_user)
        identibooru.db.session.flush()
        identibooru.db.session.commit()

        user_id = str(create_user.uid)
        bio = '''welcome to my profile

{{image}}'''

        create_user_opts = UserOpts(uid=user_id, bio=bio, views=0, avatar=0, map=0, tracking=0, sharing=1, rank=1, adult=0)
        identibooru.db.session.add(create_user_opts)
        identibooru.db.session.flush()
        identibooru.db.session.commit()

        create_user_tags = Tags(uid=user_id, tag="new_user")
        identibooru.db.session.add(create_user_tags)
        create_user_tags = Tags(uid=user_id, tag="rating:safe")
        identibooru.db.session.add(create_user_tags)
        identibooru.db.session.flush()
        identibooru.db.session.commit()

        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L
        )
        qr.add_data(get_request().url_root + username)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        if img:
            qr_to_save = identibooru.app.static_folder + '/files/{}-qr.png'.format(username)
            img.save(qr_to_save)

        user = Users.query.filter_by(uid=user_id).first()
        user.is_authenticated = True
        identibooru.login_user(user)

        return identibooru.redirect("/" + username + "/edit")
    identibooru.flash("registration failed", "danger")
    return identibooru.redirect(identibooru.url_for('account_register'))