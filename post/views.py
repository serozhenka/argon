import json
import os
import threading
import time

from PIL import Image
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .models import Post, PostLike, Comment, CommentLike
from .tasks import process_new_post_images, post_make_posted
from .utils import (
    is_post_liked_by_user,
    private_account_action_permission,

    get_s3_client,
    put_new_image_to_s3,
)

@login_required(login_url=reverse_lazy('account:login'))
def feed_page(request):
    return render(request, 'post/feed.html')


@login_required(login_url=reverse_lazy('account:login'))
def post_add_page(request):
    if request.method == "GET":
        context = {
            'DATA_UPLOAD_MAX_MEMORY_SIZE': settings.DATA_UPLOAD_MAX_MEMORY_SIZE,
        }
        return render(request, 'post/post_add.html', context=context)

    elif request.method == "POST":
        images = request.FILES.getlist('images')
        if not images:
            return redirect('post:feed')

        description = request.POST.get('description')
        post = Post.objects.create(user=request.user, description=description)

        s3_client = get_s3_client()
        threads, pkeys = [], []

        for i in range(len(images)):
            threads.append(threading.Thread(
                target=put_new_image_to_s3,
                args=(s3_client, images[i], pkeys))
            )
            threads[i].start()

        for i in range(len(images)):
            threads[i].join()

        process_new_post_images.apply_async(
            kwargs={
                'pkeys': pkeys,
                'post_id': post.id
            },
            link=post_make_posted.si(post.id)
        )

        return redirect('account:account', request.user.username)


@login_required(login_url=reverse_lazy('account:login'))
def post_page(request, post_id):

    if request.method == "GET":
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return redirect('post:feed')

        if not private_account_action_permission(request.user, post.user):
            return redirect('post:feed')

        context = {'post': post, 'is_liked': is_post_liked_by_user(request.user, post)}
        return render(request, 'post/post_page.html', context)


@login_required(login_url=reverse_lazy('account:login'))
def post_edit_page(request, post_id):

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return redirect('post:feed')

    if post.user != request.user:
        return redirect('post:feed')

    if request.method == "GET":
        context = {'post': post}
        return render(request, 'post/post_edit.html', context)

    elif request.method == "POST":
        description = request.POST.get('description')
        post.description = description
        post.save()
        return redirect('post:post-page', post.id)


@login_required(login_url=reverse_lazy('account:login'))
def post_like_page(request, post_id):

    if request.method == "GET":
        return redirect('post:feed')

    elif request.method == "POST":
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({
                'response_result': 'error',
                'message': 'Post does not exist',
            })

        if not private_account_action_permission(request.user, post.user):
            return JsonResponse({
                'response_result': 'error',
                'message': 'You are not currently following that user',
            })

        action = json.loads(request.body).get('action')
        if not action:
            return JsonResponse({'response_result': 'error', 'message': 'No action provided'})

        post_like, created = PostLike.objects.get_or_create(user=request.user, post=post)

        if action == "like" and not post_like.is_liked:
            post_like.is_liked = True
            post_like.save()
        elif action == "dislike" and post_like.is_liked:
            post_like.is_liked = False
            post_like.save()

        return JsonResponse({
            'response_result': 'success',
            'is_liked': post_like.is_liked,
            'likes_count': post.likes_count,
        })


@login_required(login_url=reverse_lazy('account:login'))
def post_comment_page(request, post_id):

    if request.method == "GET":
        return redirect('post:feed')

    elif request.method == "POST":
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({
                'response_result': 'error',
                'message': 'Post does not exist',
            })

        if not private_account_action_permission(request.user, post.user):
            return JsonResponse({
                'response_result': 'error',
                'message': 'You are not currently following the post creator',
            })

        if description := json.loads(request.body).get('description', None):
            comment = Comment.objects.create(user=request.user, post=post, description=description)
            return JsonResponse({'response_result': 'success', 'comment_id': comment.id})
        else:
            return JsonResponse({'response_result': 'error', 'message': 'No description provided'})


@login_required(login_url=reverse_lazy('account:login'))
def post_comment_like_page(request, comment_id):

    if request.method == "GET":
        return redirect('post:feed')

    elif request.method == "POST":
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({'response_result': 'error', 'message': 'Comment does not exist'})

        if not private_account_action_permission(request.user, comment.post.user):
            return JsonResponse({
                'response_result': 'error',
                'message': 'You are not currently following the post creator',
            })

        action = json.loads(request.body).get('action')
        if not action:
            return JsonResponse({'response_result': 'error', 'message': 'No action provided'})

        comment_like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)

        if action == "like" and not comment_like.is_liked:
            comment_like.is_liked = True
        elif action == "dislike" and comment_like.is_liked:
            comment_like.is_liked = False
        comment_like.save()

        return JsonResponse({
            'response_result': 'success',
            'is_liked': comment_like.is_liked,
            'likes_count': comment.likes_count,
        })


@login_required(login_url=reverse_lazy('account:login'))
def post_comment_remove_page(request, comment_id):

    if request.method == "GET":
        return redirect('post:feed')

    elif request.method == "POST":
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({'response_result': 'error', 'message': 'Comment does not exist'})

        if not comment.user == request.user:
            return JsonResponse({'response_result': 'error', 'message': 'You are not the comment creator'})

        comment.delete()
        return JsonResponse({'response_result': 'success'})
