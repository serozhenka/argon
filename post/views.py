import json

import cv2

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .models import Post, PostImage, PostLike, Comment, CommentLike
from .utils import is_post_liked_by_user

@login_required(login_url=reverse_lazy('account:login'))
def feed_page(request):
    return render(request, 'post/feed.html')

@login_required(login_url=reverse_lazy('account:login'))
def post_add_page(request):

    if request.method == "GET":
        return render(request, 'post/post_add.html')
    elif request.method == "POST":
        images = request.FILES.getlist('images')
        post = Post.objects.create(
            user=request.user,
            description=request.POST.get('description')
        )

        for i in range(0, len(images)):
            post_img = PostImage.objects.create(
                post=post,
                image=images[i],
                order=i,
            )
            absolute_url = str(settings.BASE_DIR) + post_img.image.url
            img = cv2.imread(absolute_url)
            width = int(img.shape[1])
            height = int(img.shape[0])

            if height / width > 1.25:  # 5 / 4
                img = img[int(height/2 - 5/8*width):int(height/2 + 5/8*width), 0:width]
            elif height / width < 0.8:  # 4 / 5
                img = img[0:height, int(width/2 - 5/8*height):int(width/2 + 5/8*height)]

            cv2.imwrite(absolute_url, img)

        return redirect('account:account', request.user.username)

@login_required(login_url=reverse_lazy('account:login'))
def post_page(request, post_id):

    if request.method == "GET":
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return redirect('post:feed')

        if not post.user.is_public and not request.user.following.is_following(post.user):
            return redirect('post:feed')

        context = {'post': post, 'is_liked': is_post_liked_by_user(request.user, post)}
        return render(request, 'post/post_page.html', context)

@login_required(login_url=reverse_lazy('account:login'))
def post_like_page(request, post_id):

    if request.method == "GET":
        return render(request, 'post/feed.html')

    elif request.method == "POST":
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({
                'response_result': 'error',
                'message': 'Post does not exist',
            })

        if (
            not post.user.is_public and
            not post.user == request.user and
            not request.user.following.is_following(post.user)
        ):

            return JsonResponse({
                'response_result': 'error',
                'message': 'You are not currently following that user',
            })

        post_like, created = PostLike.objects.get_or_create(
            user=request.user,
            post=post,
        )
        action = json.loads(request.body).get('action')
        if action == "like" and not post_like.is_liked:
            post_like.is_liked = True
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
        return render(request, 'post/feed.html')

    elif request.method == "POST":
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({
                'response_result': 'error',
                'message': 'Post does not exist',
            })

        if (
                not post.user.is_public and
                not post.user == request.user and
                not request.user.following.is_following(post.user)
        ):
            return JsonResponse({
                'response_result': 'error',
                'message': 'You are not currently following the post creator',
            })

        if description := json.loads(request.body).get('description'):
            comment = Comment.objects.create(
                user=request.user,
                post=post,
                description=description,
            )
            return JsonResponse({'response_result': 'success', 'comment_id': comment.id})
        else:
            return JsonResponse({
                'response_result': 'error',
                'message': 'No description provided',
            })

@login_required(login_url=reverse_lazy('account:login'))
def post_comment_like_page(request, comment_id):

    if request.method == "GET":
        return render(request, 'post/feed.html')

    elif request.method == "POST":
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({'response_result': 'error', 'message': 'Comment does not exist'})

        if (
                not comment.post.user.is_public and
                not comment.post.user == request.user and
                not request.user.following.is_following(comment.post.user)
        ):
            return JsonResponse({
                'response_result': 'error',
                'message': 'You are not currently following the post creator',
            })

        comment_like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment,
        )

        action = json.loads(request.body).get('action')
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
