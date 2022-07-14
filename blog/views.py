from msilib.schema import PublishComponent
from multiprocessing import context
from unicodedata import category
from django.core.paginator import (Paginator, EmptyPage,PageNotAnInteger)
from django.db.models import Count, Q, F
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Post, Comment, PostCategory, PostTag, SiteAbout, PostView
from .forms import PostForm, CommentForm, RegisterForm
from django.shortcuts import redirect
from django.contrib.auth.models import User

# Create your views here.
########################################################################postlist#############################
# @login_required
# def post_list(request):
#     ordering = request.GET.get("ordering", 'newer')
#     type = request.GET.get("type", None)
#     sort = '-published_date'

#     if ordering == 'older':
#         sort = 'published_date'
#         posts = Post.objects.filter(
#             published_date__lte=timezone.now()).order_by(sort)
#     # elif ordering=='newer':
#     #     sort = sort
#     #     posts = Post.objects.filter(published_date__lte=timezone.now()).order_by(sort)
#     if type == 'draft':
#         return post_draft_list(request=request)
#         # posts = Post.objects.filter(~Q(published_date__isnull=True))
#         # return redirect('/drafts?next=')
#     else:
#         posts = Post.objects.filter(
#             published_date__lte=timezone.now()).order_by(sort)
#     return render(request, 'blog/post_list.html', {'myposts': posts})

# the avove code will not work for restframwork#########
@login_required
def post_list(request):
    ordering = request.GET.get('ordering' ,'newer')
    sort = '-published_date' if ordering == 'newer' else 'published_date'
    types = request.GET.get('types', 'published')
    # posts = Post.objects.annotate(
    #     num_views=Count('post_views'), id_2=F('id')*2).all()
    posts = Post.objects.annotate(num_views=Count('post_views')).all()
    if types == 'published':
        posts = posts.filter(published_date__isnull=False)
    else:
        posts = posts.filter(published_date__isnull=True)

    about_us_info = SiteAbout.objects.all()
    recently_post = Post.objects.filter(published_date__isnull=False).order_by('-published_date')[:5]
    most_visit_post = posts.filter(num_views__gt=0).order_by('-num_views','-published_date')[:5]
    category_post = PostCategory.objects.filter(post__published_date__isnull=False).annotate(
        posts_count=Count('post')).all().order_by('-posts_count')
  

    paginator = Paginator(posts.order_by(sort), 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'myposts': paginator, 
        'page_obj': page_obj, 
        'about_us_info': about_us_info,
        'recently_posts':recently_post,
        'most_visit_post':most_visit_post,
        'category_post': category_post,
      
    }
    return render(request, 'blog/post_list.html', context)

########################################################################detaillist#############################

@login_required
def post_category_detail(request, pk):
    category = get_object_or_404(PostCategory, pk=pk)
    related_post = Post.objects.filter(categories=category, published_date__isnull=False)

    paginator = Paginator(related_post, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_category.html', {'related_post': related_post, 'page_obj': page_obj})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # if not PostView.objects.filter(post_id=pk, user_id=request.user.id).exists():
    #     PostView.objects.create(post_id=pk, user_id=request.user.id)
    obj, created=PostView.objects.get_or_create(post_id=pk, user_id=request.user.id)


    posts = Post.objects.annotate(num_views=Count('post_views')).all()  
    recently_post = Post.objects.filter(
        published_date__isnull=False).order_by('-published_date')[:5]
    most_visit_post = posts.filter(num_views__gt=0).order_by(
        '-num_views', '-published_date')[:5]
    # category_post = PostCategory.objects.all().annotate(
    #     posts_count=Count('post')).order_by('-posts_count')
    category_post = PostCategory.objects.filter(post__published_date__isnull=False).annotate(
        posts_count=Count('post')).all().order_by('-posts_count')



    context = {
        'post': post,
        'recently_posts': recently_post,
        'most_visit_post': most_visit_post,
        'category_post': category_post
    }

    return render(request, 'blog/post_detail.html', context)

########################################################################postnew#############################

# @login_required
# def post_new(request):
#     if request.method == "POST":
#         form=PostForm(request.POST)
#         if form.is_valid():
#             post=form.save(commit=False)
#             post.auther = request.user
#             # post.published_date =  timezone.now()
#             post.save()
#             return redirect('post_detail', pk=post.pk)
#     else:
#         form = PostForm()
#     return render(request, 'blog/post_edit.html', {'form': form})

# class for the above def################


class CreatePost(View):
    template_name = 'blog/post_edit.html'
    form_class = PostForm

    def get(self, request):
        # form = self.form_class()
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.auther = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
        return render(request, self.template_name, {'form': form, 'image': self.PostForm.image})

########################################################################postedit#############################

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.auther = request.user
            # post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

########################################################################postdraft#############################

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(
        published_date__isnull=True).order_by('-created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

########################################################################postpublish#############################

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

########################################################################postremove#############################

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

########################################################################comment#############################

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.auther = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    print("####", redirect('post_detail', pk=comment.post.pk))
    return redirect('post_detail', pk=comment.post.pk)

########################################################################aboutas#############################

class About_Us(View):
    def get(self, request):
        queryset = SiteAbout.objects.all()
        template_name = 'blog/about_us.html'
        return render(request, template_name, {'data': queryset})
# barai nemoneh boud#####################
# class About_Us(View):
#     template_name = 'blog/about_us.html'
#     queryset = SiteAbout.objects.all()

#     def get(self, request):
#         return render(request, self.template_name, {'data':self.queryset})

# class About_Us(View):
#     template_name = 'blog/about_us.html'
#     model = SiteAbout

#     def get(self, request):
#         return render(request, self.template_name, {'data':self.model.object.all()})

# class About_Us(View):
#     template_name = 'blog/about_us.html'
#     model = SiteAbout

#     def get(self, request):
#         return render(request, self.template_name, {'data':self.model.object.get(pk)})

########################################################################postuniqueview#############################
#  baraye shomaresh view ha
# def post_view_count(request, pk):
#     post_visit = Post.objects.get(pk=pk)
#     return render(request,'blog/post_detail.html', pk=post_visit.pk)
########################################################################postuniqueview#############################
# baraye tarifeh karbar yekta
# def unique_visitor(request, pk):
#     post_visit = Post.objects.get(pk=pk)
#     user = request.user
#     queryset = Post.objects.annotate(num_views=Count('viewers'))
#     if user.is_authenticated and user.username not in queryset:
#         post_visit.visit_count += 1
#         post_visit.save()
#         # add username to viewers list
#         post_visit.visitors+=user.username
#         post_visit.save()
#     else:
#         return redirect('post_detail', pk=post_visit.pk)
#     return render(request, 'blog/post_detail', pk=post_visit.pk)


# def pagination(request):
#     post_list = Post.objects.all()
#     paginator = Paginator(post_list, 5)  # Show 25 contacts per page.

#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, 'list.html', {'page_obj': page_obj})


def register_page(request):
    register_form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if register_form.is_valid():
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            User.objects.create_user(
                username=name, email=email, password=password)
            return redirect('post_list')
    return render(request, './registration/register.html', {'register_form': register_form})


def post_index(request, pk):
    post_tag = get_object_or_404(PostTag, pk=pk)
    related_post = Post.objects.filter(tag=post_tag, published_date__isnull=False)
    # query = request.GET.get('q')
    # if query:
    #     post_list = Post.search(query)
    paginator = Paginator(related_post, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render (request, 'blog/post_tag_search.html',{'post_tag':post_tag, 'page_obj':page_obj })