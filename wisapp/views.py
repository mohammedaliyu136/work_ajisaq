from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Staff, Department
from django.contrib import messages
from .forms import StaffAddForm
from django.http import HttpResponse
from weasyprint import HTML, CSS
from django.template.loader import get_template
from datetime import date
import datetime
from datetime import timedelta
from django.db.models import Q


def home_page(request):
	temp = 'wisapp/home.html'
	departments_count = Department.objects.all().count()
	staff_count = Staff.objects.all().count()
	ct = {
		'departments_count': departments_count,
		'staff_count': staff_count
		}
	return render(request, temp, ct)

def staff_list(request):
	departments = Department.objects.all()
	ct = {'departments': departments}
	temp = 'wisapp/staff_list.html'
	return render(request, temp, ct)

def payroll_list(request):
	departments = Department.objects.all()
	ct = {'departments': departments}
	temp = 'wisapp/payroll.html'
	return render(request, temp, ct)

def department_list(request):
	temp = 'wisapp/department_list.html'
	departments = Department.objects.all()
	ct = {'departments': departments}
	return render(request, temp, ct)

def get_staff_list(request):
	print(request.GET.get('dept_id'))
	print(request.GET.get('employment_status'))
	employment_status = request.GET.get('employment_status')
	temp = 'wisapp/async/async_staff_list.html'
	dept_id = request.GET.get('dept_id')
	print(request.GET)
	#staff_list = Staff.objects.filter(department=dept_id)
	#-------------------------------
	date_of_retirement_date_of_employment = datetime.datetime.now() - datetime.timedelta(days=30*365)
	date_of_birth_date_of_employment = datetime.datetime.now() - datetime.timedelta(days=60*365)
	print("00000000000000000000000")
	print(date_of_retirement_date_of_employment)
	#still_working = Staff.objects.filter(date_of_employment__gt=latest_retirees_dob)
	still_working = Staff.objects.filter(Q(department=dept_id) & Q(date_of_employment__gt=date_of_retirement_date_of_employment) & Q(date_of_birth__gt=date_of_birth_date_of_employment))
	retired = Staff.objects.filter(Q(department=dept_id) & Q(date_of_employment__lte=date_of_retirement_date_of_employment) | Q(date_of_birth__lte=date_of_birth_date_of_employment))
	print(len(still_working))
	print(len(retired))
	if(employment_status=="all"):
		staff_list = Staff.objects.filter(department=dept_id)
	elif(employment_status=="Retired"):
		staff_list=retired
	else:
		staff_list=still_working
	#-------------------------------
	ct = {
		'staff_list': staff_list,
	}

	return render(request, temp, ct)

def staff_add(request):
	departments = Department.objects.all()
	ct = {'departments': departments}
	temp = 'wisapp/staff_add.html'
	return render(request, temp, ct)

def department_add(request):
	if request.method == 'POST':
		data = request.POST
		dept_name = data.get('dept_name')
		dept_code = data.get('dept_code')
		dept_head = data.get('dept_head')

		Department.objects.create(
			name=dept_name,
			dept_id=dept_code,
			hod=dept_head
		).save()

		messages.success(request, f'{dept_name} was successfully added')

		return redirect('departments')
	else:
		messages.error(request, f'Only POST request is allowed')
		return redirect('departments')

def department_update(request):
	if request.method == 'POST':
		data = request.POST
		dept_id = data.get('dept_name_id')
		dept_name = data.get('dept_name')
		dept_code = data.get('dept_code')
		dept_head = data.get('dept_head')

		department = Department.objects.get(pk=dept_id)
		department.name = dept_name
		department.dept_id = dept_code
		department.hod = dept_head
		department.save()
		print(department.dept_id)
		messages.success(request, f'{dept_name} was successfully updated')

		return redirect('departments')
	else:
		messages.error(request, f'Only POST request is allowed')
		return redirect('departments')

def department_delete(request):
	if request.method == 'POST':
		data = request.POST
		dept_id = data.get('dept_name_id')

		department = Department.objects.get(pk=dept_id)
		staff = Staff.objects.filter(department=department)
		print(staff.count)
		messages.success(request, f'{len(staff)} was successfully updated')

		return redirect('departments')
	else:
		messages.error(request, f'Only POST request is allowed')
		return redirect('departments')

def staff_save(request):
	context = {}
	if request.method == 'POST':
		form = StaffAddForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, f'record successfully added')
			return redirect('staff_add')
		else:
			departments = Department.objects.all()
			context =  {"form": form, "departments": departments}
	return render(request, 'wisapp/staff_add.html', context)


def staff_search(request):
	from django.db.models import Q
	keyword = request.GET.get('q')
	query_r = Staff.objects.filter(
		Q(nimc__contains=keyword) |
		Q(first_name__contains=keyword) |
		Q(last_name__contains=keyword)
	)
	temp = 'wisapp/async/search_results.html'
	return render(request, temp, {
		'staff_list': query_r,
		}
	)

def department_report(request, department):
	department = Department.objects.get(id=department)
	staff_list = Staff.objects.filter(department=department.id)
	ct = {
		'staff_list': staff_list, 
		'department': department
	}
	template = "wisapp/report/department.html"
	template = get_template(template)
	html = template.render(ct)

	css_string = """@page {
		size: a4 portrait;
		margin: 1mm;
		counter-increment: page;
	}"""

	pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
			stylesheets=[CSS(string=css_string)],presentational_hints=True)
	#pdf_file=""


	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="STAFF LIST FOR THE DEPARTMENT OF '+department.name+'.pdf"'
	return response
	return HttpResponse(response.getvalue(), content_type='application/pdf')

def list_of_department_report(request):
	department = Department.objects.all()
	#staff_list = Staff.objects.filter(department=department.id)
	ct = {
		#'staff_list': staff_list, 
		'departments': department
	}
	template = "wisapp/report/list_of_departments.html"
	template = get_template(template)
	html = template.render(ct)

	css_string = """@page {
		size: a4 portrait;
		margin: 1mm;
		counter-increment: page;
	}"""

	pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
			stylesheets=[CSS(string=css_string)],presentational_hints=True)
	#pdf_file=""


	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="LIST OF DEPARTMENTS.pdf"'
	return response
	return HttpResponse(response.getvalue(), content_type='application/pdf')

def bank_report(request, department):
	department = Department.objects.get(id=department)
	staff_list = Staff.objects.filter(department=department.id)
	ct = {
		'staff_list': staff_list, 
		'department': department
	}
	template = "wisapp/report/bank_details.html"
	template = get_template(template)
	html = template.render(ct)

	css_string = """@page {
		size: a4 portrait;
		margin: 1mm;
		counter-increment: page;
	}"""

	pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
			stylesheets=[CSS(string=css_string)],presentational_hints=True)
	#pdf_file = ""

	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="BANK DETAILS FOR STAFF OF '+department.name+' DEPARTMENT.pdf"'
	return response
	return HttpResponse(response.getvalue(), content_type='application/pdf')

#---------------------------reports--------------------------------payroll_list
def staff_list_report(request):
	employment_status = request.GET.get('status')
	dept_id = request.GET.get('department')
	
	#-------------------------------
	date_of_retirement_date_of_employment = datetime.datetime.now() - datetime.timedelta(days=30*365)
	date_of_birth_date_of_employment = datetime.datetime.now() - datetime.timedelta(days=60*365)
	print("00000000000000000000000")
	print(date_of_retirement_date_of_employment)
	#still_working = Staff.objects.filter(date_of_employment__gt=latest_retirees_dob)
	still_working = Staff.objects.filter(Q(department=dept_id) & Q(date_of_employment__gt=date_of_retirement_date_of_employment) & Q(date_of_birth__gt=date_of_birth_date_of_employment))
	retired = Staff.objects.filter(Q(department=dept_id) & Q(date_of_employment__lte=date_of_retirement_date_of_employment) | Q(date_of_birth__lte=date_of_birth_date_of_employment))
	print(len(still_working))
	print(len(retired))
	file_name=""
	if(employment_status=="all"):
		staff_list = Staff.objects.filter(department=dept_id)
		print("++++++++++++++++++++++++++++++++++++")
		print("++++++++++++++++++++++++++++++++++++")
		print("++++++++++++++++++++++++++++++++++++")
		print("++++++++++++++++++++++++++++++++++++")
		print(len(staff_list))
		print(dept_id)
		file_name="All Staff List "+str(datetime.date.today())
	elif(employment_status=="Retired"):
		staff_list=retired
		file_name="All Retired Staff List "+str(datetime.date.today())
	else:
		staff_list=still_working
		file_name="All Active Staff List "+str(datetime.date.today())
	#-------------------------------

	ct = {
		'staff_list': staff_list, 
		'file_name': file_name
		#'department': department
	}
	template = "wisapp/report/staff_list.html"
	template = get_template(template)
	html = template.render(ct)

	css_string = """@page {
		size: a4 portrait;
		margin: 1mm;
		counter-increment: page;
	}"""

	pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
			stylesheets=[CSS(string=css_string)],presentational_hints=True)
	#pdf_file = ""

	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="'+file_name+'.pdf"'
	return response
	return HttpResponse(response.getvalue(), content_type='application/pdf')

def payroll_list_report(request):
	employment_status = request.GET.get('status')
	dept_id = request.GET.get('department')
	
	#-------------------------------
	date_of_retirement_date_of_employment = datetime.datetime.now() - datetime.timedelta(days=30*365)
	date_of_birth_date_of_employment = datetime.datetime.now() - datetime.timedelta(days=60*365)
	print("00000000000000000000000")
	print(date_of_retirement_date_of_employment)
	#still_working = Staff.objects.filter(date_of_employment__gt=latest_retirees_dob)
	still_working = Staff.objects.filter(Q(department=dept_id) & Q(date_of_employment__gt=date_of_retirement_date_of_employment) & Q(date_of_birth__gt=date_of_birth_date_of_employment))
	#retired = Staff.objects.filter(Q(department=dept_id) & Q(date_of_employment__lte=date_of_retirement_date_of_employment) | Q(date_of_birth__lte=date_of_birth_date_of_employment))
	#print(len(still_working))
	#print(len(retired))
	file_name="Payroll Staff List "+str(datetime.date.today())
	#-------------------------------

	ct = {
		'staff_list': still_working, 
		'file_name': file_name
		#'department': department
	}
	template = "wisapp/report/payroll_report.html"
	template = get_template(template)
	html = template.render(ct)

	css_string = """@page {
		size: a4 portrait;
		margin: 1mm;
		counter-increment: page;
	}"""

	pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
			stylesheets=[CSS(string=css_string)],presentational_hints=True)
	#pdf_file = ""

	response = HttpResponse(pdf_file, content_type='application/pdf')
	response['Content-Disposition'] = 'filename="'+file_name+'.pdf"'
	return response
	return HttpResponse(response.getvalue(), content_type='application/pdf')