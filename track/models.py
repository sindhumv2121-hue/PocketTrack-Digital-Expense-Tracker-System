from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model): 
    user = models.OneToOneField(User,on_delete=models.CASCADE) 
    currency = models.CharField(max_length=10,  
        choices=[
        ('₹','Indian Rupee'),
        ('$','US Dollar'),
       ('SGD','Singapore Dollar'),
        ('AED','UAE Dirham'),
    ],
    default='₹'
    )
    
class Category(models.Model):
   name = models.CharField(max_length=150) 
   user = models.ForeignKey(User,on_delete=models.CASCADE) #ONE USER CAN HAVE MAY CATEGORIES
   def __str__(self):
      return self.name

class Income(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    source = models.CharField(max_length=150)

class Expenses(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)

class Budget(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    month = models.DateField()



