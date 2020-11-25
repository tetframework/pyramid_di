pyramid_di
==========

Easier service location and dependency injection for Pyramid.

Usage
-----

Define services:

```python
# app/services/__init__.py

from .my import MyService
from .another import AnotherService
```

```python
# app/services/my.py
from pyramid_di import service, RequestScopedBaseService, autowired

@service()
class MyService(RequestScopedBaseService):
    def my_method(self):
        return 'foobar'
```

```python
# app/services/another.py
from pyramid_di import service, RequestScopedBaseService, autowired
from .my import MyService

@service()
class AnotherService(RequestScopedBaseService):
    dependency = autowired(MyService)

    def another_method(self):
        return self.dependency.my_method()
```

Setup when creating the Pyramid app:

```python
# Pyramid setup code:
from pyramid.config import Configurator

with Configurator() as config:
    config.include('pyramid_di')
    config.scan_services('app.services')
```


Use in views:

```python
from pyramid_di import autowired
from pyramid.view import view_config
from my.services import AnotherService

class MyViews:
    service = autowired(AnotherService)

    def __init__(self, request):
        # self.request is required for autowired to work
        self.request = request

    @view_config(route_name='some_view', renderer='json')
    def some_view(self):
        return self.service.another_method()  # 'foobar'

# alternatively, without class-based views:

@view_config(route_name='some_view')
def some_view(request):
    service = request.find_service(AnotherService)
    service.another_method()  # 'foobar'
```

Mocking services for testing
----------------------------

```python3
class MockService:
    def another_method(self):
        return 'mocked'

def test_views():
    request = DummyRequest()
    my_views = MyViews(request)
    my_views.service = MockService()
    assert my_views.some_view() == 'mocked'
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
