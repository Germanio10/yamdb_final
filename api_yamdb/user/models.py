from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_user

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'

USER_ROLE = (
    (USER, 'user'),
    (MODERATOR, 'moderator'),
    (ADMIN, 'admin'),
)


class User(AbstractUser):
    username = models.CharField(max_length=80,
                                verbose_name='Логин',
                                help_text='Укажите логин',
                                unique=True,
                                validators=[validate_user])
    email = models.EmailField(max_length=100,
                              verbose_name='Email',
                              help_text='Введите email',
                              unique=True,
                              null=False)
    first_name = models.CharField(max_length=100,
                                  blank=True,
                                  verbose_name='Имя',
                                  help_text='Введите Ваше имя')
    last_name = models.CharField(max_length=100,
                                 blank=True,
                                 verbose_name='Фамилия',
                                 help_text='Введите Вашу фамилию')
    bio = models.TextField(blank=True,
                           verbose_name='Биография',
                           help_text='Расскажите о себе')
    role = models.CharField(max_length=15,
                            verbose_name='Роль',
                            choices=USER_ROLE,
                            default=USER)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser or self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
