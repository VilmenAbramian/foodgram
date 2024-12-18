from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from api.views import RedirectToRecipeView

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('s/<int:pk>/', RedirectToRecipeView.as_view(), name='short-link'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
