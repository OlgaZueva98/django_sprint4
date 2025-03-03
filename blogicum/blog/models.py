from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


TITLE_LENGTH = 256
MAX_SYMBOLS = 20

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=TITLE_LENGTH, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:MAX_SYMBOLS]


class Location(BaseModel):
    name = models.CharField(
        max_length=TITLE_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:MAX_SYMBOLS]


class Post(BaseModel):
    title = models.CharField(max_length=TITLE_LENGTH, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — можно делать '
            'отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория'
    )
    image = models.ImageField(
        upload_to='posts_images',
        blank=True,
        verbose_name='Фото'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:MAX_SYMBOLS]


class Comment(BaseModel):
    text = models.TextField(verbose_name='Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('created_at',)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.post.pk})
