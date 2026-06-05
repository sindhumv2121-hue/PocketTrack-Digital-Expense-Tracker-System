from django import forms
from .models import *

class CategoryForm(forms.ModelForm): #creates formm from model
    class Meta:
        model = Category
        fields = ['name']

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount','source','date']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expenses
        fields = ['amount','category','date']

