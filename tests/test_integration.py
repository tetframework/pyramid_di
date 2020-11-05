import pytest
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router

from pyramid_di import RequestScopedBaseService, autowired, service


@service(scope='request')
class ServiceTwo(RequestScopedBaseService):
    def bar(self):
        return 'ServiceTwo.bar'


@service(scope='request')
class ServiceOne(RequestScopedBaseService):
    dependency = autowired(ServiceTwo)

    def foo(self):
        return self.dependency.bar()


@pytest.fixture()
def pyramid_app() -> Router:
    with Configurator() as config:
        config.include('pyramid_di')
        config.scan_services(__name__)
    return config.make_wsgi_app()


@pytest.fixture()
def pyramid_request(pyramid_app) -> Request:
    wsgi_env = {}
    with pyramid_app.request_context(wsgi_env) as request:
        yield request


def test_everything(pyramid_request):
    service_one = pyramid_request.find_service(ServiceOne)
    assert service_one.foo() == 'ServiceTwo.bar'
