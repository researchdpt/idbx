

import identibooru

class Tags(identibooru.db.Model):
    __tablename__ = 'tags'
 
    id = identibooru.db.Column(identibooru.db.Integer, primary_key=True)
    uid = identibooru.db.Column(identibooru.db.Integer)
    tag = identibooru.db.Column(identibooru.db.Text)

    def __repr__(self):
        return "<Tags(id='{0}', uid='{1}', tag='{2}')>".format(
                            self.id, self.uid, self.tag)

@identibooru.cache.memoize(timeout=86400) # sort_tags
def sort_tags(tags):
    sorted_tags = {}
    sorted_tags["bio"] = {}
    sorted_tags["coordinates"] = {}
    sorted_tags["tags"] = {}
    location_types = ["lat", "lon"]
    counted_tags = count_tags()

    for tag in tags:
        if not isinstance(tag, str):
            tag = tag.tag
        groups = tag.split(":")
        if len(groups) > 1:
            if groups[0] in location_types:
                sorted_tags["coordinates"][tag] = {}
                sorted_tags["coordinates"][tag]["group"] = groups[0]
                sorted_tags["coordinates"][tag]["tag"] = groups[1]
                sorted_tags["coordinates"][tag]["src"] = tag
                sorted_tags["coordinates"][tag]["count"] = counted_tags.get(tag) if counted_tags.get(tag) else 0
            else:
                sorted_tags["bio"][tag] = {}
                sorted_tags["bio"][tag]["group"] = groups[0]
                sorted_tags["bio"][tag]["tag"] = groups[1]
                sorted_tags["bio"][tag]["src"] = tag
                sorted_tags["bio"][tag]["count"] = counted_tags.get(tag) if counted_tags.get(tag) else 0
        else:
            sorted_tags["tags"][tag] = {}
            sorted_tags["tags"][tag]["group"] = "tags"
            sorted_tags["tags"][tag]["tag"] = tag
            sorted_tags["tags"][tag]["src"] = tag
            sorted_tags["tags"][tag]["count"] = counted_tags.get(tag) if counted_tags.get(tag) else 0
    return sorted_tags

@identibooru.cache.memoize(timeout=86400) # count_tags
def count_tags():
    count = identibooru.db.engine.execute('SELECT tag, count(*) as \'num\' FROM tags GROUP BY tag')
    count_dict = {}
    for row in count:
        count_dict[row[0]] = row[1]
    return count_dict

def clean_tags(username, users_class):
    user = users_class.query.filter_by(username=username).first()
    if user:
        previous_tag = ""
        tags = Tags.query.filter_by(uid=user.uid).all()
        for tag in tags:
            if previous_tag != "":
                if tag.tag == previous_tag.tag:
                    identibooru.db.session.delete(previous_tag)
                    identibooru.db.session.commit()
                    #print("conflicting tags: " + tag.tag + " and " + previous_tag.tag)
            previous_tag = tag



def validate_tag(tag):
    regex = identibooru.re.compile('[^a-zA-Z0-9:._()-]')
    tag_processed = tag.replace(" ", "_")
    tag_processed = regex.sub('', tag_processed)
    tag_processed = tag_processed.strip()
    tag_processed = (tag_processed[:50] + '..') if len(tag_processed) > 50 else tag_processed

    if tag_processed is "":
        return False

    return tag_processed

@identibooru.cache.memoize(timeout=86400) # render_tag_list
def render_tag_list(html, tags, is_profile, is_map, remove_tags=[]):
    if is_profile:
        tag_limit = 100
    else:
        tag_limit = 50

    if is_map:
        urlbit = "/map/"
    else:
        urlbit = "/search/"
    built_list = ""

    groups = sort_tags(tags)
    min_required = 0

    if len(remove_tags) >= 1:
        if html:
            built_list = built_list + "<li><h6>hidden</h6></li>"
        for removed_tag in remove_tags:
            if html:
                built_list = built_list + '''
                <li class="tag-type-general">
                <a href="''' + urlbit + '''?t=''' + removed_tag + '''">''' + removed_tag + '''</a>
                </li>
                '''

    if not is_profile:
        if html:
            built_list = built_list + "<li><h6>tags</h6></li>"
    for group in groups.items():
        if isinstance(group[1], dict):
            if is_profile:
                if html:
                    if len(group[1].values()) >= 1:
                            if (group[0] == "coordinates" and is_profile['tracking'] != 1):
                                pass
                            else:
                                built_list = built_list + "<li><h6>"+group[0]+"</h6></li>"
                for tag in group[1].values():
                    if (group[0] == "coordinates" and is_profile['tracking'] != 1):
                        pass
                    else:
                        if (tag['count'] > min_required) and (tag['src'] not in remove_tags):
                            if identibooru.disable_search:
                                count = ""
                            else:
                                count = tag['count']
                            if html:
                                built_list = built_list + '''
                                <li class="tag-type-general">
                                <a href="''' + urlbit + '''?t=''' + tag['src'] + '''">''' + tag['src'] + '''</a> <span class="count">''' + str(count) + '''</span>
                                </li>
                                '''
                            else:
                                built_list = built_list + tag['src'] + "\n"
            else:
                for tag in group[1].values():
                    if (tag['count'] > min_required) and (tag['src'] not in remove_tags):
                        if identibooru.disable_search:
                            count = ""
                        else:
                            count = str(tag['count'])
                        if html:
                            built_list = built_list + '''
                            <li class="tag-type-general">
                            <a href="''' + urlbit + '''?t=''' + tag['src'] + '''">''' + tag['src'] + '''</a> <span class="count">''' + count + '''</span>
                            </li>
                            '''
                        else:
                            built_list = built_list + tag['src'] + "\n"
    return built_list

#@identibooru.cache.memoize(timeout=0) # render_search_results
def render_search_results(html, search_tags, remove_tags, users_class):
    search_results = {}
    built_results = ""
    no_display = 0
    found_users = []
    for result in search_tags:
        users = users_class.query.filter_by(uid=result.uid).all()
        for user in users:
            found_users.append(user)

    for user in list(dict.fromkeys(found_users)):
        for removed_tag in remove_tags:
            user_with_tag = Tags.query.filter_by(tag=removed_tag,uid=user.uid).first()
            if user_with_tag:
                no_display = 1
        if not no_display:
            search_results[user.username] = {}
            search_results[user.username]['user'] = user
    return search_results

#@identibooru.cache.memoize(timeout=0) # render_search_bar
@identibooru.app.template_filter('render_search_bar')
def render_search_bar(terms=""):
    html = '''<form class="form-search"  id="searchform" action="/search" method="get">
        <input id="search-bar" name="t" type="text" value="''' + terms + '''" placeholder="ex: age:25 programming python -java" />
    </form>'''
    return html
identibooru.app.jinja_env.globals.update(render_search_bar=render_search_bar)

#@identibooru.cache.memoize(timeout=0) # render_map_search_bar
@identibooru.app.template_filter('render_map_search_bar')
def render_map_search_bar(terms=""):
    html = '''<form class="form-search"  id="searchform" action="/map" method="get">
        <input id="search-bar" name="t" type="text" value="''' + terms + '''" placeholder="" />
    </form>'''
    return html
identibooru.app.jinja_env.globals.update(render_map_search_bar=render_map_search_bar)