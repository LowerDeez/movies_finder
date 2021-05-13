from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from telegram import InlineKeyboardButton
from telegram.ext import ConversationHandler

__all__ = (
    'ACTION_CHOICES',
    'STATE_CHOICES',
    'CONSTS',
    'YEARS_CHOICES',
    'END',
    'BACK_BUTTON'
)


ACTION_CHOICES = Choices(
    ('search_movies', 'Search movies'),
    ('discover_movies', 'Discover movies'),
    ('popular', 'Popular'),
    ('top_rated', 'Top rated'),
    ('upcoming', 'Upcoming'),
    ('now_playing', 'Now playing'),
    ('select_genre', 'Select genre'),
    ('select_years', 'Select years'),
    ('discover', 'Discover'),
    ('show_search_params', 'Show params'),
    ('next_movies', 'Next movies'),
    ('clear_search_params', 'Clear search params')
)
STATE_CHOICES = Choices(
    ('selecting_action', 'Selection action'),
    ('searching_movies', 'Searching movies'),
    ('displaying_movies', 'Displaying movies'),
    ('listing_movies', 'Listing movies'),
    ('discovering_movies', 'Discovering movies'),
    ('selecting_search_param', 'Selecting genre'),
    ('stopping', 'Stopping'),
    ('showing_search_params', 'Showing'),
)
CONSTS = Choices(
    ('search_params', 'Search params'),
    ('current_search_param', 'Current feature'),
    ('genres', 'Genre'),
    ('years', 'Years'),
    ('page', 'Page'),
    ('search_keyword', 'Search keyword'),
    ('list_method', 'List method')
)

YEARS_CHOICES = (
    ('1900-1990', '-1990'),
    ('1991-1995', '1991-1995'),
    ('1996-2000', '1996-2000'),
    ('2001-2005', '2001-2005'),
    ('2006-2010', '2006-2010'),
    ('2011-2015', '2011-2015'),
    (f'2016-{now().year}', f'2016-{now().year}'),
)

END = ConversationHandler.END

BACK_BUTTON = [
    InlineKeyboardButton(
        text=str(_('Back')),
        callback_data=str(END)
    )
]
