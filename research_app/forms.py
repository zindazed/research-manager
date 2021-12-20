from django import forms
from django.contrib.auth.models import User
from django.db.models import fields
from django.db.models.fields import TimeField
from django.forms.models import ModelForm
from django.forms.widgets import DateInput, PasswordInput, TextInput, Textarea, TimeInput

#contact us form

class Login(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={"class":"d-block d-md-inline bg-light"}))
    password = forms.CharField(label="Password",widget=forms.PasswordInput(attrs={"class":"d-block d-md-inline bg-light"}))

class ContactUs(forms.Form):
    topic = forms.CharField(label="Topic",required=True)
    message = forms.CharField(label="Body",required=True)
    email = forms.CharField(label="Email", required=True)

class Rate(forms.Form):
    ratings = forms.IntegerField(max_value=5, min_value=1 ,required=True)
    review = forms.CharField(max_length=500, required=True)
    email = forms.EmailField(max_length=100,required=True)

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

# class EventForm(forms.Form):
#     name = forms.CharField(max_length=50)
#     date = forms.DateField(widget=DateInput)
#     time = forms.TimeField(required=True, widget=TimeInput)
#     duration = forms.DurationField(widget=TimeInput)
#     description = forms.CharField(widget=Textarea)
#     members = forms.ModelMultipleChoiceField(
#         queryset=Member.objects.all(),
#         widget=forms.CheckboxSelectMultiple
#     )

class SearchForm(forms.Form):
    search = forms.CharField(required=False)
    sort = forms.ChoiceField(choices=[
        ("descriptive_name","Idea (A-Z)"),
        ("descriptive_name_asc","Idea (Z-A)"),
        ("date","Date (descending)"),
        ("date_asc","Date (ascending)"),
        ("progress","Progress (descending)"),
        ("progress_asc","Progress (ascending)"),
        ("ratings","Ratings (descending)"),
        ("ratings_asc","Ratings (ascending)"),
    ])
    #("ratings","Ratings"),("progress","Progress")


class ChangeStatus(forms.Form):
    status = forms.ChoiceField(choices=[
        ("Done","Done"),
        ("Given Up","Given up"),
        ("Being Done","Being Done"),
        ("Not Done","Not Done"),
    ])

class RateForm(forms.Form):
    ratings = forms.IntegerField(max_value=5, min_value=1 ,required=True)
    review = forms.CharField(max_length=500, required=True)