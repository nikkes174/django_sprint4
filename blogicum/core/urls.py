from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    path('404/', views.page_not_found, name='page_not_found'),
    path('500/', views.server_error, name='server_error'),
    path('403/', views.csrf_not_posted, name='csrf_error'),

]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
