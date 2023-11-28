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

from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm
from rango.forms import UserProfileForm
from rango.google_search import run_query
from rango.models import Category
from rango.models import Page
from rango.models import UserProfile
from registration.backends.simple.views import RegistrationView


def index(request):
    """
    renders index.html which then displays top 5 categories with
    the most likes and top 5 pages with most views
    """
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    """
    renders about.html
    """
    context_dict = {}
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    """
    renders the category.html and accepts the parameter
    category_name_slug to which will then be compaared to all slug
    properties from the Category model and checks if a slug property
    matche the category_name_slug parameter

    category and pages objects will then be stored into the
    context_dict variable
    """
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)

        pages = Page.objects.filter(category=category).order_by(
            '-views')
        page_list = Page.objects.filter(category=category)
        page_title = []
        page_url = []

        for page in page_list:
            page_title.append(page.title)
            page_url.append(page.url)
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    result_title = []
    result_url = []
    for result in result_list:
        result_title.append(result['title'])
        result_url.append(result['link'])

    context_dict['page_list'] = page_list
    context_dict['pages'] = pages
    context_dict['category'] = category
    context_dict['query'] = category.name
    context_dict['page_url'] = page_url
    context_dict['page_title'] = page_title
    context_dict['result_url'] = result_url
    context_dict['result_title'] = result_title
    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    """
    renders the add_category.html. this function creates a new category
    object from the CategoryForm model
    """
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    """
    renders the add_page.html. this function creates a new category
    object from the PageForm model, it accepts the
    category_name_slug which will be compared to all category objects
    to find the category object that has the same slug property of the
    model.
    """
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                """ access the form object's properties for
                customization """
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
            return show_category(request, category_name_slug)
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

    for page in created_pages:
        print(page.category)

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
