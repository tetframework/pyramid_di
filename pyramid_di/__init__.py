import re
from typing import Type, TypeVar, Any

import venusian
from pyramid.config import Configurator
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from functools import update_wrapper
from pyramid_services import _resolve_iface
import warnings


__version__ = "0.4.1"


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
    context_iface=Interface,
):
    registry = config.registry
    if scope == "global":
        warnings.warn(
            "The use of 'global' as scope parameter is deprecated. Use 'application' instead",
            DeprecationWarning,
        )
        scope = "application"

    if scope == "application":
        # register only once
        real_interface = _resolve_iface(interface)
        if registry.queryUtility(real_interface, name=name) is None:
            ob_instance = service_factory(registry=registry)
            get_service_registry(registry)._register_service(ob_instance, interface)

            registry.registerUtility(ob_instance, real_interface, name=name)

            config.register_service(
                service=ob_instance, iface=interface, context=context_iface, name=name
            )

        else:
            warnings.warn(
                f"Double registration of the same service {interface}"
                f" with name {name!r} attempted"
            )

    else:
        # noinspection PyUnusedLocal
        def wrapped_factory(context, request):
            return service_factory(request=request)

        config.register_service_factory(
            wrapped_factory, interface, context_iface, name=name
        )


_NOT_SET = object()


def service(interface=None, *, name="", context_iface=Interface, scope=_NOT_SET):

    if scope not in {"global", "application", "request", _NOT_SET}:
        raise ValueError(
            f"Invalid scope {scope}, must be either 'application' or 'request'"
        )

    if scope == "global":
        warnings.warn(
            "The use of 'global' as scope parameter is deprecated. Use 'application' instead",
            DeprecationWarning,
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

            actual_scope = scope
            if actual_scope is _NOT_SET:
                actual_scope = getattr(ob, "__pyramid_di_scope__", None)
                if actual_scope is None:
                    raise TypeError(f"Cannot infer service scope for {ob}")

                if actual_scope not in {"application", "request"}:
                    raise TypeError(
                        f"{ob} has invalid scope {actual_scope}, must be either 'application' or 'request'"
                    )

            config.register_di_service(
                ob,
                name=service_name,
                interface=iface,
                context_iface=context_iface,
                scope=actual_scope,
            )

        venusian.attach(wrapped, callback, category="pyramid_di.service")
        return wrapped

    return service_decorator


T = TypeVar("T", bound=object)


def autowired(interface: Type[T] = Interface, name: str = "") -> T:
    def getter(self) -> T:
        if hasattr(self, "request"):
            # the context-specific services wouldn't work anyway, so do it this way
            return self.request.find_service(interface, None, name)

        return self.registry.getUtility(_resolve_iface(interface), name)

    return reify_attr(getter)


class ApplicationScopedBaseService(object):
    """
    A convenience base class for application-scoped services.
    """

    __pyramid_di_scope__ = "application"

    registry: "pyramid.registry.Registry"

    def __init__(self, *, registry: "pyramid.registry.Registry", **kw):
        self.registry = registry
        super(ApplicationScopedBaseService, self).__init__(**kw)


class BaseService(ApplicationScopedBaseService):
    def __init__(self, **kw):
        warnings.warn(
            "BaseService has been renamed to ApplicationScopedBaseService",
            DeprecationWarning,
            2,
        )
        super(BaseService, self).__init__(**kw)

    def __init_subclass__(self):
        warnings.warn(
            "BaseService has been renamed to ApplicationScopedBaseService",
            DeprecationWarning,
            2,
        )


class RequestScopedBaseService(object):
    """
    A convenience class for request-scoped services.
    """

    __pyramid_di_scope__ = "request"

    request: "pyramid.request.Request"
    registry: "pyramid.registry.Registry"
    context: Any

    def __init__(self, *, request: "pyramid.request.Request", **kw):
        self.request = request
        self.context = getattr(request, "context", None)
        self.registry = request.registry
        super(RequestScopedBaseService, self).__init__(**kw)


def scan_services(config, *a, **kw):
    kw["categories"] = ("pyramid_di.service",)
    return config.scan(*a, **kw)


def includeme(config):
    config.include("pyramid_services")
    config.add_directive("scan_services", scan_services)
    config.add_directive("register_di_service", register_di_service)
    get_service_registry(config.registry)
