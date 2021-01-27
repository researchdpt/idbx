import identibooru
def error_page(error):
    return identibooru.render_template('error.html', title='error', error=error)