from  django.urls import path
from . import views

urlpatterns = [
    path('',views.loginView,name='login'),
    path('register/',views.registerView,name='register'),
    path('profile/',views.profile,name='profile'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('add_category/',views.add_category,name='add_cat'),
    path('add_expense/',views.add_expense,name='add_exp'),
    path('edit_expense/<int:id>/',views.edit_expense,name='edit_exp'),
    path('delete_expense/<int:id>/',views.delete_expense,name='delete_exp'),
    path('set_budget/',views.set_budget,name='set_budget'),
    path('add_income/',views.add_income,name='add_inc'),
    path('income_list/', views.income_list, name='income_list'),
    path('edit_inc/<int:id>/',views.edit_income,name='edit_inc'),
    path('delete_income/<int:id>/',views.delete_income,name='del_inc'),
    path('cat_chart/',views.cat_chart,name='cat_chart'),
    path('logout/',views.logoutView,name='logout')
]
