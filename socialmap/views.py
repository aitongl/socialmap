from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from socialmap.forms import LoginForm, RegisterForm, ProfileForm
from django.contrib.auth.models import User

from socialmap.forms import ProfileForm, LoginForm, RegisterForm
from socialmap.models import Profile, Chat, Message
import time
import json 
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from decimal import Decimal
from webapps import settings

# Create your views here.

def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'socialmap/login.html', context)

    # Creates a bound form from the request POST parameters
    # And makes the form available in the request context dictionary.
    form = LoginForm(request.POST)

    # Validates the form.
    if not form.is_valid():
        context['form'] = form
        return render(request, 'socialmap/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect('map_view')

def register_action(request):
    context = {}
    
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialmap/register.html', context)
    
    form = RegisterForm(request.POST)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'socialmap/register.html', context)
    
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    
    login(request, new_user)
    profile = Profile(user=new_user, 
                     grade=form.cleaned_data.get('grade', 0),
                     latitude=Decimal('40.4433'),
                     longitude=Decimal('-79.9436'))
    profile.save()
    return redirect('map_view')

@login_required
def profile_action(request):
    context = {}
    profile = Profile.objects.get(user = request.user)

    if request.method == 'GET':
        context['form'] = ProfileForm(initial={'grade': profile.grade, 'school': profile.school, 'major': profile.major, 'labels' : profile.labels})
        return render(request, 'socialmap/profile.html', context)
    
    create_form = ProfileForm(request.POST, request.FILES)
    
    if not create_form.is_valid():
        context['form'] = create_form
        context['message'] = create_form.errors.as_text()
        return render(request, 'socialmap/profile.html', context)

    profile.grade = create_form.cleaned_data["grade"]
    profile.school = create_form.cleaned_data["school"]
    profile.major = create_form.cleaned_data["major"]
    profile.labels = create_form.cleaned_data["labels"]
    pic = create_form.cleaned_data["picture"]
    pic_type = pic.content_type
    
    profile.picture.delete()
    profile.picture = pic
    profile.content_type = pic_type

    profile.save()

    context['form'] =  create_form

    return render(request, 'socialmap/profile.html', context)

@ensure_csrf_cookie
@login_required
def map_view(request):
    profiles = Profile.objects.all().values(
        'user__username', 'latitude', 'longitude', 'grade'
    )
    userP = get_object_or_404(Profile, user=request.user)
    followed_profiles = userP.following.all()
    followingList = []
    for followed in followed_profiles:
        print(followed)
        followingList.append(followed.id)
    print(followingList)
    return render(request, 'socialmap/map.html', {
        'profiles': json.dumps(list(profiles), default=str),
        'following': json.dumps(followingList),
        'user': json.dumps([str(request.user)]),
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })

@require_POST
@login_required
def update_location(request):
    try:
        print("trying to update location")
        print(request.user)
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)
        
        # Get or create user profile
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'grade': 0,  # Default grade value
                'latitude': Decimal(str(latitude)),
                'longitude': Decimal(str(longitude)),
            }
        )
        
        if not created:
            print("updated existing")
            # Update existing profile
            profile.latitude = Decimal(str(latitude))
            profile.longitude = Decimal(str(longitude))
            profile.save()
        
        print("going to return success with latitude and longitude")

        return JsonResponse({
            'success': True,
            'latitude': float(profile.latitude),
            'longitude': float(profile.longitude)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def profile_view(request, id):
    context = {}

    user = get_object_or_404(User, id=id)
    context['profile'] = user.profile
    return render(request, 'socialmap/other_profile.html', context)

@login_required
def follow(request, id):
    context = {}

    user_to_follow = get_object_or_404(User, id=id)
    context['title'] = f"Profile page for {user_to_follow.first_name + ' ' + user_to_follow.last_name}"
    context['profile'] = user_to_follow.profile
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()
    return render(request, 'socialmap/other_profile.html', context)

@login_required
def unfollow(request, id):
    context = {}

    user_to_unfollow = get_object_or_404(User, id=id)
    context['title'] = f"Profile page for {user_to_unfollow.first_name + ' ' + user_to_unfollow.last_name}"
    context['profile'] = user_to_unfollow.profile
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()
    return render(request, 'socialmap/other_profile.html', context)

@login_required
def get_photo(request, id):
    item = get_object_or_404(Profile, id=id)

    if not item.picture:
        raise Http404

    return HttpResponse(item.picture, content_type=item.content_type)
