from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def projects(request):
    text = ''
    if request.GET.get('text'):
        text = request.GET.get('text')
    tags = Tag.objects.filter(name__icontains=text)
    projects = Project.objects.distinct().filter(Q(title__icontains=text) | Q(tags__in=tags) | Q(owner__name__icontains=text))
    

    page = request.GET.get('page')
    results = 9
    paginator = Paginator(projects, results)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        page=1
        projects = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        projects = paginator.page(page)

    leftIndex = (int(page)  - 4  )
    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(page)+ 5)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages+1

    custom_index = range(leftIndex, rightIndex)

    context = {'projects':projects,'custom_index':custom_index, 'text':text, 'paginator':paginator }
    return render(request, 'projects/projects.html', context)


def project(request, pk):
    form = ReviewForm()
    project = Project.objects.get(id=pk)
    
    if request.method == "POST":
        form = ReviewForm(request.POST)
        review = form.save(commit=False)
        review.project = project
        review.owner = request.user.profile
        review.save()

        project.getVoteCount

        messages.success(request, 'Review submitted succesfully!')
        return redirect('project', pk=project.id)

    return render(request, 'projects/project.html', {'project':project, 'form':form})

@login_required(login_url='login')
def createProject(request):
    profile= request.user.profile
    form = ProjectForm()

    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(',', " ").split(" ")
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('user-account')


    context= {'form':form}
    return render(request, 'projects/project_form.html', context)

@login_required(login_url='login')
def updateProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance = project)

    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(',', " ").split(" ")
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project=form.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)

            return redirect('user-account')


    context= {'form':form, 'project':project}
    return render(request, 'projects/project_form.html', context)

@login_required(login_url='login')
def deleteProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('user-account')
    context = {
'object':project
    }
    return render(request, 'delete_template.html', context)
