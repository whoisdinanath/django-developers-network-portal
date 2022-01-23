from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Profile, Skill, Message
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm , ProfileForm, SkillCreateForm, MessageForm
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# Create your views here.


def loginUser(request):
    page= 'login'
    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,'Username does not exist')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'user-account')

        else:
            messages.error(request,'Username or password is incorrect!')
    return render(request, 'users/login.html')

def logoutUser(request):
    logout(request)
    messages.error(request,'Logged Out!')
    return redirect('login')

def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'Succefully Registered!')
            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(request, "An error occured while registering user!")

    context={
        'page':page,
        'form':form
    }
    return render(request, 'users/login.html', context)


def profiles(request):
    text = ''
    if request.GET.get('text'):
        text = request.GET.get('text')

    skills = Skill.objects.filter(name__icontains=text)
    profiles = Profile.objects.distinct().filter(Q(name__icontains=text)| Q(short_intro__icontains=text)| Q(skill__in=skills )).exclude(Q(bio__isnull=True)).exclude(Q(bio__exact=''))
    
    page = request.GET.get('page')
    results = 9
    paginator = Paginator(profiles, results)
    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        page=1
        profiles = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        profiles = paginator.page(page)

    leftIndex = (int(page)  - 4  )
    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(page)+ 5)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1

    custom_index = range(leftIndex, rightIndex)
    
    context = {
    'profiles':profiles,'text':text, 'profiles':profiles, 'custom_index':custom_index
    }
    return render(request, 'users/profiles.html', context)


def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description='')
    
    context={
'profile':profile, 'topSkills':topSkills, 'otherSkills':otherSkills
    }
    return render(request, 'users/user-profile.html', context)


@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    projects = profile.project_set.all()
    context={
    'profile':profile, 'skills':skills, 'projects':projects
    }
    return render(request, 'users/account.html', context )

@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user-account')

    context = {
'form':form
    }
    return render(request, 'users/profile_form.html' ,context)


@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form  = SkillCreateForm()
    if request.method=='POST':
        form = SkillCreateForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Skill was created successfully!')
            return redirect('user-account')

    context = {
        'form':form

    }
    return render(request, 'users/skill_form.html' , context)



@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form  = SkillCreateForm(instance=skill)
    if request.method=='POST':
        form = SkillCreateForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was updated successfully!')
            return redirect('user-account')

    context = {
        'form':form

    }
    return render(request, 'users/skill_form.html' , context)



@login_required(login_url='login')
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)

    context ={
'object':skill
    }
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill was deleted successfully!')
        return redirect('user-account')
    return render(request, 'delete_template.html', context)

@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unread_total = messageRequests.filter(is_read=False).count()
    context = {
'messageRequests':messageRequests, 'unread_total':unread_total
    }
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def message(request, pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read==False:
        message.is_read=True
        message.save()
    context = {
'message':message
    }
    return render(request, 'users/message.html', context)


def createMessage(request, pk):
    reciever = Profile.objects.get(id=pk)
    form = MessageForm()
    if request.user.is_authenticated:
        sender =  request.user.profile
    else:
        sender = None
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.reciever = reciever
            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()
            messages.success(request, "Your message was sent to the person!")
            return redirect('profile', pk=reciever.id)
    context= {
'reciever':reciever, 'form':form
    }
    return render(request, 'users/message_form.html', context)