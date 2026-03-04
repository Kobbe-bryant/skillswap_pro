from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Avg
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from skills.models import CustomUser, Profile, Skill, SwapRequest, Rating, Notification, Lesson
from skills.forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProfileForm,
    SwapRequestForm,
    RatingForm,
    LessonForm
)


def index(request):
    """Home page with overview of the platform."""
    total_users = CustomUser.objects.count()
    total_skills = Skill.objects.count()
    total_swaps = SwapRequest.objects.filter(status='Completed').count()
    
    context = {
        'total_users': total_users,
        'total_skills': total_skills,
        'total_swaps': total_swaps,
    }
    return render(request, 'index.html', context)


def signup(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('marketplace')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, error in form.errors.items():
                messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('marketplace')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('marketplace')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


@login_required(login_url='login')
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


@login_required(login_url='login')
def marketplace(request):
    """Display all users with their skills in a marketplace grid."""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    skill_filter = request.GET.get('skill', '')
    page_number = request.GET.get('page', 1)
    
    users = CustomUser.objects.exclude(id=request.user.id).prefetch_related('profile__skills_offered', 'profile__skills_wanted')
    # annotate average rating
    users = users.annotate(avg_rating=models.Avg('ratings_received__score'))
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(profile__bio__icontains=search_query)
        )
    
    if category_filter:
        users = users.filter(profile__skills_offered__category=category_filter).distinct()
    
    if skill_filter:
        users = users.filter(
            Q(profile__skills_offered__name__icontains=skill_filter) |
            Q(profile__skills_wanted__name__icontains=skill_filter)
        ).distinct()
    
    paginator = Paginator(users, 9)  # 9 cards per page
    users_page = paginator.get_page(page_number)
    
    categories = Skill.objects.values_list('category', flat=True).distinct().order_by('category')
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'categories': categories,
        'selected_category': category_filter,
        'skill_filter': skill_filter,
        'paginator': paginator,
        'page_obj': users_page,
    }
    return render(request, 'marketplace.html', context)


@login_required(login_url='login')
def user_profile(request, user_id):
    """Display detailed profile of a user."""
    user = get_object_or_404(CustomUser, id=user_id)
    profile = user.profile
    
    # Get common skills (user's wanted skills that this user offers)
    common_skills = profile.skills_offered.filter(wanted_by=request.user.profile)
    
    # Check if a swap request already exists
    existing_request = SwapRequest.objects.filter(
        sender=request.user,
        receiver=user
    ).first()
    
    # ratings
    ratings = user.ratings_received.all()
    avg_rating = ratings.aggregate(models.Avg('score'))['score__avg'] if ratings.exists() else None
    context = {
        'profile_user': user,
        'profile': profile,
        'common_skills': common_skills,
        'existing_request': existing_request,
        'ratings': ratings,
        'avg_rating': avg_rating,
    }
    return render(request, 'user_profile.html', context)


@login_required(login_url='login')
def profile_edit(request):
    """Edit current user's profile."""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_edit')
        else:
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'profile_edit.html', context)


@login_required(login_url='login')
def matching_view(request):
    """Display users whose skills match current user's skill wants."""
    current_user = request.user
    user_wants = current_user.profile.skills_wanted.all()
    
    if not user_wants.exists():
        messages.info(request, 'Please add skills you want to learn to see matches.')
        return redirect('profile_edit')
    
    # Find users who offer skills the current user wants
    matching_users = CustomUser.objects.filter(
        profile__skills_offered__in=user_wants
    ).exclude(id=current_user.id).distinct().prefetch_related('profile__skills_offered', 'profile__skills_wanted')
    
    context = {
        'matching_users': matching_users,
        'user_wants': user_wants,
    }
    return render(request, 'matching.html', context)


@login_required(login_url='login')
def send_swap_request(request, receiver_id):
    """Send a swap request to another user."""
    receiver = get_object_or_404(CustomUser, id=receiver_id)
    
    if receiver == request.user:
        messages.error(request, 'You cannot send a request to yourself.')
        return redirect('marketplace')
    
    if request.method == 'POST':
        form = SwapRequestForm(request.POST, user=request.user)
        if form.is_valid():
            swap_request = form.save(commit=False)
            swap_request.sender = request.user
            swap_request.receiver = receiver
            swap_request.save()
            # notify receiver
            Notification.objects.create(
                user=receiver,
                message=f"New swap request from {request.user.username}",
                link=request.build_absolute_uri(reverse('dashboard'))
            )
            messages.success(request, 'Swap request sent successfully!')
            return redirect('user_profile', user_id=receiver_id)
        else:
            messages.error(request, 'Error sending request. Please check the form.')
    else:
        form = SwapRequestForm(user=request.user)
    
    context = {
        'form': form,
        'receiver': receiver,
    }
    return render(request, 'send_swap_request.html', context)


@login_required(login_url='login')
def dashboard(request):
    """Dashboard to manage sent and received swap requests."""
    current_user = request.user
    
    # Get sent requests
    sent_requests = SwapRequest.objects.filter(sender=current_user).select_related('receiver', 'skill_offering', 'skill_wanting')
    
    # Get received requests
    received_requests = SwapRequest.objects.filter(receiver=current_user).select_related('sender', 'skill_offering', 'skill_wanting')
    
    # Count by status
    pending_count = received_requests.filter(status='Pending').count()
    accepted_count = received_requests.filter(status='Accepted').count()
    completed_count = SwapRequest.objects.filter(
        Q(sender=current_user) | Q(receiver=current_user),
        status='Completed'
    ).count()
    unread_notifications = current_user.notifications.filter(is_read=False).count()
    
    context = {
        'sent_requests': sent_requests,
        'received_requests': received_requests,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'completed_count': completed_count,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def notifications_list(request):
    """List notifications and mark read."""
    notes = request.user.notifications.all().order_by('-created_at')
    # mark all as read when viewed
    notes.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notes})


@login_required(login_url='login')
def leave_rating(request, swap_id):
    """Allow user to leave a rating once swap is completed."""
    swap = get_object_or_404(SwapRequest, id=swap_id, status='Completed')
    # ensure user involved
    if request.user not in [swap.sender, swap.receiver]:
        return HttpResponseForbidden()
    existing = getattr(swap, 'rating', None)
    if existing and existing.rater == request.user:
        messages.info(request, 'You already left a rating for this swap.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.swap = swap
            rating.rater = request.user
            rating.ratee = swap.receiver if swap.sender == request.user else swap.sender
            rating.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Error submitting rating. Please try again.')
    else:
        form = RatingForm()
    return render(request, 'leave_rating.html', {'form': form, 'swap': swap})


@login_required(login_url='login')
def accept_swap_request(request, request_id):
    """Accept a swap request."""
    swap_request = get_object_or_404(SwapRequest, id=request_id, receiver=request.user)
    
    if swap_request.status != 'Pending':
        messages.warning(request, 'You can only accept pending requests.')
        return redirect('dashboard')
    
    swap_request.status = 'Accepted'
    swap_request.save()
    Notification.objects.create(
        user=swap_request.sender,
        message=f"Your swap request to {request.user.username} has been accepted.",
        link=request.build_absolute_uri(reverse('dashboard'))
    )
    messages.success(request, f'You have accepted the swap request from {swap_request.sender.username}.')
    return redirect('dashboard')


@login_required(login_url='login')
def reject_swap_request(request, request_id):
    """Reject a swap request."""
    swap_request = get_object_or_404(SwapRequest, id=request_id, receiver=request.user)
    
    if swap_request.status != 'Pending':
        messages.warning(request, 'You can only reject pending requests.')
        return redirect('dashboard')
    
    swap_request.status = 'Rejected'
    swap_request.save()
    Notification.objects.create(
        user=swap_request.sender,
        message=f"Your swap request to {request.user.username} was rejected.",
        link=request.build_absolute_uri(reverse('dashboard'))
    )
    messages.success(request, 'You have rejected the swap request.')
    return redirect('dashboard')


@login_required(login_url='login')
def complete_swap_request(request, request_id):
    """Mark a swap request as completed."""
    swap_request = get_object_or_404(
        SwapRequest,
        id=request_id,
        status='Accepted'
    )
    
    # Check if user is sender or receiver
    if swap_request.sender != request.user and swap_request.receiver != request.user:
        messages.error(request, 'You are not involved in this swap.')
        return redirect('dashboard')
    
    swap_request.status = 'Completed'
    swap_request.save()
    # notify both parties to rate
    Notification.objects.create(
        user=swap_request.sender,
        message=f"Swap with {swap_request.receiver.username} completed. Please rate your experience.",
        link=request.build_absolute_uri(reverse('leave_rating', args=[swap_request.id]))
    )
    Notification.objects.create(
        user=swap_request.receiver,
        message=f"Swap with {swap_request.sender.username} completed. Please rate your experience.",
        link=request.build_absolute_uri(reverse('leave_rating', args=[swap_request.id]))
    )
    messages.success(request, 'Swap request marked as completed!')
    return redirect('dashboard')


# --- lesson/simulator functionality --------------------------------------------------
@login_required(login_url='login')
def lesson_list(request):
    """Display all upcoming lessons, allows learners to join."""
    lessons = Lesson.objects.filter(status='Scheduled').order_by('scheduled_time').select_related('tutor', 'skill')
    return render(request, 'lesson_list.html', {'lessons': lessons})


@login_required(login_url='login')
def lesson_detail(request, lesson_id):
    """Show lesson information and join button for learners."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    joined = request.user in lesson.learners.all()
    is_tutor = request.user == lesson.tutor
    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'joined': joined,
        'is_tutor': is_tutor,
    })


@login_required(login_url='login')
def lesson_create(request):
    """Allow a tutor to create a new lesson."""
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.tutor = request.user
            # prevent selecting skills the tutor doesn't offer (extra safety)
            if lesson.skill not in request.user.profile.skills_offered.all():
                messages.error(request, 'You can only create lessons for skills you offer.')
            else:
                lesson.save()
                messages.success(request, 'Lesson created successfully!')
                return redirect('lesson_detail', lesson_id=lesson.id)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = LessonForm(user=request.user)
    return render(request, 'lesson_create.html', {'form': form})


@login_required(login_url='login')
def lesson_join(request, lesson_id):
    """Enroll the current user as a learner in the lesson."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.user == lesson.tutor:
        messages.error(request, 'Tutors cannot join their own lesson as a learner.')
        return redirect('lesson_detail', lesson_id=lesson.id)
    lesson.learners.add(request.user)
    # send notification to tutor
    Notification.objects.create(
        user=lesson.tutor,
        message=f"{request.user.username} joined your lesson '{lesson.title}'.",
        link=request.build_absolute_uri(reverse('lesson_detail', args=[lesson.id]))
    )
    messages.success(request, 'You have joined the lesson!')
    return redirect('lesson_detail', lesson_id=lesson.id)


@login_required(login_url='login')
def lesson_simulator(request, lesson_id):
    """Simple simulation interface — tutors can upload content, learners view it."""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.user != lesson.tutor and request.user not in lesson.learners.all():
        return HttpResponseForbidden()
    # showing uploaded materials and video link if present
    return render(request, 'lesson_simulator.html', {'lesson': lesson})


@login_required(login_url='login')
def cancel_swap_request(request, request_id):
    """Cancel a swap request."""
    swap_request = get_object_or_404(SwapRequest, id=request_id, sender=request.user)
    
    if swap_request.status not in ['Pending', 'Accepted']:
        messages.warning(request, 'You can only cancel pending or accepted requests.')
        return redirect('dashboard')
    
    swap_request.status = 'Cancelled'
    swap_request.save()
    Notification.objects.create(
        user=swap_request.receiver,
        message=f"{request.user.username} cancelled the swap request.",
        link=request.build_absolute_uri(reverse('dashboard'))
    )
    messages.success(request, 'You have cancelled the swap request.')
    return redirect('dashboard')
