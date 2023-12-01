from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
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
    """View for rendering the index.html or index page.

    Retrieves the top five categories based on likes and also the top 
    five pages based on views. It then renders the 'rango/index.html'
    template with the obtained objects or data.

    Attributes: None

    Methods: 
        get(request, *args, **kwargs): GET request for obtaining the
        top five categories and top five pages and then renders the
        index.html. 
    """

    def get(self, request, *args, **kwargs):
        """Handles the GET request and then renders index.html.

        Gets the top five categories based on likes and top five pages
        based on views and then renders the index.html.

        Args:
            request(HttpRequest): HTTP request object
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            HttpResponse: Rendered index.html together with the 
            context_dict variable that holds the data of top categories
            and top pages.
        """
        cookie_handler_view = CookieHandlerView()
        cookie_handler_view.visitor_cookie_handler(request)
        category_list = Category.objects.order_by('-likes')[:5]

        page_list = Page.objects.order_by('-views')[:5]

        request.session.set_test_cookie()

        context_dict = {'categories': category_list,
                        'pages': page_list}

        return render(request, 'rango/index.html', context=context_dict)


class AboutView(View):
    """View for rendering the about.html or about page.

    Attributes: None

    Methods: None
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'rango/about.html')


class ShowCategoryView(View):
    """View for rendering the category.html or category page.

    Displays the selected category name and then retrieves all pages
    within the selected category and also has a search function if a
    user wants to add a page within that category. Lastly, renders the
    'rango/category.html' templte with the obtained data.

    Attributes:
        context_dict - dictionary type where it stores all the required
        data to be rendered on the page

        results - list type where it stores all the search results

    Methods: 
        get_context_dict(category, pages, results=None): method for
        storing into the context_dict variable all the required data to 
        be displayed in category.html

        get_category_and_pages: method for checking the selected
        category by comparing it with the category_name_slug and if it
        exists, gets all Page objects and orders it by views.

        get(request, category_name_slug, *args, **kwargs): GET request 
        for obtaining the selected category by comparing the slug 
        property to the category_name_slug argument and also obtaining
        all Page objects that are sorted by the number of views.
        Lastly, renders the category.html together with the obtianed
        data.

        post(request, category_name_slug, *args, **kwargs): POST request
        for performing search within the category stores the data into
        the results attribute.
    """
    context_dict = {}
    results = []

    def get_context_dict(self, category, pages):
        """Returns all the required data that should be displayed or
        rendered to the category.html.

        Args:
            category: Selected Category object.
            pages: all objects within the selected category
        
        Return/s:
            Dictionary of required data to be rendered or displayed to
            the category.html
        """
   
        if self.results:
            return {
                'pages': pages,
                'category': category,
                'search_results': self.results,
                'page_title': [page.title for page in pages]
            }
        else:
            return {
                'pages': pages,
                'category': category,
                'query': category.name
            }
        
    def get_category_and_pages(self, category_name_slug):
        """Gets the selected category object and Page objects within
        the selected category.

        Args:
            category_name_slug: the slug type of the name property of
            Category class or model.
        
        Returns:
            category: returns the selected Category object.
            pages: returns the filtered Page objects within the
            selected category.
        """
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')

        return category, pages

    def get(self, request, category_name_slug, *args, **kwargs):
        """Handles the GET request and then renders category.html.

        Gets the selected Category object and filtered Page objects 
        within the selected category object and then renders the
        category.html.

        Args:
            request(HttpRequest): HTTP request object
            category_name_slug: slug type of the category name
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            HttpResponse: Rendered index.html together with the 
            context_dict variable that holds the selected category, 
            page objects, and search results.
        """

        try:
            category, pages = self.get_category_and_pages(category_name_slug)
            self.context_dict.update(self.get_context_dict(category, pages))
        except Category.DoesNotExist:
            self.context_dict = {'category': None,
                            'pages': None}

        return render(request, 'rango/category.html', 
                      context=self.context_dict)

    def post(self, request, category_name_slug, *args, **kwargs):
        """Handles the POST request and then renders category.html.

        Gets the selected Category object and then the filtered Page
        objects within the selected category and also the search
        results.

        Args:
            request(HttpRequest): HTTP request object
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            HttpResponse: Rendered index.html together with the 
            context_dict variable that holds the data of top categories
            and top pages.
        """

        try:
            category, pages = self.get_category_and_pages(category_name_slug)

            if 'query' in request.POST:
                query = request.POST['query'].strip()

                if query:
                    self.results = run_query(query)
                    self.context_dict['query'] = query

            self.context_dict.update(self.get_context_dict(category, pages))
        except Category.DoesNotExist:
            self.context_dict = {'category': None,
                            'pages': None}

        return render(request, 'rango/category.html', 
                      context=self.context_dict)


class AddCategoryView(View):
    def get(self, request, *args, **kwargs):
        form = CategoryForm()
        context_dict = {'form': form}
        return render(request, 'rango/add_category.html', context=context_dict)

    def post(self, request, *args, **kwargs):
        try:
            form = CategoryForm(request.POST)

            if form.is_valid():
                form.save(commit=True)
                return redirect('index')
            else:
                print(form.errors)

            return render(request, 'rango/add_category.html', {'form': form})
        except IntegrityError as e:
            print(f"Integrity Error: {e}")
            form.add_error('name', 'Special Characters not allowed.')
            return render(request, 'rango/add_category.html', {'form': form})


class AddPageView(View):
    def check_category(self, category_name_slug):
        return Category.objects.get(slug=category_name_slug)

    def get(self, request, category_name_slug, *args, **kwargs):
        try:
            category = self.check_category(category_name_slug)
            form = PageForm()
        except Category.DoesNotExist:
            category = None
            form = None

        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context=context_dict)

    def post(self, request, category_name_slug, *args, **kwargs):
        try:
            category = self.check_category(category_name_slug)
        except Category.DoesNotExist:
            category = None

        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.likes = 0
                page.save()
            return redirect('show_category', category_name_slug)
        else:
            print(form.errors)

        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)


@method_decorator(login_required, name='dispatch')
class RestrictedView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Since you're logged in, you can see this text!")


@method_decorator(login_required, name='dispatch')
class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


@method_decorator(login_required, name='dispatch')
class RegisterProfileView(View):
    def get(self, request, *args, **kwargs):
        form = UserProfileForm()
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)

    def post(self, request, *args, **kwargs):
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('index')
        else:
            print(form.errors)

        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get_user(self, username):
        user = User.objects.get(username=username)
        userprofile = UserProfile.objects.get_or_create(user=user)[0]

        return user, userprofile

    def get_context_dict(self, user, userprofile):
        form = UserProfileForm({
                'website': userprofile.website,
                'picture': userprofile.picture
            })
        return {
            'userprofile': userprofile,
            'selecteduser': user,
            'form': form,
            'categories': userprofile.liked_categories.all(),
            'created_pages': Page.objects.filter(added_by=userprofile.user)
        }

    def get(self, request, username, *args, **kwargs):
        try:
            context_dict = {}
            user, userprofile = self.get_user(username)

            context_dict.update(self.get_context_dict(user, userprofile))
            return render(request, 'rango/profile.html', context=context_dict)
        except User.DoesNotExist:
            return redirect('index')

    def post(self, request, username, *args, **kwargs):
        try:
            context_dict = {}
            user, userprofile = self.get_user(username)

            form = UserProfileForm(request.POST, request.FILES,
                                   instance=userprofile)

            if form.is_valid():
                form.save(commit=True)
                context_dict.update(self.get_context_dict(user, userprofile))
                return redirect('profile', user.username)
            else:
                print(form.errors)
            return render(request, 'rango/profile.html', context=context_dict)
        except User.DoesNotExist:
            return redirect('index')


class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return reverse('register_profile')


class UserLoginView(LoginView):
    template_name = 'registration/login.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return self.render_to_response(self.get_context_data(form=form))

class CookieHandlerView(View):
    #  helper functions
    def get_server_side_cookie(self, request, cookie, default_val=None):
        val = request.session.get(cookie)

        if not val:
            val = default_val
        return val
    
    def visitor_cookie_handler(self, request):
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
    page_id = None
    url = '/rango/'

    def get(self, request, *args, **kwargs):
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
    def get(self, request, *args, **kwargs):
        userprofile_list = UserProfile.objects.all()

        return render(request, 'rango/list_profiles.html',
                      {'userprofile_list': userprofile_list})
