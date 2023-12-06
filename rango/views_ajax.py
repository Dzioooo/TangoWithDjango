from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from rango.models import Category
from rango.models import Page



@method_decorator(login_required, name='dispatch')
class LikeCategoryView(View):
    """
    View for handling category liking.

    Attributes:
        cat_id (str): The ID (primary key) of the to be liked category.

        likes (int): The current number of likes of the category.
    """
    cat_id = None
    likes = 0

    def get(self, request, *args, **kwargs):
        """
        Handle GET request for liking a category.

        Retrieves the category ID from the request, adds the category
        to the user's list of liked categories, increments the
        category's like count and lastly, renders the updated like
        count.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The number of likes for the category.
        """
        self.cat_id = request.GET.get('category_id')

        if self.cat_id:
            cat = Category.objects.get(id=int(self.cat_id))
            user = request.user.userprofile

            if cat:
                user.liked_categories.add(cat)
                self.likes = cat.likes + 1
                cat.likes = self.likes
                cat.save()
        return HttpResponse(self.likes)


@method_decorator(login_required, name='dispatch')
class CategorySearchView(View):
    """
    View for searching and retrieving the categories based on the
    search query.

    Attributes:
        starts_with (str): The starting characters for filtering the
        categories.

        cat_list (QuerySet): The list of filtered categories.
    """
    starts_with = None
    cat_list = None
    def get_category_list(self, max_results=0, starts_with=None,
                          *args, **kwargs):
        """
        Get a list of categories based on the filtered query.

        Args:
            max_results (int): The maximum number of results to return.
            starts_with (str): The starting characters for filtering
            categories depending on the entered characters.

        Returns:
            QuerySet: The filtered list of categories.
        """
        if self.starts_with:
            self.cat_list = Category.objects.filter(
                name__istartswith=self.starts_with)
        else:
            self.cat_list = Category.objects.all()

        if max_results > 0:
            if len(self.cat_list) > max_results:
                self.cat_list = self.cat_list[:max_results]
        return self.cat_list

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for category search.

        Retrieves the search suggestion from the request, gets the
        corresponding category list, and renders the 'rango/cats.html'
        template.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: Rendered response with the category list.
        """
        self.starts_with = request.GET['suggestion']

        cat_list = self.get_category_list(8)
        print("cat_list", cat_list)
        return render(request, 'rango/cats.html', {'cats': cat_list})


@method_decorator(login_required, name='dispatch')
class AutoAddPageView(View):
    """
    View for automatically adding a page to a category.

    Attributes:
        template_name (str): The name of the template for rendering the
        page list.

        cat_id (str): The ID of the category to which the page will be
        added.

        url (str): The URL of the page to be added.

        title (str): The title of the page to be added.

        context_dict (dict): The context dictionary for rendering the
        template.
    """
    template_name = 'rango/page_list.html'
    cat_id = None
    url = None
    title = None
    context_dict = {}

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for automatically adding a page.

        Retrieves the category ID, page URL, and page title from the 
        request, adds the page to the category, and renders the 
        'rango/page_list.html' template with the updated page list.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: Rendered response with the updated page list.
        """
        self.cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']

        if self.cat_id:
            category = Category.objects.get(id=int(self.cat_id))
            added_by = request.user
            p = Page.objects.get_or_create(category=category, title=title,
                                           url=url, added_by=added_by)
            pages = Page.objects.filter(category=category).order_by('-views')
            self.context_dict['pages'] = pages
        return render(request, self.template_name, self.context_dict)
