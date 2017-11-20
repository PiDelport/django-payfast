from django.db.models.base import ModelBase as DjangoModelBase

# http://djangosnippets.org/snippets/2180/


class ModelBase(DjangoModelBase):
    ''' Decouples 'help_text' attribute from field definition. '''
    def __new__(cls, name, bases, attrs):
        help_text = attrs.pop('HelpText', None)
        new_cls = super(ModelBase, cls).__new__(cls, name, bases, attrs)
        if help_text:
            for field in new_cls._meta.fields:
                field.help_text = getattr(help_text, field.name, field.help_text)
        return new_cls
