from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Profile, Message
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .utils import searchProjects, paginationProfiles


# Create your views here.


def profiles(request):
    profiles, search_query = searchProjects(request)

    custom_range, profiles = paginationProfiles(request, profiles, 3)

    return render(
        request,
        "app2/profiles.html",
        {
            "profiles": profiles,
            "search_query": search_query,
            "custom_range": custom_range,
        },
    )


def userProfile(request, pk):
    user = Profile.objects.get(id=pk)
    topSkills = user.skill_set.exclude(description__exact="")
    otherSkills = user.skill_set.filter(description="")
    return render(
        request,
        "app2/user_profile.html",
        {"user": user, "topSkills": topSkills, "otherSkills": otherSkills},
    )


def loginUser(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("profiles")

    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Username Does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET["next"] if "next" in request.GET else "account")
        else:
            messages.error(request, "Username or Password is incorrect")

    return render(request, "app2/login_register.html", {"page": page})


def logoutUser(request):
    logout(request)
    messages.info(request, "User logged out Sucessfully")
    return redirect("login")


def registerUser(request):
    page = "register"
    form = CustomUserCreationForm()
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, "Your account has been created sucessfully")
            login(request, user)
            return redirect("edit-account")
        else:
            messages.error(request, "An error has occurred during registration")

    return render(request, "app2/login_register.html", {"page": page, "form": form})


@login_required(login_url="login")
def userAccount(request):
    profile = request.user.profile

    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    return render(
        request,
        "app2/account.html",
        {"profile": profile, "skills": skills, "projects": projects},
    )


@login_required(login_url="login")
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("account")
    return render(request, "app2/profile_form.html", {"form": form})


@login_required(login_url="login")
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, "Your skill was added successfully")
            return redirect("account")
    return render(request, "app2/skill_form.html", {"form": form})


@login_required(login_url="login")
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            skill.save()
            messages.success(request, "Your skill was updated successfully")
            return redirect("account")
    return render(request, "app2/skill_form.html", {"form": form})


@login_required(login_url="login")
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Your skill has been deleted successfully")
        return redirect("account")
    return render(request, "delete_template.html", {"object": skill})


@login_required(login_url="login")
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    totalMessages = messageRequests.count()
    return render(
        request,
        "app2/inbox.html",
        {
            "messageRequests": messageRequests,
            "unreadCount": unreadCount,
            "totalMessages": totalMessages,
        },
    )


@login_required(login_url="login")
def viewMessage(request, pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    return render(request, "app2/message.html", {"message": message})


def createMessage(request, pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    if request.method == "POST":
        form = MessageForm(request.POST)

        try:
            sender = request.user.profile
        except:
            sender = None

        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request, "Message sent!")
            return redirect("user-profile", pk=recipient.id)

    return render(
        request, "app2/message_form.html", {"recipient": recipient, "form": form}
    )
