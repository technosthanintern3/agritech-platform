# Generated manually for consultation topic detail cards.

from django.db import migrations, models


DEFAULT_TOPICS = [
    {
        'title': 'Crop Planning',
        'slug': 'crop-planning',
        'icon': 'bi bi-flower1',
        'short_summary': 'Recommendations for crop selection, sowing methods, and yield improvement.',
        'detailed_description': 'Crop planning consultation helps farmers choose suitable crops, plan sowing windows, estimate input needs, and improve yield potential with practical season-wise guidance.',
        'benefits': 'Better crop selection\nImproved sowing decisions\nEfficient input planning\nHigher yield potential',
        'use_cases': 'Planning a new crop season\nChoosing crops for local soil and weather\nImproving farm productivity\nReducing avoidable input waste',
        'guidance_steps': 'Share crop, land, soil, and season details.\nAgroSthan reviews the farm context and production goals.\nReceive crop planning guidance with practical next steps.',
    },
    {
        'title': 'Irrigation Guidance',
        'slug': 'irrigation-guidance',
        'icon': 'bi bi-droplet',
        'short_summary': 'Water management practices matched to season and crop requirements.',
        'detailed_description': 'Irrigation guidance supports better water scheduling, moisture management, and irrigation method decisions so farmers can protect crop health while reducing water stress and wastage.',
        'benefits': 'Improved water efficiency\nReduced crop stress\nBetter irrigation scheduling\nPractical guidance by crop stage',
        'use_cases': 'Managing dry-season irrigation\nAdjusting water use after rainfall\nPlanning irrigation for sensitive crop stages\nReducing overwatering or underwatering',
        'guidance_steps': 'Submit crop, field, water source, and season details.\nThe team reviews crop stage and water requirement.\nReceive practical irrigation recommendations.',
    },
    {
        'title': 'Disease Prevention',
        'slug': 'disease-prevention',
        'icon': 'bi bi-shield-check',
        'short_summary': 'Identify crop health issues early and get preventive recommendations.',
        'detailed_description': 'Disease prevention consultation helps farmers understand early warning signs, reduce disease spread, and follow preventive practices before crop losses become severe.',
        'benefits': 'Earlier issue awareness\nReduced disease spread\nPreventive crop care guidance\nBetter protection of yield quality',
        'use_cases': 'Noticing early crop discoloration\nPreparing for disease-prone weather\nPreventing repeated crop infections\nBuilding a crop health routine',
        'guidance_steps': 'Share crop symptoms, field history, and available photos.\nAgroSthan reviews likely risks and prevention needs.\nReceive prevention guidance and recommended next actions.',
    },
]


def seed_topics(apps, schema_editor):
    ConsultationTopic = apps.get_model('consultation', 'ConsultationTopic')

    for topic in DEFAULT_TOPICS:
        ConsultationTopic.objects.update_or_create(
            slug=topic['slug'],
            defaults=topic,
        )


def remove_seeded_topics(apps, schema_editor):
    ConsultationTopic = apps.get_model('consultation', 'ConsultationTopic')
    ConsultationTopic.objects.filter(
        slug__in=[topic['slug'] for topic in DEFAULT_TOPICS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('consultation', '0004_consultationrequest_assigned_consultant_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultationTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('icon', models.CharField(default='bi bi-person-video3', max_length=80)),
                ('short_summary', models.TextField()),
                ('detailed_description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='consultation_topics/')),
                ('benefits', models.TextField(blank=True, help_text='Enter one benefit per line')),
                ('use_cases', models.TextField(blank=True, help_text='Enter one use case per line')),
                ('guidance_steps', models.TextField(blank=True, help_text='Enter one process/guidance step per line')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.RunPython(seed_topics, remove_seeded_topics),
    ]
