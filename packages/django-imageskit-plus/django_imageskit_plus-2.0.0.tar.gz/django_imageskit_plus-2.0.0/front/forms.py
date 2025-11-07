from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from .models import (
    CustomUser, Product, Category, CartItem, Favorite, 
    Order, OrderItem, Review, Application, News, 
    ForumTopic, ForumComment, Table, TableReservation
)
from django.utils.translation import gettext_lazy as _


# Добавьте эти формы если их нет

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'seats', 'location', 'status', 'description', 'image', 'price_per_hour']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'seats': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'shipping_address', 'phone', 'email', 'total_amount']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

class ApplicationEditForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'title', 'description']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
        help_text='Введите номер телефона в формате +7XXXXXXXXXX'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'first_name', 'last_name', 
                 'password1', 'password2', 'avatar')
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Проверка формата номера телефона для России
            if not re.match(r'^\+7\d{10}$', phone):
                raise ValidationError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return phone

class PhoneAuthForm(forms.Form):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
        help_text='Введите номер телефона в формате +7XXXXXXXXXX'
    )
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Проверка формата номера телефона для России
            if not re.match(r'^\+7\d{10}$', phone):
                raise ValidationError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        password = cleaned_data.get('password')

        if phone and password:
            self.user = authenticate(phone=phone, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный телефон или пароль")
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

class EmailAuthForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

class UsernameAuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный логин или пароль")
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)

# Новые формы для моделей

# 1. Формы для каталога
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

# 2. Форма для корзины
class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']

class CartItemQuantityForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']

# 3. Форма для избранного (не требуется отдельная форма, будет добавляться через кнопку)

# 4. Формы для заказов
class OrderForm(forms.ModelForm):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '+7XXXXXXXXXX'}),
        help_text='Введите номер телефона в формате +7XXXXXXXXXX',
        required=True
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    shipping_address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Введите адрес доставки'})
    )
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone', 'email']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Более гибкая проверка формата номера телефона
            if not re.match(r'^(\+7|8)\d{10}$', phone.replace(' ', '').replace('-', '')):
                raise ValidationError('Номер телефона должен быть в формате +7XXXXXXXXXX или 8XXXXXXXXXX')
        return phone

# 5. Форма для отзывов
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

# 6. Форма для заявок
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'title', 'description', 'field1', 'field2', 
            'field3', 'field4', 'field5', 'field6', 
            'field7', 'field8', 'field9', 'field10'
        ]

    field10 = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

# 8. Форма для новостей
class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}),
        }

# 9. Формы для форума
class ForumTopicForm(forms.ModelForm):
    class Meta:
        model = ForumTopic
        fields = ['title', 'content']

class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']

# 10. Формы для бронирования столов
class TableFilterForm(forms.Form):
    location = forms.ChoiceField(
        choices=[('', 'Все зоны')] + list(Table.TABLE_LOCATION_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_seats = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Мин. кол-во мест'})
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Макс. цена за час'})
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
class TableReservationForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label=_('Время начала')
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label=_('Время окончания')
    )
    
    class Meta:
        model = TableReservation
        fields = ['start_time', 'end_time', 'guests_count', 'notes']
        exclude = ['table', 'user', 'status', 'created_at']
        widgets = {
            'guests_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }