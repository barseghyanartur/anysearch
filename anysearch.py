"""
Compatibility library for smooth support of Elasticsearch and
OpenSearch packages (including *search-dsl).
The concept and some parts of the code have been snatched from the famous `six`
package.
"""
import logging
import os
import subprocess
import sys
import types
from importlib.util import spec_from_loader
from typing import Set

__title__ = "anysearch"
__version__ = "0.2.2"
__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2022 Artur Barseghyan"
__license__ = "MIT"

LOGGER = logging.getLogger(__name__)


def get_installed_packages() -> Set[str]:
    """Get installed packages.

    :return: Set of installed packages.
    """
    try:
        reqs = subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
        installed_packages = set(
            [r.decode().split("==")[0] for r in reqs.split()]
        )
        return installed_packages
    except subprocess.CalledProcessError:
        LOGGER.exception("Please install pip3 before running this script.")
        return set()


def check_if_package_is_installed(
    package_name, installed_packages: Set[str] = None
) -> bool:
    """Check if a package is installed.

    :param package_name: Package name.
    :param installed_packages: Set of installed packages.
    :return: True if package is installed, False otherwise.
    """
    if not installed_packages:
        installed_packages = get_installed_packages()
    return package_name in installed_packages


ELASTICSEARCH = "Elasticsearch"
OPENSEARCH = "OpenSearch"


def detect_search_backend():
    """Detect the search backend."""
    env_var = os.environ.get("ANYSEARCH_PREFERRED_BACKEND")
    if env_var == ELASTICSEARCH:
        return ELASTICSEARCH
    elif env_var == OPENSEARCH:
        return OPENSEARCH
    else:
        if check_if_package_is_installed("opensearch-dsl"):
            return OPENSEARCH
        elif check_if_package_is_installed("elasticsearch-dsl"):
            return ELASTICSEARCH

    raise Exception(
        "You should either set `ANYSEARCH_BACKEND` env var to `elasticsearch` "
        "or `opensearch` or install a combination of (1) `elasticsearch`, "
        "`elasticsearch-dsl` or (2) "
        "`opensearch-py`, `opensearch-dsl`."
    )


SEARCH_BACKEND = detect_search_backend()
IS_ELASTICSEARCH = SEARCH_BACKEND == ELASTICSEARCH
IS_OPENSEARCH = SEARCH_BACKEND == OPENSEARCH


def _import_module(name):
    """Import module, returning the module after the last dot."""
    __import__(name)
    return sys.modules[name]


class _LazyDescr(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, tp):
        result = self._resolve()
        setattr(obj, self.name, result)  # Invokes __set__.
        try:
            # This is a bit ugly, but it avoids running this again by
            # removing this descriptor.
            delattr(obj.__class__, self.name)
        except AttributeError:
            pass
        return result


class MovedModule(_LazyDescr):
    def __init__(self, name, old, new=None):
        super(MovedModule, self).__init__(name)
        if IS_OPENSEARCH:
            if new is None:
                new = name
            self.mod = new
        else:
            self.mod = old

    def _resolve(self):
        return _import_module(self.mod)

    def __getattr__(self, attr):
        _module = self._resolve()
        value = getattr(_module, attr)
        setattr(self, attr, value)
        return value


class _LazyModule(types.ModuleType):
    def __init__(self, name):
        super(_LazyModule, self).__init__(name)
        self.__doc__ = self.__class__.__doc__

    def __dir__(self):
        attrs = ["__doc__", "__name__"]
        attrs += [__attr.name for __attr in self._moved_attributes]
        return attrs

    # Subclasses should override this
    _moved_attributes = []


class MovedAttribute(_LazyDescr):
    def __init__(self, name, old_mod, new_mod, old_attr=None, new_attr=None):
        super(MovedAttribute, self).__init__(name)
        if IS_OPENSEARCH:
            if new_mod is None:
                new_mod = name
            self.mod = new_mod
            if new_attr is None:
                if old_attr is None:
                    new_attr = name
                else:
                    new_attr = old_attr
            self.attr = new_attr
        else:
            self.mod = old_mod
            if old_attr is None:
                old_attr = name
            self.attr = old_attr

    def _resolve(self):
        module = _import_module(self.mod)
        return getattr(module, self.attr)


class _AnySearchMetaPathImporter(object):

    """
    A meta path importer to import anysearch.search, anysearch.search_dsl,
    and its submodules.
    This class implements a PEP302 finder and loader. It should be compatible
    with Python 2.5 and all existing versions of Python3.
    """

    def __init__(self, module_name):
        self.name = module_name
        self.known_modules = {}

    def _add_module(self, mod, *fullnames):
        for fullname in fullnames:
            self.known_modules[self.name + "." + fullname] = mod

    def _get_module(self, fullname):
        return self.known_modules[self.name + "." + fullname]

    def find_module(self, fullname, path=None):
        if fullname in self.known_modules:
            return self
        return None

    def find_spec(self, fullname, path, target=None):
        if fullname in self.known_modules:
            return spec_from_loader(fullname, self)
        return None

    def __get_module(self, fullname):
        try:
            return self.known_modules[fullname]
        except KeyError:
            raise ImportError("This loader does not know module " + fullname)

    def load_module(self, fullname):
        try:
            # in case of a reload
            return sys.modules[fullname]
        except KeyError:
            pass
        mod = self.__get_module(fullname)
        if isinstance(mod, MovedModule):
            mod = mod._resolve()
        else:
            mod.__loader__ = self
        sys.modules[fullname] = mod
        return mod

    def is_package(self, fullname):
        """
        Return true, if the named module is a package.
        We need this method to get correct spec objects with
        Python 3.4 (see PEP451)
        """
        return hasattr(self.__get_module(fullname), "__path__")

    def get_code(self, fullname):
        """Return None
        Required, if is_package is implemented"""
        self.__get_module(fullname)  # eventually raises ImportError
        return None

    get_source = get_code  # same as get_code

    def create_module(self, spec):
        return self.load_module(spec.name)

    def exec_module(self, module):
        pass


_importer = _AnySearchMetaPathImporter(__name__)

# **************************************************
# ****************** Search ************************
# **************************************************


class _SearchMovedItems(_LazyModule):

    """Lazy loading of search objects"""

    __path__ = []  # mark as package


_search_moved_attributes = [
    # elasticsearch/opensearch
    # **********************************************
    # **************** Moved modules ***************
    # **********************************************
    # .
    MovedModule("client", "elasticsearch", "opensearchpy"),
    MovedModule("compat", "elasticsearch", "opensearchpy"),
    MovedModule("exceptions", "elasticsearch", "opensearchpy"),
    MovedModule("serializer", "elasticsearch", "opensearchpy"),
    MovedModule("transport", "elasticsearch", "opensearchpy"),
    MovedModule("helpers", "elasticsearch", "opensearchpy"),
    # As attributes of the module.
    MovedAttribute("client", "elasticsearch", "opensearchpy"),
    MovedAttribute("compat", "elasticsearch", "opensearchpy"),
    MovedAttribute("exceptions", "elasticsearch", "opensearchpy"),
    MovedAttribute("serializer", "elasticsearch", "opensearchpy"),
    MovedAttribute("transport", "elasticsearch", "opensearchpy"),
    MovedAttribute("helpers", "elasticsearch", "opensearchpy"),
    MovedAttribute("bulk", "elasticsearch.helpers", "opensearchpy.helpers"),
    MovedAttribute(
        "parallel_bulk", "elasticsearch.helpers", "opensearchpy.helpers"
    ),
    # **********************************************
    # ************* Moved attributes ***************
    # **********************************************
    # .
    MovedAttribute("__version__", "elasticsearch", "opensearchpy"),
    MovedAttribute(
        "AnySearch",
        "elasticsearch",
        "opensearchpy",
        "Elasticsearch",
        "OpenSearch",
    ),
    MovedAttribute("Transport", "elasticsearch", "opensearchpy"),
    MovedAttribute("ConnectionPool", "elasticsearch", "opensearchpy"),
    MovedAttribute("ConnectionSelector", "elasticsearch", "opensearchpy"),
    MovedAttribute("RoundRobinSelector", "elasticsearch", "opensearchpy"),
    MovedAttribute("JSONSerializer", "elasticsearch", "opensearchpy"),
    MovedAttribute("Connection", "elasticsearch", "opensearchpy"),
    MovedAttribute("RequestsHttpConnection", "elasticsearch", "opensearchpy"),
    MovedAttribute("Urllib3HttpConnection", "elasticsearch", "opensearchpy"),
    MovedAttribute("ImproperlyConfigured", "elasticsearch", "opensearchpy"),
    MovedAttribute(
        "AnySearchException",
        "elasticsearch",
        "opensearchpy",
        "ElasticsearchException",
        "OpenSearchException",
    ),
    MovedAttribute("SerializationError", "elasticsearch", "opensearchpy"),
    MovedAttribute("TransportError", "elasticsearch", "opensearchpy"),
    MovedAttribute("NotFoundError", "elasticsearch", "opensearchpy"),
    MovedAttribute("ConflictError", "elasticsearch", "opensearchpy"),
    MovedAttribute("RequestError", "elasticsearch", "opensearchpy"),
    MovedAttribute("ConnectionError", "elasticsearch", "opensearchpy"),
    MovedAttribute("SSLError", "elasticsearch", "opensearchpy"),
    MovedAttribute("ConnectionTimeout", "elasticsearch", "opensearchpy"),
    MovedAttribute("AuthenticationException", "elasticsearch", "opensearchpy"),
    MovedAttribute("AuthorizationException", "elasticsearch", "opensearchpy"),
    MovedAttribute(
        "AnySearchDeprecationWarning",
        "elasticsearch",
        "opensearchpy",
        "ElasticsearchDeprecationWarning",
        "OpenSearchDeprecationWarning",
    ),
]

for _search_attr in _search_moved_attributes:
    setattr(_SearchMovedItems, _search_attr.name, _search_attr)
    if isinstance(_search_attr, MovedModule):
        _importer._add_module(_search_attr, "search." + _search_attr.name)

try:
    del _search_attr
except NameError:
    pass

_SearchMovedItems._moved_attributes = _search_moved_attributes

search = _SearchMovedItems(__name__ + ".search")
_importer._add_module(search, "search")

# **************************************************
# **************************************************
# ****************** Search-DSL ********************
# **************************************************
# **************************************************


class _SearchDSLMovedItems(_LazyModule):

    """Lazy loading of search_dsl objects"""

    __path__ = []  # mark as package


_search_dsl_moved_attributes = [
    # elasticsearch_dsl/opensearch_dsl
    # **********************************************
    # **************** Moved modules ***************
    # **********************************************
    MovedModule("aggs", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("analysis", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("connections", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("document", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("exceptions", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("faceted_search", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("field", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("function", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("index", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("mapping", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("query", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("search", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("serializer", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("update_by_query", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("utils", "elasticsearch_dsl", "opensearch_dsl"),
    MovedModule("wrappers", "elasticsearch_dsl", "opensearch_dsl"),
    # Again, but now as attributes of the module.
    MovedAttribute("aggs", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("analysis", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("connections", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("document", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("exceptions", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("faceted_search", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("field", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("function", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("index", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("mapping", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("query", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("search", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("serializer", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("update_by_query", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("utils", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("wrappers", "elasticsearch_dsl", "opensearch_dsl"),
    # **********************************************
    # ************* Moved attributes ***************
    # **********************************************
    # .
    MovedAttribute("__version__", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("connections", "elasticsearch_dsl", "opensearch_dsl"),
    # .aggs
    MovedAttribute("A", "elasticsearch_dsl", "opensearch_dsl"),
    # .analysis
    MovedAttribute("analyzer", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("char_filter", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("normalizer", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("token_filter", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("tokenizer", "elasticsearch_dsl", "opensearch_dsl"),
    # .document
    MovedAttribute("Document", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("InnerDoc", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("MetaField", "elasticsearch_dsl", "opensearch_dsl"),
    # .exceptions
    MovedAttribute(
        "AnySearchDslException",
        "elasticsearch_dsl",
        "opensearch_dsl",
        "ElasticsearchDslException",
        "OpenSearchDslException",
    ),
    MovedAttribute("IllegalOperation", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("UnknownDslObject", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute(
        "ValidationException", "elasticsearch_dsl", "opensearch_dsl"
    ),
    # .faceted_search
    MovedAttribute("DateHistogramFacet", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Facet", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("FacetedResponse", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("FacetedSearch", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("HistogramFacet", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("NestedFacet", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("RangeFacet", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("TermsFacet", "elasticsearch_dsl", "opensearch_dsl"),
    # .field
    MovedAttribute("Binary", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Boolean", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Byte", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Completion", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("CustomField", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Date", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("DateRange", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("DenseVector", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Double", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("DoubleRange", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Field", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Float", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("FloatRange", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("GeoPoint", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("GeoShape", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("HalfFloat", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Integer", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("IntegerRange", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Ip", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("IpRange", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Join", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Keyword", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Long", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("LongRange", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Murmur3", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Nested", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Object", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Percolator", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("RangeField", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("RankFeature", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("RankFeatures", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("ScaledFloat", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("SearchAsYouType", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Short", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("SparseVector", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Text", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("TokenCount", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("construct_field", "elasticsearch_dsl", "opensearch_dsl"),
    # .function
    MovedAttribute("SF", "elasticsearch_dsl", "opensearch_dsl"),
    # .index
    MovedAttribute("Index", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("IndexTemplate", "elasticsearch_dsl", "opensearch_dsl"),
    # .mapping
    MovedAttribute("Mapping", "elasticsearch_dsl", "opensearch_dsl"),
    # .query
    MovedAttribute("Q", "elasticsearch_dsl.query", "opensearch_dsl.query"),
    # .search
    MovedAttribute("MultiSearch", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("Search", "elasticsearch_dsl", "opensearch_dsl"),
    # .update_by_query
    MovedAttribute("UpdateByQuery", "elasticsearch_dsl", "opensearch_dsl"),
    # .utils
    MovedAttribute(
        "AttrDict", "elasticsearch_dsl.utils", "opensearch_dsl.utils"
    ),
    MovedAttribute(
        "AttrList", "elasticsearch_dsl.utils", "opensearch_dsl.utils"
    ),
    MovedAttribute("DslBase", "elasticsearch_dsl", "opensearch_dsl"),
    # .wrappers
    MovedAttribute("Range", "elasticsearch_dsl", "opensearch_dsl"),
    # **********************************************
    # ********** Additional moved attributes *******
    # **********************************************
    MovedAttribute(
        "AggsProxy", "elasticsearch_dsl.search", "opensearch_dsl.search"
    ),
    MovedAttribute(
        "MoreLikeThis", "elasticsearch_dsl.query", "opensearch_dsl.query"
    ),
    MovedAttribute(
        "add_connection",
        "elasticsearch_dsl.connections",
        "opensearch_dsl.connections",
    ),
    MovedAttribute(
        "remove_connection",
        "elasticsearch_dsl.connections",
        "opensearch_dsl.connections",
    ),
    MovedAttribute(
        "create_connection",
        "elasticsearch_dsl.connections",
        "opensearch_dsl.connections",
    ),
    MovedAttribute(
        "get_connection",
        "elasticsearch_dsl.connections",
        "opensearch_dsl.connections",
    ),
]

for _search_dsl_attr in _search_dsl_moved_attributes:
    setattr(_SearchDSLMovedItems, _search_dsl_attr.name, _search_dsl_attr)
    if isinstance(_search_dsl_attr, MovedModule):
        _importer._add_module(
            _search_dsl_attr, "search_dsl." + _search_dsl_attr.name
        )

try:
    del _search_dsl_attr
except NameError:
    pass


_SearchDSLMovedItems._moved_attributes = _search_dsl_moved_attributes

search_dsl = _SearchDSLMovedItems(__name__ + ".search_dsl")
_importer._add_module(search_dsl, "search_dsl")

# # **************************************************
# # **************************************************
# # ************** Django-Search-DSL *****************
# # **************************************************
# # **************************************************
#
#
# class _DjangoSearchDSLMovedItems(_LazyModule):
#
#     """Lazy loading of django_search_dsl objects"""
#
#     __path__ = []
#
#
# _django_search_dsl_moved_attributes = [
#     # **********************************************
#     # **************** Moved modules ***************
#     # **********************************************
#     # django_elasticsearch_dsl/django_opensearch_dsl
#     MovedModule(
#         "apps", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedModule(
#         "documents", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedModule(
#         "exceptions", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedModule(
#         "fields", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     # MovedModule(
#     #     "indices", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     # ),
#     # MovedModule(
#     #     "models", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     # ),
#     MovedModule(
#         "registries", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedModule(
#         "search", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedModule(
#         "signals", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     # Again, but now as attributes of the module.
#     MovedAttribute(
#         "apps", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedAttribute(
#         "documents", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedAttribute(
#         "exceptions", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedAttribute(
#         "fields", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     # MovedAttribute(
#     #     "indices", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     # ),
#     # MovedAttribute(
#     #     "models", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     # ),
#     MovedAttribute(
#         "registries", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedAttribute(
#         "search", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     MovedAttribute(
#         "signals", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     # **********************************************
#     # *************** Moved attributes *************
#     # **********************************************
#     MovedAttribute(
#         "Document", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     ),
#     # MovedAttribute(
#     #     "Index", "django_elasticsearch_dsl", "django_opensearch_dsl"
#     # ),
#     # **********************************************
#     # ********* Additional moved attributes ********
#     # **********************************************
#     MovedAttribute(
#         "registry",
#         "django_elasticsearch_dsl.registries",
#         "django_opensearch_dsl.registries",
#     ),
#     MovedAttribute(
#         "DjangoAnySearchConfig",
#         "django_elasticsearch_dsl.apps",
#         "django_opensearch_dsl.apps",
#         "DEDConfig",
#         "DODConfig",
#     ),
#     MovedAttribute(
#         "RealTimeSignalProcessor",
#         "django_elasticsearch_dsl.signals",
#         "django_opensearch_dsl.signals",
#     ),
#     MovedAttribute(
#         "BaseSignalProcessor",
#         "django_elasticsearch_dsl.signals",
#         "django_opensearch_dsl.signals",
#     ),
# ]
#
# for _django_search_dsl_attr in _django_search_dsl_moved_attributes:
#     setattr(
#         _DjangoSearchDSLMovedItems,
#         _django_search_dsl_attr.name,
#         _django_search_dsl_attr,
#     )
#     if isinstance(_django_search_dsl_attr, MovedModule):
#         _importer._add_module(
#             _django_search_dsl_attr,
#             "django_search_dsl." + _django_search_dsl_attr.name,
#         )
#
# try:
#     del _django_search_dsl_attr
# except:
#     pass
#
#
# _DjangoSearchDSLMovedItems._moved_attributes = (
#     _django_search_dsl_moved_attributes
# )
#
# django_search_dsl = _DjangoSearchDSLMovedItems(
#     __name__ + ".django_search_dsl"
# )
# _importer._add_module(django_search_dsl, "django_search_dsl")
#
# # **************************************************
# # **************************************************
# # **************************************************
#
# Index = getattr(moves, "Index", None)
#
# if not Index:
#     from copy import deepcopy
#
#     from opensearch_dsl import Index as DSLIndex
#
#     from django_opensearch_dsl.apps import DEDConfig
#     from django_opensearch_dsl.registries import registry
#
#     class Index(DSLIndex):
#         def __init__(self, *args, **kwargs):
#             super(Index, self).__init__(*args, **kwargs)
#             default_index_settings = deepcopy(
#                 DEDConfig.default_index_settings()
#             )
#             self.settings(**default_index_settings)
#
#         def document(self, document):
#             """
#             Extend to register the document in the global document registry
#             """
#             document = super(Index, self).document(document)
#             registry.register_document(document)
#             return document
#
#         doc_type = document
#
#         def __str__(self):
#             return self._name


# Complete the moves implementation.
# This code is at the end of this module to speed up module loading.
# Turn this module into a package.
__path__ = []  # required for PEP 302 and PEP 451
__package__ = __name__  # see PEP 366 @ReservedAssignment
if globals().get("__spec__") is not None:
    __spec__.submodule_search_locations = []  # PEP 451 @UndefinedVariable
# Remove other six meta path importers, since they cause problems. This can
# happen if six is removed from sys.modules and then reloaded. (Setuptools does
# this for some reason.)
if sys.meta_path:
    for i, importer in enumerate(sys.meta_path):
        # Here's some real nastiness: Another "instance" of the six module might
        # be floating around. Therefore, we can't use isinstance() to check for
        # the six meta path importer, since the other six instance will have
        # inserted an importer with different class.
        if (
            type(importer).__name__ == "_AnySearchMetaPathImporter"
            and importer.name == __name__
        ):
            del sys.meta_path[i]
            break
    del i, importer
# Finally, add the importer to the meta path import hook.
sys.meta_path.append(_importer)
