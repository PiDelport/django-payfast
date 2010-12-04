from django.dispatch import Signal
notify = Signal(providing_args=['order'])
