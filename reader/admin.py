from django.contrib import admin
from reader.models import * 

# This website doesn't require an admin to manage 

admin.site.index_title = 'iLearn management'
admin.site.site_title = 'iLearn'
admin.site.site_header = 'iLearn'


# admin.site.register(Project)
# admin.site.register(Sources)
# admin.site.register(Note)