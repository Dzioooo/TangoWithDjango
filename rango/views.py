from datetime import datetime
from typing import Any

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
    template_name = 'rango/index.html'
    
    def get(self, request, *args, **kwargs):
        cookie_handler_view = CookieHandlerView()
        cookie_handler_view.visitor_cookie_handler(request)
        category_list = Category.objects.order_by('-likes')[:5]

        page_list = Page.objects.order_by('-views')[:5]

        request.session.set_test_cookie()

        context_dict = {'categories': category_list,
                        'pages': page_list}

        return render(request, self.template_name, context=context_dict)


class AboutView(View):
    template_name = 'rango/about.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class ShowCategoryView(View):
    context_dict = {}
    template_name = 'rango/category.html'

    def get_context_dict(self, category, pages, results=None):
        return {
            'pages': pages,
            'category': category,
            'query': category.name,
            'search_results': results,
            'page_title': [page.title for page in pages]
        }
        
    def get_category_and_pages(self, category_name_slug):
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')

        return category, pages

    def get(self, request, category_name_slug, *args, **kwargs):
        try:
            category, pages = self.get_category_and_pages(category_name_slug)
            self.context_dict.update(self.get_context_dict(category, pages))
        except Category.DoesNotExist:
            self.context_dict = {'category': None,
                            'pages': None}

        return render(request, self.template_name, context=self.context_dict)

    def post(self, request, category_name_slug, *args, **kwargs):
        try:
            category, pages = self.get_category_and_pages(category_name_slug)
            results = []

            if 'query' in request.POST:
                query = request.POST['query'].strip()

                if query:
                    results = run_query(query)
                    self.context_dict['query'] = query

            self.context_dict.update(self.get_context_dict(category, pages, 
                                                           results))
        except Category.DoesNotExist:
            self.context_dict = {'category': None,
                            'pages': None}

        return render(request, self.template_name, context=self.context_dict)


class AddCategoryView(View):
    template_name = 'rango/add_category.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.form = CategoryForm()

    def get(self, request, *args, **kwargs):
        form = CategoryForm()
        context_dict = {'form': form}
        return render(request, self.template_name, context=context_dict)

    def post(self, request, *args, **kwargs):
        try:
            self.form = CategoryForm(request.POST)

            if self.form.is_valid():
                self.form.save(commit=True)
                return redirect('index')
            else:
                print(self.form.errors)

            return render(request, 'rango/add_category.html', 
                          {'form': self.form})
        except IntegrityError as e:
            print(f"Integrity Error: {e}")
            self.form.add_error('name', 'Special Characters not allowed.')
            return render(request, self.template_name, {'form': self.form})


class AddPageView(View):
    template_name = 'rango/add_page.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.form = PageForm()

    def check_category(self, category_name_slug):
        return Category.objects.get(slug=category_name_slug)
    
    def create_context_dict(self, category, form):
        return {'form': form, 'category': category}

    def get(self, request, category_name_slug, *args, **kwargs):
        try:
            category = self.check_category(category_name_slug)
        except Category.DoesNotExist:
            category = None
            self.form = None
        
        self.form = PageForm()

        context_dict = self.create_context_dict(category, self.form)
        return render(request, self.template_name, context=context_dict)

    def post(self, request, category_name_slug, *args, **kwargs):
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
    template_name = 'rango/profile_registration.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.form = UserProfileForm()

    def get(self, request, *args, **kwargs):
        self.form = UserProfileForm()
        context_dict = {'form': self.form}
        return render(request, self.template_name, context_dict)

    def post(self, request, *args, **kwargs):
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
    user = None
    userprofile = None
    template_name = 'rango/profile.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.form = UserProfileForm()

    def get_user(self, username):
        user = User.objects.get(username=username)
        userprofile = UserProfile.objects.get_or_create(user=user)[0]

        return user, userprofile

    def get_context_dict(self, user, userprofile):
        initial_values = {
        'website': userprofile.website,
        'picture': userprofile.picture
        }
        self.form = UserProfileForm(initial=initial_values)
        return {
            'userprofile': userprofile,
            'selecteduser': user,
            'form': self.form,
            'categories': userprofile.liked_categories.all(),
            'created_pages': Page.objects.filter(added_by=userprofile.user)
        }

    def get(self, request, username, *args, **kwargs):
        try:
            context_dict = {}
            self.user, self.userprofile = self.get_user(username)

            context_dict.update(self.get_context_dict(self.user, 
                                                      self.userprofile))
            return render(request, self.template_name, context=context_dict)
        except User.DoesNotExist:
            return redirect('index')

    def post(self, request, username, *args, **kwargs):
        try:
            context_dict = {}
            self.user, self.userprofile = self.get_user(username)

            self.form = UserProfileForm(request.POST, request.FILES,
                                   instance=self.userprofile)

            if self.form.is_valid():
                self.form.save(commit=True)
                context_dict.update(self.get_context_dict(self.user, 
                                                          self.userprofile))
                return redirect('profile', self.user.username)
            else:
                print(self.form.errors)
            return render(request, self.template_name, context=context_dict)
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
