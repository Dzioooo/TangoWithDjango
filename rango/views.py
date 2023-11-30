from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages

from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm
from rango.forms import UserProfileForm
from rango.google_search import run_query
from rango.models import Category
from rango.models import Page
from rango.models import UserProfile
from registration.backends.simple.views import RegistrationView
from django.contrib.auth.views import LoginView
from django.views import View
from django.db.utils import IntegrityError

class IndexView(View):
    def get(self, request, *args, **kwargs):
        category_list = Category.objects.order_by('-likes')[:5]

        page_list = Page.objects.order_by('-views')[:5]

        context_dict = {'categories': category_list,
                        'pages': page_list}
        
        return render(request, 'rango/index.html', context=context_dict)
   
class AboutView(View):
    def get(self, request, *args, **kwargs):
        context_dict = {}

        return render(request, 'rango/about.html', context=context_dict)
    
class ShowCategoryView(View):
    def get_context_dict(self, category, pages, results=None):
        if results:
            return {
                'pages': pages,
                'category': category,
                'search_results': results,
                'page_title': [page.title for page in pages]
            }
        else:
            return {
                'pages': pages,
                'category': category,
                'query': category.name
            }

    def get(self, request, category_name_slug, *args, **kwargs):
        context_dict = {}

        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')

            context_dict.update(self.get_context_dict(category, pages))
        except Category.DoesNotExist:
            context_dict = {'category': None, 
                            'pages': None}
        
        return render(request, 'rango/category.html', context=context_dict)
    
    def post(self, request, category_name_slug, *args, **kwargs):
        context_dict = {}
        results = []

        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')            

            if 'query' in request.POST:
                query = request.POST['query'].strip()

                if query:
                    results = run_query(query)
                    context_dict['query'] = query

            context_dict.update(self.get_context_dict(category, pages, results))
        except Category.DoesNotExist:
            context_dict = {'category': None, 
                            'pages': None}

        return render(request, 'rango/category.html', context=context_dict)
    
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


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # .set_password built-in function
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {'user_form': user_form,
                    'profile_form': profile_form,
                    'registered': registered}
    return render(request, 'rango/register.html/', context_dict)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponseRedirect("Your Rango account is disabled")
        else:
            print("Invalid login details: {0}, {1}", format(username,
                                                            password))
            return HttpResponse("Invalid login details supplied")
    else:
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
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


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]

    liked_categories = userprofile.liked_categories.all()
    created_pages = Page.objects.filter(added_by=userprofile.user)

    form = UserProfileForm({
        'website': userprofile.website,
        'picture': userprofile.picture
    })

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES,
                               instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('profile', user.username)
        else:
            print(form.errors)

    return render(request, 'rango/profile.html', {'userprofile': userprofile,
                                                  'selecteduser': user,
                                                  'form': form,
                                                  'categories':
                                                  liked_categories,
                                                  'pages': created_pages})


class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return reverse('register_profile')

class CustomLoginView(LoginView):
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

#  helper functions
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)

    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request,
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


def search(request):
    result_list = []
    query = ''

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
    context_dict = {'result_list': result_list, 'query': query}

    return render(request, 'rango/search.html', context_dict)


def track_url(request):
    page_id = None
    url = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except Exception:
                pass
    return redirect(url)


def list_profiles(request):
    userprofile_list = UserProfile.objects.all()

    return render(request, 'rango/list_profiles.html',
                  {'userprofile_list': userprofile_list})
