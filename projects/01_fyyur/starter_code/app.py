#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from dateutil import tz
import sys
# from sqlalchemy .orm import

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nora@localhost:5432/fyyur'

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String()))
    shows = db.relationship('Show', backref= 'venue', lazy= True, cascade="all, delete", passive_deletes=True)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(200))


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref = 'artist', lazy=True, cascade = "all, delete", passive_deletes=True)
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default = True)
    seeking_description = db.Column(db.String(200))



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key = True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='cascade'), nullable = False)
  venue_id =db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='cascade'), nullable= False )
  start_time = db.Column(db.DateTime)
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.  
  data = []
  venues = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  venueinfo = []
  for venue in venues:
    #lopping in venues that have the same city and state
    ven = Venue.query.filter(Venue.city == venue.city).filter(Venue.state == venue.state).all()
    for v in ven:
      today = datetime.now()
      upcoming = Show.query.filter(Show.venue_id == v.id).filter(Show.start_time > today)
      num = upcoming.count()
      venueinfo.append({
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": num
      })
      
    v = {
      "city":venue.city,
      "state":venue.state,
      "venues": venueinfo
       }
    venueinfo =[]
      
    data.append(v)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searchword = request.form.get("search_term")
  query = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.ilike("%"+searchword+"%")).all()
  count =0
  data = []
  for q in query:
    count = count + 1
    show = Show.query.filter(Show.artist_id == q.id).count()
    data.append({
      "id" : q.id,
      "name" : q.name,
      "num_upcoming_shows": show
    })

  response= {
    "count": count,
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  geners = []

  venue = Venue.query.get(venue_id)
  today = datetime.now()
  upshow = []
  pastshow =[]
  countup = 0
  countpast = 0

  queryshow = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > today)
  for show in queryshow:
    countup = countup +1
    queryartist = Artist.query.filter(Artist.id == show.artist_id)
    for up in queryartist:
      upshow.append({
        "artist_id": up.id,
        "artist_name": up.name,
        "artist_image_link": up.image_link,
        "start_time": show.start_time
      })  
  queryshow = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time <= today)
  for past in queryshow:
    countpast = countpast + 1
    queryartist = Artist.query.filter(Artist.id == past.artist_id).filter(Show.start_time <= today)
    for p in queryartist:
      pastshow.append({
        "artist_id": p.id,
        "artist_name": p.name,
        "artist_image_link": p.image_link,
        "start_time": past.start_time
      })
    
  
  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone":venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":  pastshow,
    "upcoming_shows": upshow,
    "past_shows_count": countpast,
    "upcoming_shows_count": countup
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebooklink = request.form.get('facebook_link')
    imagelink = request.form.get('image_link')
  
  # TODO: modify data to be the data object returned from db insertion
    venue = Venue(name = name, city = city, state = state, address = address, phone = phone, image_link= imagelink, facebook_link = facebooklink, genres = genres)
    db.session.add(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred ' + name +' could not be added')

  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    queryven = Venue.query.filter_by(id=venue_id).delete()
    query = Show.query.filter_by(venue_id = venue_id).delete()
    db.session.commit()
    flash('Venue has been deleted successful!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred could not delete')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.with_entities(Artist.id, Artist.name).group_by(Artist.name, Artist.id).all()
  
  for artist in artists:
    data.append({ 
      "id": artist.id,
      "name": artist.name
    }) 

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searchword = request.form.get("search_term")
  count = 0
  data = []
  shownum =0
  query = Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike("%"+searchword+"%")).all()
  for q in query:
    count = count + 1
    show = Show.query.filter(Show.artist_id == q.id).count()
    data.append({
      "id": q.id,
      "name":q.name,
      "num_upcoming_shows": show
    })
  response={
    "count":count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # # TODO: replace with real venue data from the venues table, using venue_id
  data =[]

  artist = Artist.query.get(artist_id)
  today = datetime.now()
  upshow = []
  pastshow = []
  countup = 0
  countpast = 0

  queryshow = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > today)
  for show in queryshow:
    countup =countup +1
    queryvenue = Venue.query.filter(Venue.id == show.venue_id)
    for up in queryvenue:
      upshow.append({
        "venue_id": up.id,
        "venue_name": up.name,
        "venue_image_link": up.image_link,
        "start_time": show.start_time
      }) 
  queryshow = Show.query.filter(Show.artist_id == artist_id ).filter(Show.start_time <= today)
  for past in queryshow:
    countpast = countpast +1
    queryvenue= Venue.query.filter(Venue.id == past.venue_id).filter(Show.start_time <= today)
    for p in queryvenue:
      pastshow.append({
        "venue_id": p.id,
        "venue_name": p.name,
        "venue_image_link": p.image_link,
        "start_time": past.start_time
      })

  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link":artist.image_link,
    "past_shows": pastshow,
    "upcoming_shows": upshow,
    "past_shows_count": countpast,
    "upcoming_shows_count": countup,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist= Artist.query.get(artist_id)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  query = Artist.query.get(artist_id)

  try:
    query.name = request.form.get('name')
    query.city = request.form.get('city')
    query.state = request.form.get('state')
    query.phone = request.form.get('phone')
    query.genres = request.form.getlist('genres')
    query.facebook_link = request.form.get('facebook_link')
    query.image_link = request.form.get('image_link')
    
    db.session.commit()
  except:
    db.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  query = Venue.query.get(venue_id)

  try:
    query.name = request.form.get('name')
    query.city = request.form.get('city')
    query.state = request.form.get('state')
    query.address = request.form.get('address')
    query.phone = request.form.get('phone')
    query.genres = request.form.getlist('genres')
    query.facebook_link = request.form.get('facebook_link')
    query.image_link = request.form.get('image_link')
    
    db.session.commit()
  except:
    db.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    name = request.form.get("name")
    city = request.form.get("city")
    state = request.form.get("state")
    phone = request.form.get("phone")
    genres = request.form.getlist('genres')
    facebooklink = request.form.get("facebook_link")
    imagelink = request.form.get("image_link")

  # TODO: modify data to be the data object returned from db insertion
    artist = Artist(name = name, city = city, state = state, phone=phone, genres = genres, image_link = imagelink, facebook_link = facebooklink)
    db.session.add(artist)
    db.session.commit()

  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred' + name + 'could not be added')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = [] 
  shows = Show.query.join(Artist).join(Venue).all()

  for show in shows:
    sh ={
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time":show.start_time
       }
    data.append(sh)
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    show = Show(artist_id = artist_id, venue_id = venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred The show could not added')
    print(sys.exc_info())

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
