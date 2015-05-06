from env_vars import *

import os
from flask import Flask, abort, redirect, url_for, \
    render_template, render_template_string, request, session, g, flash
#from pprint import pprint

import sqlite3
import jinja2
import getpass

from flask_wtf import Form
from wtforms import validators, StringField, HiddenField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, URL

from werkzeug.contrib.cache import SimpleCache
import podcastparser
#import urllib
import json

from urllib.request import urlopen
from operator import itemgetter, attrgetter, methodcaller
import datetime 

cache = SimpleCache()
app = Flask('Ponos')
DATABASE = os.path.join(app.root_path, DB_PATH)
              
#Form classes
class AddEditFeedForm(Form):       
    feed_title = StringField(validators=[DataRequired()])
    feed_url = URLField(validators=[DataRequired(), URL()])
    feed_id = HiddenField(validators=[DataRequired()])

class DeleteForm(Form):
    feed_id = HiddenField(validators=[DataRequired()])
    
def init_db():
    from contextlib import closing
    import sqlite3

    print(DB_PATH)
    with closing(sqlite3.connect(DB_PATH)) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit() 

def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv
    
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False, close_db=True):
    cur = g.db.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    if close_db:
        g.db.close()
    return (rv[0] if rv else None) if one else rv

def insert_update_feed(method, id, title, url):
    if method == 'u' and id is not None:
        cur = g.db.cursor()
        cur.execute('update feeds set feed_title = ?, feed_url = ? where feed_id = ?;', [title, url, id])
        g.db.commit()
        return "Record updated"
    
    if method == 'i':
        feed = query_db('select feed_id from feeds where feed_url = ?', [url], one=True, close_db=False)
        print (feed)
        if feed is None:
            cur = g.db.cursor()
            cur.execute('insert into feeds (feed_title, feed_url) values (?, ?);', [title, url])
            g.db.commit()
            return "Record inserted"
        else:
            return "Feed already exists."
        
        return "Unknown insert error."
        
@app.route('/')
def index():    
    import sonos
    if 'selected_zone' in session:
        return render_template('index.html', track=sonos.get_track(session['selected_zone']), zones=get_cached_zones())   
    return render_template('index.html', zones=get_cached_zones())
    
@app.route('/feeds')
def feeds():
    title = 'Feeds'
    result = query_db('select feed_id, feed_title, feed_url from feeds')
    feeds = [dict(id=row[0], title=row[1], url=row[2]) for row in result]
    return render_template('feeds.html', title=title, activenav="feeds", feeds=feeds, zones=get_cached_zones())

def dump(rf):
  for value in rf:
    print(value)
    
@app.route('/browse_feed/<id>')
def browse_feed(id):
    feed = query_db('select feed_url from feeds where feed_id = ?', [id], one=True)
    #dump(feed)
    episodes = fetch_episodes(feed[0])
    #print(x)
    return render_template('feed.html', episodes=episodes, zones=get_cached_zones())

@app.route('/delete_feed', methods=['POST'])
@app.route('/delete_feed/<id>', methods=['GET'])
def delete_feed(id=None):
    form_submit_url = url_for('delete_feed')
    form = DeleteForm(request.form)
    
    if request.method == 'GET':
        if id is not None:
            form.feed_id.data = id
            rv = query_db('select feed_title from feeds where feed_id = ?', [id], one=True)
        return render_template('delete_feed.html', feed=rv[0], form_action=form_submit_url, form=form, zones=get_cached_zones())
        
    if request.method == 'POST':
        if form.validate():
            if form.feed_id.data:
                cur = g.db.cursor()
                cur.execute('delete from feeds where feed_id = ?;', [form.feed_id.data])
                g.db.commit()
                flash('Record deleted')
                return redirect(url_for('feeds'))
            else:
                flash('Form ID is missing.')
                return render_template('delete_feed.html', form_action=form_submit_url, form=form, zones=get_cached_zones())
        else:
            flash('Form ID is missing.')
            return render_template('delete_feed.html', form_action=form_submit_url, form=form, zones=get_cached_zones())
        return feed[0] 
    
@app.route('/edit_feed', methods=['POST'])
@app.route('/edit_feed/<id>', methods=['GET'])
def edit_feed(id=None):
    form_submit_url = url_for('edit_feed')
    title = 'Edit Feed'
    form = AddEditFeedForm(request.form)
    
    if request.method == 'POST' and form.validate():
        if form.feed_id.data:
            m = insert_update_feed("u", form.feed_id.data, form.feed_title.data, form.feed_url.data)
            flash(m)
            return redirect(url_for('feeds'))
        else:
            flash('Form submitted without an ID.  Cannot update feed.')
            return render_template('add_edit_feed.html', title=title, form_action=form_submit_url, form=form, zones=get_cached_zones())
    
    if request.method == 'POST' and not form.validate():
        flash('Form did not validate.  See errors below.')
        for key, values in form.errors.items():
            str = ''
            for v in values:
                str = str + ' ' + v
            flash(key + ': ' + str)
        return render_template('add_edit_feed.html', title=title, form_action=form_submit_url, form=form, zones=get_cached_zones())
    
    if id is None:
        flash('Unable to edit feed, ID was not provided.')
        return render_template('add_edit_feed.html', title=title, form_action=form_submit_url, form=form, zones=get_cached_zones())
        
    if request.method == 'GET':
        rf = query_db('select feed_title, feed_url from feeds where feed_id = ?', [id], one=True)
        form.feed_id.data = id
        form.feed_url.data = rf['feed_url']
        form.feed_title.data = rf['feed_title']
        return render_template('add_edit_feed.html', title=title, form_action=form_submit_url, form=form, zones=get_cached_zones())

@app.route('/add_feed', methods=['GET','POST'])
def add_feed():
    form_submit_url = url_for('add_feed')
    title = 'Add Feed'
    form = AddEditFeedForm(request.form)
    
    if request.method == 'POST' and form.validate():
        m = insert_update_feed("i", form.feed_id.data, form.feed_title.data, form.feed_url.data)
        flash(m)
        return redirect(url_for('feeds'))
 
    if request.method == 'POST' and not form.validate():
        flash('Form did not validate.  See errors below.')
        for key, values in form.errors.items():
            str = ''
            for v in values:
                str = str + ' ' + v
            flash(key + ': ' + str)
        return render_template('add_edit_feed.html', activenav="add_feed", title=title, form_action=form_submit_url, form=form, zones=get_cached_zones())
    
    form.feed_id.data = 'None'
    return render_template('add_edit_feed.html', activenav="add_feed", title=title, form_action=form_submit_url, form=form, zones=get_cached_zones())

    
@app.route('/about')
def about():
    return 'This is the test about page.'
    
@app.route('/set_zone', methods=['POST'])    
def set_zone():
    if request.method == 'POST':
        posted_data = json.loads(json.dumps(request.json))
        session['selected_zone'] = posted_data['selected_zone']
        session['selected_zone_short_name'] = posted_data['short_name']
        json_data = [{ "zone":  session['selected_zone'], "short_name": session['selected_zone_short_name'] }]
    return json.dumps(json_data)

@app.route('/fetch_feed_title', methods=['POST'])    
def fetch_feed_title():    
    if request.method == 'POST':
        posted_data = json.loads(json.dumps(request.json))
        url = posted_data['url']
        parsed = podcastparser.parse(url, urlopen(url))
        json_data = [{ "title":  parsed['title'] }]
    return json.dumps(json_data)
    
@app.route('/play_uri', methods=['POST'])    
def play_uri():
    if request.method == 'POST':
        import sonos
        
        posted_data = json.loads(json.dumps(request.json))
        uri = posted_data['uri']
        
        if not session['selected_zone']:
            json_data = [{ "message":  "Could not play.  No zone selected." }]
        else:
            if sonos.zone_play(session['selected_zone'], uri):
                json_data = [{ "message":  "Episode not playing...." }]
            else: 
                json_data = [{ "message":  "Could not play.  SoCo couldn't play it." }]
    return json.dumps(json_data)

@app.route('/player_control', methods=['POST'])
def player_control():
    #print("Inside player control")
    if request.method == 'POST':
        import sonos
        
        posted_data = json.loads(json.dumps(request.json))
        action = posted_data['action']
        if action == 'mute':
            sonos.mute_zone(session['selected_zone'])
            json_data = [{ "message":  "Muted" }]
        if action == 'unmute':
            sonos.unmute_zone(session['selected_zone'])
            json_data = [{ "message":  "Unmuted" }]
        if action == 'play':
            sonos.play(session['selected_zone'])
            json_data = [{ "message":  "Playing" }]
        if action == 'pause':
            sonos.pause(session['selected_zone'])
            json_data = [{ "message":  "Paused" }]
        if action == 'skip-back':
            track = sonos.get_track(session['selected_zone'])
            timestamp = datetime.timedelta(seconds = (track['current_secs'] - 30) )
            print("selected_zone: " + session['selected_zone'])
            sonos.skipback(session['selected_zone'], timestamp)
            json_data = [{ "message":  "Skipped Back" }]
        else:
            json_data = [{ "message":  "Could not understand command." }]
        
    return json.dumps(json_data)
    
def format_tracktime(value):
    split_time = value.split(':')
    rv = ''
    if int(split_time[0]) > 0:
        rv += str(int(split_time[0])) +':' + split_time[1] + ':' + split_time[2]
    else:
        if int(split_time[1]) > 0:
            rv += str(int(split_time[1])) + ':' + split_time[2]
        else:
            if int(split_time[2]) > 0:
                rv += '0:' + split_time[2]
    
    return str(rv)
    
jinja2.filters.FILTERS['formattracktime'] = format_tracktime

def get_cached_zones():
    debug = 0

    if debug:
        import sonos
        print('Bypassing cache')
        return sonos.get_zones()
    else:
        rv = cache.get('zones')
        if rv is None:
            import sonos
            rv = sonos.get_zones()
            cache.set('zones', rv, timeout=60)  #timeout is in seconds multiply it by 60 * minutes to increase the cache time
        return rv
    
def fetch_episodes(url):
    parsed = podcastparser.parse(url, urlopen(url))
    #print(parsed)
    new = [dict(title=episode['title'], pub=episode['published'], \
    duration=str(datetime.timedelta(seconds = episode['total_time'])),  \
    description=episode['description'], uri_link=episode['enclosures'][0]['url']) for episode in parsed['episodes']]
    return new
    
def fetch_feed_details(url):
    parsed = podcastparser.parse(url, urlopen(url))
    #print(parsed)
    feed_det = [dict(link=parsed['link'], title=parsed['title'], cover_url=parsed['cover_url'], description=parsed['description'])]
    #print(feed_det)
    return feed_det
    
if __name__ == "__main__":
    print("Effective user is " + getpass.getuser())

    app.secret_key = SECRET_KEY
    app.run(debug=DEBUG, host=HOST, port=PORT)
    #session['selected_zone'] = None
