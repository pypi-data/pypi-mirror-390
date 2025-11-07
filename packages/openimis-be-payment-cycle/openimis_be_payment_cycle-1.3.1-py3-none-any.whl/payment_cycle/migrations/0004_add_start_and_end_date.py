from django.db import migrations, models
import string
import random
import core.fields
from django.utils.translation import gettext_lazy as _
from datetime import date
from calendar import monthrange, month_name


def generate_random_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))


def get_default_date():
    return date(1999, 6, 28)


def get_date(year, month):
    first_day = 1
    _, last_day = monthrange(year, month)
    return date(year, month, first_day), date(year, month, last_day)


def create_code_from_date(apps, schema_editor):
    PaymentCycle = apps.get_model('payment_cycle', 'PaymentCycle')
    for payment_cycle in PaymentCycle.objects.all():
        month_name_string = month_name[payment_cycle.run_month]
        year_month_code = f"{payment_cycle.run_year}-{month_name_string}"

        new_code = year_month_code
        while PaymentCycle.objects.filter(code=new_code).exists():
            new_code = f"{year_month_code}-{generate_random_code()}"

        payment_cycle.code = new_code
        payment_cycle.save()


def set_default_start_end_date_and_status(apps, schema_editor):
    PaymentCycle = apps.get_model('payment_cycle', 'PaymentCycle')

    for payment_cycle in PaymentCycle.objects.all():
        start_date, end_date = get_date(payment_cycle.run_year, payment_cycle.run_month)
        payment_cycle.start_date = start_date
        payment_cycle.end_date = end_date
        payment_cycle.save()


def create_unique_code_historical(apps, schema_editor):
    PaymentCycle = apps.get_model('payment_cycle', 'PaymentCycle')
    HistoricalPaymentCycle = apps.get_model('payment_cycle', 'HistoricalPaymentCycle')

    for payment_cycle in PaymentCycle.objects.all():
        historical_payment_cycles = HistoricalPaymentCycle.objects.filter(id=payment_cycle.id)
        for historical in historical_payment_cycles:
            historical.code = payment_cycle.code
            historical.save()


def set_default_start_end_date_and_status_historical(apps, schema_editor):
    HistoricalPaymentCycle = apps.get_model('payment_cycle', 'HistoricalPaymentCycle')

    for payment_cycle in HistoricalPaymentCycle.objects.all():
        start_date, end_date = get_date(payment_cycle.run_year, payment_cycle.run_month)
        payment_cycle.start_date = start_date
        payment_cycle.end_date = end_date
        payment_cycle.save()


class Migration(migrations.Migration):
    dependencies = [
        ('payment_cycle', '0003_alter_historicalpaymentcycle_date_created_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentcycle',
            name='code',
            field=models.CharField(max_length=255, default=generate_random_code()),
        ),
        migrations.AddField(
            model_name='paymentcycle',
            name='start_date',
            field=core.fields.DateField(default=get_default_date()),
        ),
        migrations.AddField(
            model_name='paymentcycle',
            name='end_date',
            field=core.fields.DateField(default=get_default_date()),
        ),
        migrations.AddField(
            model_name='paymentcycle',
            name='status',
            field=models.CharField(max_length=255, choices=[('PENDING', _('PENDING')), ('ACTIVE', _('ACTIVE')),
                                                            ('SUSPENDED', _('SUSPENDED'))], default='PENDING'),
        ),
        migrations.RunPython(set_default_start_end_date_and_status),
        migrations.RunPython(create_code_from_date),
        # historical
        migrations.AddField(
            model_name='historicalpaymentcycle',
            name='code',
            field=models.CharField(max_length=255, default=generate_random_code()),
        ),
        migrations.AddField(
            model_name='historicalpaymentcycle',
            name='start_date',
            field=core.fields.DateField(default=get_default_date()),
        ),
        migrations.AddField(
            model_name='historicalpaymentcycle',
            name='end_date',
            field=core.fields.DateField(default=get_default_date()),
        ),
        migrations.AddField(
            model_name='historicalpaymentcycle',
            name='status',
            field=models.CharField(max_length=255, choices=[('PENDING', _('PENDING')), ('ACTIVE', _('ACTIVE')),
                                                            ('SUSPENDED', _('SUSPENDED'))], default='PENDING'),
        ),
        migrations.RunPython(set_default_start_end_date_and_status_historical),
        migrations.RunPython(create_unique_code_historical),
    ]
