from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from .models import Account


@register(Account)
class AccountIndex(AlgoliaIndex):
    fields = ('username', 'name', 'image_url', 'is_public')
    settings = {'searchableAttributes': ['username', 'name']}