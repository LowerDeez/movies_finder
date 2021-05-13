import dj_database_url

from .default import env, MIDDLEWARE, INSTALLED_APPS, DATABASES

heroku_mode_enable = env.bool('HEROKU_MODE', default=False)

if heroku_mode_enable:
    INSTALLED_APPS += [
        'whitenoise',
    ]

    ALLOWED_HOSTS = ['.herokuapp.com']

    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware',)

    prod_db = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(prod_db)
