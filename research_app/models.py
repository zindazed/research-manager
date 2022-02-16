from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.aggregates import Avg, Max, Sum
from django.db.models.deletion import CASCADE
from django.db.models.query_utils import PathInfo
from datetime import timedelta, datetime
import math
import json

# Create your models here.

# class Topic(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField(null=True,blank=True)
#     parentFolder = models.ForeignKey("Folder", related_name = "topics",null=True,blank=True,on_delete=models.CASCADE)
#     researcher = models.ForeignKey(User, related_name="topics", on_delete=models.CASCADE)
#     docType = models.CharField(max_length=50)
#     CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
#     LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

#     def __str__(self):
#         return f"{self.name} {self.docType}"
    

class Folder(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    parentFolder = models.ForeignKey("Folder", related_name = "folders",null=True,blank=True,on_delete=models.CASCADE)
    researcher = models.ForeignKey(User, related_name="folders", on_delete=models.CASCADE)
    docType = models.CharField(max_length=50, default="Folder")
    # topic = models.OneToOneField("Topic", related_name = "folder", on_delete=models.CASCADE)
    CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
    LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.name}"

class ResearchWork(models.Model):
    # topic = models.OneToOneField("Topic", related_name = "ResearchWork", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    parentFolder = models.ForeignKey("Folder", related_name = "researchWorks",null=True,blank=True,on_delete=models.CASCADE)
    researcher = models.ForeignKey(User, related_name="researchWorks", on_delete=models.CASCADE)
    docType = models.CharField(max_length=50, default="Research Work")
    work = models.TextField(default="")
    CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
    LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.name}"

class ResearchWorkDuplicate(models.Model):
    reason = models.TextField()
    work = models.TextField(default="")
    originalResearchWork = models.ForeignKey("ResearchWork", related_name="researchWorkDuplicates", on_delete=models.CASCADE)
    CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
    LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.originalResearchWork.name} Duplicated, Reason: {self.reason}"

class Link(models.Model):
    name = models.CharField(max_length=200)
    url = models.TextField()
    researchWork = models.ForeignKey("ResearchWork", related_name="links", on_delete=models.CASCADE,null=True,blank=True)
    researchWorkDuplicate = models.ForeignKey("ResearchWorkDuplicate", related_name="links", on_delete=models.CASCADE,null=True,blank=True)
    CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
    LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.name}"

class ResearchSummary(models.Model):
    work = models.TextField(default="")
    researchWork = models.OneToOneField("ResearchWork", related_name="researchSummary", on_delete=models.CASCADE)
    CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
    LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.researchWork.name}"

class ResearchSummaryDuplicate(models.Model):
    reason = models.TextField()
    work = models.TextField(default="")
    originalResearchSummary = models.ForeignKey("ResearchSummary", related_name="researchSummaryDuplicates", on_delete=models.CASCADE)
    CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
    LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.originalResearchSummary.researchWork.name} Duplicated, Reason: {self.reason}"

class MergedSummary(models.Model):
    # topic = models.OneToOneField("Topic", related_name = "MergedSummary", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    parentFolder = models.ForeignKey("Folder", related_name = "mergedSummaries",null=True,blank=True,on_delete=models.CASCADE)
    researcher = models.ForeignKey(User, related_name="mergedSummaries", on_delete=models.CASCADE)
    docType = models.CharField(max_length=50, default="Merged Summary")
    work = models.TextField(default="")
    attachedResearchWorks = models.ManyToManyField("ResearchWork", related_name="linkedMergedSummaries",blank=True)
    attachedResearchSummaries = models.ManyToManyField("ResearchSummary", related_name="linkedMergedSummaries",blank=True)
    attachedMergedSummaries = models.ManyToManyField("MergedSummary", related_name="linkedMergedSummaries",blank=True)
    attachedResearchWorkDuplicates = models.ManyToManyField("ResearchWorkDuplicate", related_name="linkedMergedSummaries",blank=True)
    attachedResearchSummaryDuplicates = models.ManyToManyField("ResearchSummaryDuplicate", related_name="linkedMergedSummaries",blank=True)
    attachedMergedSummaryDuplicates = models.ManyToManyField("MergedSummaryDuplicate", related_name="linkedMergedSummaries",blank=True)
    CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
    LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.name}"

class MergedSummaryDuplicate(models.Model):
    reason = models.TextField()
    work = models.TextField(default="")
    originalMergedSummary = models.ForeignKey("MergedSummary", related_name="mergedSummaryDuplicates", on_delete=models.CASCADE)
    CreatedAt = models.DateTimeField(auto_now=False, auto_now_add=True)
    LastModifiedAt = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.originalMergedSummary.name} duplicated, Reason: {self.reason}"