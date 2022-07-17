from cgitb import text
from multiprocessing import AuthenticationError
from turtle import title
from django.db.models import Q
from django.conf import settings
from django.db import models
from django.forms import CharField
from django.urls import reverse
from django.utils import timezone
import os

# Create your models here.


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{instance.id}-{instance.title}{ext}"
    return f"images/{final_name}"


class PostCategory(models.Model):
    title_category = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.title_category

    def get_absolute_url(self):
        return reverse('post-category', kwargs={'pk': self.pk})


class PostTag(models.Model):
    subject_tag = models.CharField(max_length=200, blank=True, verbose_name='تگ')

    def __str__(self):
        return self.subject_tag
   


class Post(models.Model):
    title = models.CharField(max_length=250)
    text = models.TextField()
    auther = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(
        upload_to=upload_image_path, null=True, blank=True, verbose_name='Image')
    categories = models.ForeignKey(PostCategory, null=True, blank=True, verbose_name='Category', on_delete=models.CASCADE)
    tag = models.ManyToManyField(PostTag, blank=True, verbose_name='تگ')
    # visit_count = models.IntegerField(default=0)
    # visitors = models.ManyToManyField(settings.AUTH_USER_MODEL,
    #                                  related_name='post_visitor',
    #                                  editable=False)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse ('post_detail', kwargs={"pk":self.pk})   

    # def search(self, query):
    #     lookup = (Q(title__icontains=query) | 
    #               Q(text__icontains=query) | 
    #               Q(tag__icontains=query))
    #     return self.get_queryset().filter(lookup, published_date__isnull=False).distinct()


class Comment(models.Model):
    post = models.ForeignKey(
        'blog.Post', on_delete=models.CASCADE, related_name='comments')
    auther = models.CharField(max_length=250)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True) #equal = timezone.now() auto-now is good for  modife time
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text


class SiteAbout(models.Model):
    title = models.CharField(max_length=150)
    address = models.CharField(max_length=400)
    fax = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    about_text = models.TextField(null=True, blank=True)
    image = models.ImageField(
        upload_to=upload_image_path, null=True, blank=True, verbose_name='Image')

    def __str__(self):
        return self.about_text



class PostView(models.Model):
    post = models.ForeignKey(Post, related_name='post_views',
                             on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='user_view', on_delete=models.CASCADE)
                     


