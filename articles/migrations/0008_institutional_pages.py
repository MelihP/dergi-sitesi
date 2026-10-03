from django.db import migrations


def create_pages(apps, schema_editor):
    Page = apps.get_model("articles", "SitePage")
    for order, (slug, title) in enumerate([
        ("hakkimizda", "Hakkımızda"),
        ("kunye", "Künye"),
        ("yayin-ilkeleri", "Yayın İlkeleri"),
    ]):
        Page.objects.using(schema_editor.connection.alias).get_or_create(
            slug=slug, defaults={"title": title, "order": order},
        )


class Migration(migrations.Migration):
    dependencies = [("articles", "0007_sitepage")]
    operations = [migrations.RunPython(create_pages, migrations.RunPython.noop)]
