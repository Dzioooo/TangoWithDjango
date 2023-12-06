from datetime import datetime
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from registration.backends.simple.views import RegistrationView

from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserProfileForm
from rango.google_search import run_query
from rango.models import Category
from rango.models import Page
from rango.models import UserProfile


class IndexView(View):
    """
    View for displaying a list of top five categories based on likes
    and another list of top fice pages based on views.

    Attirubutes:
        template_name (str): contains the name of the template.
    """
    template_name = 'rango/index.html'
    
    def get(self, request, *args, **kwargs):
        """
        GET request for the Index View.

        Retrieves the top five categories based on likes and top five
        pages based on views and also calls the visitor_cookie_handler
        function from the CookieHandlerView class.

        Args:
            request (HttpRequest): The request object.
        
        Returns:
            HttpResponse: Rendered response with the template and
            context.
        """
        cookie_handler_view = CookieHandlerView()
        cookie_handler_view.visitor_cookie_handler(request)
        category_list = Category.objects.order_by('-likes')[:5]

        page_list = Page.objects.order_by('-views')[:5]

        request.session.set_test_cookie()

        context_dict = {'categories': category_list,
                        'pages': page_list}

        return render(request, self.template_name, context=context_dict)


class AboutView(View):
    """
    View for dispaying the About Page.

    Attributes:
        None
    """
    template_name = 'rango/about.html'
    def get(self, request, *args, **kwargs):
        """
        GET request for the About View

        Args:
            None
        
        Returns:
            None
        """
        return render(request, self.template_name)


class ShowCategoryView(View):
    """
    View for displaying a cateogry and its associated pages.

    Attributes:
        context_dict (dict): stores all context data that will be 
        displayed on the rendered template.

        template_name (str): A string type which contains the name of 
        the template.
    """
    context_dict = {}
    template_name = 'rango/category.html'

    def get_context_dict(self, category, pages, results=None):
        """
        Generates a context dictionary for rendering the template.

        Args:
            category (Category): The selected category object that will
            be displayed.

            pages (QuerySet): List of Page objects associated with the
            selected category object.

            results (List): List of search results from the run_query
            function.
        
        Returns:
            dict (dict): The context dictionary containing the data 
            which will be then rendered to the template.
        """
        return {
            'pages': pages,
            'category': category,
            'query': category.name,
            'search_results': results,
            'page_title': [page.title for page in pages]
        }
        
    def get_category_and_pages(self, category_name_slug):
        """
        Checks if the selected category exists and then retrieves all
        pages associated with the selected category if the Category
        exists.

        Args:
            category_name_slug (str): slug of the category name.
        
        Returns:
            category (Category): the selected category object.

            pages (QuerySet): All objects from the Page model that is
            associated with the selectec category object.
        """
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None
            pages = None
        
        pages = Page.objects.filter(category=category).order_by('-views')

        return category, pages

    def get(self, request, category_name_slug, *args, **kwargs):
        """
        Handles the GET requests for displaying the selected category
        and the associated pages of the selected category.

        Args:
            request (HttpRequest): request object.
            category_name_slug: the slug type of the selected category
            name.
        
        Returns:
            HttpResponse: Rendered response with the template and
            context.
        """
        category, pages = self.get_category_and_pages(category_name_slug)
        self.context_dict.update(self.get_context_dict(category, pages))

        return render(request, self.template_name, context=self.context_dict)

    def post(self, request, category_name_slug, *args, **kwargs):
        """
        Handles the POST requests, such as search queries from the
        query_search function updates the 'results' key of the context.

        Args:
            request (HttpRequest): request object.
            category_name_slug: the slug type of the selected category
            name.
        
        Returns:
            HttpResponse: Rendered response with the template and
            updated 'results' key of the context.
        """

        category, pages = self.get_category_and_pages(category_name_slug)
        results = []

        if 'query' in request.POST:
            query = request.POST['query'].strip()

            if query:
                results = run_query(query)
                self.context_dict['query'] = query

        self.context_dict.update(self.get_context_dict(category, pages, 
                                                        results))

        return render(request, self.template_name, context=self.context_dict)


class AddCategoryView(View):
    """
    View for adding a new category.

    Attributes:
        template_name (str): The name of the template used for
        rendering the view.

        form (CategoryForm): instance of CategoryForm that will be used
        for adding a new category.
    """

    template_name = 'rango/add_category.html'

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the AddCategoryView.

        Creates an instance of the CategoryForm that will be used
        throughout the view.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.form = CategoryForm()

    def get(self, request, *args, **kwargs):
        """
        Handles the GET requests specficically the add category form
        from CategoryForm form class.

        Args:
            request(HttpRequest): request object.
        
        Returns:
            HttpResponse: rendered response with the add category form.
        """
        context_dict = {'form': self.form}
        return render(request, self.template_name, context=context_dict)

    def post(self, request, *args, **kwargs):
        """
        Handles the POST requests for adding a new category.

        Saves the new category if the form is valid and then redirects
        to the index page. If the form is not valid, such as category
        names with special characters, the IntegrityError will then be
        triggered together with its error message.

        Args:
            request(HttpRequest): The request object.
        
        Returns:
            HttpResponse: Rendered response based on the form
            validation result.
        """
        self.form = CategoryForm(request.POST)

        if self.form.is_valid():
            self.form.save(commit=True)
            return redirect('index')
        else:
            print("form error")
            print(self.form.errors)

        return render(request, 'rango/add_category.html', 
                        {'form': self.form})


class AddPageView(View):
    """
    View for adding a new page to a category.

    Attributes:
        template_name (str): name of the template used for rendering
        the view.

        form (PageForm): instance of PageForm that will be used
        for adding a new page to a category.
    """
    template_name = 'rango/add_page.html'

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the AddPageView.

        Creates an instance of the PageForm to be used throughout the
        view.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.form = PageForm()

    def check_category(self, category_name_slug):
        """
        Retrieve a category object by using the category_name_slug
        argument.

        Args:
            category_name_slug (str): The slug type of the category
            name.
        
        Returns:
            category (Category): category object if category_name_slug 
            exists, if it does not exist, it returns None.

            form (PageForm): page form object if category_name_slug
            exists, if it does not exist, it returns None.
        """
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None
            self.form = None

        return category
    
    def create_context_dict(self, category, form):
        """
        Create a context dictionary for the context data in rendering
        the template.

        Args:
            category (Category): category object to be associated with
            the page.

            form (PageForm): form for adding pages.
        
        Returns: 
            dict: context dictionary which contains data or information
            for rendering the template.
        """
        return {'form': form, 'category': category}

    def get(self, request, category_name_slug, *args, **kwargs):
        """
        Handles GET request for displaying the add page form.

        Args:
            request (HttpRequest): the request object.

            category_name_slug (str): slug type of the category name.
        
        Returns:
            HttpResponse: rendered response with the add page form.
        """
        category = self.check_category(category_name_slug)
        self.form = PageForm()
        context_dict = self.create_context_dict(category, self.form)
        return render(request, self.template_name, context=context_dict)

    def post(self, request, category_name_slug, *args, **kwargs):
        """
        Handles POST request for adding a new page to a category.

        Creates a new page associated with the category and redirects
        to the show category page if the form is valid. Prints errors
        and renders the add page form with errors if the form is not
        valid.

        Args:
            request (HttpRequest): the request object.

            category_name_slug (str): the slug type of the category
            name.
        
        Returns:
            HttpResponse: Rendered response based on the form
            validation results.
        """
        try:
            category = self.check_category(category_name_slug)
        except Category.DoesNotExist:
            category = None

        self.form = PageForm(request.POST)

        if self.form.is_valid():
            if category:
                page = self.form.save(commit=False)
                page.category = category
                page.views = 0
                page.likes = 0
                page.save()
            return redirect('show_category', category_name_slug)
        else:
            print(self.form.errors)

        context_dict = self.create_context_dict(category, self.form)
        return render(request, self.template_name, context_dict)


@method_decorator(login_required, name='dispatch')
class UserLogoutView(View):
    """
    View for handling user logout.

    Attributes:
        login_required (bool): A method decorator ensuring that only
        logged-in users can access this view.
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for logging out the user.

        Logs the user out and redirects to the index page.

        Args:
            request (HttpRequest): the request object.
        
        Returns:
            HttpResponseRedirect: redirects to the index page after
            logging out the user.
        """
        logout(request)
        return HttpResponseRedirect(reverse('index'))


@method_decorator(login_required, name='dispatch')
class RegisterProfileView(View):
    """
    View for handling user profile registration.

    Attribtues:
        template_name (str): The name of the used for rendering the
        view.

        form (UserProfileForm): an instance of the UserProfileForm
        class used for user profile registration.

        login_required (bool): a method decorater ensuring that only
        logged-in users can access this view.
    """
    template_name = 'rango/profile_registration.html'

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the RegisterProfileView.

        Creates an instance of the UserProfileForm to be used
        throughout the view.

        Args:
            **kwargs: additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.form = UserProfileForm()

    def get(self, request, *args, **kwargs):
        """
        Handles the GET request for displaying the user profile
        registration form.

        Arrgs:
            request (HttpRequest): the request object.
        
        Returns:
            HttpResponse: rendered response with the user profile
            registration form.
        """
        self.form = UserProfileForm()
        context_dict = {'form': self.form}
        return render(request, self.template_name, context_dict)

    def post(self, request, *args, **kwargs):
        """
        Handles POST request for user profile registration.

        Associates the user profile with the current logged in user and
        then redirects it to the index page if the form is valid. If
        the form is not valid, it prints and renders the errors and 
        also the user profiek registration form with errors.

        Args:
            request (HttpRequest): the request object.
        
        Returns:
            HttpResponse: rendered response based on the form
            vlidation result.
        """
        self.form = UserProfileForm(request.POST, request.FILES)

        if self.form.is_valid():
            user_profile = self.form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('index')
        else:
            print(self.form.errors)

        context_dict = {'form': self.form}
        return render(request, self.template_name, context_dict)


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """
    View for hadnling user's profile.

    Attributes:
        template_name (str): The name of the template used for
        the view.

        user (User): instance of the User model used for getting the 
        user's profile.

        userprofile (UserProfile): instance of the UserProfile model
        used for displaying the user's profile and its data.

        login_required (bool): A decorate ensuring that only logged in
        users can access this view.
    """
    user = None
    userprofile = None
    template_name = 'rango/profile.html'

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the ProfileView.

        Creates an instance of UserProfileForm to be used throughout
        the view.

        Args:
            **kwargs: additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.form = UserProfileForm()

    def get_user(self, username):
        """
        Checks if a user exists by comparing the username argument and
        the username property of the User object.

        Args:
            username: the logged in user's username.
        
        Returns:
            user (User): an instance of the User class if the user 
            exists, if the user does not exist, it returns None.

            userprofile (UserProfile): an instance of the UserProfile
            object if the User object exists, if User object does not
            exist, it returns None.
        """
        try:
            print("username", username)
            self.user = User.objects.get(username=username)
        except User.DoesNotExist:
            print("does not exist")
            self.user = None
            self.userprofile = None

        self.userprofile = UserProfile.objects.get_or_create(user=self.user)[0]

        return self.user, self.userprofile
        
    def get_context_dict(self):
        """
        Generates a context dictionary for rendering the template.

        Args:
            category (Category): The selected category object that will
            be displayed.

            pages (QuerySet): List of Page objects associated with the
            selected category object.

            results (List): List of search results from the run_query
            function.
        
        Returns:
            dict (dict): The context dictionary containing the data 
            which will be then rendered to the template.
        """
        initial_values = {
        'website': self.userprofile.website,
        'picture': self.userprofile.picture
        }
        self.form = UserProfileForm(initial=initial_values)
        return {
            'userprofile': self.userprofile,
            'selecteduser': self.user,
            'form': self.form,
            'categories': self.userprofile.liked_categories.all(),
            'created_pages': Page.objects.filter(
                added_by=self.userprofile.user)
        }

    def get(self, request, username, *args, **kwargs):
        """
        Handles GET request for displaying the user's profile.

        Args:
            request (HttpRequest): the request object.

            username (str): the username of the logged in user.
        
        Returns:
            HttpResponse: rendered response with the user's profile
            data.
        """
        try:
            context_dict = {}
            self.get_user(username)

            context_dict.update(self.get_context_dict())
            return render(request, self.template_name, context=context_dict)
        except User.DoesNotExist:
            return redirect('index')

    def post(self, request, username, *args, **kwargs):
        """
        Handles POST request for user's profile data.

        If the form is valid, it updates the user's website and profie
        picture. If the form is not valid, it renders the user profile
        view and display the errors.

        Args:
            request (HttpRequest): the request object.

            username (str): the username of the logged in user.

        Returns:
            HttpResponse: rendered response based on the form 
            validation result.
        """
        try:
            context_dict = {}
            self.user, self.userprofile = self.get_user(username)

            self.form = UserProfileForm(request.POST, request.FILES,
                                   instance=self.userprofile)

            if self.form.is_valid():
                self.form.save(commit=True)
                context_dict.update(self.get_context_dict())
                return redirect('profile', self.user.username)
            else:
                print(self.form.errors)
            return render(request, self.template_name, context=context_dict)
        except User.DoesNotExist:
            return redirect('index')


class MyRegistrationView(RegistrationView):
    """
    Registration view which extends from the default RegistrationView
    from registration.backends.simple.views.

    It overrides the get_success_url function to redirect users to the
    register_profile view if the registration is successful.

    Attributes:
        RegistrationView: The base class for handling the user
        registration.

    """
    def get_success_url(self, user):
        """
        Gets the URL to redirect to upon succesful user registration.

        It overrrides the default behavior to redirect to the
        'register_profile' view.
        """
        return reverse('register_profile')


class UserLoginView(LoginView):
    """
    Custom login view that extends the default LoginView from
    django.contrib.auth.views.

    Attributes:
        template_name (str): The name of the template used for
        rendering the login view.
    """
    template_name = 'registration/login.html'

    def post(self, request, *args, **kwargs):
        """
        Handles POST request for user login.

        Validates the login form. If the form is valid, it calls the
        built-in form_valid function, if the form is not valid, it
        calls the form_invalid function.

        Args:
            request (HttpRequest): the request object.
        
        Returns:
            HttpResponse: Rendered resposne based on form validation
            result.
        """
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Handles the case when the login form is invalid. It will
        display an error message and then renders the login form
        with the context data.

        Args:
            form (AuthenticationForm): invalid login form.
        
        Returns:
            HttpResponse: Rendered response with error message and
            login form.
        """
        messages.error(self.request, 'Invalid username or password.')
        return self.render_to_response(self.get_context_data(form=form))

class CookieHandlerView(View):
    """
    View for handling cookies, specifically for tracking visitor 
    information.

    Attributes:
        None
    """
    def get_server_side_cookie(self, request, cookie, default_val=None):
        """
        Retrieve a value from the server-side session cookie.

        Args:
            request (HttpRequest): The request object.
            cookie (str): The name of the cookie.
            default_val: The default value to return if the cookie is 
            not found.

        Returns:
            Any: The value of the cookie or the default value.
        """
        val = request.session.get(cookie)

        if not val:
            val = default_val
        return val
    
    def visitor_cookie_handler(self, request):
        """
        Handle visitor cookie tracking.

        Updates the visit count and last visit time in the session.

        Args:
            request (HttpRequest): The request object.
        """
        visits = int(self.get_server_side_cookie(request, 'visits', '1'))
        print("visit", visits)
        last_visit_cookie = self.get_server_side_cookie(request,
                                                'last_visit',
                                                str(datetime.now()))
        last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                            '%Y-%m-%d %H:%M:%S')

        if (datetime.now() - last_visit_time).days > 0:
            visits = visits + 1
            request.session['last_visit'] = str(datetime.now())
        else:
            request.session['last_visit'] = last_visit_cookie

        request.session['visits'] = visits


class TrackUrlView(View):
    """
    View for tracking and updating the view count of a page.

    Attributes:
        page_id (int): The ID of the page to track.
        url (str): The default URL to redirect to if the page ID is not 
        found.
    """
    page_id = None
    url = '/rango/'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for tracking and updating the view count 
        of a page.

        Retrieves the page ID from the request, updates the page's view 
        count, and redirects to the page's URL.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: Redirects to the page's URL.
        """
        if 'page_id' in request.GET:
            self.page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=self.page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except Exception:
                pass
        return redirect(url)


class ListProfilesView(View):
    """
    View for listing user profiles.

    Attributes:
        None
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for listing user profiles.

        Retrieves all user profiles and renders the list_profiles.html 
        template with the user profile list.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: Rendered response with the user profile list.
        """
        userprofile_list = UserProfile.objects.all()

        return render(request, 'rango/list_profiles.html',
                      {'userprofile_list': userprofile_list})
