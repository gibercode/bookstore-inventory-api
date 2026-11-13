from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_prefix = f'{settings.API_PREFIX}/{settings.API_VERSION}/'

api_urlpatterns = [
    path('', include('core.urls')),
    # path('books/', include('books.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_prefix, include(api_urlpatterns)),
    path(f'{settings.API_PREFIX}/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        f'{settings.API_PREFIX}/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
]
