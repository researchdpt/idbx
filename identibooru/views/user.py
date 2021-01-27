import identibooru, cgi
from identibooru.models.conversions import Diff
from identibooru.models.users import Users, UserOpts, get_user_options, get_request, get_qr
from identibooru.models.tags import Tags, render_tag_list, validate_tag, clean_tags
from PIL import Image, ImageOps
import qrcode

@identibooru.app.route("/<username>")
def profile(username):
    if (username.lower() == "unendingpattern") or (username.lower() == "unswp"):
        identibooru.flash("no such profile exists", "danger")
        return identibooru.redirect(identibooru.url_for('index'))
    parsed_bio = ""
    user = Users.query.filter_by(username=username).first()
    if user:
        tags = Tags.query.filter_by(uid=user.uid).order_by(Tags.tag).all()
        opts = UserOpts.query.filter_by(uid=user.uid).first()
        opts.views = opts.views + 1
        identibooru.db.session.commit()
        tag_list = render_tag_list(html=True, tags=tags, is_profile=get_user_options(user.username), is_map=False)
        return identibooru.render_template('profile.html', title=user.username + ' - profile', user=user, tags=tags, user_options=get_user_options(username), tag_list=tag_list)
    identibooru.flash("no such profile exists", "danger")
    return identibooru.redirect(identibooru.url_for('index'))

@identibooru.app.route("/<username>/source")
def profile_source(username):
    parsed_bio = ""
    user = Users.query.filter_by(username=username).first()
    
    if user:
        return "<pre style='width: 100%; height: 100%;'>" + cgi.escape(get_user_options(username)['bio']) + "</pre>"
    return "no such profile exists"

@identibooru.app.route("/<username>/edit")
@identibooru.login_required
def profile_edit(username):
    if (username == identibooru.current_user.get_username()) or (get_user_options(identibooru.current_user.get_username())['rank'] == 99):
        user = Users.query.filter_by(username=username).first()
        if user:
            tags = Tags.query.filter_by(uid=user.uid).order_by(Tags.tag).all()
            tag_list = render_tag_list(html=False, tags=tags, is_profile=get_user_options(user.username), is_map=False)
        else:
            identibooru.flash("no such user exists", "danger")
            return identibooru.redirect(identibooru.url_for('index'))
        return identibooru.render_template('profile-edit.html', title=user.username + ' - editing profile', user=user, user_options=get_user_options(username), tags=tag_list)
    identibooru.flash("authentication failed", "danger")
    return identibooru.redirect("/" + username )

@identibooru.app.route("/<username>/settings")
@identibooru.login_required
def account_settings(username):
    if (username == identibooru.current_user.get_username()) or (get_user_options(identibooru.current_user.get_username())['rank'] == 99):
        user = Users.query.filter_by(username=username).first()
        if not user:
            identibooru.flash("no such user exists", "danger")
            return identibooru.redirect(identibooru.url_for('index'))
        return identibooru.render_template('account-settings.html', title=user.username + ' - account settings', user=user, user_options=get_user_options(username))
    identibooru.flash("authentication failed", "danger")
    return identibooru.redirect("/" + username )

@identibooru.app.route("/<username>/save", methods=['POST'])
def profile_save(username):
    if (username == identibooru.current_user.get_username()) or (get_user_options(identibooru.current_user.get_username())['rank'] == 99):
        user = Users.query.filter_by(username=username).first()
        updated_tags = False

        new_tags = identibooru.request.form['tags'].splitlines()
        new_bio = identibooru.request.form['bio']
        image = identibooru.request.files['image']

        set_rating = "rating:safe"

        if user:
            opts = UserOpts.query.filter_by(uid=user.uid).first()
            tags = Tags.query.filter_by(uid=user.uid).all()

            tag_count = Tags.query.filter_by(uid=user.uid).count()

            if tag_count >= identibooru.profile_tag_limit or len(new_tags) >= identibooru.profile_tag_limit:
                identibooru.flash("attempting to set more than " + str(identibooru.profile_tag_limit) + " tags", "danger")
                return identibooru.redirect("/" + username + "/edit")

            

            current_tags = []
            for tag in tags:
                current_tags.append(tag.tag)

            #print(new_tags)

            added = Diff(new_tags, current_tags)
            removed = Diff(current_tags, new_tags)

            #print(added)
            #print(removed)

            for tag in new_tags:
                tag = tag.lower()
                groups = tag.split(":")
                if len(groups) > 1:
                    if groups[0] == "age" and int(groups[1]) < 18:
                        identibooru.flash("Persons under the age of 18 are not allowed to create an account or otherwise use our Services.", "danger")
                        return identibooru.redirect("/info/terms")
                    

            invalid_entry = ["-", "~", "_"]
            invalid_exit = ["-", "~", "_"]

        
            if len(added) > 0:
                updated_tags = True
                for item in added:
                    validated_tag = validate_tag(item)
                    if (validated_tag is not False) and (validated_tag[-1] not in invalid_entry) and (validated_tag[-1] not in invalid_exit):
                        new_tag = Tags(uid=user.uid, tag=validated_tag)
                        identibooru.db.session.add(new_tag)
            if len(removed) > 0:
                updated_tags = True
                for item in removed:
                    to_remove = Tags.query.filter_by(tag=item).first()
                    if to_remove: identibooru.db.session.delete(to_remove)

            if opts:
                opts.bio = new_bio
            old_bio = get_user_options(user.username)['bio']
            identibooru.db.session.commit()

            new_current_tags = Tags.query.filter_by(uid=user.uid).all()
            for current_tag in new_current_tags:
                if current_tag.tag in identibooru.questionable_tag_list:
                    removed_tags = ["rating:explicit", "rating:safe"]
                    for removed_tag in removed_tags:
                        removed_tag = Tags.query.filter_by(uid=user.uid,tag=removed_tag).first()
                        if removed_tag:
                            identibooru.db.session.delete(removed_tag)
                            identibooru.db.session.commit()
                    set_rating = "rating:questionable"
                if current_tag.tag in identibooru.explicit_tag_list:
                    removed_tags = ["rating:safe", "rating:questionable"]
                    for removed_tag in removed_tags:
                        removed_tag = Tags.query.filter_by(uid=user.uid,tag=removed_tag).first()
                        if removed_tag:
                            identibooru.db.session.delete(removed_tag)
                            identibooru.db.session.commit()
                    set_rating = "rating:explicit"

            if set_rating:
                if set_rating == "rating:safe":
                    removed_tags = ["rating:explicit", "rating:questionable"]
                    for removed_tag in removed_tags:
                        removed_tag = Tags.query.filter_by(uid=user.uid,tag=removed_tag).first()
                        if removed_tag:
                            identibooru.db.session.delete(removed_tag)
                            identibooru.db.session.commit()
                new_tag = Tags(uid=user.uid, tag=validate_tag(set_rating))
                identibooru.db.session.add(new_tag)

            identibooru.db.session.commit()

            if get_qr(user.username) == "":
                qr = qrcode.QRCode(
                    error_correction=qrcode.constants.ERROR_CORRECT_L
                )
                qr.add_data(get_request().url_root + username)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                
                if img:
                    qr_to_save = identibooru.app.static_folder + '/files/{}-qr.png'.format(user.username)
                    img.save(qr_to_save)

            if image:
                avatar_to_save = identibooru.app.static_folder + '/files/{}-avatar-full.png'.format(user.username)
                avatar_to_save_thumb = identibooru.app.static_folder + '/files/{}-avatar-thumb.png'.format(user.username)
                image.save(avatar_to_save)

                try:
                    image_maxwidth = 1024 if not identibooru.image_maxwidth else int(identibooru.image_maxwidth)
                    image_maxheight = 2048 if not identibooru.image_maxheight else int(identibooru.image_maxheight)

                    thumb_maxwidth = 256 if not identibooru.thumb_maxwidth else int(identibooru.thumb_maxwidth)
                    thumb_maxheight = 1024 if not identibooru.thumb_maxheight else int(identibooru.thumb_maxheight)

                    img = Image.open(avatar_to_save)
                    img.thumbnail((image_maxwidth,image_maxheight))
                    img.save(avatar_to_save)

                    thumbnail = Image.open(avatar_to_save)
                    thumbnail.thumbnail((thumb_maxwidth, thumb_maxheight))
                    thumbnail.save(avatar_to_save_thumb)
                except IOError:
                    identibooru.flash("image upload failed", "danger")

            identibooru.cache.delete_memoized(identibooru.models.users.get_qr)
            identibooru.cache.delete_memoized(identibooru.models.users.get_avatar)
            identibooru.cache.delete_memoized(identibooru.models.conversions.sanitize_html)
            identibooru.cache.delete_memoized(identibooru.models.users.get_user_options)

            if updated_tags:
                identibooru.cache.delete_memoized(identibooru.models.users.get_stats)
                identibooru.cache.delete_memoized(identibooru.models.tags.sort_tags)
                identibooru.cache.delete_memoized(identibooru.models.tags.count_tags)
                identibooru.cache.delete_memoized(identibooru.models.tags.render_tag_list)
                identibooru.cache.delete_memoized(identibooru.models.tags.render_search_results)

            clean_tags(user.username, Users)

            return identibooru.redirect("/" + user.username + "/edit")
    identibooru.flash("authentication failed", "danger")
    return identibooru.redirect("/" + username )


@identibooru.app.route("/<username>/set", methods=['GET'])
def profile_set(username):
    coords = identibooru.request.args.get('coords', False)
    api = identibooru.request.args.get('api', False)
    if (api == get_user_options(username)['api']) or (username == identibooru.current_user.get_username()) or (get_user_options(identibooru.current_user.get_username())['rank'] == 99):
        user = Users.query.filter_by(username=username).first()
        if user:
            if coords:
                lat_lon = []
                validated_tag = validate_tag(coords)
                coords = coords.split(",")
                if len(coords) == 2:
                    lat = Tags.query.filter(Tags.tag.ilike('lat%')).filter_by(uid=user.uid).first()
                    lon = Tags.query.filter(Tags.tag.ilike('lon%')).filter_by(uid=user.uid).first()

                    if lat and lon:
                        lat.tag = "lat:"+coords[0]
                        lon.tag = "lon:"+coords[1]
                        identibooru.db.session.commit()
                    else:
                        lat = Tags(uid=user.uid, tag="lat:"+coords[0])
                        lon = Tags(uid=user.uid, tag="lon:"+coords[1])
                        identibooru.db.session.add(lat)
                        identibooru.db.session.add(lon)
                    identibooru.db.session.flush()
                    identibooru.db.session.commit()
            
                    identibooru.cache.delete_memoized(identibooru.models.tags.sort_tags)
                    identibooru.cache.delete_memoized(identibooru.models.tags.render_tag_list)
                    identibooru.cache.delete_memoized(identibooru.models.tags.render_search_results)
                    identibooru.cache.delete_memoized(identibooru.models.users.get_user_options)

                    if api: return "success"
                    identibooru.flash("location set", "success")
                    return identibooru.redirect("/" + user.username + "/settings")
        if api: return "fail"
        identibooru.flash("failed to set location", "danger")
        return identibooru.redirect("/" + user.username + "/settings")
    if api: return "authentication fail"
    identibooru.flash("authentication fail", "danger")
    return identibooru.redirect("/" + user.username + "/settings")
