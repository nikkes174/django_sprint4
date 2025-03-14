from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .constants import MAX_LENGTH_TITLE, MAX_LENGTH_NAME, MAX_LENGTH_SLUG
from .querysets import FilteredQuerySet

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_TITLE)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        help_text='Идентификатор страницы для URL; разрешены символы '
                  'латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)


class Location(PublishedModel):
    name = models.CharField('Название места', max_length=MAX_LENGTH_NAME)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)


class Post(PublishedModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_TITLE)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно делать '
                  'отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        'Фото',
        upload_to='blog_images',
        blank=True,
        null=True
    )
    objects = FilteredQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id])

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация',
        related_name='comments'

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    text = models.TextField('Текст комментария', max_length=MAX_LENGTH_TITLE)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
