from django.db.models.query import prefetch_related_objects
from django.db.models.query_utils import Q
from .models import *
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from .forms import *
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from itertools import chain
from django.core.exceptions import ObjectDoesNotExist
from dateutil.relativedelta import relativedelta
from urllib.parse import urlencode

# Create your views here.

def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    folders = Folder.objects.filter(Q(creator = request.user) & Q(parentFolders__isnull = True))
    researchWorks = ResearchWork.objects.filter(Q(researcher = request.user) & Q(folder__isnull = True))
    mergedSummaries = MergedSummary.objects.filter(Q(merger = request.user) & Q(folder__isnull = True))
    return render(request,"research_app/home.html", {
        "folders":folders,
        "researchWorks":researchWorks,
        "mergedSummaries":mergedSummaries,
    })

def signUp(request):
    if request.method=='POST':
        username = (request.POST["username"].strip())
        email = (request.POST["email"].strip())
        password = (request.POST["password"])
        cpassword = request.POST["cpassword"]

        if password == cpassword:
            if User.objects.filter(email = email).exists():
                request.session["failMessage"] = "That Email has already been used!"
                request.session["successMessage"] = ""
            else:
                the_user = User(
                    username = username,
                    email = email,
                )
                the_user.set_password(password)
                the_user.save()

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                
                request.session["failMessage"] = ""
                request.session["successMessage"] = "Signed Up successfully"
                return redirect("home")
        else:
            request.session["failMessage"] = "Passwords didn't Match"
            request.session["successMessage"] = ""
            return redirect("signup")
    else:
        request.session["failMessage"] = ""
        return render(request,"research_app/signup.html")

def logIn(request):
    if request.method=='POST':
        email = (request.POST["email"].strip())
        password = (request.POST["password"])

        if User.objects.filter(email = email).exists():
            username = User.objects.get(email = email).username
            if not User.objects.get(email = email).check_password(password):
                request.session["failMessage"] = "Wrong Password, sign up instead if you have no account"
                request.session["successMessage"] = ""
                return redirect("login")
        else:
            request.session["failMessage"] = "Wrong Email, sign up instead if you have no account"
            request.session["successMessage"] = ""
            return redirect("login")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            request.session["failMessage"] = ""
            request.session["successMessage"] = "Logged in Successfully"
            return redirect("home")
        else:
            request.session["failMessage"] = "Wrong Credentials, sign up instead if you have no account"
            request.session["successMessage"] = ""
            return redirect("login")
    else:
        request.session["failMessage"] = ""
        return render(request,"research_app/login.html")

def logOut(request):
    logout(request)
    return redirect("home")

def addTopic(request):
    if request.method=='POST':
        parentFolder = (request.POST.get("folder",False))
        docType = (request.POST["type"].strip())
        name = (request.POST["name"].strip())
        description = (request.POST["description"].strip())

        if docType == "folder":
            if not Folder.objects.filter(Q(name = name) & Q(creator = request.user)).exists():
                if parentFolder:
                    newFolder = Folder(
                        name = name,
                        description = description,
                        folder = parentFolder,
                        creator = request.user,
                    )
                else:
                    newFolder = Folder(
                        name = name,
                        description = description,
                        creator = request.user,
                    )
                newFolder.save()
                request.session["successMessage"] = "Folder Created successfully"
                request.session["failMessage"] = ""

            else:
                request.session["failMessage"] = "You already created a folder with that same name, search for it to see it"
                request.session["successMessage"] = ""

        elif docType == "researchWork":
            if not ResearchWork.objects.filter(Q(name = name) & Q(researcher = request.user)).exists():
                if parentFolder:
                    newResearchWork = ResearchWork(
                        name = name,
                        description = description,
                        folder = parentFolder,
                        researcher = request.user,
                    )
                else:
                    newResearchWork = ResearchWork(
                        name = name,
                        description = description,
                        researcher = request.user,
                    )
                newResearchWork.save()
                request.session["successMessage"] = "Research Work Created successfully"
                request.session["failMessage"] = ""

            else:
                request.session["failMessage"] = "You already created a research work with that same name, search for it to see it"
                request.session["successMessage"] = ""

        elif docType == "mergedSummary":
            if not MergedSummary.objects.filter(Q(name = name) & Q(merger = request.user)).exists():
                if parentFolder:
                    newMergedSummary = MergedSummary(
                        name = name,
                        description = description,
                        folder = parentFolder,
                        merger = request.user,
                    )
                else:
                    newMergedSummary = MergedSummary(
                        name = name,
                        description = description,
                        merger = request.user,
                    )
                newMergedSummary.save()
                request.session["successMessage"] = "Merged Summary Created successfully"
                request.session["failMessage"] = ""

            else:
                request.session["failMessage"] = "You already created a Merged Summary with that same name, search for it to see it"
                request.session["successMessage"] = ""
        return redirect("home")

def editTopic(request):
    if request.method=='POST':
        topicId = int(request.POST["id"].strip())
        docType = (request.POST["type"].strip())
        name = (request.POST["name"].strip())
        description = (request.POST["description"].strip())

        if docType == "folder":
            folder = Folder.objects.get(id = topicId)
            folder.name = name
            folder.description = description
            folder.save()

            request.session["successMessage"] = "Folder Editting was successful"
            request.session["failMessage"] = ""

        elif docType == "researchWork":
            researckWork = ResearchWork.objects.get(id = topicId)
            researckWork.name = name
            researckWork.description = description
            researckWork.save()

            request.session["successMessage"] = "Research Work Editting was successful"
            request.session["failMessage"] = ""

        elif docType == "mergedSummary":
            mergedSummary = MergedSummary.objects.get(id = topicId)
            mergedSummary.name = name
            mergedSummary.description = description
            mergedSummary.save()

            request.session["successMessage"] = "Merged Summary Editting was successful"
            request.session["failMessage"] = ""

        request.session["editId"] = ""
        request.session["editType"] = ""
        
    elif request.method=='GET':
        topicId = int(request.GET["id"])
        docType = request.GET["type"]

        if docType == "folder":
            folder = Folder.objects.get(id = topicId)
            request.session["name"] = folder.name
            request.session["description"] = folder.description

        elif docType == "researchWork":
            researchWork = ResearchWork.objects.get(id = topicId)
            request.session["name"] = researchWork.name
            request.session["description"] = researchWork.description

        elif docType == "mergedSummary":
            mergedSummary = MergedSummary.objects.get(id = topicId)
            request.session["name"] = mergedSummary.name
            request.session["description"] = mergedSummary.description

        request.session["editId"] = topicId
        request.session["editType"] = docType
    return redirect("home")

def deleteTopic(request):
    if request.method=='GET':
        topicId = int(request.GET["id"])
        docType = request.GET["type"]

        if docType == "folder":
            Folder.objects.get(id = topicId).delete()
            request.session["successMessage"] = "Folder deleted successfully"
            request.session["failMessage"] = ""

        elif docType == "researchWork":
            ResearchWork.objects.get(id = topicId).delete()
            request.session["successMessage"] = "Research Work deleted successfully"
            request.session["failMessage"] = ""

        elif docType == "mergedSummary":
            MergedSummary.objects.get(id = topicId).delete()
            request.session["successMessage"] = "Merged Summary deleted successfully"
            request.session["failMessage"] = ""

        return redirect("home")

# #home page
# def home_out(request):
#     user = User.objects.filter(is_active = True)
#     profiles = Member.objects.filter(user__in = user)
#     projects = ProjectMade.objects.all()
    
#     highest_performance = 0
#     highest_creativity = 0
#     highest_research = 0
#     for the_profile in profiles:
#         if MonthlyTracking.objects.filter(member = the_profile).count() >= 3:
#             query = MonthlyTracking.objects.filter(member = the_profile).order_by("-date")
#             the_lastone = query[2]
#         else:
#             the_lastone = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = the_profile,)
#         if (the_profile.performance()-the_lastone.performance) > highest_performance:
#             highest_performance = (the_profile.performance()-the_lastone.performance)
#         if (the_profile.creativity()-the_lastone.creativity) > highest_creativity:
#             highest_creativity = (the_profile.creativity()-the_lastone.creativity)
#         if (the_profile.research()-the_lastone.research) > highest_research:
#             highest_research = (the_profile.research()-the_lastone.research)
        
#     class The_Profile:
#         def __init__(self,pbadge,cbadge,rbadge,rank):
#             self.pbadge = pbadge
#             self.cbadge = cbadge
#             self.rbadge = rbadge
#             self.rank = rank

#     the_profiles = []
#     for the_profile in profiles:
#         if the_profile.monthly_tracking.all().count() >= 3:
#             query = the_profile.monthly_tracking.all().order_by("-date")
#             lastone = query[2]
#         else:
#             lastone = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = the_profile,)
        
#         if (the_profile.performance()-lastone.performance) > ((highest_performance/2)+(2*(highest_performance/2)/3)):
#             pbadge = 3
#         elif (the_profile.performance()-lastone.performance) > ((highest_performance/2)+(1*(highest_performance/2)/3)):
#             pbadge = 2
#         elif (the_profile.performance()-lastone.performance) > (highest_performance/2):
#             pbadge = 1
#         else:
#             pbadge = 0

#         if (the_profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(2*(highest_creativity/2)/3)):
#             cbadge = 3
#         elif (the_profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(1*(highest_creativity/2)/3)):
#             cbadge = 2
#         elif (the_profile.creativity()-lastone.creativity) > (highest_creativity/2):
#             cbadge = 1
#         else:
#             cbadge = 0

#         if (the_profile.research()-lastone.research) > ((highest_research/2)+(2*(highest_research/2)/3)):
#             rbadge = 3
#         elif (the_profile.research()-lastone.research) > ((highest_research/2)+(1*(highest_research/2)/3)):
#             rbadge = 2
#         elif (the_profile.research()-lastone.research) > (highest_research/2):
#             rbadge = 1
#         else:
#             rbadge = 0

#         if pbadge == 0 or cbadge == 0 or rbadge == 0:
#             rank = "Novice"
#         if pbadge == 1 or cbadge == 1 or rbadge == 1:
#             rank = "Junior"
#         if pbadge == 1 and cbadge == 1 and rbadge == 1:
#             rank = "All-Rounder"
#         if pbadge == 2 or cbadge == 2 or rbadge == 2:
#             rank = "Senior"
#         if (pbadge >= 1 and cbadge >= 1 and rbadge == 2) or (pbadge >= 1 and cbadge == 2 and rbadge >= 1) or (pbadge == 2 and cbadge >= 1 and rbadge >= 1):
#             rank = "Pro"  
#         if pbadge == 3 or cbadge == 3 or rbadge == 3:
#             rank = "Specialist"
#         if (pbadge >= 1 and cbadge >= 1 and rbadge == 3) or (pbadge >= 1 and cbadge == 3 and rbadge >= 1) or (pbadge == 3 and cbadge >= 1 and rbadge >= 1):  
#             rank = "Expert"
#         if pbadge == 2 and cbadge == 2 and rbadge == 2:
#             rank = "Master"
#         if (pbadge >= 2 and cbadge >= 2 and rbadge == 3) or (pbadge >= 2 and cbadge == 3 and rbadge >= 2) or (pbadge == 3 and cbadge >= 2 and rbadge >= 2):
#             rank = "Genius"
#         if pbadge == 3 and cbadge == 3 and rbadge == 3:
#             rank = "GrandMaster"

#         def pbadge1(x):
#             if x == 1:
#                 return "Doer"
#             elif x == 2:
#                 return "Executor"
#             elif x == 3:
#                 return "Achiever"
#             elif x == 0:
#                 return "Lazy Dog"
#             else:
#                 return ""
        
#         def cbadge1(x):
#             if x == 1:
#                 return "Dreamer"
#             elif x == 2:
#                 return "Idealist"
#             elif x == 3:
#                 return "Visionary"
#             elif x == 0:
#                 return "Uncreative"
#             else:
#                 return ""

#         def rbadge1(x):
#             if x == 1:
#                 return "Learner"
#             elif x == 2:
#                 return "Researcher"
#             elif x == 3:
#                 return "Consultant"
#             elif x == 0:
#                 return "Ignorant"
#             else:
#                 return ""

#         the_profiles.append(The_Profile(pbadge1(pbadge),cbadge1(cbadge),rbadge1(rbadge),rank))

#     if request.method=='POST':
#         username = (request.POST["username"]).strip()
#         password = (request.POST["password"])
#         user = authenticate(request, username=username, password=password)
#         if user is not None and Member.objects.filter(user = user).exists():
#             login(request, user)
            
#             #updating profile status
#             member = Member.objects.get(user = request.user)
            

#             if not MonthlyTracking.objects.filter(Q(member = member) & Q(date__year = (datetime.now() + relativedelta(months=-1)).year) & Q(date__month = (datetime.now() + relativedelta(months=-1)).month)).exists():
                
#                 if MonthlyTracking.objects.filter(member = member).count() >= 3:
#                     query = MonthlyTracking.objects.filter(member = member).order_by("-date")
#                     lastone = query[2]
#                 else:
#                     lastone = MonthlyTracking(
#                             date = datetime.now() + relativedelta(months=-1),
#                             member = member,)
                
#                 monthly_tracking = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = member,

#                     performance = float(member.performance() or 0),
#                     tasks_done = float(member.tasks_done or 0),
#                     tasks_approved = float(member.approved_tasks() or 0),
#                     tasks_unapproved = float(member.unapproved_tasks() or 0),
#                     deadlines_beaten = float(member.deadlines_met or 0),
#                     deadlines_missed = float(member.deadlines_missed or 0),
#                     tasks_given_up = float(member.tasks_givenup or 0),

#                     avg_tasks_approval = float(member.avg_tasks_approval() or 0),
#                     num_tasks_approval = float(member.num_tasks_approval() or 0),

#                     avg_tasks_progress = float(member.progress() or 0),
#                     num_tasks_progress = float(member.num_progress() or 0),

#                     #use tasks_done
#                     total_tasks_completion_speed = float(member.duration_in_seconds(member.total_tasks_duration() or 0)),

#                     tasks_started = float(member.tasks_started() or 0),
#                     tasks_rectified = float(member.tasks_rectified or 0),

#                     avg_projects_contribution = float(member.avg_project_contribution() or 0),
#                     num_projects_contributed = float(member.num_project_contribution() or 0),

#                     total_dealine_excess_time = float(member.duration_in_seconds(member.passed_deadline() or 0)),
#                     tasks_approvals_made = float(member.approvals_made() or 0),
#                     tasks_objections_made = float(member.tasks_objections_made or 0),

#                     requirements_engineering = float(member.re() or 0),
#                     sad = float(member.sad() or 0),
#                     ui = float(member.ui() or 0),
#                     dsa = float(member.dsa() or 0),
#                     code = float(member.code() or 0),
#                     test = float(member.test() or 0),

#                     creativity = float(member.creativity() or 0),
#                     ideas_generated = float(member.ideas_num() or 0),

#                     avg_ideas_ratings = float(member.ideas_avg_ratings() or 0),
#                     num_ideas_ratings = float(member.ideas_num_ratings() or 0),
                    
#                     supplements_made = float(member.supplements_num() or 0),
#                     supplements_implemented = float(member.supplements_implemented() or 0),
#                     your_ideas_realised = float(member.realised_ideas() or 0),

#                     avg_your_ideas_realised_ratings = float(member.realised_ideas_ratings() or 0),
#                     num_your_ideas_realised_raters = float(member.realised_ideas_raters() or 0),

#                     research = float(member.research() or 0),
#                     resources_shared = float(member.resources_shared() or 0),

#                     avg_resources_shared_ratings = float(member.resources_shared_ratings() or 0),
#                     num_resources_shared_ratings = float(member.resources_shared_ratings_num() or 0),

#                     resource_ratings_made = float(member.resource_ratings_made() or 0),
#                     experience_shared = float(member.experience_shared() or 0),

#                     avg_experience_shared_ratings = float(member.experience_shared_ratings() or 0),
#                     num_experience_shared_ratings = float(member.experience_shared_ratings_num() or 0),

#                     experience_ratings_made = float(member.experience_ratings_made() or 0),
#                     ideas_ratings_made = float(member.idea_ratings_made() or 0),
#                 )
#                 monthly_tracking.save()

#                 if member.highest_performance < (monthly_tracking.performance - lastone.performance):
#                     member.highest_performance = (monthly_tracking.performance - lastone.performance)
#                 if member.highest_creativity < (monthly_tracking.creativity - lastone.creativity):
#                     member.highest_creativity = (monthly_tracking.creativity - lastone.creativity)
#                 if member.highest_research < (monthly_tracking.research - lastone.research):
#                     member.highest_research = (monthly_tracking.research - lastone.research)
#                 member.save()
                
#             #end of updating profile status

#             return HttpResponseRedirect(reverse("home_in"))
#         else:
#             return render(request, "Accounts/home-logout.html", {
#                 "message":"Invalid Credentials",
#                 "ContactUs": ContactUs(),
#                 "login": Login(),
#                 "rate":Rate(),
#                 "profiles":zip(profiles,the_profiles),
#                 "projects":projects,
#             })
#     return render(request, "Accounts/home-logout.html", {
#                 "ContactUs": ContactUs(),
#                 "login": Login(),
#                 "rate":Rate(),
#                 "profiles":zip(profiles,the_profiles), 
#                 "projects":projects,
#             })
    
# def home_in(request):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect(reverse("home_out"))
#     user = User.objects.filter(is_active = True)
#     profiles = Member.objects.filter(user__in = user)
#     projects = ProjectMade.objects.all()

#     highest_performance = 0
#     highest_creativity = 0
#     highest_research = 0
#     for the_profile in profiles:
#         if MonthlyTracking.objects.filter(member = the_profile).count() >= 3:
#             query = MonthlyTracking.objects.filter(member = the_profile).order_by("-date")
#             the_lastone = query[2]
#         else:
#             the_lastone = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = the_profile,)
#         if (the_profile.performance()-the_lastone.performance) > highest_performance:
#             highest_performance = (the_profile.performance()-the_lastone.performance)
#         if (the_profile.creativity()-the_lastone.creativity) > highest_creativity:
#             highest_creativity = (the_profile.creativity()-the_lastone.creativity)
#         if (the_profile.research()-the_lastone.research) > highest_research:
#             highest_research = (the_profile.research()-the_lastone.research)
        
#     class The_Profile:
#         def __init__(self,pbadge,cbadge,rbadge,rank):
#             self.pbadge = pbadge
#             self.cbadge = cbadge
#             self.rbadge = rbadge
#             self.rank = rank

#     the_profiles = []
#     for the_profile in profiles:
#         if the_profile.monthly_tracking.all().count() >= 3:
#             query = the_profile.monthly_tracking.all().order_by("-date")
#             lastone = query[2]
#         else:
#             lastone = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = the_profile,)
        
#         if (the_profile.performance()-lastone.performance) > ((highest_performance/2)+(2*(highest_performance/2)/3)):
#             pbadge = 3
#         elif (the_profile.performance()-lastone.performance) > ((highest_performance/2)+(1*(highest_performance/2)/3)):
#             pbadge = 2
#         elif (the_profile.performance()-lastone.performance) > (highest_performance/2):
#             pbadge = 1
#         else:
#             pbadge = 0

#         if (the_profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(2*(highest_creativity/2)/3)):
#             cbadge = 3
#         elif (the_profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(1*(highest_creativity/2)/3)):
#             cbadge = 2
#         elif (the_profile.creativity()-lastone.creativity) > (highest_creativity/2):
#             cbadge = 1
#         else:
#             cbadge = 0

#         if (the_profile.research()-lastone.research) > ((highest_research/2)+(2*(highest_research/2)/3)):
#             rbadge = 3
#         elif (the_profile.research()-lastone.research) > ((highest_research/2)+(1*(highest_research/2)/3)):
#             rbadge = 2
#         elif (the_profile.research()-lastone.research) > (highest_research/2):
#             rbadge = 1
#         else:
#             rbadge = 0

#         if pbadge == 0 or cbadge == 0 or rbadge == 0:
#             rank = "Novice"
#         if pbadge == 1 or cbadge == 1 or rbadge == 1:
#             rank = "Junior"
#         if pbadge == 1 and cbadge == 1 and rbadge == 1:
#             rank = "All-Rounder"
#         if pbadge == 2 or cbadge == 2 or rbadge == 2:
#             rank = "Senior"
#         if (pbadge >= 1 and cbadge >= 1 and rbadge == 2) or (pbadge >= 1 and cbadge == 2 and rbadge >= 1) or (pbadge == 2 and cbadge >= 1 and rbadge >= 1):
#             rank = "Pro"  
#         if pbadge == 3 or cbadge == 3 or rbadge == 3:
#             rank = "Specialist"
#         if (pbadge >= 1 and cbadge >= 1 and rbadge == 3) or (pbadge >= 1 and cbadge == 3 and rbadge >= 1) or (pbadge == 3 and cbadge >= 1 and rbadge >= 1):  
#             rank = "Expert"
#         if pbadge == 2 and cbadge == 2 and rbadge == 2:
#             rank = "Master"
#         if (pbadge >= 2 and cbadge >= 2 and rbadge == 3) or (pbadge >= 2 and cbadge == 3 and rbadge >= 2) or (pbadge == 3 and cbadge >= 2 and rbadge >= 2):
#             rank = "Genius"
#         if pbadge == 3 and cbadge == 3 and rbadge == 3:
#             rank = "GrandMaster"

#         def pbadge1(x):
#             if x == 1:
#                 return "Doer"
#             elif x == 2:
#                 return "Executor"
#             elif x == 3:
#                 return "Achiever"
#             elif x == 0:
#                 return "Lazy Dog"
#             else:
#                 return ""
        
#         def cbadge1(x):
#             if x == 1:
#                 return "Dreamer"
#             elif x == 2:
#                 return "Idealist"
#             elif x == 3:
#                 return "Visionary"
#             elif x == 0:
#                 return "Uncreative"
#             else:
#                 return ""

#         def rbadge1(x):
#             if x == 1:
#                 return "Learner"
#             elif x == 2:
#                 return "Researcher"
#             elif x == 3:
#                 return "Consultant"
#             elif x == 0:
#                 return "Ignorant"
#             else:
#                 return ""

#         the_profiles.append(The_Profile(pbadge1(pbadge),cbadge1(cbadge),rbadge1(rbadge),rank))
#     return render(request, "Accounts/home-login.html", {
#         "profiles":zip(profiles,the_profiles),
#         "projects":projects,
#         # "event":EventForm(),
#         "reply":ReplyForm,
#         "User":User.objects.all(),
#     })

# def log_out(request):
#     logout(request)
#     user = User.objects.filter(is_active = True)
#     profiles = Member.objects.filter(user__in = user)
#     projects = ProjectMade.objects.all()

#     highest_performance = 0
#     highest_creativity = 0
#     highest_research = 0
#     for the_profile in profiles:
#         if MonthlyTracking.objects.filter(member = the_profile).count() >= 3:
#             query = MonthlyTracking.objects.filter(member = the_profile).order_by("-date")
#             the_lastone = query[2]
#         else:
#             the_lastone = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = the_profile,)
#         if (the_profile.performance()-the_lastone.performance) > highest_performance:
#             highest_performance = (the_profile.performance()-the_lastone.performance)
#         if (the_profile.creativity()-the_lastone.creativity) > highest_creativity:
#             highest_creativity = (the_profile.creativity()-the_lastone.creativity)
#         if (the_profile.research()-the_lastone.research) > highest_research:
#             highest_research = (the_profile.research()-the_lastone.research)
        
#     class The_Profile:
#         def __init__(self,pbadge,cbadge,rbadge,rank):
#             self.pbadge = pbadge
#             self.cbadge = cbadge
#             self.rbadge = rbadge
#             self.rank = rank

#     the_profiles = []
#     for the_profile in profiles:
#         if the_profile.monthly_tracking.all().count() >= 3:
#             query = the_profile.monthly_tracking.all().order_by("-date")
#             lastone = query[2]
#         else:
#             lastone = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = the_profile,)
        
#         if (the_profile.performance()-lastone.performance) > ((highest_performance/2)+(2*(highest_performance/2)/3)):
#             pbadge = 3
#         elif (the_profile.performance()-lastone.performance) > ((highest_performance/2)+(1*(highest_performance/2)/3)):
#             pbadge = 2
#         elif (the_profile.performance()-lastone.performance) > (highest_performance/2):
#             pbadge = 1
#         else:
#             pbadge = 0

#         if (the_profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(2*(highest_creativity/2)/3)):
#             cbadge = 3
#         elif (the_profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(1*(highest_creativity/2)/3)):
#             cbadge = 2
#         elif (the_profile.creativity()-lastone.creativity) > (highest_creativity/2):
#             cbadge = 1
#         else:
#             cbadge = 0

#         if (the_profile.research()-lastone.research) > ((highest_research/2)+(2*(highest_research/2)/3)):
#             rbadge = 3
#         elif (the_profile.research()-lastone.research) > ((highest_research/2)+(1*(highest_research/2)/3)):
#             rbadge = 2
#         elif (the_profile.research()-lastone.research) > (highest_research/2):
#             rbadge = 1
#         else:
#             rbadge = 0

#         if pbadge == 0 or cbadge == 0 or rbadge == 0:
#             rank = "Novice"
#         if pbadge == 1 or cbadge == 1 or rbadge == 1:
#             rank = "Junior"
#         if pbadge == 1 and cbadge == 1 and rbadge == 1:
#             rank = "All-Rounder"
#         if pbadge == 2 or cbadge == 2 or rbadge == 2:
#             rank = "Senior"
#         if (pbadge >= 1 and cbadge >= 1 and rbadge == 2) or (pbadge >= 1 and cbadge == 2 and rbadge >= 1) or (pbadge == 2 and cbadge >= 1 and rbadge >= 1):
#             rank = "Pro"  
#         if pbadge == 3 or cbadge == 3 or rbadge == 3:
#             rank = "Specialist"
#         if (pbadge >= 1 and cbadge >= 1 and rbadge == 3) or (pbadge >= 1 and cbadge == 3 and rbadge >= 1) or (pbadge == 3 and cbadge >= 1 and rbadge >= 1):  
#             rank = "Expert"
#         if pbadge == 2 and cbadge == 2 and rbadge == 2:
#             rank = "Master"
#         if (pbadge >= 2 and cbadge >= 2 and rbadge == 3) or (pbadge >= 2 and cbadge == 3 and rbadge >= 2) or (pbadge == 3 and cbadge >= 2 and rbadge >= 2):
#             rank = "Genius"
#         if pbadge == 3 and cbadge == 3 and rbadge == 3:
#             rank = "GrandMaster"

#         def pbadge1(x):
#             if x == 1:
#                 return "Doer"
#             elif x == 2:
#                 return "Executor"
#             elif x == 3:
#                 return "Achiever"
#             elif x == 0:
#                 return "Lazy Dog"
#             else:
#                 return ""
        
#         def cbadge1(x):
#             if x == 1:
#                 return "Dreamer"
#             elif x == 2:
#                 return "Idealist"
#             elif x == 3:
#                 return "Visionary"
#             elif x == 0:
#                 return "Uncreative"
#             else:
#                 return ""

#         def rbadge1(x):
#             if x == 1:
#                 return "Learner"
#             elif x == 2:
#                 return "Researcher"
#             elif x == 3:
#                 return "Consultant"
#             elif x == 0:
#                 return "Ignorant"
#             else:
#                 return ""

#         the_profiles.append(The_Profile(pbadge1(pbadge),cbadge1(cbadge),rbadge1(rbadge),rank))

#     return render(request, "Accounts/home-logout.html", {
#                 "message":"Logged Out",
#                 "ContactUs": ContactUs(),
#                 "login": Login(),
#                 "rate":Rate(),
#                 "profiles":zip(profiles,the_profiles), 
#                 "projects":projects,
#     })

# def rate_project(request,project_id):
#     if request.method=='POST':
#         form = Rate(request.POST)
#         if form.is_valid():
#             ratings = int((form.cleaned_data["ratings"]))
#             review = (form.cleaned_data["review"]).strip()
#             email = (form.cleaned_data["email"]).strip()
            
#             project = ProjectMade.objects.get(id=project_id)
#             if(ProjectRatings.objects.filter(email=email).exists()):
#                 project_rating = ProjectRatings.objects.get(email = email)
#                 project.avg_ratings = ((project.avg_ratings * project.num_ratings) - project_rating.ratings + ratings)/(project.num_ratings)
#                 project.save()

#                 project_rating.ratings = ratings
#                 project_rating.review = review
#                 project_rating.save()
#             else:            
#                 project.avg_ratings = ((project.avg_ratings * project.num_ratings)+ ratings)/(project.num_ratings + 1)
#                 project.num_ratings = project.num_ratings + 1
#                 project.save()


#                 project_rating = ProjectRatings(
#                     ratings = ratings,
#                     review = review,
#                     email = email,
#                     project = project, 
#                 )
#                 project_rating.save()
#         else:
#             user = User.objects.filter(is_active = True)
#             profiles = Member.objects.filter(user__in = user)
#             projects = ProjectMade.objects.all()
#             return render(request,'Accounts/home-logout.html',{
#                 "ContactUs": ContactUs(),
#                 "login": Login(),
#                 "rate":Rate(request.POST),
#                 "profiles":profiles, 
#                 "projects":projects,
#             })
#     return HttpResponseRedirect(reverse("home_out")) 

# def reply(request,rating_id):
#     if request.method=='POST':
#         form = ReplyForm(request.POST)
#         if form.is_valid():
#             reply = form.save(commit=False)
#             reply.ratings = ProjectRatings.objects.get(id=rating_id)
#             reply.member = Member.objects.get(user=request.user)
#             reply.save()
#     return redirect("home_in")
    
# def profile(request,member):
#     defined = request.GET.get("defined")
#     described = request.GET.get("described")
#     if not defined:
#         defined = ""
#     if not described:
#         described = ""
#     profile = Member.objects.get(id=member)

#     if MonthlyTracking.objects.filter(member = profile).count() >= 3:
#         query = MonthlyTracking.objects.filter(member = profile).order_by("-date")
#         lastone = query[2]
#     else:
#         lastone = MonthlyTracking(
#                 date = datetime.now() + relativedelta(months=-1),
#                 member = profile,)

#     #rank against yourself
#     if (profile.performance()-lastone.performance) > ((profile.highest_performance/2)+(2*(profile.highest_performance/2)/3)):
#         pbadge1 = 3
#     elif (profile.performance()-lastone.performance) > ((profile.highest_performance/2)+(1*(profile.highest_performance/2)/3)):
#         pbadge1 = 2
#     elif (profile.performance()-lastone.performance) > (profile.highest_performance/2):
#         pbadge1 = 1
#     else:
#         pbadge1 = 0

#     if (profile.creativity()-lastone.creativity) > ((profile.highest_creativity/2)+(2*(profile.highest_creativity/2)/3)):
#         cbadge1 = 3
#     elif (profile.creativity()-lastone.creativity) > ((profile.highest_creativity/2)+(1*(profile.highest_creativity/2)/3)):
#         cbadge1 = 2
#     elif (profile.creativity()-lastone.creativity) > (profile.highest_creativity/2):
#         cbadge1 = 1
#     else:
#         cbadge1 = 0

#     if (profile.research()-lastone.research) > ((profile.highest_research/2)+(2*(profile.highest_research/2)/3)):
#         rbadge1 = 3
#     elif (profile.research()-lastone.research) > ((profile.highest_research/2)+(1*(profile.highest_research/2)/3)):
#         rbadge1 = 2
#     elif (profile.research()-lastone.research) > (profile.highest_research/2):
#         rbadge1 = 1
#     else:
#         rbadge1 = 0

#     def ranker(pbadge,cbadge,rbadge):
#         if pbadge == 0 or cbadge == 0 or rbadge == 0:
#             rank = "Novice"
#         if pbadge == 1 or cbadge == 1 or rbadge == 1:
#             rank = "Junior"
#         if pbadge == 1 and cbadge == 1 and rbadge == 1:
#             rank = "All-Rounder"
#         if pbadge == 2 or cbadge == 2 or rbadge == 2:
#             rank = "Senior"
#         if (pbadge >= 1 and cbadge >= 1 and rbadge == 2) or (pbadge >= 1 and cbadge == 2 and rbadge >= 1) or (pbadge == 2 and cbadge >= 1 and rbadge >= 1):
#             rank = "Pro"  
#         if pbadge == 3 or cbadge == 3 or rbadge == 3:
#             rank = "Specialist"
#         if (pbadge >= 1 and cbadge >= 1 and rbadge == 3) or (pbadge >= 1 and cbadge == 3 and rbadge >= 1) or (pbadge == 3 and cbadge >= 1 and rbadge >= 1):  
#             rank = "Expert"
#         if pbadge == 2 and cbadge == 2 and rbadge == 2:
#             rank = "Master"
#         if (pbadge >= 2 and cbadge >= 2 and rbadge == 3) or (pbadge >= 2 and cbadge == 3 and rbadge >= 2) or (pbadge == 3 and cbadge >= 2 and rbadge >= 2):
#             rank = "Genius"
#         if pbadge == 3 and cbadge == 3 and rbadge == 3:
#             rank = "GrandMaster"
#         return rank

#     #against each other
#     user = User.objects.filter(is_active = True)
#     profiles = Member.objects.filter(user__in = user)
#     highest_performance = 0
#     highest_creativity = 0
#     highest_research = 0
#     for the_profile in profiles:
#         if MonthlyTracking.objects.filter(member = the_profile).count() >= 3:
#             query = MonthlyTracking.objects.filter(member = the_profile).order_by("-date")
#             the_lastone = query[2]
#         else:
#             the_lastone = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = the_profile,)
#         if (the_profile.performance()-the_lastone.performance) > highest_performance:
#             highest_performance = (the_profile.performance()-the_lastone.performance)
#         if (the_profile.creativity()-the_lastone.creativity) > highest_creativity:
#             highest_creativity = (the_profile.creativity()-the_lastone.creativity)
#         if (the_profile.research()-the_lastone.research) > highest_research:
#             highest_research = (the_profile.research()-the_lastone.research)
    
#     if (profile.performance()-lastone.performance) > ((highest_performance/2)+(2*(highest_performance/2)/3)):
#         pbadge2 = 3
#     elif (profile.performance()-lastone.performance) > ((highest_performance/2)+(1*(highest_performance/2)/3)):
#         pbadge2 = 2
#     elif (profile.performance()-lastone.performance) > (highest_performance/2):
#         pbadge2 = 1
#     else:
#         pbadge2 = 0

#     if (profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(2*(highest_creativity/2)/3)):
#         cbadge2 = 3
#     elif (profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(1*(highest_creativity/2)/3)):
#         cbadge2 = 2
#     elif (profile.creativity()-lastone.creativity) > (highest_creativity/2):
#         cbadge2 = 1
#     else:
#         cbadge2 = 0

#     if (profile.research()-lastone.research) > ((highest_research/2)+(2*(highest_research/2)/3)):
#         rbadge2 = 3
#     elif (profile.research()-lastone.research) > ((highest_research/2)+(1*(highest_research/2)/3)):
#         rbadge2 = 2
#     elif (profile.research()-lastone.research) > (highest_research/2):
#         rbadge2 = 1
#     else:
#         rbadge2 = 0


#     #against the legends
#     for the_profile in profiles:
#         if the_profile.highest_performance > highest_performance:
#             highest_performance = the_profile.highest_performance
#         if the_profile.highest_creativity > highest_creativity:
#             highest_creativity = the_profile.highest_creativity
#         if the_profile.highest_research > highest_research:
#             highest_research = the_profile.highest_research
    
#     if (profile.performance()-lastone.performance) > ((highest_performance/2)+(2*(highest_performance/2)/3)):
#         pbadge3 = 3
#     elif (profile.performance()-lastone.performance) > ((highest_performance/2)+(1*(highest_performance/2)/3)):
#         pbadge3 = 2
#     elif (profile.performance()-lastone.performance) > (highest_performance/2):
#         pbadge3 = 1
#     else:
#         pbadge3 = 0

#     if (profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(2*(highest_creativity/2)/3)):
#         cbadge3 = 3
#     elif (profile.creativity()-lastone.creativity) > ((highest_creativity/2)+(1*(highest_creativity/2)/3)):
#         cbadge3 = 2
#     elif (profile.creativity()-lastone.creativity) > (highest_creativity/2):
#         cbadge3 = 1
#     else:
#         cbadge3 = 0

#     if (profile.research()-lastone.research) > ((highest_research/2)+(2*(highest_research/2)/3)):
#         rbadge3 = 3
#     elif (profile.research()-lastone.research) > ((highest_research/2)+(1*(highest_research/2)/3)):
#         rbadge3 = 2
#     elif (profile.research()-lastone.research) > (highest_research/2):
#         rbadge3 = 1
#     else:
#         rbadge3 = 0

#     def pbadge(x):
#         if x == 1:
#             return "Doer"
#         elif x == 2:
#             return "Executor"
#         elif x == 3:
#             return "Achiever"
#         elif x == 0:
#             return "Lazy Dog"
#         else:
#             return ""
    
#     def cbadge(x):
#         if x == 1:
#             return "Dreamer"
#         elif x == 2:
#             return "Idealist"
#         elif x == 3:
#             return "Visionary"
#         elif x == 0:
#             return "Uncreative"
#         else:
#             return ""

#     def rbadge(x):
#         if x == 1:
#             return "Learner"
#         elif x == 2:
#             return "Researcher"
#         elif x == 3:
#             return "Consultant"
#         elif x == 0:
#             return "Ignorant"
#         else:
#             return ""

#     def avg(current,current_num,last,last_num):
#         if current_num - last_num == 0:
#             return 0
#         else:
#             return ((current*current_num)-(last*last_num))/(current_num - last_num)
        
#     def major_role():
#         role = {
#             "Unknown":0,
#             "Software Analyst":profile.re()-lastone.requirements_engineering,
#             "Software Architect":profile.sad()-lastone.sad,
#             "UI/UX Designer":profile.ui()-lastone.ui,
#             "Software Engineer":profile.dsa()-lastone.dsa,
#             "Software Developer":profile.code()-lastone.code,
#             "Software Tester":profile.test()-lastone.test,
#             }
#         return max(role, key=role.get)

#     avg_tasks_approval = avg(profile.avg_tasks_approval(),profile.num_tasks_approval(),lastone.avg_tasks_approval,lastone.num_tasks_approval)
#     progress = avg(profile.progress(),profile.num_progress(),lastone.avg_tasks_progress,lastone.num_tasks_progress)
#     avg_project_contribution = avg(profile.avg_project_contribution(),profile.num_project_contribution(),lastone.avg_projects_contribution,lastone.num_projects_contributed)
#     ideas_avg_ratings = avg(profile.ideas_avg_ratings(),profile.ideas_num_ratings(),lastone.avg_ideas_ratings,lastone.num_ideas_ratings)
#     realised_ideas_ratings = avg(profile.realised_ideas_ratings(),profile.realised_ideas_raters(),lastone.avg_your_ideas_realised_ratings,lastone.num_your_ideas_realised_raters)
#     resources_shared_ratings = avg(profile.resources_shared_ratings(),profile.resources_shared_ratings_num(),lastone.avg_resources_shared_ratings,lastone.num_resources_shared_ratings)
#     experience_shared_ratings = avg(profile.experience_shared_ratings(),profile.experience_shared_ratings_num(),lastone.avg_experience_shared_ratings,lastone.num_experience_shared_ratings)

#     try:
#         task_speed = profile.not_seconds_hours(((profile.duration_in_seconds(profile.task_speed())*profile.tasks_done)-(lastone.total_tasks_completion_speed))/(profile.tasks_done - lastone.tasks_done))
#     except ZeroDivisionError:
#         task_speed = "infinity"
        
#     total_tasks_duration = profile.not_seconds_hours(((profile.duration_in_seconds(profile.total_tasks_duration()))-(lastone.total_tasks_completion_speed)))
#     passed_deadline = profile.not_seconds_hours(((profile.duration_in_seconds(profile.passed_deadline()))-(lastone.total_dealine_excess_time)))


#     return render(request,"Accounts/profile.html",{
#         "profile":profile,
#         "lastone":lastone,
#         "major_role":major_role(),

#         "task_speed":task_speed,
#         "total_tasks_duration":total_tasks_duration,
#         "passed_deadline":passed_deadline,

#         "avg_tasks_approval":avg_tasks_approval,
#         "progress":progress,
#         "progress":progress,
#         "avg_project_contribution":avg_project_contribution,
#         "ideas_avg_ratings":ideas_avg_ratings,
#         "realised_ideas_ratings":realised_ideas_ratings,
#         "resources_shared_ratings":resources_shared_ratings,
#         "experience_shared_ratings":experience_shared_ratings,

#         "myself": ranker(pbadge1,cbadge1,rbadge1),
#         "others": ranker(pbadge2,cbadge2,rbadge2),
#         "goats": ranker(pbadge3,cbadge3,rbadge3),

#         "pbadge1": pbadge(pbadge1),
#         "pbadge2": pbadge(pbadge2),
#         "pbadge3": pbadge(pbadge3),

#         "cbadge1": cbadge(cbadge1),
#         "cbadge2": cbadge(cbadge2),
#         "cbadge3": cbadge(cbadge3),

#         "rbadge1": rbadge(rbadge1),
#         "rbadge2": rbadge(rbadge2),
#         "rbadge3": rbadge(rbadge3),

#         "ContactUs": ContactUs(),
#         "defined":defined,
#         "described":described,
#         "login": Login(),
#         # "event":EventForm(),
#     })

# def contact_us(request):
#     if request.method=='POST':
#         form = ContactUs(request.POST)
#         if form.is_valid():
#             topic = (form.cleaned_data["topic"]).strip()
#             message = (form.cleaned_data["message"]).strip()
#             email = (form.cleaned_data["email"]).strip()

#             msg = Contact_Us(
#                 topic = topic,
#                 message = message,
#                 email = email,
#             )
#             msg.save()
#         else:
#             user = User.objects.filter(is_active = True)
#             profiles = Member.objects.filter(user__in = user)
#             projects = ProjectMade.objects.all()
#             return render(request,'Accounts/home-logout.html',{
#                 "ContactUs": ContactUs(request.POST),
#                 "login": Login(),
#                 "rate":Rate(),
#                 "profiles":profiles, 
#                 "projects":projects,
#             })
#     return HttpResponseRedirect(reverse("home_out"))

# # def event(request):
# #     if request.method=='POST':
# #         form = EventForm(request.POST)
# #         if form.is_valid():
# #             name = form.cleaned_data["name"]
# #             date = form.cleaned_data["date"]
# #             time = form.cleaned_data["time"]
# #             duration = form.cleaned_data["duration"]
# #             description = form.cleaned_data["description"]
# #             members = form.cleaned_data["members"]
            
# #             when = datetime.combine(date,time)

# #             event = Event(
# #                 name = name,
# #                 when = when,
# #                 duration = duration,
# #                 description = description,
# #             )
# #             event.save()
# #             event.members.set(members)
# #         else:
# #             user = User.objects.filter(is_active = True)
# #             profiles = Member.objects.filter(user__in = user)
# #             projects = ProjectMade.objects.all()
# #             return render(request, "Accounts/home-login.html", {
# #                 "profiles":profiles, 
# #                 "projects":projects,
# #                 "event":EventForm(request.POST),
# #             })
# #     return HttpResponseRedirect(reverse("home_in"))

# def user(request):
#     if request.method=='POST':
#         image = request.FILES.get("image",False)
#         user_id = request.POST.get("user_id",False)
#         if not image:
#             username = (request.POST["username"].strip())
#             email = (request.POST["email"].strip())
#             password = (request.POST["password"])
#             old_password = request.POST.get("old_password",False)

#         if user_id:
#             user_id = int((user_id))
#             the_user = User.objects.get(id=user_id)
#             member = Member.objects.get(user = the_user)
#             if image:
#                 member.image = image
#                 member.save()
#                 return redirect("profile",member.id)
#             else:
#                 if the_user.check_password(old_password) and (not User.objects.filter(username = username).exists() or the_user.username == username):
#                     the_user.username = username
#                     the_user.email = email
#                     the_user.set_password(password)
#                     the_user.save()
#                     user = authenticate(request, username=username, password=password)
#                     if user is not None:
#                         login(request, user)
#                     return redirect("profile",member.id)
#                 else:
#                     request.session["message"] = "Either wrong password or the Username used already exists, please check your credentials"
#                     return redirect("profile",member.id)
#         else:
#             username = (request.POST["username"].strip())
#             email = (request.POST["email"].strip())
#             password = (request.POST["password"])
#             if User.objects.filter(username = username).exists():
#                 user = User.objects.get(username = username)
#                 user.is_active = True
#                 user.save()
#             else:
#                 the_user = User(
#                     username = username,
#                     email = email,
#                 )
#                 the_user.set_password(password)
#                 the_user.save()

#                 member = Member(
#                     user = the_user,
#                     image = image,
#                 )
#                 member.save()

#     return redirect("home_in")

# def remove_user(request, profile_id):
#     user = User.objects.get(id=profile_id)
#     user.is_active = False
#     user.save()
    
#     return redirect("home_in")

# def definition(request, profile_id):
#     define = (request.POST["define"]).strip()
#     defining_user = User.objects.get(id=int(request.POST['user_id']))
#     defining_member = Member.objects.get(user = defining_user)
#     if Definition.objects.filter(defining_member = defining_member).exists():
#         definition = Definition.objects.get(defining_member = defining_member)
#         definition.definition = define
#         definition.save()
#     else:
#         definition = Definition(
#             defined_member = Member.objects.get(id = profile_id),
#             defining_member = defining_member,
#             definition = define
#         )
#         definition.save()
    
#     return redirect("profile",profile_id)

# def edit_definition(request, profile_id):
#     profile = Member.objects.get(id=profile_id)
#     defining_user = User.objects.get(id=int(request.GET['user_id']))
#     defining_member = Member.objects.get(user = defining_user)
#     definition = Definition.objects.get(defining_member = defining_member)
#     base_url = reverse("profile", kwargs={'member': profile_id})
#     query_String = urlencode({"defined": definition.definition,
#                             })
#     url = '{}?{}'.format(base_url, query_String)
#     return redirect(url)

# def remove_definition(request, profile_id):
#     defining_user = User.objects.get(id=int(request.GET['user_id']))
#     defining_member = Member.objects.get(user = defining_user)
#     Definition.objects.get(defining_member = defining_member).delete()

#     return redirect("profile",profile_id)

# def description(request, profile_id):
#     describe = (request.POST["describe"]).strip()
#     describing_user = User.objects.get(id=int(request.POST['user_id']))
#     describing_member = Member.objects.get(user = describing_user)
#     if Description.objects.filter(describing_member = describing_member).exists():
#         description = Description.objects.get(describing_member = describing_member)
#         description.description = describe
#         description.save()
#     else:
#         description = Description(
#             described_member = Member.objects.get(id = profile_id),
#             describing_member = describing_member,
#             description = describe
#         )
#         description.save()
    
#     return redirect("profile",profile_id)
    
# def edit_description(request, profile_id):
#     profile = Member.objects.get(id=profile_id)
#     describing_user = User.objects.get(id=int(request.GET['user_id']))
#     describing_member = Member.objects.get(user = describing_user)
#     description = Description.objects.get(describing_member = describing_member)
    
#     base_url = reverse("profile", kwargs={'member': profile_id})
#     query_String = urlencode({"described": description.description,
#                             })
#     url = '{}?{}'.format(base_url, query_String)
#     return redirect(url)

# def remove_description(request, profile_id):
#     describing_user = User.objects.get(id=int(request.GET['user_id']))
#     describing_member = Member.objects.get(user = describing_user)
#     Description.objects.get(describing_member = describing_member).delete()

#     return redirect("profile",profile_id)


# #@login_required(login_url='home_out')
# def idea(request):
#     return render(request,'ideas/idea.html',{
#                 # "event":EventForm(),
#                 "search":SearchForm(),
#                 "ideas":Idea.objects.all(),
#             })

# def add_idea(request):
#     if request.method=='POST':
#         idea_id = request.POST.get("idea_id",False)
#         name = (request.POST["idea_name"]).strip()
#         descriptive_name = (request.POST["idea_descriptive_name"]).strip()
#         description = (request.POST["idea_description"]).strip()

#         if idea_id:
#             idea_id = int((idea_id))
#             new_idea = Idea.objects.get(id = idea_id)
#             new_idea.name = name
#             new_idea.descriptive_name = descriptive_name
#             new_idea.description = description
#             new_idea.save()
#         else:
#             idealist = Member.objects.get(user=request.user)
#             new_idea = Idea(
#                 name = name,
#                 descriptive_name = descriptive_name,
#                 description = description,
#                 idealist = idealist, 
#             )
#             new_idea.save()
#     return redirect("idea")

# def delete_idea(request, idea_id):
#     Idea.objects.get(id= idea_id).delete()

#     return redirect("idea")

# def edit_idea(request,idea_id):
#     idea = Idea.objects.get(id= idea_id)
#     return render(request,'ideas/idea.html',{
#                 # "event":EventForm(),
#                 "search":SearchForm(),
#                 "ideas":Idea.objects.all(),
#                 "idea":idea,
#             })

# def search(request):
#     if request.method== "GET":
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             search = (form.cleaned_data["search"]).strip()
#             sort = (form.cleaned_data["sort"]).strip()
#             ideas = []
#             users = User.objects.filter(username__icontains=search)
#             for user in users:
#                 member = Member.objects.get(user=user)
#                 idea = Idea.objects.filter(idealist=member)
#                 ideas = list(chain(ideas,idea))
                
#             idea = Idea.objects.filter(Q(name__icontains=search)|Q(descriptive_name__icontains=search)|Q(description__icontains=search))
#             ideas = list(chain(ideas,idea))
#             ideas = list(set(ideas))
#             if sort == "date":
#                 ideas = sorted(ideas,key=lambda instance: instance.date)
#             elif sort == "date_asc":
#                 ideas = sorted(ideas,key=lambda instance: instance.date,reverse=True)
#             elif sort =="descriptive_name":
#                 ideas = sorted(ideas,key=lambda instance: instance.descriptive_name)
#             elif sort =="descriptive_name_asc":
#                 ideas = sorted(ideas,key=lambda instance: instance.descriptive_name,reverse=True) 
            
#             elif sort =="progress":
#                 ideas = sorted(ideas,key=lambda instance: instance.progress(),reverse=True)
#             elif sort =="progress_asc":
#                 ideas = sorted(ideas,key=lambda instance: instance.progress())
#             elif sort =="ratings":
#                 ideas = sorted(ideas,key=lambda instance: instance.avg_ratings,reverse=True)
#             elif sort =="ratings_asc":
#                 ideas = sorted(ideas,key=lambda instance: instance.avg_ratings)    
#             return render(request,"ideas/idea.html",{
#                 # "event":EventForm(),
#                 "search":SearchForm(request.GET),
#                 "ideas":ideas,
#             })
#         else:
#             return HttpResponseRedirect(reverse("idea"))

# def rate(request,idea_id):
#     if request.method=='POST':
#         form = RateForm(request.POST)
#         if form.is_valid():
#             ratings = int((form.cleaned_data["ratings"]))
#             review = (form.cleaned_data["review"]).strip()

#             member = Member.objects.get(user=request.user)
#             idea = Idea.objects.get(id=idea_id)

#             if IdeaRatings.objects.filter(Q(member=member) & Q(idea = idea)).count() >= 1:
#                 idea_rate = IdeaRatings.objects.get(Q(member=member) & Q(idea = idea))
#                 idea.avg_ratings = ((idea.avg_ratings * idea.num_ratings) - idea_rate.ratings + ratings)/(idea.num_ratings)
#                 idea.save()

#                 idea_rate.ratings = ratings
#                 idea_rate.review = review
#                 idea_rate.save()
#             else:
#                 idea.avg_ratings = ((idea.avg_ratings * idea.num_ratings)+ ratings)/(idea.num_ratings + 1)
#                 idea.num_ratings = idea.num_ratings + 1
#                 idea.save()


#                 idea_rating = IdeaRatings(
#                     ratings = ratings,
#                     review = review,
#                     member = member,
#                     idea = idea, 
#                 )
#                 idea_rating.save()
#         else:
#             return render(request, "ideas/idea_details.html", {
#                 "idea":Idea.objects.get(id=idea_id),
#                 "rate":RateForm(request.POST),
#             })
#     return redirect("idea_details",idea_id)

# def idea_details(request,idea_id):
#     tasks = [
#         {
#             "name":"Requirements Eliciting",
#             "description":"This involves reading and understanding the goals of the project. Then clearly extracting unambigous atomic requirements one by one. These requirements clearly state out what is expected of the system as well as the users. they also talk about the different users of the project and what each will be using the project for. The template of a requirement is: {[when] [under what conditions] [who] [shall/will/should] [process] [thing to be processed] [process details]}  An example of a requirement is: {when the user visits the campiagn podium for the first time, The system shall trigger a prompt asking them to enter their google credetials, the google credentials shall include their gmail and password}. the keywords shall, will and should are each used for a specific purpose. Shall-if the requirement must be fulfilled instantly. Should-if the requirement is optional. will-if the requirement must be fulfilled but not neccesarily in the first release. For more information, please visit the internet to come up with the best possible Requirements for this project",
#             "stage":"Requirements Engineering",
#         },
#         {
#             "name":"Data Flow Diagrams",
#             "description":"The DFD clearly illustrates how the data will flow within the project. This diagram has different levels. The levels depend on how complex the project is. The deepest level should always demonstrate all the processes clearly exploded in the project and the data flow lines between them. For more information, please visit the internet to come up with the best possible Data flow Diagrams for this project",
#             "stage":"Systems Analysis and Design",
#         },
#         {
#             "name":"Entity Relationship Diagram",
#             "description":"The ERD illustrates how the data that flows to the database is stored. This ERD should also include the models clearly extracted from it at the end. Clearly draw the ERD showing all the available Entities together with their properties and the relationships between them clear marked. one to one relationships, many to many etc. Then Models should clearly be extracted therefrom that are well normalised. For more information, please visit the internet to come up with the best possible ERD and Models for this project",
#             "stage":"Systems Analysis and Design",
#         },
#         {
#             "name":"User Experience Design",
#             "description":"The UX is the design that clearly shows how the interface of the project should be organised. It is a wireframe clearly demostrating what goes where, what each page should contain and where exactly are the components placed within the page. The focus here is on what is needed and where should it go so as to make the interface as intuitive and user friendly as possible. All the needed interface components are identified from here so as to give the user the best experience while using the application. Scenarios like {where can I delete my post from} are all answered here. For more information, please visit the internet to come up with the best possible UX Design for this project",
#             "stage":"UI/UX Design",
#         },
#         {
#             "name":"User Interface Design",
#             "description":"The UI is the design that beautifies the interfaces and make them so much attractive to look at and later alone use. Its to deal with the aesthetics of the components that are visible to the users as they use the app. how they are shown to the users for interface transitions e.t.c. as long as the interfaces are pleasing to look at, then you have clearly done the job. For more information, please visit the internet to come up with the best possible UI design for this project",
#             "stage":"UI/UX Design",
#         },
#         {
#             "name":"Algorithms",
#             "description":"The Algorithms deals with the way the project will go about processing of the data input into it. This ensures that efficient algorithms are being used to carry out the processing plus using the most effective data structures within those algorithms so that the program can run as effiecient as possible giving the users the best performance. Refractoring of the algorithms to make them even better is highly recommended. Speed, minimizing resource usage like memory and storage are some of the aims of writing efficient algorithms. For more information, please visit the internet to come up with the best possible Algorithms and Data structures for this project",
#             "stage":"Data Structures and Algorithms",
#         },
#         {
#             "name":"Front End Development",
#             "description":"Front End development is the actualization of the UI/UX design. By use of front end technologies like Javascript and CSS, The User Interface is built and put into place. The main focus here is to know the technologies to build truly wonderful and good looking interfaces that the users will interact with while using the application. For more information, please visit the internet to come up with the best possible Front End Code for this project",
#             "stage":"Computer Programming and Coding",
#         },
#         {
#             "name":"Back End Development",
#             "description":"Back end Development is writing code to ensure that the programs capture the input data, process it to give the desirable output work as expected. This also includes building the databases that store the data. For more information, please visit the internet to come up with the best possible Back end code for this project",
#             "stage":"Computer Programming and Coding",
#         },
#         {
#             "name":"System Test",
#             "description":"system testing involves testing the application to check whether there are any glitches or bugs that can be found while using the program. It also involves testing whether the program meets all the needed requirements specified for it. is it user friendly? Any problem that is found in the application is reported in a very well crafted test report done after the whole testing process. this is what is reffered to as system testing that is done after the application is deemed finished to be developed. The task evaluations shall be acting as the unit tests for the application. For more information, please visit the internet to come up with the best possible System Test for this project",
#             "stage":"System Testing",
#         },
#     ]

#     idea = Idea.objects.get(id = idea_id)
#     if Tasks.objects.filter(idea = idea).exists():
#         version = Tasks.objects.filter(idea = idea).order_by("-version").first().version
#         update = Tasks.objects.filter(idea = idea).order_by("-update").first().update
#     else:
#         version = 1
#         update = 0
#     search = Tasks.objects.filter(idea = idea)
#     return render(request, "ideas/idea_details.html", {
#         "idea": idea,
#         "rate":RateForm(),
#         "tasks":tasks,
#         "selected_tasks":search,
#         "version":version,
#         "members": Member.objects.all(),
#         "update":update
#     })

# def supplement(request,idea_id):
#     if request.method=='POST':
#         supplement_id = request.POST.get("supplement_id",False)
#         name = (request.POST["sup_name"]).strip()
#         description = (request.POST["sup_description"]).strip()

#         if supplement_id:
#             supplement_id = int((supplement_id))
#             supplement = Supplements.objects.get(id= supplement_id)
#             supplement.name = name
#             supplement.description = description
#             supplement.save()
        
#         else:
#             supplement = Supplements(
#                 name = name,
#                 description = description,
#                 idea = Idea.objects.get(id=idea_id),
#                 member = Member.objects.get(user=request.user),
#             )
#             supplement.save()
#     return redirect("idea_details",idea_id)

# def edit_supplement(request, idea_id):
#     idea = Idea.objects.get(id = idea_id)
#     supplement_id = int((request.GET["supplement_id"]))
#     supplement = Supplements.objects.get(id= supplement_id)
#     if Tasks.objects.filter(idea = idea).exists():
#         version = Tasks.objects.filter(idea = idea).order_by("-version").first().version
#         update = Tasks.objects.filter(idea = idea).order_by("-update").first().update
#     else:
#         version = 1
#         update = 0
#     return render(request, "ideas/idea_details.html", {
#         "idea":idea,
#         "supplement":supplement,
#         "rate":RateForm(),
#         "version":version,
#         "update":update,
#     })

# def delete_supplement(request, idea_id):
#     supplement_id = int((request.POST["supplement_id"]))
#     Supplements.objects.get(id= supplement_id).delete()

#     return redirect("idea_details",idea_id)

# def task(request,idea_id):
#     request.session["milestone"] = ""
#     if request.method=='POST':
#         task = request.POST["the_task"]
#         task = task.replace("'","\"")
#         task = json.loads(task)

#         if Tasks.objects.filter(Q(name = task["name"]) &
#             Q(stage = task['stage']) &
#             Q(idea = Idea.objects.get(id=idea_id))).exists():
#             request.session["task_exists"] = f"{task['name']} already exists, you may update it instead"                
#             return redirect("idea_details",idea_id)

#         else:
#             duration = int((request.POST["duration"]))
#             time = (request.POST["time"]).strip()
#             version = int((request.POST["version"]))

#             member = Member.objects.get(user = request.user)
#             member.tasks_being_done += 1
#             member.save()

#             if time == "days":
#                 deadline = datetime.now(timezone.utc) + timedelta(days=duration)
#             elif time == "hours":
#                 deadline = datetime.now(timezone.utc) + timedelta(hours=duration)
#             else:
#                 deadline = datetime.now(timezone.utc) + timedelta(minutes=duration)

#             the_task = Tasks(
#                 name = task['name'],

#                 member = member,
#                 deadline = deadline,
#                 start_date = datetime.now(timezone.utc),
#                 status = "Being Done",
                
#                 description = task['description'],
#                 stage = task['stage'],
#                 update = 0,
#                 version = version,
#                 idea = Idea.objects.get(id=idea_id)
#             )
#             the_task.save()
#             request.session["task_exists"] = ""
#     return redirect("task_details",the_task.id)

# def delete_task(request, idea_id):
#     task_id = int((request.POST["task_id"]))
#     task = Tasks.objects.get(id= task_id)
#     if Tasks.objects.filter(Q(update__gt = task.update) & Q(name = task.name)).exists():
#         if task.update == 0:
#             request.session["task_exists"] = f"Can't delete {task.name} without first deleting its Update {task.update +1}"
#         else:
#             request.session["task_exists"] = f"Can't delete Update {task.update} of {task.name} without first deleting its Update {task.update +1}"
#     else:
#         member = Member.objects.get(user = request.user)
#         if task.status == "Being Done":
#             member.tasks_being_done -= 1
#         elif task.status == "Done":
#             member.tasks_done -= 1
            
#         member.tasks_givenup += 1
#         member.save()
#         task.delete()
#         request.session["task_exists"] = ""

#     return redirect("idea_details",idea_id)

# def update_task(request,idea_id):
#     task_id = int((request.POST["task_id"]))
#     task = Tasks.objects.get(id= task_id)
    
#     if Tasks.objects.filter(name = task.name,
#             description = task.description,
#             stage = task.stage,
#             update = task.update + 1,
#             idea = Idea.objects.get(id=idea_id)).exists():
#             request.session["task_exists"] = f"{task.name} was already upgraded to update {task.update +1}, Maybe try upgrading its update {task.update +1} instead"

#             return redirect("idea_details",idea_id)

#     else:

#         duration = int((request.POST["duration"]))
#         time = (request.POST["time"]).strip()

#         member = Member.objects.get(user = request.user)
#         member.tasks_being_done += 1
#         member.save()

#         if time == "days":
#             deadline = datetime.now(timezone.utc) + timedelta(days=duration)
#         elif time == "hours":
#             deadline = datetime.now(timezone.utc) + timedelta(hours=duration)
#         else:
#             deadline = datetime.now(timezone.utc) + timedelta(minutes=duration)

#         the_task = Tasks(
#             name = task.name,

#             member = member,
#             deadline = deadline,
#             start_date = datetime.now(timezone.utc),
#             status = "Being Done",
            
#             description = task.description,
#             stage = task.stage,
#             update = task.update + 1,
#             idea = Idea.objects.get(id=idea_id)
#         )
#         the_task.save()
#         request.session["task_exists"] = ""

#         return redirect("task_details",the_task.id)

# def get_tasks(request,idea_id):
#     idea = Idea.objects.get(id = idea_id)
#     if request.method== "GET":
#         task = (request.GET["the_task"]).strip()
#         if task == "all":
#             task = ["Requirements Eliciting","Data Flow Diagrams","Entity Relationship Diagram","User Experience Design","User Interface Design","Algorithms","Front End Development","Back End Development","System Test"]
#         else:
#             task = [task]

#         version = (request.GET["version"])
#         if version == "all":
#             if Tasks.objects.filter(idea = idea).exists():
#                 version = list(range(1,Tasks.objects.filter(idea = idea).order_by("-version").first().version+1))
#             else:
#                 version = [1]
#         else:
#             version = [version]

#         update = (request.GET["update"])
#         if update == "all":
#             if Tasks.objects.filter(idea = idea).exists():
#                 update = list(range(Tasks.objects.filter(idea = idea).order_by("-update").first().update+1))
#             else:
#                 update = [0]
#         else:
#             update = [update]

#         member_id = (request.GET["member"])
#         if member_id == "all":
#             member = Member.objects.all()
#         else:
#             member = [Member.objects.get(id = int(member_id))]

#         status = (request.GET["status"]).strip()
#         if status == "all":
#             status = ["Given Up","Being Done","Done"]
#         else:
#             status = [status]
        
#         sort = (request.GET["sort"]).strip()


#         if sort == "progress_desc":
#             search = Tasks.objects.filter(Q(name__in = task)  
#                         & Q(version__in = version) 
#                         & Q(update__in = update)
#                         & Q(member__in = member)
#                         & Q(status__in = status)
#                         & Q(idea = idea)
#                         ).order_by("-progress")

#         elif sort == "progress_asc":
#             search = Tasks.objects.filter(Q(name__in = task) & 
#                         Q(version__in = version) &
#                         Q(update__in = update) &
#                         Q(member__in = member) &
#                         Q(status__in = status) &
#                         Q(idea = idea)
#                     ).order_by("progress")
#         elif sort == "time_left_desc":
#             search = Tasks.objects.filter(Q(name__in = task) & 
#                         Q(version__in = version) &
#                         Q(update__in = update) &
#                         Q(member__in = member) &
#                         Q(status__in = status) &
#                         Q(idea = idea)
#                     ).order_by("-deadline")
#         elif sort == "time_left_asc":
#             search = Tasks.objects.filter(Q(name__in = task) & 
#                         Q(version__in = version) &
#                         Q(update__in = update) &
#                         Q(member__in = member) &
#                         Q(status__in = status) &
#                         Q(idea = idea)
#                     ).order_by("deadline")

#     tasks = [
#         {
#             "name":"Requirements Eliciting",
#             "description":"This involves reading and understanding the goals of the project. Then clearly extracting unambigous atomic requirements one by one. These requirements clearly state out what is expected of the system as well as the users. they also talk about the different users of the project and what each will be using the project for. The template of a requirement is: {[when] [under what conditions] [who] [shall/will/should] [process] [thing to be processed] [process details]}  An example of a requirement is: {when the user visits the campiagn podium for the first time, The system shall trigger a prompt asking them to enter their google credetials, the google credentials shall include their gmail and password}. the keywords shall, will and should are each used for a specific purpose. Shall-if the requirement must be fulfilled instantly. Should-if the requirement is optional. will-if the requirement must be fulfilled but not neccesarily in the first release. For more information, please visit the internet to come up with the best possible Requirements for this project",
#             "stage":"Requirements Engineering",
#         },
#         {
#             "name":"Data Flow Diagrams",
#             "description":"The DFD clearly illustrates how the data will flow within the project. This diagram has different levels. The levels depend on how complex the project is. The deepest level should always demonstrate all the processes clearly exploded in the project and the data flow lines between them. For more information, please visit the internet to come up with the best possible Data flow Diagrams for this project",
#             "stage":"Systems Analysis and Design",
#         },
#         {
#             "name":"Entity Relationship Diagram",
#             "description":"The ERD illustrates how the data that flows to the database is stored. This ERD should also include the models clearly extracted from it at the end. Clearly draw the ERD showing all the available Entities together with their properties and the relationships between them clear marked. one to one relationships, many to many etc. Then Models should clearly be extracted therefrom that are well normalised. For more information, please visit the internet to come up with the best possible ERD and Models for this project",
#             "stage":"Systems Analysis and Design",
#         },
#         {
#             "name":"User Experience Design",
#             "description":"The UX is the design that clearly shows how the interface of the project should be organised. It is a wireframe clearly demostrating what goes where, what each page should contain and where exactly are the components placed within the page. The focus here is on what is needed and where should it go so as to make the interface as intuitive and user friendly as possible. All the needed interface components are identified from here so as to give the user the best experience while using the application. Scenarios like {where can I delete my post from} are all answered here. For more information, please visit the internet to come up with the best possible UX Design for this project",
#             "stage":"UI/UX Design",
#         },
#         {
#             "name":"User Interface Design",
#             "description":"The UI is the design that beautifies the interfaces and make them so much attractive to look at and later alone use. Its to deal with the aesthetics of the components that are visible to the users as they use the app. how they are shown to the users for interface transitions e.t.c. as long as the interfaces are pleasing to look at, then you have clearly done the job. For more information, please visit the internet to come up with the best possible UI design for this project",
#             "stage":"UI/UX Design",
#         },
#         {
#             "name":"Algorithms",
#             "description":"The Algorithms deals with the way the project will go about processing of the data input into it. This ensures that efficient algorithms are being used to carry out the processing plus using the most effective data structures within those algorithms so that the program can run as effiecient as possible giving the users the best performance. Refractoring of the algorithms to make them even better is highly recommended. Speed, minimizing resource usage like memory and storage are some of the aims of writing efficient algorithms. For more information, please visit the internet to come up with the best possible Algorithms and Data structures for this project",
#             "stage":"Data Structures and Algorithms",
#         },
#         {
#             "name":"Front End Development",
#             "description":"Front End development is the actualization of the UI/UX design. By use of front end technologies like Javascript and CSS, The User Interface is built and put into place. The main focus here is to know the technologies to build truly wonderful and good looking interfaces that the users will interact with while using the application. For more information, please visit the internet to come up with the best possible Front End Code for this project",
#             "stage":"Computer Programming and Coding",
#         },
#         {
#             "name":"Back End Development",
#             "description":"Back end Development is writing code to ensure that the programs capture the input data, process it to give the desirable output work as expected. This also includes building the databases that store the data. For more information, please visit the internet to come up with the best possible Back end code for this project",
#             "stage":"Computer Programming and Coding",
#         },
#         {
#             "name":"System Test",
#             "description":"system testing involves testing the application to check whether there are any glitches or bugs that can be found while using the program. It also involves testing whether the program meets all the needed requirements specified for it. is it user friendly? Any problem that is found in the application is reported in a very well crafted test report done after the whole testing process. this is what is reffered to as system testing that is done after the application is deemed finished to be developed. The task evaluations shall be acting as the unit tests for the application. For more information, please visit the internet to come up with the best possible System Test for this project",
#             "stage":"System Testing",
#         },
#     ]
    
#     if Tasks.objects.filter(idea = idea).exists():
#         version = Tasks.objects.filter(idea = idea).order_by("-version").first().version
#         update = Tasks.objects.filter(idea = idea).order_by("-update").first().update
#     else:
#         version = 1
#         update = 0
#     return render(request, "ideas/idea_details.html", {
#         "idea":idea,
#         "rate":RateForm(),
#         "tasks":tasks,
#         "selected_tasks":search,
#         "version":version,
#         "members": Member.objects.all(),
#         "update":update
#     })    


# def update_version(request,idea_id):
#     task_id = int((request.POST["task_id"]))
#     task = Tasks.objects.get(id= task_id)
#     version = int((request.POST["version"]))
#     task.version = version
#     task.save()

#     return redirect("idea_details",idea_id)


# def task_details(request,task_id):
#     task = Tasks.objects.get(id=task_id)
#     idea = task.idea
#     return render(request,"ideas/task_details.html", {
#         "task":task,
#         "idea":idea,
#         "status":ChangeStatus(),
#         "rate":RateForm(),
#         "member":Member.objects.all(),
#     })

# def edit_milestone(request,milestone_id):
#     task_id = int((request.GET["task"]))
#     task = Tasks.objects.get(id=task_id)
#     idea = task.idea
#     milestone = Milestone.objects.get(id=milestone_id)
#     return render(request,"ideas/task_details.html", {
#         "task":task,
#         "idea":idea,
#         "milestone":milestone,
#         "status":ChangeStatus(),
#         "rate":RateForm(),
#         "member":Member.objects.all(),
#     })

# def approve(request,task_id):
#     if request.method=='POST':
#         completion = (request.POST["completion"]).strip()
#         evaluation = int((request.POST["evaluation"]))
#         reasons = (request.POST["reasons"]).strip()

#         assessor = Member.objects.get(user=request.user)
#         task = Tasks.objects.get(id=task_id)
#         doer = Member.objects.get(user=task.member.user)
#         try:
#             approved = TaskApproval.objects.get(Q(member=assessor)&Q(task = task))

#             if completion == "Completed":
#                 if approved.completion == "Completed":
#                     task.avg_evaluation = ((task.avg_evaluation * task.num_evaluation)-approved.evaluation + evaluation)/(task.num_evaluation)
#                 else:
#                     task.avg_evaluation = ((task.avg_evaluation * task.num_evaluation) + evaluation)/(task.num_evaluation + 1)
#                     task.num_evaluation = task.num_evaluation + 1
#                     try:
#                         task.progress = ((task.progress * task.num_progress)- approved.evaluation)/(task.num_progress - 1)
#                     except ZeroDivisionError:
#                         task.progress = 0
#                     task.num_progress = task.num_progress - 1
#                     doer.tasks_approved += 0.25
#                     doer.tasks_unapproved -= 0.25
#                 task.save()
#             elif completion == "Incomplete":
#                 assessor.tasks_objections_made += 1
#                 assessor.save()
#                 if approved.completion == "Incomplete":
#                     task.progress = ((task.progress * task.num_progress)-approved.evaluation + evaluation)/(task.num_progress)
#                 else:
#                     task.progress = ((task.progress * task.num_progress) + evaluation)/(task.num_progress + 1)
#                     task.num_progress = task.num_progress + 1
#                     try:
#                         task.avg_evaluation = ((task.avg_evaluation * task.num_evaluation)- approved.evaluation)/(task.num_evaluation - 1)
#                     except ZeroDivisionError:
#                         task.avg_evaluation = 0
#                     task.num_evaluation = task.num_evaluation - 1
#                     doer.tasks_unapproved += 0.25
#                     doer.tasks_approved -= 0.25
#                 task.save()
#             doer.save()

#             approved.completion = completion
#             approved.evaluation = evaluation
#             approved.reasons = reasons
#             approved.save()
#         except ObjectDoesNotExist:
#             if completion == "Completed":
#                 task.avg_evaluation = ((task.avg_evaluation * task.num_evaluation)+ evaluation)/(task.num_evaluation + 1)
#                 task.num_evaluation = task.num_evaluation + 1
#                 task.save()
#                 doer.tasks_approved += 0.25
#             elif completion == "Incomplete":
#                 assessor.tasks_objections_made += 1
#                 assessor.save()
#                 task.progress = ((task.progress * task.num_progress)+ evaluation)/(task.num_progress + 1)
#                 task.num_progress = task.num_progress + 1
#                 task.save()
#                 doer.tasks_unapproved +=0.25
#             doer.save()

#             task_approval = TaskApproval(
#                 completion = completion,
#                 evaluation = evaluation,
#                 reasons = reasons,
#                 member = assessor,
#                 task = task, 
#             )
#             task_approval.save()
#     return redirect("task_details",task_id)

# #this function works on changing status of a task from done to being done to given up to not done
# def status(request, task_id):
#     request.session["milestone"] = ""
#     if request.method == "POST":
#         status = (request.POST["status"]).strip()
#         duration = request.POST.get("duration",False)
#         if duration != False:
#             duration = int((duration))
#         time = request.POST.get("time",False)
#         if time != False:
#             time = (time).strip()
#         the_task = Tasks.objects.get(id=task_id)

#         member = Member.objects.get(user=request.user)
#         if the_task.status != "Not Done":
#             previous_member = Member.objects.get(user=the_task.member.user)
#         if status == "Being Redone":
#             member.tasks_rectified += 1
#             member.save()
#             status = "Being Done"
        
#         if status == "Being Done":
#             member.tasks_being_done += 1
#             if the_task.status == "Done":
#                 member.tasks_done -= 1
#             member.save()

#             the_task.member = member
#             if time == "days":
#                 deadline = datetime.now(timezone.utc) + timedelta(days=duration)
#             elif time == "hours":
#                 deadline = datetime.now(timezone.utc) + timedelta(hours=duration)
#             else:
#                 deadline = datetime.now(timezone.utc) + timedelta(minutes=duration)
#             the_task.deadline = deadline
#             the_task.start_date = datetime.now(timezone.utc)
        
#         if status == "Done":
#             if the_task.milestones.filter().exists():
#                 if not the_task.milestones.exclude(status = "Done").exists():
#                     member.tasks_being_done -= 1
#                     member.tasks_done += 1

#                     member.tasks_duration += (datetime.now(timezone.utc) - the_task.start_date)

#                     if datetime.now(timezone.utc) <= the_task.deadline:
#                         member.deadlines_met += 1
#                     else:
#                         member.deadlines_missed += 1
#                         member.deadline_excess += (datetime.now(timezone.utc)-the_task.deadline)
#                     member.save()

#                 else:
#                     status = "Being Done"
#                     request.session["milestone"] = "You can't finish a task without finishing all the milestones, you could give up instead"
#             else:
#                 status = "Being Done"
#                 request.session["milestone"] = "You must have atleast one milestone, you could give up instead"
        
#         if status == "Given Up":
#             if datetime.now(timezone.utc) > the_task.deadline and the_task.status != "Done":
#                 member.deadline_excess += (datetime.now(timezone.utc)-the_task.deadline)

#             if the_task.status != "Done":
#                 member.tasks_duration += (datetime.now(timezone.utc) - the_task.start_date)

#             member.tasks_givenup += 1
#             if the_task.status == "Being Done":
#                 member.tasks_being_done -= 1
#             elif the_task.status == "Done":
#                 member.tasks_done -= 1
#             member.save()

#         the_task.status = status
#         the_task.save()

#     return redirect("task_details",task_id)

# def link(request,task_id):
#     the_link = (request.POST["link"]).strip()
#     the_task = Tasks.objects.get(id=task_id)
#     the_task.link = the_link
#     the_task.save()

#     return redirect("task_details",task_id)
    
# def idea_link(request,idea_id):
#     the_link = (request.POST["link"]).strip()

#     if not the_link.startswith("http") and not the_link.startswith("//"):
#         the_link = "//"+the_link
#     the_idea = Idea.objects.get(id=idea_id)
#     the_idea.link = the_link.strip(".git")
#     the_idea.save()

#     return redirect("idea_details",idea_id)

# def reference(request,task_id):
#     the_reference = request.POST.get("tasks",False)
#     if the_reference:
#         the_reference = int((the_reference).strip().split(".",1)[0])
#     else:
#         return redirect("task_details",task_id)
#     referring_task = Tasks.objects.get(id=task_id)
#     referred_task = Tasks.objects.get(id=the_reference)

#     if referring_task != referred_task:
#         if not Reference.objects.filter(referred_task = referred_task).exists():
#             refer = Reference(
#                         referred_task = referred_task,
#                         referring_task = referring_task, 
#                     )
#             refer.save()

#     return redirect("task_details",task_id)

# def remove_reference(request, reference_id):
#     task_id = int((request.POST["task"]))
#     reference = Reference.objects.get(id = reference_id)
#     reference.delete()

#     return redirect("task_details",task_id)

# def milestones(request,task_id):
#     milestone_id = (request.POST.get("milestone_id",False))
#     name = (request.POST["name"]).strip()
#     description = (request.POST["description"]).strip()
#     the_task = Tasks.objects.get(id=task_id)
#     num_milestones = Milestone.objects.filter(task = the_task).count()
#     num_done = Milestone.objects.filter(Q(task = the_task) & Q(status = "Done")).count()

#     if milestone_id:
#         milestone_id = int(milestone_id)
#         milestone = Milestone.objects.get(id=milestone_id)
#         milestone.name = name
#         milestone.description = description
#         milestone.save()
#     else:
#         if num_milestones == 0:
#             the_task.progress = (the_task.progress + ((num_done)/(num_milestones+1)*100))
#             the_task.num_progress = the_task.num_progress + 1
#         else:
#             #because the milestones are treated as one entity
#             the_task.progress = (the_task.progress - ((num_done)/(num_milestones)*100) + ((num_done)/(num_milestones+1)*100))
#         the_task.save()

#         milestone = Milestone(
#             name = name,
#             description = description,
#             task = the_task
#         )
#         milestone.save()

#     return redirect("task_details",task_id)

# def milestone_status(request, milestone_id):
#     task_id = int((request.POST["task"]))
#     new_status = (request.POST["status"]).strip()
#     milestone = Milestone.objects.get(id=milestone_id)
#     task = Tasks.objects.get(id=task_id)
#     num_milestones = Milestone.objects.filter(task = task).count()
#     num_done = Milestone.objects.filter(Q(task = task) & Q(status = "Done")).count()


#     if new_status == "Delete it":
#         if milestone.status == "Done":
#             if num_milestones - 1 == 0:
#                 task.progress = (task.progress- ((num_done)/(num_milestones)*100))
#             else:    
#                 task.progress = (task.progress- ((num_done)/(num_milestones)*100) + ((num_done-1)/(num_milestones-1)*100))
#         else:
#             if num_milestones - 1 != 0:
#                 task.progress = (task.progress- ((num_done)/(num_milestones)*100) + ((num_done)/(num_milestones-1)*100))
#         milestone.delete()
#         task.save()
#     else:
#         if new_status == "Done":
#             if milestone.status != "Done":
#                 task.progress = (task.progress- ((num_done)/(num_milestones)*100) + ((num_done+1)/(num_milestones)*100))
#         else:
#             if milestone.status == "Done":
#                 task.progress = (task.progress- ((num_done)/(num_milestones)*100) + ((num_done-1)/(num_milestones)*100))
        
#         milestone.status = new_status
#         milestone.save()
#         task.save()

#     return redirect("task_details",task_id)

# def learning(request,task_id):
#     resource_name = (request.POST["resource_name"]).strip()
#     resource_link = (request.POST["resource_link"]).strip()
#     if not resource_link.startswith("http") and not resource_link.startswith("//"):
#         resource_link = "//"+resource_link
#     resource_description = (request.POST["resource_description"]).strip()
#     resource_type = (request.POST["resource_type"]).strip()
#     whose = (request.POST["whose"]).strip()
#     resource_id = request.POST.get("resource_id",False)

#     if resource_id:
#         resource_id = int((resource_id))
#         resource = Learning.objects.get(id=resource_id)
#         resource.name = resource_name
#         resource.description = resource_description
#         resource.link = resource_link
#         resource.form = resource_type
#         resource.whose = whose
#         resource.save()
#     else:
#         task = Tasks.objects.get(id=task_id)
#         researcher = task.member
#         resource = Learning(
#             name = resource_name,
#             description = resource_description,
#             link = resource_link,
#             form = resource_type,
#             task = task,
#             whose = whose,
#             researcher = researcher,
#         )
#         resource.save()

#     return redirect("task_details",task_id)

# def edit_resource(request,resource_id):
#     task_id = int((request.GET["task_id"]))
#     task = Tasks.objects.get(id=task_id)
#     idea = task.idea
#     edit_resource = Learning.objects.get(id=resource_id)
#     return render(request,"ideas/task_details.html", {
#         "task":task,
#         "idea":idea,
#         "edit_resource":edit_resource,
#         "status":ChangeStatus(),
#         "rate":RateForm(),
#         "member":Member.objects.all(),
#     })

# def delete_resource(request,resource_id):
#     task_id = int((request.POST["task_id"]))
#     Learning.objects.get(id=resource_id).delete()

#     return redirect("task_details",task_id)

# def rate_resource(request,resource_id):
#     if request.method=='POST':
#         task_id = int((request.POST['task']))
#         form = RateForm(request.POST)
#         if form.is_valid():
#             ratings = int((form.cleaned_data["ratings"]))
#             review = (form.cleaned_data["review"]).strip()

#             member = Member.objects.get(user=request.user)
#             resource = Learning.objects.get(id=resource_id)

#             if LearningRatings.objects.filter(Q(member=member) & Q(resource = resource)).count() >= 1:
#                 learn_rate = LearningRatings.objects.get(Q(member=member) & Q(resource = resource))
#                 resource.avg_ratings = ((resource.avg_ratings * resource.num_ratings) - learn_rate.ratings + ratings)/(resource.num_ratings)                
#                 resource.save()

#                 learn_rate.ratings = ratings
#                 learn_rate.review = review
#                 learn_rate.save()
#             else:
#                 resource.avg_ratings = ((resource.avg_ratings * resource.num_ratings)+ ratings)/(resource.num_ratings + 1)
#                 resource.num_ratings = resource.num_ratings + 1
#                 resource.save()


#                 task_rating = LearningRatings(
#                     ratings = ratings,
#                     review = review,
#                     member = member,
#                     resource = resource, 
#                 )
#                 task_rating.save()
#         else:
#             return render(request,"ideas/task_details.html", {
#         "task":task,
#         "idea":idea,
#         "status":ChangeStatus(),
#         "rate":RateForm(request.POST)
#     })
#     return redirect("task_details",task_id)

# def search_resource(request,task_id):
#     keyword = (request.GET["keyword"]).strip()
#     stage = (request.GET["stage"]).strip()
#     sorting = (request.GET["sorting"]).strip()
#     form = (request.GET["form"]).strip()
#     researcher_id = (request.GET["researcher"])
#     if researcher_id != "all":
#         researcher_id = int(researcher_id)

#     if researcher_id == "all" and form == "all" and stage == "all":
#         resources = Learning.objects.filter(Q(name__icontains=keyword)|Q(description__icontains=keyword)|Q(link__icontains=keyword))
#     else:
#         resources_1 = set()
#         resources_2 = set()
#         resources_3 = set()
#         if researcher_id != "all":
#             researcher = Member.objects.get(id=researcher_id)
#             resources_1 = set(Learning.objects.filter((Q(name__icontains=keyword)|Q(description__icontains=keyword)|Q(link__icontains=keyword))&Q(researcher=researcher)))
#         if form != "all":
#             resources_2 = set(Learning.objects.filter((Q(name__icontains=keyword)|Q(description__icontains=keyword)|Q(link__icontains=keyword))&Q(form=form)))
#         if stage != "all":
#             tasks = Tasks.objects.filter(stage=stage)
#             for task in tasks:
#                 resource_3 = Learning.objects.filter((Q(name__icontains=keyword)|Q(description__icontains=keyword)|Q(link__icontains=keyword))&Q(task=task))
#                 resources_3 = list(chain(resources_3,resource_3))
#             resources_3 = set(resources_3)
        
#         if resources_1 != set() and resources_2 != set() and resources_3 != set():
#             resources = resources_1 & resources_2 & resources_3
#         elif resources_1 != set() and resources_2 != set():
#             resources = resources_1 & resources_2
#         elif resources_1 != set() and resources_3 != set():
#             resources = resources_1 & resources_3
#         elif resources_2 != set() and resources_3 != set():
#             resources = resources_2 & resources_3
#         else:
#             resources = resources_1 | resources_2 | resources_3


#     resources = list(resources)
#     if sorting == "date-asc":
#         resources = sorted(resources,key=lambda instance: instance.date)
#     elif sorting == "date-desc":
#         resources = sorted(resources,key=lambda instance: instance.date,reverse=True)
#     elif sorting =="rating-asc":
#         resources = sorted(resources,key=lambda instance: instance.avg_ratings)
#     elif sorting =="rating-desc":
#         resources = sorted(resources,key=lambda instance: instance.avg_ratings,reverse=True)
    
#     task = Tasks.objects.get(id=task_id)
#     idea = task.idea    
#     return render(request,"ideas/task_details.html", {
#         "task":task,
#         "idea":idea,
#         "status":ChangeStatus(),
#         "rate":RateForm(),
#         "member":Member.objects.all(),
#         "resources":resources,
#     })

# def publish(request, idea_id):
#     name = (request.POST["name"]).strip()
#     description = (request.POST["description"]).strip()
#     image = request.FILES["image"]
#     the_link = (request.POST["link"]).strip()
#     if not the_link.startswith("http") and not the_link.startswith("//"):
#         the_link = "//"+the_link

#     if ProjectMade.objects.filter(id=idea_id).count() >= 1:
#         project = ProjectMade.objects.get(id=idea_id)
#         project.name = name
#         project.description = description
#         project.image = image
#         project.link = the_link
#         project.save()
#     else:
#         idea = Idea.objects.get(id = idea_id)
#         project = ProjectMade(
#             idea = idea,
#             name = name,
#             description = description,
#             image = image,
#             link = the_link,
#         )
#         project.save()
    
#     return redirect("idea_details",idea_id)

# def supplement_status(request, idea_id):
#     supplement_id = int((request.POST["supplement_id"]))
#     status = (request.POST["status"]).strip()

#     supplement = Supplements.objects.get(id = supplement_id)
#     supplement.status = status
#     supplement.save()

#     return redirect("idea_details",idea_id)