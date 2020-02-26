from .import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', views.home_page, name="home_page"),
	path('staff/', views.staff_list, name="staff"),
	path('staff/add/', views.staff_add, name="staff_add"),
	path('staff/save/', views.staff_save, name="staff_save"),
	path('staff/search/', views.staff_search, name="staff_search"),
	path('departments/', views.department_list, name="departments"),
	path('departments/add/', views.department_add, name="department_add"),
	path('departments/update/', views.department_update, name="department_update"),
	path('departments/delete/', views.department_delete, name="department_delete"),
	path('payroll/', views.payroll_list, name="payroll_list"),
	path('async/staff/list/', views.get_staff_list, name="get_staff_list"),
	path('report/department/<int:department>/', views.department_report, name="staff_pdf_report"),
	path('report/bank/<int:department>/', views.bank_report, name="staff_bank_pdf_report"),
	path('report/list/departments', views.list_of_department_report, name="list_of_department_report"),
	path('report/staff/list', views.staff_list_report, name="staff_list_report"),
	path('report/payroll/list', views.payroll_list_report, name="payroll_list_report"),
	path('logout/', auth_views.LogoutView.as_view(), name='logout'),
	path('login/', auth_views.LoginView.as_view(), name='login'),
]