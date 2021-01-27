import identibooru
import fnmatch, itertools
import numpy as np
from identibooru.models.users import Users, get_avatar, get_user_options
from identibooru.models.tags import Tags, render_tag_list, render_search_results


@identibooru.app.route("/search", strict_slashes=False)
def search():
    terms = identibooru.request.args.get('t', False)
    confirm_adult = identibooru.request.args.get('confirm_adult', False)
    search_tags = []
    remove_tags = []

    relevant_tags = []
    relevant_tag_list = []
    if not terms:
        identibooru.flash("no search terms specified", "danger")
        return identibooru.redirect(identibooru.url_for('index'))
    if identibooru.disable_search and get_user_options(identibooru.current_user.get_username())['rank'] != 99:
        identibooru.flash("not enough tags to form search results yet, please contribute by registering and tagging yourself!", "success")
        return identibooru.redirect(identibooru.url_for('index'))

    if " " in terms:
        terms_list = terms.split(" ")
    else:
        terms_list = [terms]
    if get_user_options(identibooru.current_user.get_username())['adult'] == 0 and not confirm_adult:
        adult_tags = ["-rating:explicit", "-rating:questionable"]
        fullpath = identibooru.request.full_path

        for adult_tag in adult_tags:
            if not adult_tag in terms_list:
                terms_list.append(adult_tag)
    
    tags = Tags.query.all()
    for term in terms_list:
        for tag in tags:
            if fnmatch.fnmatch(tag.tag, term):
                search_tags.append(tag)
        if term[0] is "-":
                remove_tags.append(term.strip("-"))

    
    search_results = render_search_results(html=True, search_tags=search_tags, remove_tags=remove_tags, users_class=Users)

    for result in search_results.values():
        relevant_tags.append(Tags.query.filter_by(uid=result['user'].uid).all())
            
    tags = Tags.query.all()
    for term in terms_list:
        for tag in tags:
            if fnmatch.fnmatch(tag.tag, term):
                relevant_tag_list.append(tag)
    for tag in list(itertools.chain(*relevant_tags)):
        relevant_tag_list.append(tag.tag)

    tag_list = render_tag_list(html=True, tags=relevant_tag_list, is_profile=False, is_map=False, remove_tags=remove_tags)
    return identibooru.render_template('search.html', title=terms + ' - search', results=search_results, tags=tag_list, keywords=terms)

@identibooru.app.route("/map", strict_slashes=False)
def map():
    search_results = False
    search_user_results = False
    terms = identibooru.request.args.get('t', False)

    search_users = ""

    if not terms:
        identibooru.flash("no search terms specified", "danger")
        return identibooru.redirect(identibooru.url_for('index'))
    if terms:
        if " " in terms:
            terms_list = terms.split(" ")
        else:
            terms_list = [terms]

        terms_list = [terms]
        if get_user_options(identibooru.current_user.get_username())['adult'] == 0:
            adult_tags = ["-rating:explicit", "-rating:questionable"]
            fullpath = identibooru.request.full_path

            for adult_tag in adult_tags:
                if not adult_tag in terms_list:
                    terms_list.append(adult_tag)

        search_tags = []
        remove_tags = []

        relevant_tags = []
        relevant_tag_list = []

        tags = Tags.query.all()
        for term in terms_list:
            groups = term.split(":")
            if len(groups) > 1:
                if groups[0] == "user":
                    search_user_results = Users.query.filter_by(username=groups[1].strip(" "))
            elif len(groups) == 1 and not identibooru.disable_search or get_user_options(identibooru.current_user.get_username())['rank'] == 99:
                for tag in tags:
                    if fnmatch.fnmatch(tag.tag, term):
                        search_tags.append(tag)
                if term[0] is "-":
                        remove_tags.append(term.strip("-"))
        search_results = render_search_results(html=False, search_tags=search_tags, remove_tags=remove_tags, users_class=Users)

    #tag_list = render_tag_list(html=True, tags=relevant_tag_list, is_profile=False, is_map=True, remove_tags=remove_tags)
    return identibooru.render_template('map.html', title='map', tag_results=search_results, search_users=search_user_results, keywords=terms)
