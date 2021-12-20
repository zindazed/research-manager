# Generated by Django 2.2.12 on 2021-12-19 07:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='folders', to=settings.AUTH_USER_MODEL)),
                ('parentFolder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='childFolders', to='research_app.Folder')),
            ],
        ),
        migrations.CreateModel(
            name='MergedSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('work', models.TextField()),
                ('attachedMergedSummaries', models.ManyToManyField(related_name='linkedMergedSummaries', to='research_app.MergedSummary')),
            ],
        ),
        migrations.CreateModel(
            name='ResearchSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ResearchWork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('work', models.TextField()),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='researchWorks', to='research_app.Folder')),
                ('researcher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='researchWorks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResearchWorkDuplicate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('work', models.TextField()),
                ('originalResearchWork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='researchWorkDuplicates', to='research_app.ResearchWork')),
                ('originalResearchWorkDuplicate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='researchWorkDuplicates', to='research_app.ResearchWorkDuplicate')),
            ],
        ),
        migrations.CreateModel(
            name='ResearchSummaryDuplicate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('work', models.TextField()),
                ('originalResearchSummary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='researchSummaryDuplicates', to='research_app.ResearchSummary')),
                ('originalResearchSummaryDuplicate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='researchSummaryDuplicates', to='research_app.ResearchSummaryDuplicate')),
            ],
        ),
        migrations.AddField(
            model_name='researchsummary',
            name='researchWork',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='researchSummary', to='research_app.ResearchWork'),
        ),
        migrations.CreateModel(
            name='MergedSummaryDuplicate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('work', models.TextField()),
                ('attachedMergedSummary', models.ManyToManyField(related_name='linkedMergedSummaryDuplicates', to='research_app.MergedSummary')),
                ('attachedResearchSummary', models.ManyToManyField(related_name='linkedMergedSummaryDuplicates', to='research_app.ResearchSummary')),
                ('attachedResearchWorks', models.ManyToManyField(related_name='linkedMergedSummaryDuplicates', to='research_app.ResearchWork')),
                ('originalMergedSummary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mergedSummaryDuplicates', to='research_app.MergedSummary')),
            ],
        ),
        migrations.AddField(
            model_name='mergedsummary',
            name='attachedResearchSummaries',
            field=models.ManyToManyField(related_name='linkedMergedSummaries', to='research_app.ResearchSummary'),
        ),
        migrations.AddField(
            model_name='mergedsummary',
            name='attachedResearchWorks',
            field=models.ManyToManyField(related_name='linkedMergedSummaries', to='research_app.ResearchWork'),
        ),
        migrations.AddField(
            model_name='mergedsummary',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mergedSummaries', to='research_app.Folder'),
        ),
        migrations.AddField(
            model_name='mergedsummary',
            name='merger',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mergedSummaries', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('url', models.TextField()),
                ('researchWork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='research_app.ResearchWork')),
                ('researchWorkDuplicate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='research_app.ResearchWorkDuplicate')),
            ],
        ),
    ]