from django.db import migrations
from django.utils.translation import activate
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def forwards_func(apps, schema_editor):
    MyModel = apps.get_model('governanceplatform', 'Regulator')
    MyModelTranslation = apps.get_model('governanceplatform', 'RegulatorTranslation')
    activate('en')

    for object in MyModel.objects.all():
        MyModelTranslation.objects.create(
            master_id=object.pk,
            language_code=settings.LANGUAGE_CODE,
            name=object.name,
            full_name=object.full_name,
            description=object.description,
        )


def backwards_func(apps, schema_editor):
    MyModel = apps.get_model('governanceplatform', 'Regulator')
    MyModelTranslation = apps.get_model('governanceplatform', 'RegulatorTranslation')

    for object in MyModel.objects.all():
        translation = _get_translation(object, MyModelTranslation)
        object.name = translation.name
        object.full_name = translation.full_name
        object.description = translation.description
        object.save()   # Note this only calls Model.save()


def _get_translation(object, MyModelTranslation):
    translations = MyModelTranslation.objects.filter(master_id=object.pk)
    try:
        # Try default translation
        return translations.get(language_code=settings.LANGUAGE_CODE)
    except ObjectDoesNotExist:
        try:
            # Try default language
            return translations.get(language_code=settings.PARLER_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            # Maybe the object was translated only in a specific language?
            # Hope there is a single translation
            return translations.get()


class Migration(migrations.Migration):

    dependencies = [
        ('governanceplatform', '0011_remove_regulator_description_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
