import identibooru
from html_sanitizer import Sanitizer

@identibooru.cache.memoize(timeout=86400) # sanitize_html
def sanitize_html(input):
    DEFAULT_SETTINGS = {
        "tags": {
            "abbr", "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
            "li", "br", "sub", "sup", "hr", "style", "pre", "span", "font",
        },
        "attributes": {"a": ("href", "name", "target", "title", "id", "rel"), "font": ("size", "color", "face"), "span": ("style", "id", "class"), "p": ("style", "id", "class")},
        "empty": {"hr", "a", "br"},
        "separate": {"a", "p", "li"},
        "whitespace": {"br"},
        "keep_typographic_whitespace": True,
        "add_nofollow": True,
        "autolink": True,
    }

    sanitizer = Sanitizer(DEFAULT_SETTINGS)
    return sanitizer.sanitize(input)

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

@identibooru.app.template_filter('get_filemtime')
@identibooru.cache.memoize(timeout=60) # get_filemtime
def get_filemtime(file):
    filepath = identibooru.app.static_folder + file
    print(filepath)
    if identibooru.os.path.isfile(filepath) and not identibooru.app.debug:
        filetime = int(identibooru.os.stat(filepath).st_mtime)
        if filetime:
            return "/static" + file + "?v=" + str(filetime)
    else:
        return "/static" + file
identibooru.app.jinja_env.globals.update(get_filemtime=get_filemtime)


def display_time(seconds, granularity=2):
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

@identibooru.app.before_request
def before_request():
    identibooru.g.request_start_time = identibooru.time.time()
    identibooru.g.request_time = lambda: "%.5f" % (identibooru.time.time() - identibooru.g.request_start_time)

@identibooru.app.context_processor
def current_time():
    return {'now': identibooru.datetime.utcnow()}

def unix_current_time():
    return int(identibooru.time.time())
identibooru.app.jinja_env.globals.update(unix_current_time=unix_current_time)

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b
def Diff(li1, li2): 
    return (list(set(li1) - set(li2))) 