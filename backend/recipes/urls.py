from django.urls import path
from api.views import redirect_to_recipe

urlpatterns = [
    path('<int:pk>/', redirect_to_recipe, name='short-link'),
]
