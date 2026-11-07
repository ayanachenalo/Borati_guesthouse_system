from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from boratiapp import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('accounts/', include('allauth.urls')), 
    path('', include('boratiapp.urls')), 
]

# Media files (suuraalee kutaawwan upload godhaman agarsiisuuf)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
