from django.urls import path
from . import views
from .views import register_user, user_dashboard, delete_user_product, reset_password
from django.contrib.auth import views as auth_views

app_name = 'app'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/load-more-products/', views.load_more_products, name='load_more_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('tag/<int:tag_id>/', views.tag_detail, name='tag_detail'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('faq/', views.faq, name='faq'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', views.robots, name='robots'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/comment/', views.add_product_comment, name='add_product_comment'),
    path('products/<int:product_id>/chat/', views.start_chat, name='start_chat'),
    path('products/<int:pk>/report/', views.report_abuse, name='report_abuse'),
    path('register/', views.register_product, name='register_product'),
    path('set-language/', views.set_language, name='set_language'),
    path('admin-stats/', views.admin_stats, name='admin_stats'),  # URL for admin dashboard stats
    path('feedback/', views.feedback, name='feedback'),     # Feedback form
    path('dashboard/', views.user_dashboard, name='user_dashboard'),  # User dashboard
    path('my-products/', views.user_products, name='user_products'),  # User products page
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('update-notification-settings/', views.update_notification_settings, name='update_notification_settings'),

    # Management URLs
    path('manage/products/', views.manage_products, name='manage_products'),
    path('manage/products/approve/<int:pk>/', views.approve_product, name='approve_product'),
    path('manage/products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('manage/products/edit/<int:pk>/', views.edit_product, name='edit_product'),

    path('manage/categories/', views.manage_categories, name='manage_categories'),
    path('manage/categories/add/', views.add_category, name='add_category'),
    path('manage/categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('manage/categories/delete/<int:pk>/', views.delete_category, name='delete_category'),

    path('featured-products/', views.featured_products, name='featured_products'),
    path('discounted-products/', views.discounted_products, name='discounted_products'),
    path('register-user/', register_user, name='register_user'),
    path('dashboard/delete-product/<int:pk>/', delete_user_product, name='delete_user_product'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('admin/abuse-reports/', views.abuse_reports, name='abuse_reports'),
    path('admin/abuse-reports/<int:pk>/review/', views.review_abuse_report, name='review_abuse_report'),
    path('admin/contact-messages/', views.contact_messages, name='contact_messages'),
    path('reset-password/', reset_password, name='reset_password'),
    path('jobs/', views.jobs_list, name='jobs_list'),
    path('jobs/new/', views.jobad_create, name='jobad_create'),
    path('jobs/<int:pk>/', views.jobad_detail, name='jobad_detail'),
    path('dashboard/delete-jobad/<int:pk>/', views.delete_jobad, name='delete_jobad'),
    path('requests/', views.requests_list, name='requests_list'),
    path('requests/new/', views.request_create, name='request_create'),
    path('dashboard/delete-request/<int:pk>/', views.delete_user_request, name='delete_user_request'),
    path('health/', views.health, name='health'),
    path('status/', views.status, name='status'),  # صفحه status کامل - فقط ادمین
    
    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
    path('api/notifications/count/', views.get_unread_notifications_count, name='get_unread_notifications_count'),
    path('api/notifications/recent/', views.get_recent_notifications, name='get_recent_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Chat URLs
    path('api/send-chat-message/<int:product_id>/', views.send_chat_message, name='send_chat_message'),
    path('api/get-chat-messages/<int:product_id>/', views.get_chat_messages, name='get_chat_messages'),
    
    # Admin Notification URLs
    path('admin/send-notification-all/', views.send_notification_to_all_users, name='send_notification_to_all_users'),
    path('admin/send-notification-user/', views.send_notification_to_user, name='send_notification_to_user'),
]
