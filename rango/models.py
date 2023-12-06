from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


class Category(models.Model):
    """
    Model representing a category.

    Attributes:
        name (str): name of the category.

        views (int): the number of views for the category, default
        value is zero.

        likes (int): the number of likes for the category, default
        value is zero.

        slug (str): the slug type of the category name.
    """
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to generate a slug from the category
        name.
        """
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the category.

        Returns:
            name (str): name of the category.
        """
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Page(models.Model):
    """
    Model representing a page.

    Attributes: 
        category (Category): The category (foreign key) 
        where the created page object is associated to.

        title (str): The title of the page.

        url (str): The URL of the page.

        views (int): The number of views for the page.

        added_by (User): The user (foreign key) who added the page.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 blank=True)

    def __str__(self):
        """
        String representation of the page.

        Returns:
            title (str): The title of the page.
        """
        return self.title


class UserProfile(models.Model):
    """
    Model representing a user profile.

    Attributes:
        user (User): The associated user.

        liked_categories (Category): The categories liked by the user.

        website (str): The user's website URL.

        picture (ImageField): The user's profile picture.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liked_categories = models.ManyToManyField(Category, blank=True)

    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        """
        String representation of the user profile.

        Returns"
            username (str): The username of the associated user.
        """
        return self.user.username
