from django.dispatch import Signal

pre_post = Signal() # args: entry
post_post = Signal() # args: entry