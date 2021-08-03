from django.core import paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Tag, Review
from .forms import ProjectForm, ReviewForm
from .utils import searchProject, paginationProjects

# Create your views here.


def projects(request):
    projectsList, search_query = searchProject(request)
    custom_range, projectsList = paginationProjects(request, projectsList, 6)

    return render(
        request,
        "app1/projects.html",
        {
            "projects": projectsList,
            "search_query": search_query,
            "custom_range": custom_range,
        },
    )


def project(request, pk):
    projectObj = Project.objects.get(id=pk)
    form = ReviewForm()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        review = form.save(commit=False)
        review.project = projectObj
        review.owner = request.user.profile
        review.save()

        projectObj.getVoteCount

        messages.success(request, "Your review has been submitted sucessfully")
        return redirect("project", pk=projectObj.id)

    return render(
        request, "app1/single-project.html", {"obj": projectObj, "form": form}
    )


@login_required(login_url="login")
def createProject(request):
    profile = request.user.profile
    form = ProjectForm()
    if request.method == "POST":
        newtags = request.POST.get('newtags').replace(',',' ').split()

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()

            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)

            return redirect("account")
    return render(request, "app1/project_form.html", {"form": form})


@login_required(login_url="login")
def updateProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance=project)

    if request.method == "POST":
        newtags = request.POST.get('newtags').replace(',',' ').split()

        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save()

            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)

            return redirect("projects")
    return render(request, "app1/project_form.html", {"form": form,'project':project})


@login_required(login_url="login")
def deleteProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    if request.method == "POST":
        project.delete()
        return redirect("projects")
    return render(request, "delete_template.html", {"object": project})
