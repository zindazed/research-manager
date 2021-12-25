from django.db.models.query_utils import Q
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from itertools import chain
from urllib.parse import urlencode

# Create your views here.

def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    topics = Topic.objects.filter(Q(researcher = request.user) & Q(parentFolder__isnull = True)).order_by("docType")
    return render(request,"research_app/home.html", {
        "topics":topics,
    })

def signUp(request):
    failMessage = ""
    if request.method=='POST':
        last_name = (request.POST["username"].strip())
        email = (request.POST["email"].strip())
        password = (request.POST["password"])
        cpassword = request.POST["cpassword"]
        
        username = email.split("@",1)[0]
        print(username)
        if password == cpassword:
            if User.objects.filter(email = email).exists():
                failMessage = "That Email has already been used!"
            else:
                the_user = User(
                    last_name = last_name,
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
            failMessage = "Passwords didn't Match"

    return render(request,"research_app/signup.html",{
        "failMessage":failMessage
    })

def logIn(request):
    failMessage = ""
    if request.method=='POST':
        email = (request.POST["email"].strip())
        password = (request.POST["password"])

        if User.objects.filter(email = email).exists():
            username = User.objects.get(email = email).username
            if User.objects.get(email = email).check_password(password):
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    
                    request.session["failMessage"] = ""
                    request.session["successMessage"] = "Logged in Successfully"
                    return redirect("home")
                else:
                    failMessage = "Something Went Wrong, Please try again"
            else:
                failMessage = "Wrong Password, please try again"

        else:
            failMessage = "Wrong Email, sign up instead if you have no account"
 
    return render(request,"research_app/login.html",{
        "failMessage":failMessage,
    })

def logOut(request):
    logout(request)
    return redirect("home")

def addTopic(request):
    if request.method=='POST':
        topicId = False
        folderId = (request.POST.get("folder",False))
        docType = (request.POST["type"].strip())
        name = (request.POST["name"].strip())
        description = (request.POST["description"].strip())
        
        folder = False
        if folderId:
            folder = Folder.objects.get(id = int(folderId))

        if folder:
            newTopic = Topic(
                name = name,
                description = description,
                parentFolder = folder,
                researcher = request.user,
                docType = docType,
            )
            topicId = folder.topic.id
        else:
            newTopic = Topic(
                name = name,
                description = description,
                researcher = request.user,
                docType = docType,
            )
        
        topic = Topic.objects.filter(Q(name = name) & Q(researcher = request.user))
        if docType == "Folder":
            if not Folder.objects.filter(topic__in = topic).exists():
                newTopic.save()
                newFolder = Folder(
                    topic = newTopic,
                )
                newFolder.save()
                request.session["successMessage"] = "Folder Created successfully"
                request.session["failMessage"] = ""

            else:
                request.session["failMessage"] = "You already created a folder with that same name, search for it to see it"
                request.session["successMessage"] = ""

        elif docType == "Research Work":
            if not ResearchWork.objects.filter(topic__in = topic).exists():
                newTopic.save()
                newResearchWork = ResearchWork(
                    topic = newTopic,
                )
                newResearchWork.save()
                request.session["successMessage"] = "Research Work Created successfully"
                request.session["failMessage"] = ""

            else:
                request.session["failMessage"] = "You already created a Research Work with that same name, search for it to see it"
                request.session["successMessage"] = ""

        elif docType == "Merged Summary":
            if not MergedSummary.objects.filter(topic__in = topic).exists():
                newTopic.save()
                newMergedSummary = MergedSummary(
                    topic = newTopic,
                )
                newMergedSummary.save()
                request.session["successMessage"] = "Merged Summary Created successfully"
                request.session["failMessage"] = ""

            else:
                request.session["failMessage"] = "You already created a Merged Summary with that same name, search for it to see it"
                request.session["successMessage"] = ""
        
        if topicId:
            return redirect("folder",topicId)
        else:
            return redirect("home")

def editTopic(request):
    folderTopicId = False
    if request.method=='POST':
        folderTopicId = request.POST.get("folderTopicId",False)
        topicId = int(request.POST["id"].strip())
        name = (request.POST["name"].strip())
        description = (request.POST["description"].strip())

        topic = Topic.objects.get(id = topicId)
        topic.name = name
        topic.description = description
        topic.save()

        request.session["successMessage"] = "Editted successfully"
        request.session["failMessage"] = ""

        request.session["editId"] = ""
        request.session["editType"] = ""
        
    elif request.method=='GET':
        folderTopicId = request.GET.get("folderTopicId",False)
        topicId = int(request.GET["id"])

        topic = Topic.objects.get(id = topicId)
        request.session["name"] = topic.name
        request.session["description"] = topic.description

        request.session["editId"] = topicId
    if folderTopicId:
        return redirect("folder",folderTopicId)
    else:
        return redirect("home")

def deleteTopic(request):
    folderTopicId = False
    if request.method=='GET':
        topicId = int(request.GET["id"])
        folderTopicId = request.GET.get("folderTopicId",False)

        topic = Topic.objects.get(id = topicId)
        topic.delete()
        request.session["successMessage"] = f"{topic.name} {topic.docType} deleted successfully".capitalize()
        request.session["failMessage"] = ""

        if folderTopicId:
            return redirect("folder",folderTopicId)
        else:
            return redirect("home")

def search(request,topicId):
    if request.method=='GET':
        results = list()
        search = request.GET["search"]
        filter = request.GET.getlist("filter")
        docTypes = request.GET.getlist("docType")

        nameResults = list()
        descriptionResults = list()
        workResults = list()

        if docTypes:
            if "name" in filter:
                nameResults = Topic.objects.filter(Q(name__icontains = search) & Q(researcher = request.user) & Q(docType__in = docTypes))
                nameResults = list(nameResults)

            if "description" in filter:
                descriptionResults = Topic.objects.filter(Q(description__icontains = search) & Q(researcher = request.user) & Q(docType__in = docTypes))
                descriptionResults = list(descriptionResults)

            if "work" in filter:
                researchWorkResults = []
                if "Research Work" in docTypes:
                        researchWorkResults = ResearchWork.objects.filter(work__icontains = search)

                MergedSummaryResults = []
                if "Merged Summary" in docTypes:
                        MergedSummaryResults = MergedSummary.objects.filter(work__icontains = search)
                
                for researchWorkResult in researchWorkResults:
                    if researchWorkResult.topic.researcher == request.user:
                        workResults.append(researchWorkResult.topic)
                
                for MergedSummaryResult in MergedSummaryResults:
                    if MergedSummaryResult.topic.researcher == request.user:
                        workResults.append(MergedSummaryResult.topic)
                
                workResults = list(workResults)

        results = chain(nameResults,descriptionResults,workResults)
        results = list(set(results))

        if results:
            request.session["successMessage"] = f"{len(results)} Topics found and successfully returned"
            request.session["failMessage"] = ""
        else:
            request.session["successMessage"] = ""
            request.session["failMessage"] = "0 Topics found, No topic matched the specified search criteria"
            
        topic = Topic.objects.get(id=topicId)
        the_topic = topic
        folder = Folder.objects.get(topic = topic)
        path = []
        path.append(topic)
        while True:
            if topic.parentFolder:
                path.append(topic.parentFolder.topic)
                topic = topic.parentFolder.topic
            else:
                break
        path.reverse()
        topics = Topic.objects.filter(Q(researcher = request.user) & Q(parentFolder = folder)).order_by("docType")
        return render(request,"research_app/folder.html",{
            "folder":folder,
            "folderTopic":the_topic,
            "path":path,
            "topics":topics,
            "searchResults":results,
        })

def searchHome(request):
    if request.method=='GET':
        results = list()
        search = request.GET["search"]
        filter = request.GET.getlist("filter")
        docTypes = request.GET.getlist("docType")

        nameResults = list()
        descriptionResults = list()
        workResults = list()

        if docTypes:
            if "name" in filter:
                nameResults = Topic.objects.filter(Q(name__icontains = search) & Q(researcher = request.user) & Q(docType__in = docTypes))
                nameResults = list(nameResults)

            if "description" in filter:
                descriptionResults = Topic.objects.filter(Q(description__icontains = search) & Q(researcher = request.user) & Q(docType__in = docTypes))
                descriptionResults = list(descriptionResults)

            if "work" in filter:
                researchWorkResults = []
                if "Research Work" in docTypes:
                        researchWorkResults = ResearchWork.objects.filter(work__icontains = search)

                MergedSummaryResults = []
                if "Merged Summary" in docTypes:
                        MergedSummaryResults = MergedSummary.objects.filter(work__icontains = search)
                
                for researchWorkResult in researchWorkResults:
                    if researchWorkResult.topic.researcher == request.user:
                        workResults.append(researchWorkResult.topic)
                
                for MergedSummaryResult in MergedSummaryResults:
                    if MergedSummaryResult.topic.researcher == request.user:
                        workResults.append(MergedSummaryResult.topic)
                
                workResults = list(workResults)

        results = chain(nameResults,descriptionResults,workResults)
        results = list(set(results))

        if results:
            request.session["successMessage"] = f"{len(results)} Topics found and successfully returned"
            request.session["failMessage"] = ""
        else:
            request.session["successMessage"] = ""
            request.session["failMessage"] = "0 Topics found, No topic matched the specified search criteria"


        topics = Topic.objects.filter(Q(researcher = request.user) & Q(parentFolder__isnull = True)).order_by("docType")
        return render(request,"research_app/home.html",{
            "searchResults":results,
            "topics":topics
        })


def folder(request,topicId):
    topic = Topic.objects.get(id=topicId)
    the_topic = topic
    folder = Folder.objects.get(topic = topic)
    path = []
    path.append(topic)
    while True:
        if topic.parentFolder:
            path.append(topic.parentFolder.topic)
            topic = topic.parentFolder.topic
        else:
            break
    path.reverse()
    topics = Topic.objects.filter(Q(researcher = request.user) & Q(parentFolder = folder)).order_by("docType")
    return render(request,"research_app/folder.html",{
        "folder":folder,
        "folderTopic":the_topic,
        "path":path,
        "topics":topics,
    })

def researchWork(request,topicId):
    topic = Topic.objects.get(id=topicId)
    the_topic = topic
    researchWork = ResearchWork.objects.get(topic = topic)
    path = []
    path.append(topic)
    while True:
        if topic.parentFolder:
            path.append(topic.parentFolder.topic)
            topic = topic.parentFolder.topic
        else:
            break
    path.reverse()

    links = Link.objects.filter(researchWork = researchWork)

    try:
        originalResearchSummary = researchWork.researchSummary
        summaries = ResearchSummaryDuplicate.objects.filter(originalResearchSummary = originalResearchSummary)
    except ObjectDoesNotExist:
        summaries = []
    researches = ResearchWorkDuplicate.objects.filter(originalResearchWork = researchWork)
    return render(request,"research_app/researchWork.html",{
        "researchWork":researchWork,
        "researchWorkTopic":the_topic,
        "path":path,
        "links":links,
        "summaries":summaries,
        "researches":researches,
    })

def editResearch(request,topicId):
    if request.method=='POST':
        work = request.POST["researchWork"].strip()
        summary = request.POST["researchSummary"].strip()
        duplicateId = request.POST.get("duplicateId",False) 
        researchWorkDuplicateId = request.POST.get("researchWorkDuplicateId",False)
        
        researchTopic = Topic.objects.get(id = topicId)
        researchWork = ResearchWork.objects.get(topic = researchTopic)

        if researchWorkDuplicateId:
            researchWorkDuplicate = ResearchWorkDuplicate.objects.get(id = researchWorkDuplicateId)
            words = work.split(";;")
            for i,word in enumerate(words):
                if word.startswith(";"):
                    link = word[word.index("::")+2:]
                    name = word[1:word.index("::")]
                    words[i] = "link:"+name
                    if not link.startswith("http") and not link.startswith("//"):
                        link = "//"+link
                    if not Link.objects.filter(Q(name = name) & Q(url = link) & Q(researchWorkDuplicate = researchWorkDuplicate)).exists():
                        the_link = Link(
                            name = name,
                            url = link,
                            researchWorkDuplicate = researchWorkDuplicate,
                        )
                        the_link.save()

            work = "".join(words)

            links = Link.objects.filter(researchWorkDuplicate = researchWorkDuplicate)
            for link in links:
                if not "link:"+link.name in work:
                    link.delete()

            researchWorkDuplicate.work = work
            researchWorkDuplicate.save()
        else:
            words = work.split(";;")
            for i,word in enumerate(words):
                if word.startswith(";"):
                    link = word[word.index("::")+2:]
                    name = word[1:word.index("::")]
                    words[i] = "link:"+name
                    if not link.startswith("http") and not link.startswith("//"):
                        link = "//"+link
                    if not Link.objects.filter(Q(name = name) & Q(url = link) & Q(researchWork = researchWork)).exists():
                        the_link = Link(
                            name = name,
                            url = link,
                            researchWork = researchWork,
                        )
                        the_link.save()

            work = "".join(words)

            links = Link.objects.filter(researchWork = researchWork)
            for link in links:
                if not "link:"+link.name in work:
                    link.delete()

            researchWork.work = work
            researchWork.save()

        if duplicateId:
            reason = request.POST.get("reason",False)
            researchSummary = ResearchSummary.objects.get(researchWork = researchWork)
            if(ResearchSummaryDuplicate.objects.filter(Q(originalResearchSummary = researchSummary) & Q(reason = reason)).exists()):
                researchSummaryDuplicate = ResearchSummaryDuplicate.objects.get(Q(originalResearchSummary = researchSummary) & Q(reason = reason))
                researchSummaryDuplicate.work = summary
                researchSummaryDuplicate.save()
            else:
                researchSummaryDuplicate = ResearchSummaryDuplicate(
                    work = summary,
                    originalResearchSummary = researchSummary,
                )
                researchSummaryDuplicate.save()
            request.session["successMessage"] = "Saved the work successfully"
            request.session["failMessage"] = ""
        else:
            if(ResearchSummary.objects.filter(researchWork = researchWork).exists()):
                researchSummary = ResearchSummary.objects.get(researchWork = researchWork)
                researchSummary.work = summary
                researchSummary.save()
            else:
                researchSummary = ResearchSummary(
                    work = summary,
                    researchWork = researchWork,
                )
                researchSummary.save()
            request.session["successMessage"] = "Saved Work successfully"
            request.session["failMessage"] = ""

        if researchWorkDuplicateId:
            if duplicateId:
                base_url = reverse("researchWorkDuplicate", kwargs={'duplicateId': researchWorkDuplicateId})
                query_String = urlencode({"summaryDuplicateId": duplicateId,
                                        })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                return redirect("researchWorkDuplicate",researchWorkDuplicateId)
        else:
            if duplicateId:
                return redirect("researchSummaryDuplicate",duplicateId)
            else:
                return redirect("researchWork",topicId)

def editWork(request,mergedSummaryTopicId):
    if request.method=='POST':
        workId = request.POST.get("workId",False) 
        if workId:
            docType = request.POST["docType"].strip()
            work = request.POST["work"].strip()
            isDuplicate = request.POST.get("isDuplicate",False) 
        duplicateId = request.POST.get("duplicateId",False)
        if duplicateId:
            reason = request.POST["reason"].strip()
        mergedSummaryWork = request.POST["mergedSummary"].strip()

        if workId:
            if docType == "researchWork":
                if isDuplicate:
                    researchWorkDuplicate = ResearchWorkDuplicate.objects.get(id = workId)
                    words = work.split(";;")
                    for i,word in enumerate(words):
                        if word.startswith(";"):
                            link = word[word.index("::")+2:]
                            name = word[1:word.index("::")]
                            words[i] = "link:"+name
                            if not link.startswith("http") and not link.startswith("//"):
                                link = "//"+link
                            if not Link.objects.filter(Q(name = name) & Q(url = link) & Q(researchWorkDuplicate = researchWorkDuplicate)).exists():
                                the_link = Link(
                                    name = name,
                                    url = link,
                                    researchWorkDuplicate = researchWorkDuplicate,
                                )
                                the_link.save()

                    work = "".join(words)

                    links = Link.objects.filter(researchWorkDuplicate = researchWorkDuplicate)
                    for link in links:
                        if not "link:"+link.name in work:
                            link.delete()

                    researchWorkDuplicate.work = work
                    researchWorkDuplicate.save()                
                else:
                    researchWork = ResearchWork.objects.get(id = workId)
                    words = work.split(";;")
                    for i,word in enumerate(words):
                        if word.startswith(";"):
                            link = word[word.index("::")+2:]
                            name = word[1:word.index("::")]
                            words[i] = "link:"+name
                            if not link.startswith("http") and not link.startswith("//"):
                                link = "//"+link
                            if not Link.objects.filter(Q(name = name) & Q(url = link) & Q(researchWork = researchWork)).exists():
                                the_link = Link(
                                    name = name,
                                    url = link,
                                    researchWork = researchWork,
                                )
                                the_link.save()

                    work = "".join(words)

                    links = Link.objects.filter(researchWork = researchWork)
                    for link in links:
                        if not "link:"+link.name in work:
                            link.delete()

                    researchWork.work = work
                    researchWork.save()
            elif docType == "researchSummary":
                if isDuplicate:
                    researchSummaryDuplicate = ResearchSummaryDuplicate.objects.get(id = workId)
                    researchSummaryDuplicate.work = work
                    researchSummaryDuplicate.save()
                else:
                    researchSummary = ResearchSummary.objects.get(id = workId)
                    researchSummary.work = work
                    researchSummary.save()
            elif docType == "mergedSummary":
                if isDuplicate:
                    mergedSummaryDuplicate = MergedSummaryDuplicate.objects.get(id = workId)
                    mergedSummaryDuplicate.work = mergedSummaryWork
                    mergedSummaryDuplicate.save()
                else:
                    mergedSummary = MergedSummary.objects.get(id = workId)
                    mergedSummary.work = mergedSummary
                    mergedSummary.save()

        
        if duplicateId:
            theMergedSummaryDuplicate = MergedSummaryDuplicate.objects.get(id = duplicateId)
            theMergedSummaryDuplicate.work = mergedSummaryWork
            theMergedSummaryDuplicate.save()
        else:
            mergedSummaryTopic = Topic.objects.get(id = mergedSummaryTopicId)
            theMergedSummary = MergedSummary.objects.get(topic = mergedSummaryTopic)
            theMergedSummary.work = mergedSummaryWork
            theMergedSummary.save()

        request.session["successMessage"] = "Saved Work successfully"
        request.session["failMessage"] = ""

        if duplicateId:
            if isDuplicate:
                base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
                query_String = urlencode({
                    "duplicateId": duplicateId,
                    "docType": docType,
                    "workId": workId,
                    "isDuplicate": isDuplicate,
                    })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
                query_String = urlencode({
                    "duplicateId": duplicateId,
                    "docType": docType,
                    "workId": workId,
                    })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
        else:
            if isDuplicate:
                base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
                query_String = urlencode({
                    "docType": docType,
                    "workId": workId,
                    "isDuplicate": isDuplicate,
                    })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
                query_String = urlencode({
                    "docType": docType,
                    "workId": workId,
                    })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)

def detachWork(request, mergedSummaryTopicId):
    if request.method == "POST":
        duplicateId = request.POST.get("duplicateId",False)
        isDuplicate = request.POST.get("isDuplicate",False)
        workId = request.POST.get("workId",False)
        docType = request.POST.get("docType",False)

        isResultDuplicate = request.POST["isResultDuplicate"]
        resultDocType = request.POST["resultDocType"]
        resultId = request.POST["resultId"]

        if isDuplicate == isResultDuplicate and resultDocType == docType and resultId ==workId:
            workId = ""

        mergedSummaryTopic = Topic.objects.get(id = mergedSummaryTopicId)
        mergedSummary = MergedSummary.objects.get(topic = mergedSummaryTopic)
        if resultDocType == "researchWork":
            if isResultDuplicate == "True":
                researchWorkDuplicate = ResearchWorkDuplicate.objects.get(id = resultId)
                mergedSummary.attachedResearchWorkDuplicates.remove(researchWorkDuplicate)
            else:
                researchWork = ResearchWork.objects.get(id = resultId)
                mergedSummary.attachedResearchWorks.remove(researchWork)
        elif resultDocType == "researchSummary":
            if isResultDuplicate == "True":
                researchSummaryDuplicate = ResearchSummaryDuplicate.objects.get(id = resultId)
                mergedSummary.attachedResearchSummaryDuplicates.remove(researchSummaryDuplicate)
            else:
                researchSummary = ResearchSummary.objects.get(id = resultId)
                mergedSummary.attachedResearchSummaries.remove(researchSummary)
        if resultDocType == "mergedSummary":
            if isResultDuplicate == "True":
                mergedSummaryDuplicate = MergedSummaryDuplicate.objects.get(id = resultId)
                mergedSummary.attachedMergedSummaryDuplicates.remove(mergedSummaryDuplicate)
            else:
                attachedMergedSummary = MergedSummary.objects.get(id = resultId)
                mergedSummary.attachedMergedSummaries.remove(attachedMergedSummary)

        mergedSummary.save()
        request.session["failMessage"] = ""
        request.session["successMessage"] = "Work Detached successfully"
        base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
        query_String = urlencode({
            "duplicateId": duplicateId,
            "docType": docType,
            "workId": workId,
            "isDuplicate": isDuplicate,
            })
        url = '{}?{}'.format(base_url, query_String)
        return redirect(url)

def attachWork(request, mergedSummaryTopicId):
    if request.method == "POST":
        duplicateId = request.POST.get("duplicateId",False)
        isDuplicate = request.POST.get("isDuplicate",False)
        workId = request.POST.get("workId",False)
        docType = request.POST.get("docType",False)

        isResultDuplicate = request.POST["isResultDuplicate"]
        resultDocType = request.POST["resultDocType"]
        resultId = request.POST["resultId"]

        mergedSummaryTopic = Topic.objects.get(id = mergedSummaryTopicId)
        mergedSummary = MergedSummary.objects.get(topic = mergedSummaryTopic)
        if resultDocType == "researchWork":
            if isResultDuplicate == "True":
                researchWorkDuplicate = ResearchWorkDuplicate.objects.get(id = resultId)
                mergedSummary.attachedResearchWorkDuplicates.add(researchWorkDuplicate)
            else:
                researchWork = ResearchWork.objects.get(id = resultId)
                mergedSummary.attachedResearchWorks.add(researchWork)
        elif resultDocType == "researchSummary":
            if isResultDuplicate == "True":
                researchSummaryDuplicate = ResearchSummaryDuplicate.objects.get(id = resultId)
                mergedSummary.attachedResearchSummaryDuplicates.add(researchSummaryDuplicate)
            else:
                researchSummary = ResearchSummary.objects.get(id = resultId)
                mergedSummary.attachedResearchSummaries.add(researchSummary)
        if resultDocType == "mergedSummary":
            if isResultDuplicate == "True":
                mergedSummaryDuplicate = MergedSummaryDuplicate.objects.get(id = resultId)
                mergedSummary.attachedMergedSummaryDuplicates.add(mergedSummaryDuplicate)
            else:
                attachedMergedSummary = MergedSummary.objects.get(id = resultId)
                mergedSummary.attachedMergedSummaries.add(attachedMergedSummary)

        mergedSummary.save()
        request.session["failMessage"] = ""
        request.session["successMessage"] = "Work attached Successfully"
        base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
        query_String = urlencode({
            "duplicateId": duplicateId,
            "docType": docType,
            "workId": workId,
            "isDuplicate": isDuplicate,
            })
        url = '{}?{}'.format(base_url, query_String)
        return redirect(url)

def mergedSearch(request,topicId):
    if request.method=='GET':
        search = request.GET["search"]
        docTypes = request.GET.getlist("docTypes")

        searchResults = []
        if docTypes:
            nameResults = Topic.objects.filter(Q(name__icontains = search) & Q(researcher = request.user))
            
            docType = False
            for nameResult in nameResults:
                if nameResult.docType == "Research Work" and "Research Work" in docTypes:
                    docType = "researchWork"
                    result = {
                        "id": nameResult.ResearchWork.id,
                        "isDuplicate": False,
                        "docType": docType,
                        "name": nameResult.name,
                        "reason": False,
                    }
                    searchResults.append(result)

                if nameResult.docType == "Merged Summary" and "Merged Summary" in docTypes:
                    docType = "mergedSummary"
                    result = {
                        "id": nameResult.MergedSummary.id,
                        "isDuplicate": False,
                        "docType": docType,
                        "name": nameResult.name,
                        "reason": False,
                    }
                    searchResults.append(result)
                
                if nameResult.docType == "Research Work" and "Research Summary" in docTypes:
                    result = {
                    "id": nameResult.ResearchWork.researchSummary.id,
                    "isDuplicate": False,
                    "docType": "researchSummary",
                    "name": nameResult.name,
                    "reason": False,
                    }
                    searchResults.append(result)

                if nameResult.docType == "Research Work" and "Research Work Duplicate" in docTypes:
                    for researchDuplicate in nameResult.ResearchWork.researchWorkDuplicates.all():
                        result = {
                        "id": researchDuplicate.id,
                        "isDuplicate": "True",
                        "docType": "researchWork",
                        "name": nameResult.name,
                        "reason": researchDuplicate.reason,
                        }
                        searchResults.append(result)

                if nameResult.docType == "Research Work" and "Research Summary Duplicate" in docTypes:
                    for summaryDuplicate in nameResult.ResearchWork.researchSummary.researchSummaryDuplicates.all():
                        result = {
                        "id": summaryDuplicate.id,
                        "isDuplicate": "True",
                        "docType": "researchSummary",
                        "name": nameResult.name,
                        "reason": summaryDuplicate.reason,
                        }
                        searchResults.append(result)
                
                if nameResult.docType == "Merged Summary" and "Merged Summary Duplicate" in docTypes:
                    for mergedDuplicate in nameResult.MergedSummary.mergedSummaryDuplicates.all():
                        result = {
                        "id": mergedDuplicate.id,
                        "isDuplicate": "True",
                        "docType": "mergedSummary",
                        "name": nameResult.name,
                        "reason": mergedDuplicate.reason,
                        }
                        searchResults.append(result)

        results = searchResults

        if results:
            request.session["successMessage"] = f"{len(results)} Topics found and successfully returned"
            request.session["failMessage"] = ""
        else:
            request.session["successMessage"] = ""
            request.session["failMessage"] = "0 Topics found, No topic matched the specified search criteria"
            
        duplicateId = request.GET.get("duplicateId",False)
        isDuplicate = request.GET.get("isDuplicate",False)
        workId = request.GET.get("workId",False)
        docType = request.GET.get("docType",False)
        print(f"docType id is {docType}")
        if workId:
            workTopic = False
            work = False
            links = []
            if docType == "researchWork":
                if isDuplicate == "True":
                    work = ResearchWorkDuplicate.objects.get(id = workId)
                    workTopic = work.originalResearchWork.topic
                    links = Link.objects.filter(researchWorkDuplicate = work)
                else:
                    work = ResearchWork.objects.get(id = workId)
                    workTopic = work.topic
                    links = Link.objects.filter(researchWork = work)
            if docType == "researchSummary":
                if isDuplicate == "True":
                    work = ResearchSummaryDuplicate.objects.get(id = workId)
                    workTopic = work.originalResearchSummary.researchWork.topic
                else:
                    work = ResearchSummary.objects.get(id = workId)
                    workTopic = work.researchWork.topic
            if docType == "mergedSummary":
                if isDuplicate == "True":
                    work = MergedSummaryDuplicate.objects.get(id = workId)
                    workTopic = work.originalMergedSummary.topic
                else:
                    work = MergedSummary.objects.get(id = workId)
                    workTopic = work.topic


            summaryDuplicate = False
            if duplicateId:
                summaryDuplicate = MergedSummaryDuplicate.objects.get(id = duplicateId)
        else:
            work = False
            summaryDuplicate = False
            workTopic = False
            links = []

        topic = Topic.objects.get(id=topicId)
        the_topic = topic
        mergedSummary = MergedSummary.objects.get(topic = topic)
        path = []
        path.append(topic)
        while True:
            if topic.parentFolder:
                path.append(topic.parentFolder.topic)
                topic = topic.parentFolder.topic
            else:
                break
        path.reverse()

        attachedWork = []
        for attachedResult in mergedSummary.attachedResearchWorks.all():
            result = {
                "id": attachedResult.id,
                "isDuplicate": False,
                "docType": "researchWork",
                "name": attachedResult.topic.name,
                "reason": False,
            }
            attachedWork.append(result)

        for attachedResult in mergedSummary.attachedResearchWorkDuplicates.all():
            result = {
                "id": attachedResult.id,
                "isDuplicate": "True",
                "docType": "researchWork",
                "name": attachedResult.originalResearchWork.topic.name,
                "reason": attachedResult.reason,
            }
            attachedWork.append(result)
        
        for attachedResult in mergedSummary.attachedResearchSummaries.all():
            result = {
                "id": attachedResult.id,
                "isDuplicate": False,
                "docType": "researchSummary",
                "name": attachedResult.researchWork.topic.name,
                "reason": False,
            }
            attachedWork.append(result)

        for attachedResult in mergedSummary.attachedResearchSummaryDuplicates.all():
            result = {
                "id": attachedResult.id,
                "isDuplicate": "True",
                "docType": "researchSummary",
                "name": attachedResult.originalResearchSummary.researchWork.topic.name,
                "reason": attachedResult.reason,
            }
            attachedWork.append(result)
        
        for attachedResult in mergedSummary.attachedMergedSummaries.all():
            result = {
                "id": attachedResult.id,
                "isDuplicate": False,
                "docType": "mergedSummary",
                "name": attachedResult.topic.name,
                "reason": False,
            }
            attachedWork.append(result)

        for attachedResult in mergedSummary.attachedMergedSummaryDuplicates.all():
            result = {
                "id": attachedResult.id,
                "isDuplicate": "True",
                "docType": "mergedSummary",
                "name": attachedResult.originalMergedSummary.topic.name,
                "reason": attachedResult.reason,
            }
            attachedWork.append(result)

        return render(request,"research_app/mergedSummary.html",{
            "mergedSummary":mergedSummary,
            "mergedSummaryTopic":the_topic,
            "path":path,
            "workTopic":workTopic,
            "isDuplicate":isDuplicate,
            "work":work,
            "type":docType,
            "summaryDuplicate":summaryDuplicate,
            "links":links,
            "searchResults":results,
            "attachedWork":attachedWork,
        })

def switchWork(request, mergedSummaryTopicId):
    if request.method=='GET':
        attachedWork = request.GET["attachedWork"]

        attachedParts = attachedWork.split("-")
        request.session["failMessage"] = ""
        request.session["successMessage"] = "Switched attached Work Successfully"
        base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
        query_String = urlencode({
            "docType": attachedParts[1],
            "isDuplicate": attachedParts[2],
            "workId": attachedParts[0],
            })
        url = '{}?{}'.format(base_url, query_String)
        return redirect(url)

def switchMerge(request, mergedSummaryTopicId):
    if request.method=='GET': 
        merge = request.GET["merge"]
        
        duplicateId = request.GET.get("duplicateId",False)
        isDuplicate = request.GET.get("isDuplicate",False)
        workId = request.GET.get("workId",False)
        docType = request.GET.get("docType",False)
        if merge == "original":
            request.session["failMessage"] = ""
            request.session["successMessage"] = "Switched to original Merged Summary Successfully"
            base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
            query_String = urlencode({
                "docType": docType,
                "workId": workId,
                "isDuplicate": isDuplicate,
                })
            url = '{}?{}'.format(base_url, query_String)
            return redirect(url)  
        else:
            request.session["failMessage"] = ""
            request.session["successMessage"] = "Switched to the Merged Summary Duplicate successfully"
            base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
            query_String = urlencode({
                "docType": docType,
                "workId": workId,
                "isDuplicate": isDuplicate,
                "duplicateId": merge,
                })
            url = '{}?{}'.format(base_url, query_String)
            return redirect(url) 

def duplicateMerge(request, mergedSummaryTopicId):
    if request.method=='POST':
        reason = request.POST["reason"]

        mergedSummaryTopic = Topic.objects.get(id = mergedSummaryTopicId)
        mergedSummary = MergedSummary.objects.get(topic = mergedSummaryTopic)
        
        if MergedSummaryDuplicate.objects.filter(Q(reason = reason) & Q(originalMergedSummary = mergedSummary)).exists():
            request.session["successMessage"] = ""
            request.session["failMessage"] = f"A Duplicate of this Merged Summary with the reason ({reason}) already exists"
        else:
            mergedSummaryDuplicate = MergedSummaryDuplicate(
                reason = reason,
                originalMergedSummary = mergedSummary,
            )
            mergedSummaryDuplicate.save()

            request.session["successMessage"] = f"Merged Summary Duplicate, (reason:{reason}) created successfully"
            request.session["failMessage"] = ""

        duplicateId = request.POST.get("duplicateId",False)
        isDuplicate = request.POST.get("isDuplicate",False)
        workId = request.POST.get("workId",False)
        docType = request.POST.get("docType",False)

        base_url = reverse("mergedSummary", kwargs={'topicId': mergedSummaryTopicId})
        query_String = urlencode({
            "docType": docType,
            "workId": workId,
            "isDuplicate": isDuplicate,
            "duplicateId": duplicateId,
            })
        url = '{}?{}'.format(base_url, query_String)
        return redirect(url)        

def mergedSummary(request,topicId):
    duplicateId = request.GET.get("duplicateId",False)
    isDuplicate = request.GET.get("isDuplicate",False)
    docType = request.GET.get("docType",False)
    workId = request.GET.get("workId",False)
    
    if workId:
        workTopic = False
        work = False
        links = []
        if docType == "researchWork":
            if isDuplicate == "True":
                work = ResearchWorkDuplicate.objects.get(id = workId)
                workTopic = work.originalResearchWork.topic
                links = Link.objects.filter(researchWorkDuplicate = work)
            else:
                work = ResearchWork.objects.get(id = workId)
                workTopic = work.topic
                links = Link.objects.filter(researchWork = work)
        if docType == "researchSummary":
            if isDuplicate == "True":
                work = ResearchSummaryDuplicate.objects.get(id = workId)
                workTopic = work.originalResearchSummary.researchWork.topic
            else:
                work = ResearchSummary.objects.get(id = workId)
                workTopic = work.researchWork.topic
        if docType == "mergedSummary":
            if isDuplicate == "True":
                work = MergedSummaryDuplicate.objects.get(id = workId)
                workTopic = work.originalMergedSummary.topic
            else:
                work = MergedSummary.objects.get(id = workId)
                workTopic = work.topic

        summaryDuplicate = False
        if duplicateId:
            summaryDuplicate = MergedSummaryDuplicate.objects.get(id = duplicateId)
    else:
        work = False
        summaryDuplicate = False
        workTopic = False
        links = []

    topic = Topic.objects.get(id=topicId)
    the_topic = topic
    mergedSummary = MergedSummary.objects.get(topic = topic)
    path = []
    path.append(topic)
    while True:
        if topic.parentFolder:
            path.append(topic.parentFolder.topic)
            topic = topic.parentFolder.topic
        else:
            break
    path.reverse()

    attachedWork = []
    for attachedResult in mergedSummary.attachedResearchWorks.all():
        result = {
            "id": attachedResult.id,
            "isDuplicate": False,
            "docType": "researchWork",
            "name": attachedResult.topic.name,
            "reason": False,
        }
        attachedWork.append(result)

    for attachedResult in mergedSummary.attachedResearchWorkDuplicates.all():
        result = {
            "id": attachedResult.id,
            "isDuplicate": "True",
            "docType": "researchWork",
            "name": attachedResult.originalResearchWork.topic.name,
            "reason": attachedResult.reason,
        }
        attachedWork.append(result)
    
    for attachedResult in mergedSummary.attachedResearchSummaries.all():
        result = {
            "id": attachedResult.id,
            "isDuplicate": False,
            "docType": "researchSummary",
            "name": attachedResult.researchWork.topic.name,
            "reason": False,
        }
        attachedWork.append(result)

    for attachedResult in mergedSummary.attachedResearchSummaryDuplicates.all():
        result = {
            "id": attachedResult.id,
            "isDuplicate": "True",
            "docType": "researchSummary",
            "name": attachedResult.originalResearchSummary.researchWork.topic.name,
            "reason": attachedResult.reason,
        }
        attachedWork.append(result)
    
    for attachedResult in mergedSummary.attachedMergedSummaries.all():
        result = {
            "id": attachedResult.id,
            "isDuplicate": False,
            "docType": "mergedSummary",
            "name": attachedResult.topic.name,
            "reason": False,
        }
        attachedWork.append(result)

    for attachedResult in mergedSummary.attachedMergedSummaryDuplicates.all():
        result = {
            "id": attachedResult.id,
            "isDuplicate": "True",
            "docType": "mergedSummary",
            "name": attachedResult.originalMergedSummary.topic.name,
            "reason": attachedResult.reason,
        }
        attachedWork.append(result)

    return render(request,"research_app/mergedSummary.html",{
        "mergedSummary":mergedSummary,
        "mergedSummaryTopic":the_topic,
        "path":path,
        "workTopic":workTopic,
        "isDuplicate":isDuplicate,
        "work":work,
        "type":docType,
        "summaryDuplicate":summaryDuplicate,
        "links":links,
        "attachedWork":attachedWork,
    })

def moveTopic(request):
    if request.method=='GET':
        topicId = int(request.GET["id"])
        folderTopicId = request.GET.get("folderTopicId",False)
        topic = Topic.objects.get(id = topicId)
        request.session["movingTopic"] = topicId
        request.session["successMessage"] = f"{topic} was added to the clipboard"
        request.session["failMessage"] = ""
        if folderTopicId:
            return redirect("folder",folderTopicId)
        else:
            return redirect("home")
    
    elif request.method=='POST':
        topicId = int(request.POST["topicId"])
        folderTopicId = int(request.POST.get("folderTopicId",False))
        topic = Topic.objects.get(id = topicId)
        path = []
        if folderTopicId:
            folderTopic = Topic.objects.get(id = folderTopicId)
            newParentFolder = Folder.objects.get(topic = folderTopic)

            parentFolderTopic = folderTopic
            path.append(parentFolderTopic)
            while True:
                if parentFolderTopic.parentFolder:
                    path.append(parentFolderTopic.parentFolder.topic)
                    parentFolderTopic = parentFolderTopic.parentFolder.topic
                else:
                    break
        else:
            newParentFolder = "Home"
        oldParentFolder = topic.parentFolder

        if not topic in path:
            if folderTopicId:
                topic.parentFolder = newParentFolder
            else:
                topic.parentFolder = None
            topic.save()
            
            if oldParentFolder:
                request.session["successMessage"] = f"{topic} has been moved from The {oldParentFolder} Folder to The {newParentFolder} Folder successfully"
            else:
                request.session["successMessage"] = f"{topic} has been moved from The Home Folder to The {newParentFolder} Folder successfully"

            request.session["failMessage"] = ""
            request.session["movingTopic"] = ""
        else:
            request.session["failMessage"] = "Can't copy a folder into itself, Paste it elsewhere"
            request.session["successMessage"] = ""
        if folderTopicId:
            return redirect("folder",folderTopicId)
        else:
            return redirect("home")

def visitLink(request):
    if request.method=='GET':
        link = request.GET["link"]

        request.session["successMessage"] = "link visited successfully"
        request.session["failMessage"] = ""
        return redirect(link)

def duplicateResearch(request, topicId):
    if request.method=='POST':
        reason = request.POST["reason"]
        researchTopic = Topic.objects.get(id = topicId)
        originalResearchWork = ResearchWork.objects.get(topic = researchTopic)
        summaryDuplicateId = request.POST.get("duplicateId",False)
        researchWorkDuplicateId = request.POST.get("researchWorkDuplicateId",False)

        if ResearchWorkDuplicate.objects.filter(Q(originalResearchWork = originalResearchWork) & Q(reason = reason)).exists():
            request.session["failMessage"] = f"'{reason}' already exists as a reason for some other duplicate of this very Research Work"
            request.session["successMessage"] = ""
        else:
            duplicate = ResearchWorkDuplicate(
                reason = reason,
                originalResearchWork = originalResearchWork,
            )
            duplicate.save()
            request.session["successMessage"] = f"{originalResearchWork} research work duplicated successfully. Reason: {reason}"
            request.session["failMessage"] = ""
        
        if researchWorkDuplicateId:
            if summaryDuplicateId:
                base_url = reverse("researchWorkDuplicate", kwargs={'duplicateId': researchWorkDuplicateId})
                query_String = urlencode({"summaryDuplicateId": summaryDuplicateId,
                                        })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                return redirect("researchWorkDuplicate",researchWorkDuplicateId)
        else:
            if summaryDuplicateId:
                return redirect("researchSummaryDuplicate",summaryDuplicateId)
            else:
                return redirect("researchWork",topicId)


def duplicateSummary(request, topicId):
    if request.method=='POST':
        reason = request.POST["reason"]
        researchTopic = Topic.objects.get(id = topicId)
        researchWork = ResearchWork.objects.get(topic = researchTopic)
        originalResearchSummary = ResearchSummary.objects.get(researchWork = researchWork)
        
        summaryDuplicateId = request.POST.get("duplicateId",False)
        researchWorkDuplicateId = request.POST.get("researchWorkDuplicateId",False)

        if ResearchSummaryDuplicate.objects.filter(Q(originalResearchSummary = originalResearchSummary) & Q(reason = reason)).exists():
            request.session["failMessage"] = f"'{reason}' already exists as a reason for some other Summary duplicate of this very Research Work"
            request.session["successMessage"] = ""
        else:
            duplicate = ResearchSummaryDuplicate(
                reason = reason,
                originalResearchSummary = originalResearchSummary,
            )
            duplicate.save()
            request.session["successMessage"] = f"Research Summary duplicated successfully. Reason: {reason}"
            request.session["failMessage"] = ""
        
        if researchWorkDuplicateId:
            if summaryDuplicateId:
                base_url = reverse("researchWorkDuplicate", kwargs={'duplicateId': researchWorkDuplicateId})
                query_String = urlencode({"summaryDuplicateId": summaryDuplicateId,
                                        })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                return redirect("researchWorkDuplicate",researchWorkDuplicateId)
        else:
            if summaryDuplicateId:
                return redirect("researchSummaryDuplicate",summaryDuplicateId)
            else:
                return redirect("researchWork",topicId)

def switchSummary(request, topicId):
    if request.method=='GET':
        summary = request.GET["summary"]
        researchWorkDuplicateId = request.GET.get("duplicateId",False)

        if summary == "original":
            request.session["successMessage"] = "Switched to original Summary successfully"
            request.session["failMessage"] = ""

            if researchWorkDuplicateId:
                return redirect("researchWorkDuplicate",researchWorkDuplicateId)
            return redirect("researchWork",topicId)
        else:
            request.session["successMessage"] = "Switched to duplicate Summary successfully"
            request.session["failMessage"] = ""

            if researchWorkDuplicateId:
                base_url = reverse("researchSummaryDuplicate", kwargs={'duplicateId': summary})
                query_String = urlencode({"researchWorkDuplicateId": researchWorkDuplicateId,
                                        })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                return redirect("researchSummaryDuplicate",summary)

def switchResearch(request, topicId):
    if request.method=='GET':
        research = request.GET["research"]
        summaryDuplicateId = request.GET.get("duplicateId",False)


        if research == "original":
            request.session["successMessage"] = "Switched to original research successfully"
            request.session["failMessage"] = ""

            if summaryDuplicateId:
                return redirect("researchSummaryDuplicate",summaryDuplicateId)
            return redirect("researchWork",topicId)
        else:
            request.session["successMessage"] = "Switched to duplicate research successfully"
            request.session["failMessage"] = ""

            if summaryDuplicateId:
                base_url = reverse("researchWorkDuplicate", kwargs={'duplicateId': research})
                query_String = urlencode({"summaryDuplicateId": summaryDuplicateId,
                                        })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                return redirect("researchWorkDuplicate",research)


def deleteSummary(request, topicId):
    if request.method=='GET':
        summaryId = request.GET["summary"]
        researchWorkDuplicateId = request.GET.get("duplicateId",False)
        summaryDuplicateId = request.GET.get("summaryDuplicateId",False)

        summary = ResearchSummaryDuplicate.objects.get(id = summaryId)
        summary.delete()

        request.session["successMessage"] = f"Summary duplicate (with reason: {summary.reason}) deleted successfully"
        request.session["failMessage"] = ""

        if researchWorkDuplicateId:
            if summaryDuplicateId:
                base_url = reverse("researchWorkDuplicate", kwargs={'duplicateId': researchWorkDuplicateId})
                query_String = urlencode({"summaryDuplicateId": summaryDuplicateId,
                                        })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                return redirect("researchWorkDuplicate",researchWorkDuplicateId)
        else:
            if summaryDuplicateId:
                return redirect("researchSummaryDuplicate",summaryDuplicateId)
            else:
                return redirect("researchWork",topicId)

def deleteResearch(request, topicId):
    if request.method=='GET':
        researchDuplicateId = request.GET["research"]
        summaryDuplicateId = request.GET.get("duplicateId",False)
        researchWorkDuplicateId = request.GET.get("researchWorkDuplicateId",False)
        
        research = ResearchWorkDuplicate.objects.get(id = researchDuplicateId)
        research.delete()

        request.session["successMessage"] = f"Research duplicate (with reason:{research.reason}) deleted successfully"
        request.session["failMessage"] = ""

        if researchWorkDuplicateId:
            if summaryDuplicateId:
                base_url = reverse("researchWorkDuplicate", kwargs={'duplicateId': researchWorkDuplicateId})
                query_String = urlencode({"summaryDuplicateId": summaryDuplicateId,
                                        })
                url = '{}?{}'.format(base_url, query_String)
                return redirect(url)
            else:
                return redirect("researchWorkDuplicate",researchWorkDuplicateId)
        else:
            if summaryDuplicateId:
                return redirect("researchSummaryDuplicate",summaryDuplicateId)
            else:
                return redirect("researchWork",topicId)

def researchWorkDuplicate(request, duplicateId):
    researchDuplicate = ResearchWorkDuplicate.objects.get(id = duplicateId)
    originalResearchWork = researchDuplicate.originalResearchWork
    researches = ResearchWorkDuplicate.objects.filter(originalResearchWork = originalResearchWork)

    summaryDuplicateId = request.GET.get("summaryDuplicateId",False)
    if summaryDuplicateId:
        summaryDuplicate = ResearchSummaryDuplicate.objects.get(id = int(summaryDuplicateId))
    else:
        summaryDuplicate = False

    topicId = researchDuplicate.originalResearchWork.topic.id

    topic = Topic.objects.get(id=topicId)
    the_topic = topic
    researchWork = ResearchWork.objects.get(topic = topic)
    path = []
    path.append(topic)
    while True:
        if topic.parentFolder:
            path.append(topic.parentFolder.topic)
            topic = topic.parentFolder.topic
        else:
            break
    path.reverse()

    links = Link.objects.filter(researchWorkDuplicate = researchDuplicate)
    
    try:
        originalResearchSummary = researchWork.researchSummary
        summaries = ResearchSummaryDuplicate.objects.filter(originalResearchSummary = originalResearchSummary)
    except ObjectDoesNotExist:
        summaries = []
    return render(request,"research_app/researchWork.html",{
        "summaries":summaries,
        "researchWork":researchWork,
        "researchWorkTopic":the_topic,
        "path":path,
        "links":links,
        "researches":researches,
        "researchWorkDuplicate":researchDuplicate,
        "summaryDuplicate":summaryDuplicate,
    })

def researchSummaryDuplicate(request, duplicateId):
    summaryDuplicate = ResearchSummaryDuplicate.objects.get(id = duplicateId)
    originalResearchSummary = summaryDuplicate.originalResearchSummary
    summaries = ResearchSummaryDuplicate.objects.filter(originalResearchSummary = originalResearchSummary)
    
    researchWorkDuplicateId = request.GET.get("researchWorkDuplicateId",False)
    if researchWorkDuplicateId:
        researchWorkDuplicate = ResearchWorkDuplicate.objects.get(id = researchWorkDuplicateId)
    else:
        researchWorkDuplicate = False

    topicId = summaryDuplicate.originalResearchSummary.researchWork.topic.id

    topic = Topic.objects.get(id=topicId)
    the_topic = topic
    researchWork = ResearchWork.objects.get(topic = topic)
    path = []
    path.append(topic)
    while True:
        if topic.parentFolder:
            path.append(topic.parentFolder.topic)
            topic = topic.parentFolder.topic
        else:
            break
    path.reverse()

    links = Link.objects.filter(researchWork = researchWork)
    researches = ResearchWorkDuplicate.objects.filter(originalResearchWork = researchWork)
    return render(request,"research_app/researchWork.html",{
        "summaryDuplicate":summaryDuplicate,
        "summaries":summaries,
        "researchWork":researchWork,
        "researchWorkTopic":the_topic,
        "path":path,
        "links":links,
        "researches":researches,
        "researchWorkDuplicate":researchWorkDuplicate,
    })