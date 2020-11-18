import re
from typing import Type, TypeVar

import venusian
from pyramid.config import Configurator
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from functools import update_wrapper
from pyramid_services import _resolve_iface

_to_underscores = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")


class reify_attr(object):
    """
    reify_attr is like pyramid reify, but instead of getting the name of the
    attribute from the decorated method, it uses the name of actual attribute,
    by finding it on the class in Python <=3.5, and using the ``__set_name__``
    on Python 3.6.
    """

    names = None

    def __init__(self, wrapped):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self

        if self.names is None:
            raise TypeError(
                f"reify_attr decorating {self.wrapped} not bound to a named attribute!"
            )

        val = self.wrapped(inst)
        for name in self.names:
            setattr(inst, name, val)

        return val

    def __set_name__(self, owner, name):
        if self.names is None:
            self.names = [name]

        else:
            self.names.append(name)


def _underscore(name):
    return _to_underscores.sub(r"_\1", name).lower()


_is_iface_name = re.compile("^I[A-Z].*")


class ServiceRegistry(object):
    def __init__(self):
        self.__services__ = []

    def _register_service(self, instance, interface):
        self.__services__.append((instance, interface))
        name = interface.__name__
        if interface is _resolve_iface(interface) and _is_iface_name.match(name):
            name = name[1:]

        setattr(self, _underscore(name), instance)


def get_service_registry(registry):
    if not hasattr(registry, "services"):
        registry.services = ServiceRegistry()

    return registry.services


def register_di_service(
    config: Configurator,
    service_factory,
    *,
    scope,
    interface=Interface,
    name="",
    context_iface=Interface
):
    registry = config.registry
    if scope == "global":
        # register only once
        if registry.queryUtility(interface, name=name) is None:
            ob_instance = service_factory(registry=registry)
            get_service_registry(registry)._register_service(ob_instance, interface)

            real_interface = _resolve_iface(interface)
            registry.registerUtility(ob_instance, real_interface, name=name)

            config.register_service(
                service=ob_instance, iface=interface, context=context_iface, name=name
            )

        else:
            warn
    else:
        # noinspection PyUnusedLocal
        def wrapped_factory(context, request):
            return service_factory(request=request)

        config.register_service_factory(
            wrapped_factory, interface, context_iface, name=name
        )


def service(interface=None, *, name="", context_iface=Interface, scope):

    if scope not in {"global", "request"}:
        raise ValueError(
            "Invalid scope {}, must be either 'global' or 'request'".format(scope)
        )

    service_name = name

    def service_decorator(wrapped):
        # noinspection PyUnusedLocal,PyShadowingNames
        def callback(scanner, name, ob):
            config = scanner.config

            iface = interface
            if iface is None:
                if service_name:
                    iface = Interface
                else:
                    iface = ob

            config.register_di_service(
                ob,
                name=service_name,
                interface=iface,
                context_iface=context_iface,
                scope=scope,
            )

        venusian.attach(wrapped, callback, category="pyramid_di.service")
        return wrapped

    return service_decorator


T = TypeVar("T", bound=object)


def autowired(interface: Type[T] = Interface, name: str = "") -> T:
    @reify_attr
    def getter(self):
        if hasattr(self, "request"):
            context = getattr(self.request, "context", None)
            return self.request.find_service(interface, context, name)

        return self.registry.getUtility(interface, name)

    return getter


class BaseService(object):
    def __init__(self, **kw):
        try:
            self.registry = kw.pop("registry")
            super(BaseService, self).__init__(**kw)

        except KeyError:
            raise TypeError("Registry to the base business must be provided")


class RequestScopedBaseService(BaseService):
    """
    :type request: pyramid.request.Request
    """

    def __init__(self, **kw):
        try:
            self.request = kw.pop("request")
            kw["registry"] = self.request.registry
            super(RequestScopedBaseService, self).__init__(**kw)

        except KeyError:
            raise TypeError("Request to the base business must be provided")


def scan_services(config, *a, **kw):
    kw["categories"] = ("pyramid_di.service",)
    return config.scan(*a, **kw)


def includeme(config):
    config.include("pyramid_services")
    config.add_directive("scan_services", scan_services)
    config.add_directive("register_di_service", register_di_service)
    get_service_registry(config.registry)
