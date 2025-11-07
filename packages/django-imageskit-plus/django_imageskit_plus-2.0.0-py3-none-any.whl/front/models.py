from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    # Переопределение стандартных полей
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        null=True,
        blank=True
    )
    
    # Дополнительные поля
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True
    )
    
    address = models.TextField(
        _('address'),
        blank=True
    )
    
    age = models.IntegerField(
        _('age'),
        null=True,
        blank=True
    )
    
    birth_date = models.DateField(
        _('birth date'),
        null=True,
        blank=True
    )
    
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
    ]
    gender = models.CharField(
        _('gender'),
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True
    )
    
    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True
    )
    
    occupation = models.CharField(
        _('occupation'),
        max_length=100,
        blank=True
    )
    
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def get_full_name(self):
        """Возвращает полное имя пользователя."""
        return f'{self.first_name} {self.last_name}'
    
    def __str__(self):
        full_name = self.get_full_name()
        if full_name.strip():
            return full_name
        return self.username

# 1. Модели для каталога
class Category(models.Model):
    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    image = models.ImageField(_('image'), upload_to='categories/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    
    def __str__(self):
        return self.name or ''

class Product(models.Model):
    name = models.CharField(_('name'), max_length=200, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(_('image'), upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
    
    def __str__(self):
        return self.name or ''

# 2. Модель для корзины
class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(_('quantity'), default=1, blank=True, null=True)
    added_at = models.DateTimeField(_('added at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else ''}"
    
    def get_total(self):
        if self.product and self.product.price and self.quantity:
            return self.product.price * self.quantity
        return 0

# 3. Модель для избранного
class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    added_at = models.DateTimeField(_('added at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')
        # Избранное должно быть уникальным для пары пользователь-продукт
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username if self.user else ''} - {self.product.name if self.product else ''}"

# 4. Модели для заказов
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='orders', blank=True, null=True)
    status = models.CharField(_('status'), max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    shipping_address = models.TextField(_('shipping address'), blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('email'), blank=True, null=True)
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username if self.user else ''}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(_('quantity'), default=1, blank=True, null=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else ''}"
    
    def get_total(self):
        if self.price and self.quantity:
            return self.price * self.quantity
        return 0

# 5. Модель для отзывов
class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='reviews', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', blank=True, null=True)
    rating = models.IntegerField(_('rating'), choices=RATING_CHOICES, blank=True, null=True)
    comment = models.TextField(_('comment'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
    
    def __str__(self):
        return f"Review by {self.user.username if self.user else ''} for {self.product.name if self.product else ''}"

# 6. Модель для заявок
class Application(models.Model):
    STATUS_CHOICES = [
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('rejected', _('Rejected')),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='applications', blank=True, null=True)
    title = models.CharField(_('title'), max_length=200, blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    field1 = models.CharField(_('field 1'), max_length=200, blank=True, null=True)
    field2 = models.CharField(_('field 2'), max_length=200, blank=True, null=True)
    field3 = models.CharField(_('field 3'), max_length=200, blank=True, null=True)
    field4 = models.CharField(_('field 4'), max_length=200, blank=True, null=True)
    field5 = models.CharField(_('field 5'), max_length=200, blank=True, null=True)
    field6 = models.CharField(_('field 6'), max_length=200, blank=True, null=True)
    field7 = models.CharField(_('field 7'), max_length=200, blank=True, null=True)
    field8 = models.CharField(_('field 8'), max_length=200, blank=True, null=True)
    field9 = models.IntegerField(_('field 9'), blank=True, null=True)
    field10 = models.DateField(_('field 10'), blank=True, null=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='new', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('application')
        verbose_name_plural = _('applications')
    
    def __str__(self):
        return f"Application #{self.id} - {self.title or ''}"

# 8. Модель для новостей
class News(models.Model):
    title = models.CharField(_('title'), max_length=200, blank=True, null=True)
    content = models.TextField(_('content'), blank=True, null=True)
    image = models.ImageField(_('image'), upload_to='news/', blank=True, null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='news', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('news')
        verbose_name_plural = _('news')
    
    def __str__(self):
        return self.title or ''

# 9. Модели для форума
class ForumTopic(models.Model):
    title = models.CharField(_('title'), max_length=200, blank=True, null=True)
    content = models.TextField(_('content'), blank=True, null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='forum_topics', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('forum topic')
        verbose_name_plural = _('forum topics')
    
    def __str__(self):
        return self.title or ''

class ForumComment(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='comments', blank=True, null=True)
    content = models.TextField(_('content'), blank=True, null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='forum_comments', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('forum comment')
        verbose_name_plural = _('forum comments')
    
    def __str__(self):
        return f"Comment by {self.author.username if self.author else ''} on {self.topic.title if self.topic else ''}"

# 10. Модели для бронирования столов
class Table(models.Model):
    TABLE_STATUS_CHOICES = [
        ('available', _('Доступен')),
        ('reserved', _('Зарезервирован')),
        ('occupied', _('Занят')),
        ('maintenance', _('На обслуживании')),
    ]
    
    TABLE_LOCATION_CHOICES = [
        ('indoor', _('В помещении')),
        ('outdoor', _('На улице')),
        ('vip', _('VIP-зона')),
    ]
    
    number = models.IntegerField(_('номер стола'), unique=True)
    seats = models.IntegerField(_('количество мест'))
    location = models.CharField(_('расположение'), max_length=20, choices=TABLE_LOCATION_CHOICES, default='indoor')
    status = models.CharField(_('статус'), max_length=20, choices=TABLE_STATUS_CHOICES, default='available')
    description = models.TextField(_('описание'), blank=True, null=True)
    image = models.ImageField(_('изображение'), upload_to='tables/', blank=True, null=True)
    price_per_hour = models.DecimalField(_('цена за час'), max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('стол')
        verbose_name_plural = _('столы')
        ordering = ['number']
    
    def __str__(self):
        return f"Стол #{self.number} ({self.get_location_display()}, {self.seats} мест)"
    
    def is_available(self):
        return self.status == 'available'
    
class TableReservation(models.Model):
    RESERVATION_STATUS_CHOICES = [
        ('pending', _('Ожидает подтверждения')),
        ('confirmed', _('Подтверждено')),
        ('completed', _('Завершено')),
        ('cancelled', _('Отменено')),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations', verbose_name=_('стол'))
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='table_reservations', verbose_name=_('пользователь'))
    start_time = models.DateTimeField(_('время начала'))
    end_time = models.DateTimeField(_('время окончания'))
    guests_count = models.IntegerField(_('количество гостей'), default=1)
    status = models.CharField(_('статус'), max_length=20, choices=RESERVATION_STATUS_CHOICES, default='pending')
    notes = models.TextField(_('примечания'), blank=True, null=True)
    created_at = models.DateTimeField(_('создано'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('бронирование стола')
        verbose_name_plural = _('бронирования столов')
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Бронь #{self.id} - Стол #{self.table.number} ({self.start_time.strftime('%d.%m.%Y %H:%M')})"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_('Время окончания должно быть позже времени начала'))
        
        # Проверка, что стол определен
        if not hasattr(self, 'table') or self.table is None:
            return  # Пропускаем проверку пересечений, если стол еще не определен
        
        # Проверка на пересечение с существующими бронированиями
        overlapping_reservations = TableReservation.objects.filter(
            table=self.table,
            status__in=['pending', 'confirmed'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if overlapping_reservations.exists():
            raise ValidationError(_('На это время стол уже забронирован'))