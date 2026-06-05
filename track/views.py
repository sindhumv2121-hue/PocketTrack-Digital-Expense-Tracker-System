from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *
from django.db.models import Sum
from datetime import datetime
from django.db.models.functions import TruncDay,TruncMonth

@login_required
def profile(request):
    p,created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        p.currency = request.POST.get('currency','₹')
        p.save()
        return redirect('profile')
    return render(request,'profile.html',{'profile':p})

@login_required
def dashboard(request):
    p,created = Profile.objects.get_or_create(user=request.user)
    currency = p.currency or "₹"
    month = request.GET.get('month')
    if month:
        selected_date = datetime.strptime(month,"%Y-%m")
        selected_month = month
    else:
        selected_date = datetime.now()
        selected_month = ""
    month_name = selected_date.strftime('%B %Y')
    search_query = request.GET.get('search','') # '' whn search is missing empty str
    expenses = Expenses.objects.filter(
        user=request.user,
        date__year=selected_date.year,
        date__month=selected_date.month)
    if search_query:
        expenses = expenses.filter(
            category__name__icontains = search_query)

    budget = Budget.objects.filter(
        user = request.user,
        month__year = selected_date.year,
        month__month = selected_date.month
    ).first()

    income = Income.objects.filter(
        user = request.user ,
        date__year = selected_date.year,
        date__month = selected_date.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    expenses_total = expenses.aggregate(
        Sum('amount')
        )['amount__sum'] or 0

    percent = 0
    if budget:
        percent = int(
            (expenses_total/budget.amount) * 100
        ) if budget.amount else 0 

    savings = income - expenses_total
    savings_percent = 100 - percent #remaining budget percentage
    alert_msg = " " 
    if percent >= 100:
        alert_msg = "Budget Exceeded!"
    elif percent >= 75:
        alert_msg = "Warning: Near budget limit"

    top_category = expenses.values(
        'category__name'
    ).annotate(
       total=(Sum('amount'))
    ).order_by(
        '-total'
    ).first()

    avg_daily = round(
        expenses_total / 30 , 2
    ) if expenses_total else 0
    data = expenses.annotate(
        x = TruncDay('date')
        ). values('x'
        ) . annotate (
            total = Sum('amount')
        ).order_by('x') #contains date and expense total in value format of a day

    labels = [
        d['x'].strftime('%d %b')
        for d in data
    ] #x label(01 jun) to display
    totals = [
        float(d['total'])
        for d in data
    ] #expense amt
    max_amount = max(totals) if totals else 1 #find highst expense for a day

    daily_cards = [] #stores daily expense data for template display
    for i,label in enumerate(labels):
        amount = totals[i]
        percent_height = int(
            (amount/max_amount) * 100
        ) if max_amount else 0
        daily_cards.append({
            'day' : label,
            'amount' : amount,
            'percent' : percent_height
        })

    month_data = Expenses.objects.filter(
        user = request.user
    ).annotate(
        m=TruncMonth('date')
    ).values(
        'm'
    ).annotate(
        total = Sum('amount')
    ).order_by('m')

    month_labels = [
        d['m'].strftime('%b')
        for d in month_data
    ]  #x label

    month_totals = [
        float(d['total'])
        for d in month_data
    ] #monthly expense total(y-axis)
    return render(
        request,
        'dashboard.html',
        {
            'income': income,
            'expense': expenses_total,
            'balance': savings,
            'expenses': expenses,
            'search_query': search_query,
            'labels': labels,
            'totals': totals,
            'budget': budget,
            'percent': percent,
            'top_category': top_category,
            'avg_daily': avg_daily,
            'alert_msg': alert_msg,
            'currency': currency,
            'savings_percent': savings_percent,
            'selected_month': selected_month,
            'month_name': month_name,
            'month_labels': month_labels,
            'month_totals': month_totals,
            'daily_cards': daily_cards
        }
    )

def registerView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if not username or not password1 or not password2:
            messages.error(request,"All fields are required")
            return render(request,'register.html')
        if password1 != password2:
            messages.error(request,"Password doesnot match")
            return render(request,'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request,"Username already exists")
            return render(request,'register.html')
        if len(password1) < 8:
            messages.error(request,"Password is too short")
            return render(request,'register.html')
        user = User.objects.create_user(
            username=username,
            password = password1
        ) #creates new user table using username enetered in form n password is hashed(encrypted before saving db)
        Profile.objects.create(user=user) #when new user is created for that new profile is created for that specific user
        return redirect('login')
    return render(request,'register.html')

def loginView(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'],password=request.POST['password'])
        if user:
            login(request,user)
            return redirect('dashboard')
        messages.error(request,"Invalid username or password")
        return render(request,'login.html')
    return render(request,'login.html')
    
def logoutView(request):
    logout(request)
    return redirect('login')

@login_required
def add_expense(request):
    month = request.GET.get('month')
    if month:
        selected_date = datetime.strptime(month,"%Y-%m")
        selected_month = month
    else:
        selected_date = datetime.now()
        selected_month= ""
    month_name = selected_date.strftime( "%B %Y")
    default_date = selected_date.strftime("%Y-%m-01")

    form  = ExpenseForm(request.POST or None)
    if form.is_valid():
        exp = form.save(commit=False) #before saving user need to b added
        exp.user = request.user
        exp.save()
        return redirect('dashboard')
    return render(request,'add_expense.html',{'form':form,'default_date':default_date,'selected_month':selected_month,'month_name':month_name})

@login_required
def edit_expense(request,id):
    exp = get_object_or_404(Expenses,id=id,user=request.user)
    form = ExpenseForm(request.POST or None , instance=exp)#instance is edit existing record(expense) otherwise django creates new expense
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request,'add_expense.html',{'form':form})

@login_required
def delete_expense(request,id):
    Expenses.objects.filter(id=id,user=request.user).delete()
    return redirect('dashboard')
    
@login_required
def add_income(request):
    month = request.GET.get('month')
    if month:
        selected_date = datetime.strptime(month,"%Y-%m")
        selected_month = month
    else:
        selected_date = datetime.now()
        selected_month = ""
    month_name = selected_date.strftime('%B %Y')
    default_date = selected_date.strftime("%Y-%m-01")
    form = IncomeForm(request.POST or None)
    if form.is_valid():
        inc = form.save(commit=False)#saves temporarily
        inc.user = request.user
        inc.save() #after user is addedd its saved in DB
        return redirect('dashboard')
    return render(request,'add_income.html',{'form':form,'default_date':default_date,'month_name':month_name,'selected_month':selected_month})

@login_required
def edit_income(request,id):
    inc = get_object_or_404(Income,id=id,user=request.user)
    form = IncomeForm(request.POST or None , instance=inc)#instance is edit existing record(expense) otherwise django creates new expense
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request,'add_income.html',{'form':form})

@login_required
def delete_income(request,id):
    Income.objects.filter(id=id,user=request.user).delete()
    return redirect('dashboard')

@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    p,created= Profile.objects.get_or_create(user=request.user)# TO GET CURRENTLY LOGGED-IN USERS PROFILE(CURRENCY)
    return render(request, 'income_list.html', {'incomes': incomes,'currency':p.currency})

@login_required
def set_budget(request):
    alert = False
    alert_msg = ""
    month = request.GET.get('month')
    if month:
        selected_date = datetime.strptime(month, "%Y-%m")
        selected_month = month
    else:
        selected_date = datetime.now()
        selected_month = selected_date.strftime('%Y-%m')

    month_name = selected_date.strftime('%B %Y')#CREATE READABLE MONTH
    if request.method == "POST":
        month_value = request.POST.get('month')
        amount = request.POST.get('amount')
        month_date = datetime.strptime(month_value, "%Y-%m").date()
        budget, created = Budget.objects.update_or_create(
            user=request.user,
            month=month_date,
            defaults={'amount': amount}
        )
        month_name = month_date.strftime("%B")#Converts month date into month name.
        alert = True
        if created:
            alert_msg = f"{month_name} budget added successfully!"
        else:
            alert_msg = f"{month_name} budget updated successfully!"
    return render(request, 'set_budget.html', {
        'alert': alert,
        'alert_msg': alert_msg,
        'selected_month':selected_month,
        'month_name':month_name
    })

@login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get('name') #category name from form
        custom = request.POST.get('custom_category')
        if custom:
            name = custom #use custom one instead of selected one
        Category.objects.create(
            user=request.user,
            name=name
        )
        return redirect('dashboard')
    return render(request,'add_category.html')

@login_required
def cat_chart(request):
    expenses = Expenses.objects.filter(user=request.user)
    category_data = expenses.values('category__name')\
        .annotate(total=Sum('amount'))\
        .order_by('category__name')
    chart_labels=[]
    chart_totals=[]
    for c in category_data:
        chart_labels.append(c['category__name']) #adds category name into list(chart_labels)
        chart_totals.append(float(c['total']))
    profile,created = Profile.objects.get_or_create(user=request.user)
    return render(request , 'category_chart.html',{
        'chart_labels':chart_labels,
        'chart_totals':chart_totals,
        'currency':profile.currency
    })
  


 



    



