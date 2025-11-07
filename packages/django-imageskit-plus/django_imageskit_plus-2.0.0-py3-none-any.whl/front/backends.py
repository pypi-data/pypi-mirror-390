from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Если в kwargs есть email или phone, используем их вместо username
        if 'email' in kwargs:
            username = kwargs.get('email')
            field = 'email'
        elif 'phone' in kwargs:
            username = kwargs.get('phone')
            field = 'phone'
        else:
            field = 'username'

        if username is None or password is None:
            return None
            
        try:
            # Строим запрос на основе используемого поля
            if field == 'phone':
                # Нормализация телефона (удаление пробелов, скобок, дефисов)
                clean_phone = ''.join(c for c in username if c.isdigit() or c == '+')
                user = User.objects.get(phone=clean_phone)
            elif field == 'email':
                user = User.objects.get(email__iexact=username)
            else:
                # Если это обычный логин или запрос с неизвестного поля,
                # пробуем найти по всем полям
                user = User.objects.get(
                    Q(phone=username) |
                    Q(email__iexact=username) |
                    Q(username=username)
                )
                
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Если найдено несколько пользователей, возвращаем None для безопасности
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None