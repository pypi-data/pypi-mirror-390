# Generated manually for namespace subscription models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SocketConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('socket_id', models.CharField(db_index=True, max_length=255, unique=True)),
                ('connected_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'statezero_socket_connection',
            },
        ),
        migrations.CreateModel(
            name='NamespaceSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(db_index=True, max_length=255)),
                ('namespace', models.JSONField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('connection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='statezero.socketconnection')),
            ],
            options={
                'db_table': 'statezero_namespace_subscription',
            },
        ),
        migrations.AddIndex(
            model_name='socketconnection',
            index=models.Index(fields=['socket_id'], name='statezero_s_socket__a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='socketconnection',
            index=models.Index(fields=['user'], name='statezero_s_user_id_d4e5f6_idx'),
        ),
        migrations.AddIndex(
            model_name='namespacesubscription',
            index=models.Index(fields=['model_name'], name='statezero_n_model_n_g7h8i9_idx'),
        ),
        migrations.AddIndex(
            model_name='namespacesubscription',
            index=models.Index(fields=['connection'], name='statezero_n_connect_j1k2l3_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='namespacesubscription',
            unique_together={('connection', 'model_name', 'namespace')},
        ),
    ]
