from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.apps import apps


class FilteredQuerySet(models.QuerySet):
    def prepare_posts(
            self,
            select_related=True,
            annotate_comments=True,
            apply_filters=True):
        Post = apps.get_model('blog', 'Post')
        posts = self
        if apply_filters:
            posts = posts.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        if select_related:
            posts = posts.select_related(
                'location',
                'category',
                'author'
            )
        if annotate_comments:
            posts = (
                posts.annotate(comment_count=Count('comments'))
                .order_by(*Post._meta.ordering)
            )
        return posts
