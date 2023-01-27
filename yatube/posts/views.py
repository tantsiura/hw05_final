
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.conf import settings
from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, User, Follow
from .utils import get_page_of_paginator

@cache_page(settings.CACHES_TIME_DEFAULT_IN_SEC, key_prefix='index_page')
def index(request):
    """Главная страница"""
    posts = Post.objects.all()
    page_obj = get_page_of_paginator(request, posts)
    template = 'posts/index.html'

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)

def group_posts(request, slug):
    """Страница постов по группам"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_of_paginator(request, posts)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    """Страница профиля пользователя"""
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).all()
    posts_count = author.posts.all().count
    page_obj = get_page_of_paginator(request, posts)
    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count
    }

    return render(request, template, context)

def post_detail(request, post_id):
    """Страница конкретного поста"""
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(author=post.author).all()
    form = CommentForm(request.POST or None)
    template ='posts/post_detail.html'
    context = {
        'post': post,
        'comments' : comments,
        'form' : form
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Создать новый пост"""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    template = 'posts/create_post.html'
    if not form.is_valid():
        return render(request, template, {'form': form, 'is_edit': True})
    new_post = form.save(commit=False)
    new_post.author = request.user
    form.save()
    return redirect('posts:profile', new_post.author)


@login_required
def post_edit(request, post_id):
    """Редактирование поста"""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None, 
        files=request.FILES or None,
        instance=post
    )
    template = 'posts/create_post.html'
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if not form.is_valid():
        context = {
            'form': form,
            'post': post,
            'is_edit': True,
        }
        return render(request, template, context)
    form.save()
    return redirect('posts:post_detail', post_id)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    """Страница с выводом постов авторов,
    на которых подписан текущий пользователь.
    """
    posts = Follow.objects.filter(user=request.user).all()
    page_obj = get_page_of_paginator(request, posts)
    template = 'posts/follow.html'

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)

@login_required
def profile_follow(request, username):
    """ Подписка на автора """
    author = get_object_or_404(User, username = username)
    if request.user != author:
        Follow.objects.update_or_create(user=request.user, author=author)

    return redirect('posts:profile', username=username)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username = username)
    if request.user != author:
        Follow.objects.filter(author=author).delete()

    return redirect('posts:profile', username=username)