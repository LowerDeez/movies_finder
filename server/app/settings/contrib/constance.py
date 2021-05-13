from django.utils.translation import ugettext_lazy as _

from ..default import TEMPLATES

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'constance.context_processors.config',
]

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_DATABASE_CACHE_BACKEND = 'default'

CONSTANCE_ADDITIONAL_FIELDS = {
    'email_field': ['django.forms.EmailField', {}],
    'image_field': ['django.forms.ImageField', {}],
}

CONSTANCE_CONFIG = {
    'MOVIE_DB_API_KEY': ('', _('Movie DB API key'), str),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'General': (
        'MOVIE_DB_API_KEY',
    ),
}
