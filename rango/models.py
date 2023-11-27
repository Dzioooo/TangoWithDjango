from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        if self.views < 0:
            self.views = 0
        super(Category, self).save(*args, *kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                 blank=True)

    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    # Links UserProfile model to User Model instance
    user = models.OneToOneField(User)
    liked_categories = models.ManyToManyField(Category, blank=True)

    # Additional attributes to include
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username
