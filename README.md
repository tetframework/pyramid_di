pyramid_di
==========

Easier service location and dependency injection for Pyramid.

Usage
-----

Define services:
```python
# my_service_package.py
from pyramid_di import service, RequestScopedBaseService, autowired

@service(scope='request')
class MyService(RequestScopedBaseService):
    def my_method(self):
        return 'foobar'


@service(scope='request')
class AnotherService(RequestScopedBaseService):
    dependency = autowired(MyService)

    def another_method(self):
        return self.dependency.my_method()
```

Setup when creating the Pyramid app:
```python
# Pyramid setup code:
import my_service_package
from pyramid.config import Configurator

with Configurator() as config:
    config.include('pyramid_di')
    config.scan_services(my_service_package)
```


Use in views:
```python
from pyramid_di import autowired
from pyramid.view import view_config
from my_service_package import AnotherService

class MyViews:
    service = autowired(AnotherService)

    def __init__(self, request):
        # self.request is required for autowired to work
        self.request = request

    @view_config(route_name='some_view')
    def some_view(self):
        self.service.another_method()  # 'foobar'

# alternatively, without class-based views:

@view_config(route_name='some_view')
def some_view(request):
    service = request.find_service(AnotherService)
    service.another_method()  # 'foobar'
```

Development
-----------

Dev setup:
```
$ python3 -m venv venv
$ pip install -e '.[dev]'
```

Tests are run with pytest:
```
$ pytest
```