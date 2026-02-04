from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("habits", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="habit",
            name="reward",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Вознаграждение"
            ),
        ),
    ]
