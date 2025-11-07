from django.contrib import admin
from django.urls import path
from front import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Администрирование и аутентификация
    path('admin/', admin.site.urls, name='admin'),
    path('myadmin/', views.custom_admin_dashboard, name='custom_admin'),  # Кастомная админка
    path('myadmin/<str:model_name>/', views.custom_admin_model, name='custom_admin_model'),
    path('myadmin/<str:model_name>/add/', views.custom_admin_add, name='custom_admin_add'),
    path('myadmin/<str:model_name>/<int:object_id>/edit/', views.custom_admin_edit, name='custom_admin_edit'),
    path('myadmin/<str:model_name>/<int:object_id>/delete/', views.custom_admin_delete, name='custom_admin_delete'),
    path('admin/', admin.site.urls, name='admin'),
    path('', views.main_page, name='main_page'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('modal/register/', views.modal_register_view, name='modal_register'),
    path('modal/login/', views.modal_login_view, name='modal_login'),
    path('profile/', views.profile_view, name='profile'),
    
    # 1. Каталог товаров
    path('catalog/', views.catalog_view, name='catalog'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    
    # 2. Корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # 3. Избранное
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/add/<int:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:favorite_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    
    # 4. Заказы
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('orders/', views.orders_view, name='orders'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    
    # 5. Отзывы
    path('reviews/', views.reviews_view, name='reviews'),
    
    # 6-7. Заявки
    path('application/new/', views.application_form_view, name='application_form'),
    path('application/success/', views.application_success_view, name='application_success'),
    path('applications/', views.user_applications_view, name='user_applications'),
    path('application/edit/<int:application_id>/', views.edit_application_view, name='edit_application'),
    
    # 8. Новости
    path('news/', views.news_list_view, name='news_list'),
    path('news/<int:news_id>/', views.news_detail_view, name='news_detail'),
    
    # 9. Форум
    path('forum/', views.forum_list_view, name='forum_list'),
    path('forum/topic/<int:topic_id>/', views.forum_topic_view, name='forum_topic'),
    path('forum/topic/create/', views.create_forum_topic_view, name='create_forum_topic'),
    path('forum/topic/<int:topic_id>/edit/', views.edit_forum_topic_view, name='edit_forum_topic'),
    
    # 10. Бронирование столов
    path('tables/', views.tables_catalog_view, name='tables_catalog'),
    path('tables/<int:table_id>/', views.table_detail_view, name='table_detail'),
    path('reservations/', views.user_reservations_view, name='user_reservations'),
    path('reservations/cancel/<int:reservation_id>/', views.cancel_reservation_view, name='cancel_reservation'),

    # 11. Контакты
    path('contacts/', views.contacts, name='contacts'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)