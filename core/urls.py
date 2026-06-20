from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('servicos/', views.services, name='services'),
    path('produtos/', views.products, name='products'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('blog/', views.blog, name='blog'),
    path('contato/', views.contact, name='contact'),
    path('contato/sucesso/', views.contact_success, name='contact_success'),
    path('htmx/products/map/', views.htmx_products_map, name='htmx_products_map'),
    path('htmx/products/map/search/', views.htmx_products_map_search, name='htmx_products_map_search'),
    path('htmx/products/chat/', views.htmx_products_chat, name='htmx_products_chat'),
    path('htmx/products/chat/advance/', views.htmx_products_chat_advance, name='htmx_products_chat_advance'),
    path('htmx/products/chat/reset/', views.htmx_products_chat_reset, name='htmx_products_chat_reset'),
    path('htmx/products/kanban/', views.htmx_products_kanban, name='htmx_products_kanban'),
]
