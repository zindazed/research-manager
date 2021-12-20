from dateutil.relativedelta import relativedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.aggregates import Avg, Max, Sum
from django.db.models.deletion import CASCADE
from django.db.models.query_utils import PathInfo
from datetime import timedelta
import math
import json

# Create your models here.

class Folder(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    parentFolders = models.ManyToManyField("Folder", related_name = "childFolders",blank=True)
    creator = models.ForeignKey(User, related_name="folders", on_delete=models.CASCADE)

class ResearchWork(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    work = models.TextField(null=True,blank=True)
    folder = models.ManyToManyField("Folder", related_name = "researchWorks",blank=True)
    researcher = models.ForeignKey(User, related_name="researchWorks", on_delete=models.CASCADE)

class ResearchWorkDuplicate(models.Model):
    reason = models.TextField()
    work = models.TextField(null=True,blank=True)
    originalResearchWork = models.ForeignKey("ResearchWork", related_name="researchWorkDuplicates", on_delete=models.CASCADE)
    originalResearchWorkDuplicate = models.ForeignKey("ResearchWorkDuplicate", related_name="researchWorkDuplicates", on_delete=models.CASCADE,null=True,blank=True)

class Link(models.Model):
    name = models.CharField(max_length=200)
    url = models.TextField()
    researchWork = models.ForeignKey("ResearchWork", related_name="links", on_delete=models.CASCADE,null=True,blank=True)
    researchWorkDuplicate = models.ForeignKey("ResearchWorkDuplicate", related_name="links", on_delete=models.CASCADE,null=True,blank=True)

class ResearchSummary(models.Model):
    work = models.TextField(null=True,blank=True)
    researchWork = models.OneToOneField("ResearchWork", related_name="researchSummary", on_delete=models.CASCADE)

class ResearchSummaryDuplicate(models.Model):
    reason = models.TextField()
    work = models.TextField(null=True,blank=True)
    originalResearchSummary = models.ForeignKey("ResearchSummary", related_name="researchSummaryDuplicates", on_delete=models.CASCADE)
    originalResearchSummaryDuplicate = models.ForeignKey("ResearchSummaryDuplicate", related_name="researchSummaryDuplicates", on_delete=models.CASCADE,null=True,blank=True)

class MergedSummary(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    work = models.TextField(null=True,blank=True)
    folder = models.ManyToManyField("Folder", related_name = "mergedSummaries",blank=True)
    merger = models.ForeignKey(User, related_name="mergedSummaries", on_delete=models.CASCADE)
    attachedResearchWorks = models.ManyToManyField("ResearchWork", related_name="linkedMergedSummaries",blank=True)
    attachedResearchSummaries = models.ManyToManyField("ResearchSummary", related_name="linkedMergedSummaries",blank=True)
    attachedMergedSummaries = models.ManyToManyField("MergedSummary", related_name="linkedMergedSummaries",blank=True)

class MergedSummaryDuplicate(models.Model):
    reason = models.TextField()
    work = models.TextField(null=True,blank=True)
    originalMergedSummary = models.ForeignKey("MergedSummary", related_name="mergedSummaryDuplicates", on_delete=models.CASCADE)
    attachedResearchWorks = models.ManyToManyField("ResearchWork", related_name="linkedMergedSummaryDuplicates",blank=True)
    attachedResearchSummary = models.ManyToManyField("ResearchSummary", related_name="linkedMergedSummaryDuplicates",blank=True)
    attachedMergedSummary = models.ManyToManyField("MergedSummary", related_name="linkedMergedSummaryDuplicates",blank=True)

# class Member(models.Model):
#     user = models.OneToOneField(User,on_delete=models.CASCADE)
#     image = models.ImageField(upload_to="assets/images/")
#     deadlines_met=models.FloatField(default=0)
#     deadlines_missed=models.FloatField(default=0)
#     tasks_being_done = models.FloatField(default=0)
#     tasks_done = models.FloatField(default=0) 
#     tasks_givenup=models.FloatField(default=0) 
#     tasks_approved = models.FloatField(default=0)
#     tasks_unapproved = models.FloatField(default=0)
#     tasks_rectified = models.FloatField(default=0)
#     tasks_duration = models.DurationField(default = timedelta(0))
#     deadline_excess = models.DurationField(default = timedelta(0))
#     tasks_objections_made = models.IntegerField(default=0)
#     highest_performance = models.FloatField(default=0)
#     highest_creativity = models.FloatField(default=0)
#     highest_research = models.FloatField(default=0)

#     def major_role(self):
#         if self.monthly_tracking.all().count() >= 3:
#             query = self.monthly_tracking.all().order_by("-date")
#             lastone = query[2]
#         else:
#             lastone = MonthlyTracking(
#                     date = datetime.now() + relativedelta(months=-1),
#                     member = self,)
#         role = {
#             "Unknown":0,
#             "Software Analyst":self.re()-lastone.requirements_engineering,
#             "Software Architect":self.sad()-lastone.sad,
#             "UI/UX Designer":self.ui()-lastone.ui,
#             "Software Engineer":self.dsa()-lastone.dsa,
#             "Software Developer":self.code()-lastone.code,
#             "Software Tester":self.test()-lastone.test,
#             }
#         return max(role, key=role.get)

#     def total_tasks_duration(self):
#         result = self.tasks_duration
#         minutes, seconds = divmod(result.total_seconds(), 60)
#         hours, minutes = divmod(minutes, 60)
#         days, hours = divmod(hours, 24)
#         speed = ""
#         if days == 0:
#             if hours == 0:
#                 if minutes == 0:
#                     speed += f"{str(round(seconds)).rjust(2, '0')} seconds"
#                 else:
#                     speed += f"{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} minutes"
#             else:
#                 speed += f"{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} hours"
#         else:
#             speed += f"{str(round(days)).rjust(2, '0')} days "
#             if hours == 0:
#                 if minutes == 0:
#                     speed += f"{str(round(seconds)).rjust(2, '0')} seconds"
#                 else:
#                     speed += f"{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} minutes"
#             else:
#                 speed += f"{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} hours"
#         return speed

#     def not_seconds_hours(self,result):
#         result = result * 60 * 60
#         minutes, seconds = divmod(result, 60)
#         hours, minutes = divmod(minutes, 60)
#         days, hours = divmod(hours, 24)
#         speed = ""
#         if days == 0:
#             if hours == 0:
#                 if minutes == 0:
#                     speed += f"{str(round(seconds)).rjust(2, '0')} seconds"
#                 else:
#                     speed += f"{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} minutes"
#             else:
#                 speed += f"{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} hours"
#         else:
#             speed += f"{str(round(days)).rjust(2, '0')} days "
#             if hours == 0:
#                 if minutes == 0:
#                     speed += f"{str(round(seconds)).rjust(2, '0')} seconds"
#                 else:
#                     speed += f"{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} minutes"
#             else:
#                 speed += f"{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} hours"
#         return speed

#     def duration_in_seconds(self,task):
#             def day(x):
#                 return x*24
#             def minute(x):
#                 return x/60
#             def second(x):
#                 return x/(60*60)
                
#             if "days" in task:
#                 speed = task.split()
#                 time = speed[2].split(':')
#                 return day(int(speed[0]))+int(time[0])+minute(int(time[1]))+second(int(time[2]))
#             elif "hours" in task:
#                 speed = task.split()
#                 time = speed[0].split(':')
#                 return int(time[0])+minute(int(time[1]))+second(int(time[2]))
#             elif "minutes" in task:
#                 speed = task.split()
#                 time = speed[0].split(':')
#                 return minute(int(time[0]))+second(int(time[1]))
#             elif "seconds" in task:
#                 speed = task.split()
#                 return second(int(speed[0]))
#             else:
#                 return 0

#     def d(self,x,y):
#            return (x/5) * y

#     def research(self):
#         return (
#             + self.d(3,float(self.resources_shared() or 0))
#             + self.d(2,float(self.resources_shared_ratings() or 0))
#             + self.d(2,float(self.resource_ratings_made() or 0))
#             + self.d(5,float(self.experience_shared() or 0))
#             + self.d(4,float(self.experience_shared_ratings() or 0))
#             + self.d(4,float(self.experience_ratings_made() or 0))
#             + self.d(1,float(self.idea_ratings_made() or 0))
#         )

#     def creativity(self):
#         return (
#             + self.d(5,float(self.ideas_num() or 0))
#             + self.d(3,float(self.ideas_avg_ratings() or 0))
#             + self.d(4,float(self.supplements_num() or 0))
#             + self.d(1,float(self.supplements_implemented() or 0))
#             + self.d(4,float(self.realised_ideas() or 0))
#             + self.d(5,float(self.realised_ideas_ratings() or 0))
#             + self.d(1,float(self.realised_ideas_raters() or 0))
#         )

#     def performance(self):
#         if self.tasks_being_done == 0:
#             tasks_being_done = 0
#         else:
#             tasks_being_done = 1
#         return (
#             + self.d(5,float(self.tasks_done) or 0)
#             + self.d(4,float(self.approved_tasks() or 0))
#             - self.d(2,float(self.unapproved_tasks() or 0))
#             + self.d(2,float(self.deadlines_met or 0))
#             - self.d(2,float(self.deadlines_missed or 0))
#             - self.d(3,float(self.tasks_givenup or 0))
#             + self.d(0.4,float(self.avg_tasks_approval() or 0))
#             + self.d(0.1,float(self.progress() or 0))
#             + self.d(0.5,float(self.avg_progress("Done") or 0))
#             - self.d(4,float(self.duration_in_seconds(self.task_speed() or 0)))
#             + self.d(1,float(self.duration_in_seconds(self.total_tasks_duration() or 0)))
#             + self.d(5,float(tasks_being_done or 0))
#             + self.d(1,float(self.tasks_started() or 0))
#             - self.d(1,float(self.tasks_rectified or 0))
#             + self.d(0.3,float(self.avg_project_contribution() or 0))
#             - self.d(5,float(self.duration_in_seconds(self.passed_deadline() or 0)))
#         )

#     def idea_ratings_made(self):
#         return self.rater.all().count()

#     def approvals_made(self):
#         return self.approvals.filter(completion = "Completed").count()

#     def resource_ratings_made(self):
#         return self.ratings.filter(resource__in = Learning.objects.filter(whose = "Not Mine")).count()
        
#     def experience_ratings_made(self):
#         return self.ratings.filter(resource__in = Learning.objects.filter(whose = "Mine")).count()

#     def resources_shared(self):
#         return self.learning.filter(whose = "Not Mine").count()
        
#     def resources_shared_ratings(self):
#         return float(self.learning.filter(whose = "Not Mine").aggregate(Avg("avg_ratings"))["avg_ratings__avg"] or 0)

#     def resources_shared_ratings_num(self):
#         return float(self.learning.filter(whose = "Not Mine").aggregate(Sum("num_ratings"))["num_ratings__sum"] or 0)
        
#     def experience_shared(self):
#         return self.learning.filter(whose = "Mine").count()
        
#     def experience_shared_ratings(self):
#         return float(self.learning.filter(whose = "Mine").aggregate(Avg("avg_ratings"))["avg_ratings__avg"] or 0)

#     def experience_shared_ratings_num(self):
#         return float(self.learning.filter(whose = "Mine").aggregate(Sum("num_ratings"))["num_ratings__sum"] or 0)

#     def realised_ideas(self):
#         realised = ProjectMade.objects.filter(idea__in = self.ideas.all()).count()
#         return realised
        
#     def realised_ideas_ratings(self):
#         realised_ratings = ProjectMade.objects.filter(idea__in = self.ideas.all()).aggregate(Avg("avg_ratings"))
#         return float(realised_ratings['avg_ratings__avg'] or 0)
        
#     def realised_ideas_raters(self):
#         realised_ratings = ProjectMade.objects.filter(idea__in = self.ideas.all()).aggregate(Sum("num_ratings"))
#         return float(realised_ratings['num_ratings__sum'] or 0)

#     def supplements_num(self):
#         return self.supplements.all().count()
        
#     def supplements_implemented(self):
#         return self.supplements.filter(status = "Done").count()

#     def ideas_num(self):
#         return self.ideas.all().count()

#     def ideas_avg_ratings(self):
#         sum = 0
#         for idea in self.ideas.all():
#             sum += idea.avg_ratings
#         if self.ideas.all().count() == 0:
#             return 0
#         else:
#             return sum/self.ideas.all().count()

#     def ideas_num_ratings(self):
#         num = 0
#         for idea in self.ideas.all():
#             num += idea.num_ratings
#         return num

#     def re(self):
#         stage = "Requirements Engineering"
#         return (
#             + self.d(1,float(self.tasks.filter(stage = stage).count() or 0))
#             + self.d(4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).count() or 0))
#             + self.d(2,float(self.tasks.filter(Q(stage = stage) & Q(status = "Being Done")).count() or 0))
#             - self.d(5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Given Up")).count() or 0))
#             + self.d(0.4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("avg_evaluation"))['avg_evaluation__avg'] or 0.0))
#             + self.d(0.1,float(self.tasks.filter(Q(stage = stage)).aggregate(Avg("progress"))['progress__avg'] or 0.0))
#             + self.d(0.5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("progress"))['progress__avg'] or 0.0))
#         )
    
#     def sad(self):
#         stage = "Systems Analysis and Design"
#         return (
#             + self.d(1,float(self.tasks.filter(stage = stage).count() or 0))
#             + self.d(4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).count() or 0))
#             + self.d(2,float(self.tasks.filter(Q(stage = stage) & Q(status = "Being Done")).count() or 0))
#             - self.d(5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Given Up")).count() or 0))
#             + self.d(0.4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("avg_evaluation"))['avg_evaluation__avg'] or 0.0))
#             + self.d(0.1,float(self.tasks.filter(Q(stage = stage)).aggregate(Avg("progress"))['progress__avg'] or 0.0))
#             + self.d(0.5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("progress"))['progress__avg']or 0.0))
#         )

#     def ui(self):
#         stage = "UI/UX Design"
#         return (
#             + self.d(1,float(self.tasks.filter(stage = stage).count() or 0))
#             + self.d(4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).count() or 0))
#             + self.d(2,float(self.tasks.filter(Q(stage = stage) & Q(status = "Being Done")).count() or 0))
#             - self.d(5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Given Up")).count() or 0))
#             + self.d(0.4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("avg_evaluation"))['avg_evaluation__avg'] or 0.0))
#             + self.d(0.1,float(self.tasks.filter(Q(stage = stage)).aggregate(Avg("progress"))['progress__avg'] or 0.0))
#             + self.d(0.5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("progress"))['progress__avg']or 0.0))
#         )
    
#     def dsa(self):
#         stage = "Data Structures and Algorithms"
#         return (
#             + self.d(1,float(self.tasks.filter(stage = stage).count() or 0))
#             + self.d(4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).count() or 0))
#             + self.d(2,float(self.tasks.filter(Q(stage = stage) & Q(status = "Being Done")).count() or 0))
#             - self.d(5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Given Up")).count() or 0))
#             + self.d(0.4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("avg_evaluation"))['avg_evaluation__avg'] or 0.0))
#             + self.d(0.1,float(self.tasks.filter(Q(stage = stage)).aggregate(Avg("progress"))['progress__avg'] or 0.0))
#             + self.d(0.5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("progress"))['progress__avg']or 0.0))
#         )
    
#     def code(self):
#         stage = "Computer Programming and Coding"
#         return (
#             + self.d(1,float(self.tasks.filter(stage = stage).count() or 0))
#             + self.d(4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).count() or 0))
#             + self.d(2,float(self.tasks.filter(Q(stage = stage) & Q(status = "Being Done")).count() or 0))
#             - self.d(5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Given Up")).count() or 0))
#             + self.d(0.4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("avg_evaluation"))['avg_evaluation__avg'] or 0.0))
#             + self.d(0.1,float(self.tasks.filter(Q(stage = stage)).aggregate(Avg("progress"))['progress__avg'] or 0.0))
#             + self.d(0.5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("progress"))['progress__avg']or 0.0))
#         )
    
#     def test(self):
#         stage = "System Testing"
#         return (
#             + self.d(1,float(self.tasks.filter(stage = stage).count() or 0))
#             + self.d(4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).count() or 0))
#             + self.d(2,float(self.tasks.filter(Q(stage = stage) & Q(status = "Being Done")).count() or 0))
#             - self.d(5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Given Up")).count() or 0))
#             + self.d(0.4,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("avg_evaluation"))['avg_evaluation__avg'] or 0.0))
#             + self.d(0.1,float(self.tasks.filter(Q(stage = stage)).aggregate(Avg("progress"))['progress__avg'] or 0.0))
#             + self.d(0.5,float(self.tasks.filter(Q(stage = stage) & Q(status = "Done")).aggregate(Avg("progress"))['progress__avg']or 0.0))
#             + self.d(3,self.approvals_made())
#             + self.d(3,self.tasks_objections_made)
#         )
    
#     def passed_deadline(self):
#         result = self.deadline_excess
#         minutes, seconds = divmod(result.total_seconds(), 60)
#         hours, minutes = divmod(minutes, 60)
#         days, hours = divmod(hours, 24)
#         speed = ""
#         if days == 0:
#             if hours == 0:
#                 if minutes == 0:
#                     speed += f"{str(round(seconds)).rjust(2, '0')} seconds"
#                 else:
#                     speed += f"{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} minutes"
#             else:
#                 speed += f"{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} hours"
#         else:
#             speed += f"{str(round(days)).rjust(2, '0')} days "
#             if hours == 0:
#                 if minutes == 0:
#                     speed += f"{str(round(seconds)).rjust(2, '0')} seconds"
#                 else:
#                     speed += f"{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} minutes"
#             else:
#                 speed += f"{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} hours"
#         return speed
    
#     def avg_project_contribution(self):
#         el_progress = 0
#         el_num = 0
#         for project in ProjectMade.objects.all():
#             progress = 0
#             num = 0
#             for task in self.tasks.filter(idea = project.idea):
#                 progress += task.progress
#                 num += 1
#             if num == 0:
#                 el_progress += 0
#                 el_num += 0
#             else:
#                 el_progress += (progress/num)
#                 el_num += 1
#         if el_num == 0:
#             return 0
#         else:
#             return (el_progress/el_num)

#     def num_project_contribution(self):
#         num = 0
#         for project in ProjectMade.objects.all():
#             for task in self.tasks.filter(idea = project.idea):
#                 num += task.num_progress
#         return num

#     def tasks_started(self):
#         return self.tasks_givenup + self.tasks_being_done + self.tasks_done

#     def task_speed(self):
#         if self.tasks_done == 0:
#             return "infinity"
#         else:
#             result = (self.tasks_duration/self.tasks_done)
#             minutes, seconds = divmod(result.total_seconds(), 60)
#             hours, minutes = divmod(minutes, 60)
#             days, hours = divmod(hours, 24)
#             speed = ""
#         if days == 0:
#             if hours == 0:
#                 if minutes == 0:
#                     speed += f"{str(round(seconds)).rjust(2, '0')} seconds"
#                 else:
#                     speed += f"{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} minutes"
#             else:
#                 speed += f"{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} hours"
#         else:
#             speed += f"{str(round(days)).rjust(2, '0')} days "
#             if hours == 0:
#                 if minutes == 0:
#                     speed += f"{str(round(seconds)).rjust(2, '0')} seconds"
#                 else:
#                     speed += f"{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} minutes"
#             else:
#                 speed += f"{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')} hours"
#         return speed

#     def unapproved_tasks(self):
#         return math.ceil(self.tasks_unapproved)
        
#     def approved_tasks(self):
#         return math.ceil(self.tasks_approved)


#     def avg_tasks_approval(self):
#         avg = 0
#         num = 0
#         for task in self.tasks.all():
#             if task.status == "Done":
#                 avg += task.avg_evaluation
#                 num += 1
#         if num == 0:
#             return 0
#         else:
#             return avg/num
    
#     def num_tasks_approval(self):
#         num = 0
#         for task in self.tasks.all():
#             if task.status == "Done":
#                 num += task.num_evaluation
#         return num

#     def progress(self):
#         tasks = self.tasks.all()
#         num_tasks = self.tasks.all().count()
#         progress = 0
#         for task in tasks:
#             progress += task.progress
#         if num_tasks != 0:
#             progress = progress / num_tasks
#         else:
#             progress = 0
#         return progress

#     def avg_progress(self,status):
#         tasks = self.tasks.filter(status = status)
#         num_tasks = self.tasks.filter(status = status).count()
#         progress = 0
#         for task in tasks:
#             progress += task.progress
#         if num_tasks != 0:
#             progress = progress / num_tasks
#         else:
#             progress = 0
#         return progress


#     def num_progress(self):
#         tasks = self.tasks.all()
#         num = 0
#         for task in tasks:
#             num += task.num_progress
#         return num
    
#     def __str__(self):
#         return f"{self.user.username}"


# class Definition(models.Model):
#     defined_member = models.ForeignKey(Member, related_name="definitions",on_delete=models.CASCADE)
#     defining_member = models.ForeignKey(Member, on_delete=models.CASCADE)
#     definition = models.TextField()

#     def toJSON(self):
#         return json.dumps(self, default=lambda o: o.__dict__, 
#             sort_keys=True, indent=4)

#     def __str__(self):
#         return f"{self.defining_member.user}'s definition of {self.defined_member.user}"

# class Description(models.Model):
#     described_member = models.ForeignKey(Member, related_name="descriptions", on_delete=models.CASCADE)
#     describing_member = models.ForeignKey(Member, on_delete=models.CASCADE)
#     description = models.TextField()

#     def __str__(self):
#         return f"{self.describing_member.user}'s description of {self.described_member.user}"
    

# # class Event(models.Model):
# #     name = models.CharField(max_length=50)
# #     when = models.DateTimeField(auto_now_add=False, auto_now_add=False)
# #     duration = models.DurationField()
# #     description = models.TextField()
# #     members = models.ManyToManyField("Member", related_name="events")

# #     def __str__(self):
# #         when_f = self.when.strftime('%d %B, %Y at %I:%M %p')
# #         return f"You have the {self.name} event on {when_f}"
    

# class Contact_Us(models.Model):
#     topic = models.CharField(max_length=50)
#     message = models.TextField()
#     email = models.CharField(max_length=100)
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.topic} by {self.email}"

# from django.db import models
# from django.db.models.fields.related import ForeignKey
# from Accounts.models import Member
# from datetime import date, datetime, timezone
# from django.utils.timezone import now
# from django.db.models.query_utils import Q

# # Create your models here.

# class IdeaRatings(models.Model):
#     idea = models.ForeignKey("Idea", related_name="ratings", on_delete=models.CASCADE)
#     member = models.ForeignKey(Member, related_name="rater", on_delete=models.CASCADE)
#     ratings = models.FloatField()
#     review = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.idea} by {self.member}"
    

# class Supplements(models.Model):
#     name = models.TextField()
#     idea = models.ForeignKey("Idea", related_name="supplements", on_delete=models.CASCADE)
#     description = models.TextField()
#     member = models.ForeignKey(Member, related_name="supplements", on_delete=models.CASCADE)
#     status = models.CharField(max_length=50, default="Not Done")

#     def __str__(self):
#         return self.name
    

# class Tasks(models.Model):
#     idea = models.ForeignKey("Idea", related_name="tasks", on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     update = models.IntegerField(default=0)
#     version = models.IntegerField(default=1)
#     stage = models.CharField(max_length=100)
#     progress = models.FloatField(default=0)
#     num_progress = models.FloatField(default=0)
#     status = models.CharField(max_length=50,default="Not Done")
#     start_date = models.DateTimeField(default=now)
#     deadline = models.DateTimeField(default=now)
#     member = models.ForeignKey(Member, related_name="tasks", on_delete=models.CASCADE,null=True, blank=True)
#     avg_evaluation = models.FloatField(default=0)
#     num_evaluation = models.FloatField(default=0)
#     link = models.TextField()

#     def __str__(self):
#         return self.name

#     def period(self):
#         today = datetime.now(timezone.utc)
#         if today > self.deadline:
#             return "Time-Up"
#         result = self.deadline - today
#         minutes, seconds = divmod(result.total_seconds(), 60)
#         hours, minutes = divmod(minutes, 60)
#         days, hours = divmod(hours, 24)
#         return f"{str(round(days)).rjust(2, '0')}:{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')}"

#     def time(self):
#         today = datetime.now(timezone.utc)
#         result = self.deadline - today

#         if result.days >= 1:
#             if result.days > 1:
#                 return f"{result.days} days"
#             else:
#                 return f"{result.days} day"
#         elif result.total_seconds()/3600 >=1:
#             if result.total_seconds()/3600 >1:
#                 return f"{int(round(result.total_seconds()/3600,0))} hours"
#             else:
#                 return f"{int(round(result.total_seconds()/3600,0))} hour"
#         elif result.total_seconds()/60 >=1:
#             if result.total_seconds()/60 >1:
#                 return f"{int(round(result.total_seconds()/60,0))} minutes"
#             else:
#                 return f"{int(round(result.total_seconds()/60,0))} minute"
#         elif result.total_seconds() >=1:
#             if result.total_seconds() >1:
#                 return f"{int(round(result.total_seconds(),0))} seconds"
#             else:
#                 return f"{int(round(result.total_seconds(),0))} second"
#         else:
#             return f"Time Up"

#     def duration(self):
#         today = datetime.now(timezone.utc)
#         result = today - self.start_date
#         minutes, seconds = divmod(result.total_seconds(), 60)
#         hours, minutes = divmod(minutes, 60)
#         days, hours = divmod(hours, 24)
#         return f"{str(round(days)).rjust(2, '0')}:{str(round(hours)).rjust(2, '0')}:{str(round(minutes)).rjust(2, '0')}:{str(round(seconds)).rjust(2, '0')}"
        
# class Milestone(models.Model):
#     task = models.ForeignKey("Tasks", related_name="milestones", on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     status = models.CharField(max_length=50,default="Being Done")

#     def __str__(self):
#         return self.name

# class Learning(models.Model):
#     task = models.ForeignKey("Tasks", related_name="learning", on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     form = models.CharField(max_length=50, default="Video")
#     description = models.TextField()
#     whose = models.CharField(max_length=50, default="Not Mine")
#     researcher = models.ForeignKey(Member, related_name="learning", on_delete=models.CASCADE)
#     link = models.TextField()
#     avg_ratings = models.FloatField(default=0)
#     num_ratings = models.FloatField(default=0)
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name
    
# class LearningRatings(models.Model):
#     resource = models.ForeignKey("Learning", related_name="rating", on_delete=models.CASCADE)
#     member = models.ForeignKey(Member, related_name="ratings", on_delete=models.CASCADE)
#     ratings = models.FloatField()
#     review = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.resource} by {self.member}"

# class Reference(models.Model):
#     referring_task = models.ForeignKey("Tasks", related_name="references", on_delete=models.CASCADE)
#     referred_task = models.ForeignKey("Tasks", related_name="tasks", on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.referring_task} refers {self.referred_task}"


# class TaskApproval(models.Model):
#     task = models.ForeignKey("Tasks", related_name="approvals", on_delete=models.CASCADE)
#     member = models.ForeignKey(Member, related_name="approvals", on_delete=models.CASCADE)
#     completion = models.CharField(max_length=50)
#     evaluation = models.FloatField()
#     reasons = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.member.user}'s approval"

# class TaskApprovalReply(models.Model):
#     task_approval = models.ForeignKey("TaskApproval", related_name="replies", on_delete=models.CASCADE)
#     member = models.ForeignKey(Member,related_name="replier", on_delete=models.DO_NOTHING)
#     reply = models.TextField(default="good")
#     date = models.DateTimeField(auto_now_add=True)

# class Idea(models.Model):
#     name = models.CharField(max_length=100)
#     descriptive_name = models.TextField()
#     description = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)
#     idealist = models.ForeignKey(Member, related_name="ideas", on_delete=models.CASCADE)
#     link = models.TextField(default="https://github.com/")
#     avg_ratings = models.FloatField(default=0)
#     num_ratings = models.FloatField(default=0)
        
#     def __str__(self):
#         return f"{self.idealist.user}'s {self.name} idea called {self.name}"

#     def number(self):
#         return self.tasks.all().count()

#     def progress(self):
#         progresses = []
#         tasks = [
#             {
#                 "name":"Requirements Eliciting",
#                 "description":"Clearly list the requirements one by one",
#                 "stage":"Requirements Engineering",
#             },
#             {
#                 "name":"Data Flow Diagrams",
#                 "description":"Draw DFDs of all the necessary levels",
#                 "stage":"Systems Analysis and Design",
#             },
#             {
#                 "name":"Entity Relationship Diagram",
#                 "description":"Include of the necessary entities",
#                 "stage":"Systems Analysis and Design",
#             },
#             {
#                 "name":"User Experience Design",
#                 "description":"Make the UX feel intuitive to interact with",
#                 "stage":"UI/UX Design",
#             },
#             {
#                 "name":"User Interface Design",
#                 "description":"Make the UI Look attractive to the users",
#                 "stage":"UI/UX Design",
#             },
#             {
#                 "name":"Algorithms",
#                 "description":"write out efficient algorithms for the processes",
#                 "stage":"Data Structures and Algorithms",
#             },
#             {
#                 "name":"Front End Development",
#                 "description":"Bring the UI to life",
#                 "stage":"Computer Programming and Coding",
#             },
#             {
#                 "name":"Back End Development",
#                 "description":"Code out the instructions for the computer to execute",
#                 "stage":"Computer Programming and Coding",
#             },
#             {
#                 "name":"System Test",
#                 "description":"Test if the application works as expected meeting all the goals with no errors in doing so",
#                 "stage":"System Testing",
#             },
#         ]

#         if self.tasks.filter().exists():
#             highest_version = int(self.tasks.all().order_by("-version").first().version)
#         else:
#             highest_version = 1
#         progress = 0
#         num_tasks = len(tasks)
#         for version in range(highest_version):
#             for task in tasks:
#                 if self.tasks.filter(Q(version = version+1) & Q(name = task["name"])).exists():
#                     the_task = self.tasks.filter(Q(version = version+1) & Q(name = task["name"])).order_by("-update").first()
#                     progress += the_task.progress
#             progress = progress / num_tasks
#             progresses.append(progress)
#         return progresses

#     def version(self):
#         if self.tasks.filter().exists():
#             highest_version = int(self.tasks.all().order_by("-version").first().version)
#         else:
#             highest_version = 1
#         return highest_version

#     def num_done(self):
#         return self.tasks.filter(Q(status = "Done") & Q(progress = 100) & Q(avg_evaluation__gte = 80) & Q(num_evaluation__gte = 1)).count()

#     def period(self):
#         today = datetime.now(timezone.utc)
#         result = today - self.date
#         if result.days >= 1:
#             if result.days > 1:
#                 return f"Idealised {result.days} days ago"
#             else:
#                 return f"Idealised {result.days} day ago"
#         elif round(result.total_seconds()/3600,0) >=1:
#             if round(result.total_seconds()/3600,0) >1:
#                 return f"Idealised {int(round(result.total_seconds()/3600,0))} hours ago"
#             else:
#                 return f"Idealised {int(round(result.total_seconds()/3600,0))} hour ago"
#         elif round(result.total_seconds()/60,0) >=1:
#             if round(result.total_seconds()/60,0) >1:
#                 return f"Idealised {int(round(result.total_seconds()/60,0))} minutes ago"
#             else:
#                 return f"Idealised {int(round(result.total_seconds()/60,0))} minute ago"
#         elif round(result.total_seconds(),0) >=1:
#             if round(result.total_seconds(),0) >1:
#                 return f"Idealised {int(round(result.total_seconds(),0))} seconds ago"
#             else:
#                 return f"Idealised {int(round(result.total_seconds(),0))} second ago"
#         else:
#             return f"Idealised just now"
    
    
# class ProjectMade(models.Model):
#     idea = models.OneToOneField("Idea", related_name="project", on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     image = models.ImageField(upload_to="assets/images/")
#     date = models.DateTimeField(auto_now_add=True)
#     avg_ratings = models.FloatField(default=0)
#     num_ratings = models.FloatField(default=0)
#     link = models.TextField()

#     def __str__(self):
#         return self.name

# class ProjectRatings(models.Model):
#     project = models.ForeignKey("ProjectMade", related_name="ratings", on_delete=models.CASCADE)
#     email = models.EmailField(max_length=100)
#     ratings = models.FloatField()
#     review = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.email
    
# class RatingsReply(models.Model):
#     ratings = models.ForeignKey("ProjectRatings", related_name="replies", on_delete=models.CASCADE)
#     member = models.ForeignKey(Member, related_name="replies", on_delete=models.CASCADE)
#     reply = models.TextField()

#     def __str__(self):
#         return self.ratings.email

# class MonthlyTracking(models.Model):
#     date = models.DateField(auto_now=False, auto_now_add=False, default=now)
#     member = models.ForeignKey(Member, related_name="monthly_tracking", on_delete=models.CASCADE)

#     performance = models.FloatField(default=0)
#     tasks_done = models.FloatField(default=0)
#     tasks_approved = models.FloatField(default=0)
#     tasks_unapproved = models.FloatField(default=0)
#     deadlines_beaten = models.FloatField(default=0)
#     deadlines_missed = models.FloatField(default=0)
#     tasks_given_up = models.FloatField(default=0)
#     tasks_deleted = models.FloatField(default=0)

#     avg_tasks_approval = models.FloatField(default=0)
#     num_tasks_approval = models.FloatField(default=0)

#     avg_tasks_progress = models.FloatField(default=0)
#     num_tasks_progress = models.FloatField(default=0)

#     #has two, use tasks_done for speed
#     total_tasks_completion_speed = models.FloatField(default=0)

#     tasks_started = models.FloatField(default=0)
#     tasks_rectified = models.FloatField(default=0)

#     avg_projects_contribution = models.FloatField(default=0)
#     num_projects_contributed = models.FloatField(default=0)

#     total_dealine_excess_time = models.FloatField(default=0)
#     tasks_approvals_made = models.FloatField(default=0)
#     tasks_objections_made = models.FloatField(default=0)

#     requirements_engineering = models.FloatField(default=0)
#     sad = models.FloatField(default=0)
#     ui = models.FloatField(default=0)
#     dsa = models.FloatField(default=0)
#     code = models.FloatField(default=0)
#     test = models.FloatField(default=0)

#     creativity = models.FloatField(default=0)
#     ideas_generated = models.FloatField(default=0)

#     avg_ideas_ratings = models.FloatField(default=0)
#     num_ideas_ratings = models.FloatField(default=0)

#     supplements_made = models.FloatField(default=0)
#     supplements_implemented = models.FloatField(default=0)
#     your_ideas_realised = models.FloatField(default=0)

#     avg_your_ideas_realised_ratings = models.FloatField(default=0)
#     num_your_ideas_realised_raters = models.FloatField(default=0)

#     research = models.FloatField(default=0)
#     resources_shared = models.FloatField(default=0)

#     avg_resources_shared_ratings = models.FloatField(default=0)
#     num_resources_shared_ratings = models.FloatField(default=0)

#     resource_ratings_made = models.FloatField(default=0)
#     experience_shared = models.FloatField(default=0)

#     avg_experience_shared_ratings = models.FloatField(default=0)
#     num_experience_shared_ratings = models.FloatField(default=0)

#     experience_ratings_made = models.FloatField(default=0)
#     ideas_ratings_made = models.FloatField(default=0)

#     def __str__(self):
#         return f"{self.date.strftime('%B %G')} - {self.member.user}"
    
# class Best(models.Model):
#     highest_performance = models.FloatField(default=0)
#     highest_creativity = models.FloatField(default=0)
#     highest_research = models.FloatField(default=0)