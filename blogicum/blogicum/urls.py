from django.conf import settings
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.conf.urls.static import static
from django.urls import include, path, reverse_lazy
from django.views.generic import CreateView

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('pages/', include('pages.urls', namespace='pages')),
    path(
        'admin/', admin.site.urls),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pages.views.page_not_found'
handler403 = 'pages.views.csrf_not_posted'
handler500 = 'pages.views.server_error'
