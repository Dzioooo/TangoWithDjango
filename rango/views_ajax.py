from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from rango.models import Category
from rango.models import Page


@login_required
def like_category(request):
    cat_id = None
    likes = 0

    if request.method == 'GET':
        cat_id = request.GET['category_id']

    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        user = request.user.userprofile
        if cat:
            user.liked_categories.add(cat)
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()

    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=None):
    cat_list = []

    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list


def suggest_category(request):
    cat_list = []
    starts_with = None

    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)
    print("cat_list", cat_list)

    return render(request, 'rango/cats.html', {'cats': cat_list})


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            added_by = request.user
            p = Page.objects.get_or_create(category=category, title=title,
                                           url=url, added_by=added_by)
            print(p)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages
    return render(request, 'rango/page_list.html', context_dict)
