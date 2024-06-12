from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    re_path(r"^django-admin/", admin.site.urls),
    re_path(r"^admin/", include(wagtailadmin_urls)),
    re_path(r"^documents/", include(wagtaildocs_urls)),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic import TemplateView

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Add views for testing 404 and 500 templates
    urlpatterns += [
        path(r"^test404/$", TemplateView.as_view(template_name="404.html")),
        path(r"^test500/$", TemplateView.as_view(template_name="500.html")),
    ]

urlpatterns += [path(r"", include(wagtail_urls))]
