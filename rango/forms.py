import re

from django import forms
from django.core.exceptions import ValidationError

from rango.models import Category
from rango.models import Page
from rango.models import UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text='Category Name:')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name',)
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not re.match(r'^[a-zA-Z0-9\s.]*$', name):
            raise ValidationError('Only alphanumeric characters and '
                                  'whitespace are allowed.')
        return name


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text='Please enter the title'
                            ' of the page.')
    url = forms.URLField(max_length=200, help_text='Please enter the url of '
                         'the page', widget=forms.TextInput)
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def clean_url(self):
        url = self.cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = 'http://' + url

        return url

    class Meta:
        model = Page
        exclude = ('category', 'added_by')


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(required=False, widget=forms.TextInput)
    picture = forms.ImageField(required=False)

    def clearn_website(self):
        website = self.cleaned_data.get('website')

        if website and not website.startswith('http://'):
            website = 'http://' + website

        return website

    class Meta:
        model = UserProfile
        exclude = ('user', 'liked_categories')
