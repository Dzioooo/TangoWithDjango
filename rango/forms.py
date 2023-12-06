import re

from django import forms
from django.core.exceptions import ValidationError

from rango.models import Category
from rango.models import Page
from rango.models import UserProfile


class CategoryForm(forms.ModelForm):
    """
    Form for creating or updating a category.

    Attribtues:
        name (CharField): the name of the category.

        views (IntegerField): the number of views for the category,
        default value is zero and it is a hidden field.

        likes (IntegerField): the number of likes for the category,
        default value is zero and it is a hidden field.

        slug (CharField): the slug type of the category name, it is a
        hidden field.
    """
    name = forms.CharField(max_length=128, help_text='Category Name:')
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name',)

    def clean_name(self):
        """
        Category name validation.

        It checks if the category name contains any special characters,
        if it contains a special character, it will prompt or display
        the error message.

        Returns:
            name (str): the category name.

        Raises:
            ValidationError: if the name contains special characters.
        """
        name = self.cleaned_data.get('name')
        if not re.match(r'^[a-zA-Z0-9\s.]*$', name):
            raise ValidationError('Only alphanumeric characters and '
                                  'whitespace are allowed.')
        return name


class PageForm(forms.ModelForm):
    """
    Form for creating or updating a page.

    Attributes:
        title (CharField): the title of the page.

        url (URLField): the URL of the page.

        views (IntegerField): the views of the page.
    """
    title = forms.CharField(max_length=128, help_text='Please enter the title'
                            ' of the page.')
    url = forms.URLField(max_length=200, help_text='Please enter the url of '
                         'the page', widget=forms.TextInput)
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def clean_url(self):
        """
        Cleans and validates the URL field.

        Returns:
            url (str): The cleaned url value.
        """
        url = self.cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = 'http://' + url

        return url

    class Meta:
        model = Page
        exclude = ('category', 'added_by')


class UserProfileForm(forms.ModelForm):
    """
    Form for creating or updating a user profile.

    Attributes:
        website (URLField): the user's website URL.

        picture (ImageField): the user's profile picture.
    """
    website = forms.URLField(required=False, widget=forms.TextInput)
    picture = forms.ImageField(required=False)

    def clean_website(self):
        """
        Cleans and validates the URL field.

        Returns:
            website (str): The cleaned url value.
        """
        website = self.cleaned_data.get('website')

        if website and not website.startswith('http://'):
            website = 'http://' + website

        return website

    class Meta:
        model = UserProfile
        exclude = ('user', 'liked_categories')
