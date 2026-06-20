# Generated manually for crop problem guide detail cards.

from django.db import migrations, models


DEFAULT_GUIDES = [
    {
        'title': 'Pest Management',
        'slug': 'pest-management',
        'icon': 'bi bi-bug',
        'short_summary': 'Get practical guidance for insects, pests, and crop infestations.',
        'description': 'Pest management support helps farmers identify infestation patterns, understand likely crop risk, and take practical steps to reduce pest damage.',
        'symptoms': 'Chewed leaves or stems\nVisible insects, eggs, or larvae\nWilting or stunted plant growth\nPatchy crop damage across the field',
        'prevention_methods': 'Inspect crops frequently during vulnerable stages.\nKeep fields clean and remove heavily affected plant material.\nUse crop rotation and balanced nutrition to improve resilience.',
        'recommended_actions': 'Capture clear photos of affected plants and pests.\nSubmit crop, stage, and infestation details through the support form.\nFollow expert recommendations and monitor the field after action.',
    },
    {
        'title': 'Disease Diagnosis',
        'slug': 'disease-diagnosis',
        'icon': 'bi bi-shield-check',
        'short_summary': 'Upload crop images and receive disease identification support.',
        'description': 'Disease diagnosis support helps farmers report crop symptoms, share images, and receive practical guidance for understanding possible disease issues.',
        'symptoms': 'Leaf spots, lesions, or yellowing\nRotting roots, stems, fruits, or grains\nPowdery growth or unusual patches\nRapid spreading of unhealthy plants',
        'prevention_methods': 'Avoid excess moisture and overcrowding where possible.\nUse healthy seed and disease-aware field hygiene.\nMonitor crops after rain, humidity, or temperature changes.',
        'recommended_actions': 'Upload clear close-up and field-level images.\nDescribe when symptoms started and how quickly they spread.\nWait for expert review before applying major corrective treatments.',
    },
    {
        'title': 'Soil & Nutrients',
        'slug': 'soil-nutrients',
        'icon': 'bi bi-moisture',
        'short_summary': 'Improve soil fertility and crop health through expert recommendations.',
        'description': 'Soil and nutrient support helps farmers understand visible deficiency signs, soil health concerns, and practical steps for improving crop vigor.',
        'symptoms': 'Yellowing, purpling, or pale leaves\nWeak plant growth or poor flowering\nUneven growth across the field\nReduced crop quality or yield performance',
        'prevention_methods': 'Use balanced fertilizer practices based on crop needs.\nMaintain organic matter and proper soil moisture.\nAvoid repeated nutrient imbalance through regular observation.',
        'recommended_actions': 'Share crop stage, fertilizer history, and field photos.\nMention soil type and recent irrigation or rainfall conditions.\nFollow expert nutrient guidance and track plant response.',
    },
]


def seed_guides(apps, schema_editor):
    CropProblemGuide = apps.get_model('farmer_support', 'CropProblemGuide')

    for guide in DEFAULT_GUIDES:
        CropProblemGuide.objects.update_or_create(
            slug=guide['slug'],
            defaults=guide,
        )


def remove_seeded_guides(apps, schema_editor):
    CropProblemGuide = apps.get_model('farmer_support', 'CropProblemGuide')
    CropProblemGuide.objects.filter(
        slug__in=[guide['slug'] for guide in DEFAULT_GUIDES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('farmer_support', '0002_cropproblem_farmer'),
    ]

    operations = [
        migrations.CreateModel(
            name='CropProblemGuide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('icon', models.CharField(default='bi bi-activity', max_length=80)),
                ('short_summary', models.TextField()),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='crop_problem_guides/')),
                ('symptoms', models.TextField(blank=True, help_text='Enter one symptom per line')),
                ('prevention_methods', models.TextField(blank=True, help_text='Enter one prevention method per line')),
                ('recommended_actions', models.TextField(blank=True, help_text='Enter one recommended action per line')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.RunPython(seed_guides, remove_seeded_guides),
    ]
