import cv2
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .models import Post, PostImage, PostLike, Comment, CommentLike
from .utils import (
    is_post_liked_by_user,
    private_account_action_permission,

    get_bucket_object,
    read_image_from_bucket,
    compress_image,
    write_image_to_bucket,
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
        if not images: return redirect('post:feed')
        description = request.POST.get('description')
        post = Post.objects.create(user=request.user, description=description)

        for i in range(0, len(images)):
            post_img = PostImage.objects.create(post=post, image=images[i], order=i)
            extension = post_img.image.url.split('.')[-1]

            if settings.USE_S3:
                bucket_object = get_bucket_object(post_img.image.url)
                img, dimensions, exif = read_image_from_bucket(bucket_object)
                width, height = dimensions
            else:
                absolute_url = str(settings.BASE_DIR) + post_img.image.url
                img = cv2.imread(absolute_url)
                width, height = int(img.shape[1]), int(img.shape[0])

            if height / width > 1.5:  # 3 / 2
                img = img[int(height/2 - 0.75*width):int(height/2 + 0.75*width), 0:width]
            elif height / width < 0.67:  # 2 / 3
                img = img[0:height, int(width/2 - 0.75*height):int(width/2 + 0.75*height)]

            img = compress_image(img, extension)

            if settings.USE_S3:
                write_image_to_bucket(bucket_object, img, extension, exif)
            else:
                cv2.imwrite(absolute_url, img)

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
