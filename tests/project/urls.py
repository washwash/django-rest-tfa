from django.urls import path, include

from test_app.views import dummy_view, login_view


urlpatterns = [
    path('dummy/', dummy_view),
    path('auth/login/', login_view),
    path('auth/tfa/', include('django_rest_tfa.urls')),
]
