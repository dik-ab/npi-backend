from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'user-app', 'user_app.urls', name='user_app'),
    host(r'operation-app', 'operation_app.urls', name='operation_app'),
)
