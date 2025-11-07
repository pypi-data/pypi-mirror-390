from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone as django_timezone
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django import forms
from .forms import (
    CustomUserCreationForm, 
    PhoneAuthForm,
    EmailAuthForm,
    UsernameAuthForm,
    CategoryForm,
    ProductForm,
    CartItemForm,
    CartItemQuantityForm,
    OrderForm,
    ReviewForm,
    ApplicationForm,
    NewsForm,
    ForumTopicForm,
    ForumCommentForm,
    TableFilterForm,
    TableReservationForm,
    TableForm,
    UserEditForm,
    OrderEditForm,
    ApplicationEditForm 
)
from .models import (
    CustomUser, 
    Category,
    Product,
    CartItem,
    Favorite,
    Order,
    OrderItem,
    Review,
    Application,
    News,
    ForumTopic,
    ForumComment,
    Table,
    TableReservation,
)
from datetime import datetime, timedelta
from django.contrib import messages

# Проверка, что пользователь - администратор
def is_admin(user):
    return user.is_authenticated and user.is_staff
# Кастомная админ панель с формами для добавления удаления и т.д
@login_required
@user_passes_test(is_admin)
def custom_admin_dashboard(request):
    """Главная страница кастомной админки"""
    models_info = {
        'users': {
            'name': 'Пользователи',
            'count': CustomUser.objects.count(),
            'icon': 'bi-people',
            'color': 'primary'
        },
        'products': {
            'name': 'Товары',
            'count': Product.objects.count(),
            'icon': 'bi-box',
            'color': 'success'
        },
        'categories': {
            'name': 'Категории',
            'count': Category.objects.count(),
            'icon': 'bi-tags',
            'color': 'info'
        },
        'orders': {
            'name': 'Заказы',
            'count': Order.objects.count(),
            'icon': 'bi-cart',
            'color': 'warning'
        },
        'applications': {
            'name': 'Заявки',
            'count': Application.objects.count(),
            'icon': 'bi-file-text',
            'color': 'secondary'
        },
        'news': {
            'name': 'Новости',
            'count': News.objects.count(),
            'icon': 'bi-newspaper',
            'color': 'danger'
        },
        'tables': {
            'name': 'Столы',
            'count': Table.objects.count(),
            'icon': 'bi-table',
            'color': 'dark'
        },
    }
    
    context = {
        'models_info': models_info,
        'page_title': 'Панель управления'
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def custom_admin_model(request, model_name):
    """Список объектов конкретной модели"""
    model_map = {
        'users': (CustomUser, 'Пользователи'),
        'products': (Product, 'Товары'),
        'categories': (Category, 'Категории'),
        'orders': (Order, 'Заказы'),
        'orderitems': (OrderItem, 'Элементы заказов'),
        'reviews': (Review, 'Отзывы'),
        'applications': (Application, 'Заявки'),
        'news': (News, 'Новости'),
        'forumtopics': (ForumTopic, 'Темы форума'),
        'forumcomments': (ForumComment, 'Комментарии форума'),
        'tables': (Table, 'Столы'),
        'reservations': (TableReservation, 'Бронирования'),
        'cartitems': (CartItem, 'Корзина'),
        'favorites': (Favorite, 'Избранное'),
    }
    
    if model_name not in model_map:
        messages.error(request, 'Модель не найдена')
        return redirect('custom_admin')
    
    model, model_name_ru = model_map[model_name]
    objects = model.objects.all()
    
    # Получаем поля модели для отображения в таблице
    fields = [field.name for field in model._meta.fields if field.name not in ['password']]
    
    context = {
        'objects': objects,
        'model_name': model_name,
        'model_name_ru': model_name_ru,
        'fields': fields[:4],  # Показываем только первые 4 поля
        'page_title': f'Управление {model_name_ru.lower()}'
    }
    return render(request, 'admin/model_list.html', context)

@login_required
@user_passes_test(is_admin)
def custom_admin_add(request, model_name):
    """Добавление нового объекта"""
    model_map = {
        'categories': (Category, CategoryForm, 'Категория'),
        'products': (Product, ProductForm, 'Товар'),
        'news': (News, NewsForm, 'Новость'),
        'tables': (Table, TableForm, 'Стол'),
        'users': (CustomUser, CustomUserCreationForm, 'Пользователь'),
        'orders': (Order, OrderForm, 'Заказ'),
        'applications': (Application, ApplicationForm, 'Заявка'),
        'forumtopics': (ForumTopic, ForumTopicForm, 'Тема форума'),
    }
    
    if model_name not in model_map:
        messages.error(request, 'Добавление для этой модели не поддерживается')
        return redirect('custom_admin_model', model_name=model_name)
    
    model, form_class, model_name_ru = model_map[model_name]
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model_name_ru} успешно добавлен!')
            return redirect('custom_admin_model', model_name=model_name)
    else:
        form = form_class()
    
    context = {
        'form': form,
        'model_name': model_name,
        'model_name_ru': model_name_ru,
        'page_title': f'Добавить {model_name_ru.lower()}'
    }
    return render(request, 'admin/model_form.html', context)

@login_required
@user_passes_test(is_admin)
def custom_admin_edit(request, model_name, object_id):
    """Редактирование объекта"""
    model_map = {
        'categories': (Category, CategoryForm, 'Категория'),
        'products': (Product, ProductForm, 'Товар'),
        'news': (News, NewsForm, 'Новость'),
        'tables': (Table, TableForm, 'Стол'),
        'users': (CustomUser, UserEditForm, 'Пользователь'),
        'orders': (Order, OrderEditForm, 'Заказ'),
        'applications': (Application, ApplicationEditForm, 'Заявка'),
        'forumtopics': (ForumTopic, ForumTopicForm, 'Тема форума'),
    }
    
    if model_name not in model_map:
        messages.error(request, 'Редактирование для этой модели не поддерживается')
        return redirect('custom_admin_model', model_name=model_name)
    
    model, form_class, model_name_ru = model_map[model_name]
    obj = get_object_or_404(model, id=object_id)
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model_name_ru} успешно обновлен!')
            return redirect('custom_admin_model', model_name=model_name)
    else:
        form = form_class(instance=obj)
    
    context = {
        'form': form,
        'object': obj,
        'model_name': model_name,
        'model_name_ru': model_name_ru,
        'page_title': f'Редактировать {model_name_ru.lower()}'
    }
    return render(request, 'admin/model_form.html', context)

@login_required
@user_passes_test(is_admin)
def custom_admin_delete(request, model_name, object_id):
    """Удаление объекта"""
    model_map = {
        'categories': (Category, 'Категория'),
        'products': (Product, 'Товар'),
        'news': (News, 'Новость'),
        'tables': (Table, 'Стол'),
        'users': (CustomUser, 'Пользователь'),
    }
    
    if model_name not in model_map:
        messages.error(request, 'Удаление для этой модели не поддерживается')
        return redirect('custom_admin_model', model_name=model_name)
    
    model, model_name_ru = model_map[model_name]
    obj = get_object_or_404(model, id=object_id)
    
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'{model_name_ru} успешно удален!')
        return redirect('custom_admin_model', model_name=model_name)
    
    context = {
        'object': obj,
        'model_name': model_name,
        'model_name_ru': model_name_ru,
        'page_title': f'Удалить {model_name_ru.lower()}'
    }
    return render(request, 'admin/confirm_delete.html', context)


def main_page(request):
    # Get latest news for slider
    latest_news = News.objects.all().order_by('-created_at')[:5]
    # Get popular products for display
    popular_products = Product.objects.all()[:8]
    
    context = {
        'latest_news': latest_news,
        'popular_products': popular_products
    }
    
    return render(request, 'pages/main_page.html', context)

def contacts(request):
    context = {
        'page_title': 'Контакты',
    }
    return render(request, 'pages/contacts.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Используем ModelBackend в качестве бэкенда аутентификации по умолчанию
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main_page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'components/register.html', {'form': form})

@require_http_methods(["POST"])
def modal_register_view(request):
    form = CustomUserCreationForm(request.POST, request.FILES)
    if form.is_valid():
        user = form.save()
        # Используем ModelBackend в качестве бэкенда аутентификации по умолчанию
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return JsonResponse({'success': True, 'redirect': reverse('main_page')})
    
    # Улучшенная обработка ошибок для модального окна регистрации
    errors = {}
    
    # Добавляем ошибки валидации формы
    for field, field_errors in form.errors.items():
        errors[field] = list(field_errors)
    
    # Проверяем на наличие общих (не-полевых) ошибок
    if form.non_field_errors():
        errors['__all__'] = list(form.non_field_errors())
    
    return JsonResponse({'success': False, 'errors': errors}, status=400)

def login_view(request):
    auth_type = request.POST.get('auth_type', request.GET.get('tab', 'username'))
    
    if request.method == 'POST':
        if auth_type == 'phone':
            form = PhoneAuthForm(request.POST)
        elif auth_type == 'email':
            form = EmailAuthForm(request.POST)
        else:
            form = UsernameAuthForm(request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main_page')
    else:
        if auth_type == 'phone':
            form = PhoneAuthForm()
        elif auth_type == 'email':
            form = EmailAuthForm()
        else:
            form = UsernameAuthForm()
    
    return render(request, 'components/login.html', {
        'form': form,
        'active_tab': auth_type
    })

@require_http_methods(["POST"])
def modal_login_view(request):
    auth_type = request.POST.get('auth_type', 'username')
    
    if auth_type == 'phone':
        form = PhoneAuthForm(request.POST)
    elif auth_type == 'email':
        form = EmailAuthForm(request.POST)
    else:
        form = UsernameAuthForm(request.POST)
    
    if form.is_valid():
        user = form.get_user()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return JsonResponse({'success': True, 'redirect': reverse('main_page')})
    
    # Улучшаем обработку ошибок для модального окна
    errors = {}
    
    # Проверяем на наличие общих (не-полевых) ошибок - их добавляем только к __all__
    if form.non_field_errors():
        errors['__all__'] = list(form.non_field_errors())
    
    # Добавляем ошибки валидации формы для конкретных полей
    for field, field_errors in form.errors.items():
        if field != '__all__':  # Не дублируем общие ошибки
            errors[field] = list(field_errors)
    
    return JsonResponse({'success': False, 'errors': errors}, status=400)

def logout_view(request):
    logout(request)
    return redirect('main_page')

# 1. Каталог с фильтрацией
def catalog_view(request):
    categories = Category.objects.all()
    
    # Получение фильтров из GET-параметров
    category_id = request.GET.get('category')
    search_query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Начинаем с полной выборки товаров
    products = Product.objects.all()
    
    # Применяем фильтры
    if category_id:
        products = products.filter(category_id=category_id)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    context = {
        'categories': categories,
        'products': products,
        'selected_category': category_id,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price
    }
    
    return render(request, 'pages/catalog.html', context)

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    
    # Проверяем, добавлен ли товар в избранное пользователя
    is_favorite = False
    favorite_id = None
    if request.user.is_authenticated:
        favorite = Favorite.objects.filter(user=request.user, product=product).first()
        is_favorite = favorite is not None
        if is_favorite:
            favorite_id = favorite.id
    
    # Форма для отзыва
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid() and request.user.is_authenticated:
            review = review_form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product_id)
    else:
        review_form = ReviewForm()
    
    context = {
        'product': product,
        'reviews': reviews,
        'is_favorite': is_favorite,
        'favorite_id': favorite_id,
        'review_form': review_form
    }
    
    return render(request, 'pages/product_detail.html', context)

# 2. Корзина
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Подсчет общей суммы корзины
    total_amount = sum(item.get_total() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    
    return render(request, 'pages/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Проверяем, нет ли уже такого товара в корзине
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    # Если товар уже был в корзине, увеличиваем количество
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = CartItemQuantityForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

# 3. Избранное
@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user)
    
    context = {
        'favorites': favorites
    }
    
    return render(request, 'pages/favorites.html', context)

@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Проверяем, нет ли уже такого товара в избранном
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    # Перенаправляем обратно на страницу продукта
    return redirect('product_detail', product_id=product_id)

@login_required
def remove_from_favorites(request, favorite_id):
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    favorite.delete()
    return redirect('favorites')

# 4. Формирование заказа
@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Если корзина пуста, перенаправляем в корзину
    if not cart_items.exists():
        messages.error(request, 'Ваша корзина пуста')
        return redirect('cart')
    
    # Подсчет общей суммы заказа
    total_amount = sum(item.get_total() for item in cart_items)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                # Создаем заказ
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = total_amount
                order.status = 'pending'  # Добавляем статус по умолчанию
                order.save()
                
                # Добавляем товары из корзины в заказ
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                
                # Очищаем корзину пользователя
                cart_items.delete()
                
                messages.success(request, 'Ваш заказ успешно создан!')
                return redirect('order_success', order_id=order.id)
                
            except Exception as e:
                messages.error(request, f'Произошла ошибка при создании заказа: {str(e)}')
                return redirect('checkout')
        else:
            # Если форма невалидна, показываем ошибки
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
            print("Form errors:", form.errors)  # Для отладки
    else:
        # Предзаполняем форму данными из профиля пользователя
        initial_data = {}
        if request.user.address:
            initial_data['shipping_address'] = request.user.address
        if request.user.phone:
            initial_data['phone'] = request.user.phone
        if request.user.email:
            initial_data['email'] = request.user.email
            
        form = OrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    
    return render(request, 'pages/checkout.html', context)

@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order
    }
    
    return render(request, 'pages/order_success.html', context)

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'pages/orders.html', context)

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'pages/order_detail.html', context)

# 5. Отзывы
def reviews_view(request):
    reviews = Review.objects.all().order_by('-created_at')
    
    context = {
        'reviews': reviews
    }
    
    return render(request, 'pages/reviews.html', context)

# 6-7. Заявки
@login_required
def application_form_view(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('application_success')
    else:
        form = ApplicationForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'pages/application_form.html', context)

@login_required
def application_success_view(request):
    return render(request, 'pages/application_success.html')

@login_required
def user_applications_view(request):
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'applications': applications
    }
    
    return render(request, 'pages/user_applications.html', context)

@login_required
def edit_application_view(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect('user_applications')
    else:
        form = ApplicationForm(instance=application)
    
    context = {
        'form': form,
        'application': application
    }
    
    return render(request, 'pages/edit_application.html', context)

# 8. Новости
def news_list_view(request):
    news_list = News.objects.all().order_by('-created_at')
    
    context = {
        'news_list': news_list
    }
    
    return render(request, 'pages/news_list.html', context)

def news_detail_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    
    context = {
        'news': news
    }
    
    return render(request, 'pages/news_detail.html', context)

# 9. Форум
def forum_list_view(request):
    topics = ForumTopic.objects.all().select_related('author').order_by('-created_at')
    
    # Создание новой темы
    if request.method == 'POST' and request.user.is_authenticated:
        form = ForumTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            return redirect('forum_topic', topic_id=topic.id)
    else:
        form = ForumTopicForm()
    
    # Безопасный подсчет комментариев
    for topic in topics:
        # Используем прямое обращение к базе данных для подсчета комментариев
        topic.comment_count = ForumComment.objects.filter(topic=topic).count()
    
    context = {
        'topics': topics,
        'form': form
    }
    
    return render(request, 'pages/forum_list.html', context)

def create_forum_topic_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = ForumTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            return redirect('forum_topic', topic_id=topic.id)
    else:
        form = ForumTopicForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'pages/create_forum_topic.html', context)

def forum_topic_view(request, topic_id):
    """Просмотр темы форума и комментариев"""
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # Безопасное получение комментариев с проверкой автора
    comments = ForumComment.objects.filter(topic=topic).select_related('author').order_by('created_at')
    
    # Добавление нового комментария
    if request.method == 'POST' and request.user.is_authenticated:
        form = ForumCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.topic = topic
            comment.author = request.user
            comment.save()
            return redirect('forum_topic', topic_id=topic_id)
    else:
        form = ForumCommentForm()
    
    context = {
        'topic': topic,
        'comments': comments,
        'form': form
    }
    
    return render(request, 'pages/forum_topic.html', context)

def edit_forum_topic_view(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # Проверка прав на редактирование
    if not request.user.is_authenticated or (request.user != topic.author and not request.user.is_staff):
        return redirect('forum_topic', topic_id=topic_id)
    
    if request.method == 'POST':
        form = ForumTopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return redirect('forum_topic', topic_id=topic_id)
    else:
        form = ForumTopicForm(instance=topic)
    
    context = {
        'form': form,
        'topic': topic
    }
    
    return render(request, 'pages/edit_forum_topic.html', context)

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        # Handle form submission for profile update
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.city = request.POST.get('city', user.city)
        user.country = request.POST.get('country', user.country)
        
        # Handle avatar update
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            
        user.save()
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('profile')
    
    # FIX: Простой запрос без prefetch_related
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'orders': orders
    }
    
    return render(request, 'pages/profile.html', context)

# 10. Бронирование столов
def tables_catalog_view(request):
    tables = Table.objects.all()
    
    # Обработка фильтрации
    filter_form = TableFilterForm(request.GET)
    if filter_form.is_valid():
        location = filter_form.cleaned_data.get('location')
        min_seats = filter_form.cleaned_data.get('min_seats')
        max_price = filter_form.cleaned_data.get('max_price')
        date = filter_form.cleaned_data.get('date')
        
        if location:
            tables = tables.filter(location=location)
        
        if min_seats:
            tables = tables.filter(seats__gte=min_seats)
        
        if max_price:
            tables = tables.filter(price_per_hour__lte=max_price)
        
        # Если указана дата, исключаем столы, которые уже забронированы на эту дату
        if date:
            # Преобразуем дату в начало и конец дня
            start_datetime = django_timezone.combine(date, django_timezone.min.time())
            end_datetime = django_timezone.combine(date, django_timezone.max.time())
            
            # Находим столы, у которых есть бронирования на эту дату
            reserved_tables = TableReservation.objects.filter(
                status__in=['pending', 'confirmed'],
                start_time__lt=end_datetime,
                end_time__gt=start_datetime
            ).values_list('table_id', flat=True)
            
            # Исключаем эти столы из списка
            tables = tables.exclude(id__in=reserved_tables)
    
    context = {
        'tables': tables,
        'filter_form': filter_form
    }
    
    return render(request, 'pages/tables_catalog.html', context)

@login_required
def table_detail_view(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    
    # Если пользователь отправил форму бронирования
    if request.method == 'POST':
        form = TableReservationForm(request.POST)
        if form.is_valid():
            try:
                # Создаем объект бронирования, но не сохраняем пока
                reservation = form.save(commit=False)
                reservation.user = request.user
                reservation.table = table
                
                # Принудительно устанавливаем table_id, чтобы избежать RelatedObjectDoesNotExist
                reservation.table_id = table.id
                
                # Полная проверка перед сохранением
                reservation.full_clean()
                
                # Сохраняем объект после проверки
                reservation.save()
                
                # Обновляем статус стола
                table.status = 'reserved'
                table.save()
                
                messages.success(request, 'Ваше бронирование успешно создано!')
                return redirect('user_reservations')
            
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field if field != '__all__' else None, error)
    else:
        # Предустановка времени начала и окончания с интервалом в 2 часа
        now = django_timezone.now()
        rounded_hour = now.replace(minute=0, second=0, microsecond=0)
        if now.minute > 0:
            rounded_hour += timedelta(hours=1)
        
        initial_data = {
            'start_time': rounded_hour,
            'end_time': rounded_hour + timedelta(hours=2),
            'guests_count': 1
        }
        form = TableReservationForm(initial=initial_data)
    
    # Находим существующие бронирования на ближайшие 7 дней
    start_date = django_timezone.now().date()
    end_date = start_date + timedelta(days=7)
    existing_reservations = TableReservation.objects.filter(
        table=table,
        status__in=['pending', 'confirmed'],
        start_time__date__gte=start_date,
        start_time__date__lte=end_date
    ).order_by('start_time')
    
    context = {
        'table': table,
        'form': form,
        'existing_reservations': existing_reservations
    }
    
    return render(request, 'pages/table_detail.html', context)

@login_required
def user_reservations_view(request):
    reservations = TableReservation.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'reservations': reservations
    }
    
    return render(request, 'pages/user_reservations.html', context)

@login_required
def cancel_reservation_view(request, reservation_id):
    reservation = get_object_or_404(TableReservation, id=reservation_id, user=request.user)
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        
        # Обновляем статус стола, если нет других активных бронирований
        table = reservation.table
        if not TableReservation.objects.filter(
            table=table, 
            status__in=['pending', 'confirmed'],
            start_time__lte=django_timezone.now(),
            end_time__gte=django_timezone.now()
        ).exists():
            table.status = 'available'
            table.save()
        
        messages.success(request, 'Бронирование успешно отменено')
        return redirect('user_reservations')
    
    context = {
        'reservation': reservation
    }
    
    return render(request, 'pages/cancel_reservation.html', context)