from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Folder)
admin.site.register(ResearchWork)
admin.site.register(ResearchWorkDuplicate)
admin.site.register(Link)
admin.site.register(ResearchSummary)
admin.site.register(ResearchSummaryDuplicate)
admin.site.register(MergedSummary)
admin.site.register(MergedSummaryDuplicate)



# admin.site.register(Member)
# admin.site.register(Description)
# admin.site.register(Definition)
# admin.site.register(Contact_Us)
# # admin.site.register(Event)

# admin.site.register(Idea)
# admin.site.register(IdeaRatings)
# admin.site.register(Supplements)
# admin.site.register(Tasks)
# admin.site.register(TaskApproval)
# admin.site.register(TaskApprovalReply)
# admin.site.register(Reference)
# admin.site.register(Milestone)
# admin.site.register(Learning)
# admin.site.register(LearningRatings)
# admin.site.register(ProjectMade)
# admin.site.register(ProjectRatings)
# admin.site.register(RatingsReply)
# admin.site.register(MonthlyTracking)