from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # Django default admin (optional)
    path('accounts/', include('allauth.urls')), # Allauth urls kan user social median ittin seenu
    path('', include('boratiapp.urls')), # App urls keenya hundi as jala jiru
]

# Media files (suuraalee kutaawwan upload godhaman agarsiisuuf)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
