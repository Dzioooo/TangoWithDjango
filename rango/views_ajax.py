from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from rango.models import Category
from rango.models import Page


@method_decorator(login_required, name='dispatch')
class LikeCategoryView(View):
    cat_id = None
    likes = 0

    def get(self, request, *args, **kwargs):
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
    def get_category_list(self, max_results=0, starts_with=None, 
                          *args, **kwargs):
        
        if starts_with:
            self.cat_list = Category.objects.filter(
                name__istartswith=self.starts_with)
        else:
            self.cat_list = Category.objects.all()
        
        if max_results > 0:
            if len(self.cat_list) > max_results:
                self.cat_list = self.cat_list[:max_results]
        return self.cat_list
    
    def get(self, request, *args, **kwargs):
        self.starts_with = request.GET['suggestion']

        cat_list = self.get_category_list(8)
        return render(request, 'rango/cats.html', {'cats': cat_list})


@method_decorator(login_required, name='dispatch')
class AutoAddPageView(View):
    template_name = 'rango/page_list.html'
    cat_id = None
    url = None
    title = None
    context_dict = {}

    def get(self, request, *args, **kwargs):
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
