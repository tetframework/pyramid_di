import pytest
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.router import Router
import random
from pyramid.registry import Registry

from pyramid_di import BaseService, RequestScopedBaseService, autowired, service, reify_attr, ApplicationScopedBaseService

from zope.interface import Interface


class IInterfacedService(Interface):
    def something():
        ...


@service(interface=IInterfacedService)
class InterfacedService(ApplicationScopedBaseService):
    def something(self):
        return 'something'


@service()
class GlobalService(ApplicationScopedBaseService):
    def baz(self):
        return 'global'


@service()
class ServiceTwo(ApplicationScopedBaseService):
    global_service_dependency = autowired(GlobalService)
    interfaced_service = autowired(IInterfacedService)

    def bar(self):
        if (self.global_service_dependency.baz() == 'global' and
            self.interfaced_service.something() == 'something'):
            return 'ServiceTwo.bar'


@service(scope='request', name='name_only')
class NamedService(RequestScopedBaseService):
    def foo(self):
        return 'named'


@service(scope='request')
class ServiceOne(RequestScopedBaseService):
    dependency = autowired(ServiceTwo)
    named_dependency = autowired(name='name_only')

    def foo(self):
        return self.dependency.bar()


@pytest.fixture()
def config():
    with Configurator() as config:
        config.include('pyramid_di')
        config.scan_services(__name__)

    return config

@pytest.fixture()
def pyramid_app(config) -> Router:
    return config.make_wsgi_app()


@pytest.fixture()
def pyramid_request(pyramid_app) -> Request:
    wsgi_env = {}
    with pyramid_app.request_context(wsgi_env) as request:
        yield request


class ReifyAttrTest:
    @reify_attr
    def foo(self):
        return 42

    @reify_attr
    def ham(self):
        return random.random()

    spam = ham

def test_service_decorator():
    with pytest.raises(ValueError, match='.*Invalid scope.*'):
        @service(scope='something else')
        class Test:
            pass

    with pytest.warns(DeprecationWarning, match='.*global.*'):
        @service(scope='global')
        class Test:
            pass

    with pytest.warns(DeprecationWarning, match='.*renamed.*'):
        class Test(BaseService):
            pass

    with pytest.warns(DeprecationWarning, match='.*renamed.*'):
        Test(registry=Registry())


def test_reify_attr():
    assert type(ReifyAttrTest.foo) is reify_attr
    rat = ReifyAttrTest()
    assert rat.foo == 42

    ReifyAttrTest.bar = reify_attr(lambda self: 666)
    with pytest.raises(TypeError, match='.*not bound to a named attribute.*') as excinfo:
        rat.bar()

    assert rat.ham is rat.spam


def test_everything(pyramid_request):
    service_one = pyramid_request.find_service(ServiceOne)
    assert service_one.foo() == 'ServiceTwo.bar'
    assert service_one.named_dependency.foo() == 'named'


def test_reregistration_raises_warning(config):
    with pytest.warns(UserWarning, match='.*Double registration of the same service.*'):
        config.register_di_service(InterfacedService, scope='global')
