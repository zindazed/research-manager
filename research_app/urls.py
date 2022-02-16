from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name="home"),
    path('youtube/<int:topicId>', views.youtube, name="youtube"),
    path('signup/', views.signUp, name="signup"),
    path('login/', views.logIn, name="login"),
    path('logout/', views.logOut, name="logout"),

    path('addTopic/', views.addTopic, name="addTopic"),
    path('editTopic/', views.editTopic, name="editTopic"),
    path('deleteTopic/', views.deleteTopic, name="deleteTopic"),
    path('search/<int:topicId>', views.search, name="search"),

    path('mergedSearch/<int:topicId>', views.mergedSearch, name="mergedSearch"),
    path('searchHome/', views.searchHome, name="searchHome"),

    path('folder/<int:topicId>', views.folder, name="folder"),
    path('researchWork/<int:topicId>', views.researchWork, name="researchWork"),
    path('editResearch/<int:topicId>', views.editResearch, name="editResearch"),
    path('editWork/<int:mergedSummaryTopicId>', views.editWork, name="editWork"),

    # path('switchMerge/<int:mergedSummaryTopicId>', views.switchMerge, name="switchMerge"),
    
    path('attachWork/<int:mergedSummaryTopicId>', views.attachWork, name="attachWork"),
    path('detachWork/<int:mergedSummaryTopicId>', views.detachWork, name="detachWork"),
    
    # path('duplicateMerge/<int:mergedSummaryTopicId>', views.duplicateMerge, name="duplicateMerge"),

    # path('switchSummary/<int:topicId>', views.switchSummary, name="switchSummary"),
    path('switchResearch/<int:topicId>', views.switchResearch, name="switchResearch"),
    path('switchWork/<int:mergedSummaryTopicId>', views.switchWork, name="switchWork"),
    
    # path('deleteSummary/<int:topicId>', views.deleteSummary, name="deleteSummary"),
    path('deleteResearch/<int:topicId>', views.deleteResearch, name="deleteResearch"),
    # path('researchSummaryDuplicate/<int:duplicateId>', views.researchSummaryDuplicate, name="researchSummaryDuplicate"),
    path('researchWorkDuplicate/<int:duplicateId>', views.researchWorkDuplicate, name="researchWorkDuplicate"),

    path('mergedSummary/<int:topicId>', views.mergedSummary, name="mergedSummary"),
    # path('duplicateSummary/<int:topicId>', views.duplicateSummary, name="duplicateSummary"),
    path('duplicateResearch/<int:topicId>', views.duplicateResearch, name="duplicateResearch"),
    path('moveTopic/', views.moveTopic, name="moveTopic"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)