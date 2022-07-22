# ---------------- DEFAULT IMPORTS ---------------- #

import datetime
import json

from flask import Blueprint, jsonify, session, request
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from tools import c_response, pprint

from manga.models import Sources, Mangas, Authors, Genres, Chapters
from users.models import Ratings, Users, History, Favorites





# ---------------- STARTING ROUTE ----------------- #

users = Blueprint('users', __name__)



# --------------------- LOGIN ---------------------- #

@users.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        email, password = request.args.get('email'), request.args.get('password')

        if session.get('login_atp_qt') is None:
            session['login_atp_qt'] = 0
            session['login_atp_ts'] = 0

        ## IMPORTANT: NOT WORKING, NEED TODO
        if session['login_atp_qt'] > 3:
            if session['login_atp_ts'] > datetime.datetime.now() - datetime.timedelta(minutes=5):
                pprint(f'[i] {request.path} - {email} has made too many attemps.', 'red')
                return jsonify(c_response(401, 'Too many login attempts.<br>Please try again in 5 minutes.', {'error': 'too_many_login_attempts'}))

        if not email and not password:
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            pprint(f'[i] Info: {request.path} - Missing information on requisition.', 'yellow')
            return jsonify(c_response(401, 'Missing email or password'))

        user = Users.query.filter_by(email=email).first()

        if not user:
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            pprint(f'[i] Info: {request.path} - User {email} not found.', 'yellow')
            return jsonify(c_response(401, 'User not found', {'error': 'email'}))

        if not check_password_hash(user.password, password):
            session['login_atp_qt'] += 1
            session['login_atp_ts'] = datetime.datetime.now()

            pprint(f'[i] Info: {request.path} - Wrong password for {email}.', 'yellow')
            return jsonify(c_response(401, 'Wrong password', {'error': 'password'}))

        else:
            session['email'] = email

            pprint(f'[i] Info: {request.path} - User {email} logged in.', 'green')
            return jsonify(c_response(200, 'Logged in'))
            

    elif request.method == 'POST':
        try:
            data = request.get_json()

            if not data:
                pprint(f'[i] Info: {request.path} - Missing information on requisition.', 'yellow')
                return jsonify(c_response(401, 'Missing data'))

            email, password = data.get('email'), data.get('password')

            if not email and not password:
                pprint(f'[i] Info: {request.path} - Missing information on requisition.', 'yellow')
                return jsonify(c_response(401, 'Missing email or password', {'error': 'missing_data'}))

            user = Users.query.filter_by(email=email).first()

            if user:
                pprint(f'[i] Info: {request.path} - User {email} already exists.', 'yellow')
                return jsonify(c_response(401, 'Email already register', {'error': 'email'}))

            user = Users(email, generate_password_hash(password))

            db.session.add(user)
            db.session.commit()

            return jsonify(c_response(200, 'User created successfully'))
        
        except Exception as e:
            print(e)
            return jsonify(c_response(401, 'Error creating user', {'error': str(e)})), 500



# -------------------- LOGOUT ---------------------- #

@users.route('/logout')
def logout():
    pprint(f'[i] Info: {request.path} - User {session.get("email")} logged out.', 'green')
    session.pop('email', None)

    return jsonify(c_response(200, 'Logged out'))



# -------------------- SESSION --------------------- #

@users.route('/session/get_profile')
def session_get_profile():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()

        pprint(f'[i] Info: {request.path} - User {user.email} requested profile.', 'green')
        return jsonify(c_response(200, 'Profile send', user.serialize()))

    else:
        return jsonify(c_response(403, 'Not logged in'))


@users.route('/session/is_alive')
def session_is_alive():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()

        pprint(f'[i] Info: {request.path} - User {user.email} is logged.', 'green')
        return jsonify(c_response(200, 'Logged in', {'username': user.username}))

    else:
        return jsonify(c_response(401, 'Not logged in'))


@users.route('/session/update/<section>', methods = ['POST'])
def session_update_info(section):
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        data = request.get_json()

        if not data:
            pprint(f'[i] Info: {request.path} - Missing information on requisition.', 'yellow')
            return jsonify(c_response(401, 'Missing data'))

        if not data.get('target'):
            pprint(f'[i] Info: {request.path} - Missing target on requisition.', 'yellow')
            return jsonify(c_response(401, f'Missing {section}'))

        if section not in ['username', 'password', 'email']:
            pprint(f'[i] Info: {request.path} - Invalid section on requisition.', 'yellow')
            return jsonify(c_response(401, 'Invalid section'))

        if user and check_password_hash(user.password, data.get('password')):
            if section == 'username':
                pprint(f'[i] Info: {request.path} - User {user.username} updated username.', 'green')
                user.username = data.get('target')
                db.session.commit()

                return jsonify(c_response(200, 'Username updated'))
            
            elif section == 'password':
                user.password = generate_password_hash(data.get('target'))
                db.session.commit()

                pprint(f'[i] Info: {request.path} - User {user.username} updated password.', 'green')
                return jsonify(c_response(200, 'Password updated'))

        else:
            pprint(f'[i] {request.path} - Wrong password for {user.username}.', 'red')
            return jsonify(c_response(401, 'Wrong password'))

    else:
        return jsonify(c_response(401, 'Not logged in'))


@users.route('/session/history')
def session_history():
    if 'email' in session:
        user = Users.query.filter_by(email=session['email']).first()
        
        data = []
        for item in user.history:
            manga = Mangas.query.filter_by(id = item.manga_id).first()
            
            output ={
                'manga_title': manga.title,
                'manga_slug': manga.slug,
                'manga_source': manga.source,
                'image': manga.image,
                'date': item.updated_at
            }
        
            chapter = Chapters.query.filter_by(id = item.chapter_id).first()
            if chapter:
                output['chapter_title'] = chapter.title
                output['chapter_slug'] = chapter.slug
                output['chapter_link'] = chapter.chapter_link
            else:
                output['chapter_title'] = None
                output['chapter_slug'] = None
                output['chapter_link'] = None

            data.append(output)


        data = sorted(data, key=lambda k: k['date'], reverse=True)

        pprint(f'[i] Info: {request.path} - User {user.username} requested history.', 'green')
        return jsonify(c_response(200, 'History sent', data))

    else:
        return jsonify(c_response(401, 'Not logged in'))


@users.route('/session/favorite')
def session_favorites():
    if request.method == 'GET':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            
            data = []
            for fav in user.favorites:
                manga = Mangas.query.filter_by(id = fav.manga_id).first()
                output ={
                    'manga_title': manga.title,
                    'manga_slug': manga.slug,
                    'manga_source': manga.source,
                    'image': manga.image,
                    'date': fav.updated_at
                }
                data.append(output)

            data = sorted(data, key=lambda k: k['date'], reverse=True)

            pprint(f'[i] Info: {request.path} - Favorites of {user.username}', 'green')
            return jsonify(c_response(200, 'Favorites sent', data))

        else:
            return jsonify(c_response(401, 'Not logged in'))

@users.route('/session/favorite/<string:manga>', methods = ['GET', 'POST'])
def session_favorites_manga(manga = None):
    if request.method == 'GET':
        session['email'] = 'admin@admin.com'
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            manga = Mangas.query.filter_by(slug = manga).first()

            if user.favorites.filter_by(manga_id = manga.id).first():
                pprint(f'[i] Info: {request.path} - {user.username} requested in his favorites and have.', 'green')
                return jsonify(c_response(200, 'Sended', {'status': 'true'}))

            else:
                pprint(f'[i] Info: {request.path} - {user.username} requested in his favorites and have not.', 'green')
                return jsonify(c_response(200, 'Sended', {'status': 'false'}))

        else:
            return jsonify(c_response(401, 'Not logged in'))

    elif request.method == 'POST':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            data = request.get_json()

            manga = Mangas.query.filter_by(slug = manga).first()
            if not manga:
                pprint(f'[i] Info: {request.path} - Manga {manga} not found.', 'yellow')
                return jsonify(c_response(401, 'Manga not found'))

            removed = False
            for item in user.favorites:
                if item.manga_id == manga.id:
                    favorite = Favorites.query.filter_by(user_id = user.id, manga_id = manga.id).first()
                    user.favorites.remove(favorite)
                    db.session.delete(favorite)
                    db.session.commit()
                    removed = True

                    pprint(f'[i] Info: {request.path} - Removed manga {manga} from {user.username} favorites.', 'green')
                    return jsonify(c_response(200, 'Manga already in favorites. Removed', {'operation': 'removed'}))
                    
            if not removed:
                favorite = Favorites(user_id = user.id, manga_id = manga.id)
                db.session.add(favorite)
                db.session.commit()
                user.favorites.append(favorite)
                db.session.commit()
                pprint(f'[i] Info: {request.path} - Added manga {manga} to {user.username} favorites.', 'green')
                return jsonify(c_response(200, 'Manga added to favorites', {'operation': 'added'}))

        else:
            return jsonify(c_response(401, 'Not logged in'))


@users.route('/session/rating/<string:manga>')
@users.route('/session/rating/<string:manga>/<int:rating_i>', methods = ['POST'])
def session_rating(manga, rating_i = None):
    if request.method == 'GET':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            manga = Mangas.query.filter_by(slug=manga).first()
            rating = user.ratings.filter_by(user_id=user.id, manga_id=manga.id).first()

            if rating:
                pprint(f'[i] Info: {request.path} - Rating of {manga.title} from {user.username}', 'green')
                return jsonify(c_response(200, 'Rating sent', rating.rating))

            else:
                try:
                    pprint(f'[i] Info: {request.path} - User {user.username} havent rated {manga.title} yet.', 'green')
                    return jsonify(c_response(200, 'Not rated', None))
                except:
                    return jsonify(c_response(200, 'Rating not found'))

        else:
            return jsonify(c_response(401, 'Not logged in'))

    elif request.method == 'POST':
        if 'email' in session:
            user = Users.query.filter_by(email=session['email']).first()
            manga = Mangas.query.filter_by(slug=manga).first()
            
            rating = Ratings.query.filter_by(user_id=user.id, manga_id=manga.id).first()
            if rating:
                rating.rating = rating_i
                db.session.commit()

                pprint(f'[i] Info: {request.path} - User {user.username} rated {manga.title} with {rating_i} star.', 'green')
                return jsonify(c_response(200, 'Rating updated'))


            else:
                rating = Ratings(user_id=user.id, manga_id=manga.id, rating=rating_i)
                db.session.add(rating)
                db.session.commit()

                pprint(f'[i] Info: {request.path} - User {user.username} rated {manga.title} with {rating_i} star.', 'green')
                return jsonify(c_response(401, 'Rating not found'))

        else:
            return jsonify(c_response(401, 'Not logged in'))