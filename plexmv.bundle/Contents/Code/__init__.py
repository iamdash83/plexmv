import ssl, urllib2

API_URL = 'https://imvdb.com/api/v1'

def Start():

  HTTP.CacheTime = CACHE_1WEEK
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12.4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30'
  HTTP.Headers['Referer'] = 'http://www.imdb.com/'
  IMVDB-APP-KEY: iQUCIOYd1awwxnXdibbKYtoq1cIsdxNvoI86x6kz

def ValidatePrefs():

  pass

####################################################################################################
class IMVDbAPI(Agent.MusicVideos):

  name = 'Internet Music Video Database'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = [
    'com.plexapp.agents.imvdb',
  ]

  def search(self, results, media, lang):

    if media.primary_agent == 'com.plexapp.agents.imvdb':

      imdb_id = media.primary_metadata.id

    elif media.primary_agent == 'com.plexapp.agents.themoviedb':

      # Get the IMDb id from the Movie Database Agent
      imdb_id = Core.messaging.call_external_function(
        'com.plexapp.agents.themoviedb',
        'MessageKit:GetImdbId',
        kwargs = dict(
          tmdb_id = media.primary_metadata.id
        )
      )

      if not imdb_id:
        Log("*** Could not find IMDb id for movie with The Movie Database id: %s ***" % (media.primary_metadata.id))
        return None

    results.Append(MetadataSearchResult(
      id = imdb_id,
      score = 100
    ))

  def update(self, metadata, media, lang):

    url = API_URL % ('imdb_id', metadata.id)

    try:
      movie = JSON.ObjectFromURL(url, sleep=1.0)
    except:
      Log('*** Failed when trying to open url: %s ***' % (url))
      return None

    if not 'error' in movie:

      # Title
      if Prefs['use_title'] and movie['title']:
        metadata.title = movie['title']
      else:
        metadata.title = None

      # Year
      if Prefs['use_year'] and movie['year']:
        metadata.year = movie['year']
      else:
        metadata.year = None

      # Plot
      if Prefs['use_plot'] and movie['plot']:
        metadata.summary = movie['plot']
      else:
        metadata.summary = None

      # Content rating
      if Prefs['use_content_rating'] and movie['rated']:
        metadata.content_rating = movie['rated']
      else:
        metadata.content_rating = None

      # Release date
      if Prefs['use_release_date'] and movie['released']:
        metadata.originally_available_at = Datetime.ParseDate(movie['released']).date()
      else:
        metadata.originally_available_at = None

      # Genres
      metadata.genres.clear()

      if Prefs['use_genres'] and movie['genres']:
        for genre in movie['genres']:
          metadata.genres.add(genre.strip())

      # Production company
      if Prefs['use_production'] and movie['studio']:
        metadata.studio = movie['studio']
      else:
        metadata.studio = None

      # Directors
      metadata.directors.clear()

      if Prefs['use_directors'] and movie['directors']:
        for director in movie['directors']:
          try:
            meta_director = metadata.directors.new()
            meta_director.name = director
          except:
            try:
              metadata.directors.add(director)
            except:
              pass

      # Writers
      metadata.writers.clear()

      if Prefs['use_writers'] and movie['writers']:
        for writer in movie['writers']:
          try:
            meta_writer = metadata.writers.new()
            meta_writer.name = writer
          except:
            try:
              metadata.writers.add(writer)
            except:
              pass

      # Actors
      metadata.roles.clear()

      if Prefs['use_actors'] and movie['actors']:
        for actor in movie['actors']:
          role = metadata.roles.new()
          try:
            role.name = actor
          except:
            try:
              role.actor = actor
            except:
              pass

      # Runtime
      if Prefs['use_runtime'] and movie['runtime']:
         metadata.duration = movie['runtime'] * 1000
      else:
        metadata.duration = None

      # Poster
      valid_names = list()

      if Prefs['use_poster'] and movie['poster']:

        fullsize = '%s.jpg' % (movie['poster'].rsplit('_', 1)[0])
        thumb = '%s_SX300.jpg' % (movie['poster'].rsplit('_', 1)[0])

        valid_names.append(fullsize)

        if fullsize not in metadata.posters:

          req = urllib2.Request(thumb)
          ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
          preview = urllib2.urlopen(req, context=ctx).read()

          metadata.posters[fullsize] = Proxy.Preview(preview)

      metadata.posters.validate_keys(valid_names)

      # Rating
      if Prefs['use_rating']:

        rating_imdb = None
        rating_rt = None

        if 'imdb' in movie['ratings']:
          rating_imdb = float(movie['ratings']['imdb'])

        if 'rt' in movie['ratings']:
          rating_rt = movie['ratings']['rt']

        if Prefs['rating'] == 'IMDb' and rating_imdb:
          metadata.rating = rating_imdb
        elif Prefs['rating'] == 'Rotten Tomatoes' and rating_rt:
          metadata.rating = float(rating_rt/10)

        if metadata.summary:
          summary = [metadata.summary]
        else:
          summary = []

        if Prefs['add_rating_rt'] and rating_rt:
          summary.append('Rotten Tomatoes: %s%%' % (rating_rt))

        if Prefs['add_rating_imdb'] and rating_imdb:
          summary.append('IMDb: %s' % (rating_imdb))

        if len(summary) > 0:
          summary.reverse()
          metadata.summary = '  ★  '.join(summary)

      else:
        metadata.rating = None

    else:
      Log('*** Failed when processing data from url: %s ***' % (url))
      return None

####################################################################################################
class OmdbApi(Agent.TV_Shows):

  name = 'Open Movie Database'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = [
    'com.plexapp.agents.thetvdb'
  ]

  def search(self, results, media, lang):

    results.Append(MetadataSearchResult(
      id = media.primary_metadata.id,
      score = 100
    ))

  def update(self, metadata, media, lang):

    url = API_URL % ('tvdb_id', metadata.id)

    try:
      series = JSON.ObjectFromURL(url, sleep=1.0)
    except:
      Log('*** Failed when trying to open url: %s ***' % (url))
      return None

    if not 'error' in series:

      # Title
      if Prefs['use_title'] and series['title']:
        metadata.title = series['title']
      else:
        metadata.title = None

      # Year
      #if Prefs['use_year'] and series['year']:
      #  metadata.year = series['year']
      #else:
      #  metadata.year = None

      # Plot
      if Prefs['use_plot'] and series['plot']:
        metadata.summary = series['plot']
      else:
        metadata.summary = None

      # Content rating
      if Prefs['use_content_rating'] and series['rated']:
        metadata.content_rating = series['rated']
      else:
        metadata.content_rating = None

      # Release date
      if Prefs['use_release_date'] and series['released']:
        metadata.originally_available_at = Datetime.ParseDate(series['released']).date()
      else:
        metadata.originally_available_at = None

      # Genres
      metadata.genres.clear()

      if Prefs['use_genres'] and series['genres']:
        for genre in series['genres']:
          metadata.genres.add(genre.strip())

      # Production company
      if Prefs['use_production'] and series['studio']:
        metadata.studio = series['studio']
      else:
        metadata.studio = None

      # Directors
      #metadata.directors.clear()
      #
      #if Prefs['use_directors'] and series['directors']:
      #  for director in series['directors']:
      #    try:
      #      meta_director = metadata.directors.new()
      #      meta_director.name = director
      #    except:
      #      try:
      #        metadata.directors.add(director)
      #      except:
      #        pass

      # Writers
      #metadata.writers.clear()
      #
      #if Prefs['use_writers'] and series['writers']:
      #  for writer in series['writers']:
      #    try:
      #      meta_writer = metadata.writers.new()
      #      meta_writer.name = writer
      #    except:
      #      try:
      #        metadata.writers.add(writer)
      #      except:
      #        pass

      # Actors
      metadata.roles.clear()

      if Prefs['use_actors'] and series['actors']:
        for actor in series['actors']:
          role = metadata.roles.new()
          try:
            role.name = actor
          except:
            try:
              role.actor = actor
            except:
              pass

      # Runtime
      if Prefs['use_runtime'] and series['runtime']:
         metadata.duration = series['runtime'] * 1000
      else:
        metadata.duration = None

      # Poster
      valid_names = list()

      if Prefs['use_poster'] and series['poster']:

        fullsize = '%s.jpg' % (series['poster'].rsplit('_', 1)[0])
        thumb = '%s_SX300.jpg' % (series['poster'].rsplit('_', 1)[0])

        valid_names.append(fullsize)

        if fullsize not in metadata.posters:

          req = urllib2.Request(thumb)
          ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
          preview = urllib2.urlopen(req, context=ctx).read()

          metadata.posters[fullsize] = Proxy.Preview(preview)

      metadata.posters.validate_keys(valid_names)

      # Rating
      if Prefs['use_rating']:

        rating_imdb = None
        rating_rt = None

        if 'imdb' in series['ratings']:
          rating_imdb = float(series['ratings']['imdb'])

        if 'rt' in series['ratings']:
          rating_rt = series['ratings']['rt']

        if Prefs['rating'] == 'IMDb' and rating_imdb:
          metadata.rating = rating_imdb
        elif Prefs['rating'] == 'Rotten Tomatoes' and rating_rt:
          metadata.rating = float(rating_rt/10)

        if metadata.summary:
          summary = [metadata.summary]
        else:
          summary = []

        if Prefs['add_rating_rt'] and rating_rt:
          summary.append('Rotten Tomatoes: %s%%' % (rating_rt))

        if Prefs['add_rating_imdb'] and rating_imdb:
          summary.append('IMDb: %s' % (rating_imdb))

        if len(summary) > 0:
          summary.reverse()
          metadata.summary = '  ★  '.join(summary)

      else:
        metadata.rating = None

    else:
      Log('*** Failed when processing data from url: %s ***' % (url))
      return None
