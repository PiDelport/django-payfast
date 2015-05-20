# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PayFastOrder'
        db.create_table('payfast_payfastorder', (
            ('m_payment_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pf_payment_id', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True, null=True, blank=True)),
            ('payment_status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('item_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('item_description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('amount_gross', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=2, blank=True)),
            ('amount_fee', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=2, blank=True)),
            ('amount_net', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=15, decimal_places=2, blank=True)),
            ('custom_str1', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('custom_str2', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('custom_str3', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('custom_str4', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('custom_str5', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('custom_int1', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('custom_int2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('custom_int3', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('custom_int4', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('custom_int5', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('name_first', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name_last', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('email_address', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('merchant_id', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('signature', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('request_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('debug_info', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('trusted', self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('payfast', ['PayFastOrder'])


    def backwards(self, orm):
        
        # Deleting model 'PayFastOrder'
        db.delete_table('payfast_payfastorder')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'payfast.payfastorder': {
            'Meta': {'object_name': 'PayFastOrder'},
            'amount_fee': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'amount_gross': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'amount_net': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'custom_int1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'custom_int2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'custom_int3': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'custom_int4': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'custom_int5': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'custom_str1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom_str2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom_str3': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom_str4': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'custom_str5': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'debug_info': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'item_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'item_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'm_payment_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_id': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'name_first': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_last': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'payment_status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'pf_payment_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'request_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'signature': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'trusted': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['payfast']
