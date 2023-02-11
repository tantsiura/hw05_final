from core.models import PubdateModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='group_title',)
    description = models.TextField(verbose_name='group_description',)
    slug = models.SlugField(
        blank=True,
        null=False,
        unique=True,
        verbose_name='group_slug',
    )

    def __str__(self):
        return self.title


class Post(PubdateModel):
    text = models.TextField(
        verbose_name='post_text',
        help_text='Введите текст поста'
    )

    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='group_of_post'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='author'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:settings.ITEMS_PER_PAGE]


class Comment(PubdateModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='post'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='author'
    )
    text = models.TextField(
        verbose_name='comment_text',
        help_text='Введите текст комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:settings.ITEMS_PER_PAGE]

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='author',
        help_text='Пользователь, который подписывается на автора'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='author',
        help_text='Пользователь, на которого подписываются'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='author unique'
            ),
            models.CheckConstraint(
                check=models.Q(author__lt=models.F('user')) | models.Q(
                    author__gt=models.F('user')), name='dont subsctibe yself'
            )
        ]
