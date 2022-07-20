import logging
import os
import unittest
from importlib import import_module
from unittest import mock

from anysearch import (
    ELASTICSEARCH,
    OPENSEARCH,
    _import_module,
    check_if_package_is_installed,
    detect_search_backend,
    get_installed_packages,
)

LOGGER = logging.getLogger(__name__)


def MovedModule(*args):
    """Moved module."""
    return args


def MovedAttribute(*args):
    """Moved attribute."""
    return args


SEARCH_DSL_MOVED_MODULES = [
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
]

SEARCH_DSL_MOVED_ATTRIBUTES_TYPE_SHORTCUTS = [
    # .analysis
    MovedAttribute("analyzer", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("char_filter", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("normalizer", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("token_filter", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("tokenizer", "elasticsearch_dsl", "opensearch_dsl"),
]
SEARCH_DSL_MOVED_ATTRIBUTES = [
    # .
    # MovedAttribute("__version__", "elasticsearch_dsl", "opensearch_dsl"),
    # MovedAttribute("connections", "elasticsearch_dsl", "opensearch_dsl"),  # Probably remove
    # .aggs
    MovedAttribute("A", "elasticsearch_dsl", "opensearch_dsl"),
    # .analysis
    # MovedAttribute("analyzer", "elasticsearch_dsl", "opensearch_dsl"),
    # MovedAttribute("char_filter", "elasticsearch_dsl", "opensearch_dsl"),
    # MovedAttribute("normalizer", "elasticsearch_dsl", "opensearch_dsl"),
    # MovedAttribute("token_filter", "elasticsearch_dsl", "opensearch_dsl"),
    # MovedAttribute("tokenizer", "elasticsearch_dsl", "opensearch_dsl"),
    # .document
    MovedAttribute("Document", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("InnerDoc", "elasticsearch_dsl", "opensearch_dsl"),
    MovedAttribute("MetaField", "elasticsearch_dsl", "opensearch_dsl"),
    # .exceptions
    # MovedAttribute(
    #     "ElasticsearchDslException", "elasticsearch_dsl", "opensearch_dsl"
    # ),
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
    MovedAttribute("SparseVector", "elasticsearch_dsl", "opensearch_dsl"),
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
]

DJANGO_SEARCH_DSL_MOVED_MODULES = [
    # **********************************************
    # **************** Moved modules ***************
    # **********************************************
    # django_elasticsearch_dsl/django_opensearch_dsl
    MovedModule("apps", "django_elasticsearch_dsl", "django_opensearch_dsl"),
    MovedModule(
        "documents", "django_elasticsearch_dsl", "django_opensearch_dsl"
    ),
    MovedModule(
        "exceptions", "django_elasticsearch_dsl", "django_opensearch_dsl"
    ),
    MovedModule("fields", "django_elasticsearch_dsl", "django_opensearch_dsl"),
    # MovedModule("indices", "django_elasticsearch_dsl", "django_opensearch_dsl"),
    # MovedModule("models", "django_elasticsearch_dsl", "django_opensearch_dsl"),
    MovedModule(
        "registries", "django_elasticsearch_dsl", "django_opensearch_dsl"
    ),
    MovedModule("search", "django_elasticsearch_dsl", "django_opensearch_dsl"),
    MovedModule("signals", "django_elasticsearch_dsl", "django_opensearch_dsl"),
]

DJANGO_SEARCH_DSL_MOVED_ATTRIBUTES = [
    # **********************************************
    # *************** Moved attributes *************
    # **********************************************
    MovedAttribute(
        "Document", "django_elasticsearch_dsl", "django_opensearch_dsl"
    ),
    # MovedAttribute("Index", "django_elasticsearch_dsl", "django_opensearch_dsl"),
]


class AnySearchBaseTestCase(unittest.TestCase):
    def _assert_expected_module_path(self, attr, package, name):
        """Check that the expected path is found."""
        self.assertEqual(attr.__name__, f"{package}.{name}")

    def _assert_expected_attribute_path(self, attr, package, name):
        """Check that the expected path is found."""
        self.assertEqual(attr.__name__, name)
        self.assertTrue(attr.__module__.startswith(package))

    def _assert_expected_attribute_path_type_shortcut(
        self, attr, package, name
    ):
        """Check that the expected path is found."""
        self.assertTrue(attr.__module__.startswith(package))

    def _check_expected_module_path(self, attr, package, name):
        """Check that the expected path is found."""
        if attr.__name__ != f"{package}.{name}":
            LOGGER.exception(f"Fail: {attr.__name__} != {package}.{name}")
        else:
            LOGGER.exception(f"Pass: {attr.__name__} == {package}.{name}")

    def _check_expected_attribute_path(self, attr, package, name):
        """Check that the expected path is found."""
        if attr.__name__ != name:
            LOGGER.exception(f"Fail: {attr.__name__} != {name}")
        else:
            LOGGER.exception(f"Pass: {attr.__name__} == {name}")

    def _test_module_moved_attributes(self, module, name, package):
        with self.subTest(f"name: {name}, package: {package}"):
            module_path = f"anysearch.{module}"
            _module = import_module(module_path)
            attr = getattr(_module, name)
            self._assert_expected_attribute_path(attr, package, name)
            # self._check_expected_attribute_path(attr, package, name)

    def _test_module_moved_attributes_type_shortcuts(
        self, module, name, package
    ):
        with self.subTest(f"name: {name}, package: {package}"):
            module_path = f"anysearch.{module}"
            _module = import_module(module_path)
            attr = getattr(_module, name)
            self._assert_expected_attribute_path_type_shortcut(
                attr, package, name
            )
            # self._check_expected_attribute_path(attr, package, name)

    def _test_module_moved_modules(self, module, name, package):
        with self.subTest(f"name: {name}, package: {package}"):
            module_path = f"anysearch.{module}"
            _module = import_module(module_path)
            attr = getattr(_module, name)
            self._assert_expected_module_path(attr, package, name)
            # self._check_expected_module_path(attr, package, name)


class SearchDSLTestCase(AnySearchBaseTestCase):
    """Test search DSL."""

    def _test_moved_attributes(self, name, package):
        self._test_module_moved_attributes("search_dsl", name, package)

    def _test_moved_attributes_type_shortcuts(self, name, package):
        self._test_module_moved_attributes_type_shortcuts(
            "search_dsl", name, package
        )

    def _test_moved_modules(self, name, package):
        self._test_module_moved_modules("search_dsl", name, package)

    # **************************************************
    # ****************** opensearch-dsl ****************
    # **************************************************
    @mock.patch.dict("os.environ", {"ANYSEARCH_PREFERRED_BACKEND": OPENSEARCH})
    @unittest.skipIf(
        detect_search_backend() != OPENSEARCH,
        "Skipped, because opensearch-dsl is not installed.",
    )
    def test_opensearch_dsl_moved_attributes(self):
        """Test OpenSearch-DSL."""
        for name, _, package in SEARCH_DSL_MOVED_ATTRIBUTES:
            self._test_moved_attributes(name, package)

    @mock.patch.dict("os.environ", {"ANYSEARCH_PREFERRED_BACKEND": OPENSEARCH})
    @unittest.skipIf(
        detect_search_backend() != OPENSEARCH,
        "Skipped, because opensearch-dsl is not installed.",
    )
    def test_opensearch_dsl_moved_attributes_type_shortcuts(self):
        """Test OpenSearch-DSL."""
        for name, _, package in SEARCH_DSL_MOVED_ATTRIBUTES_TYPE_SHORTCUTS:
            self._test_moved_attributes_type_shortcuts(name, package)

    @mock.patch.dict("os.environ", {"ANYSEARCH_PREFERRED_BACKEND": OPENSEARCH})
    @unittest.skipIf(
        detect_search_backend() != OPENSEARCH,
        "Skipped, because opensearch-dsl is not installed.",
    )
    def test_opensearch_dsl_moved_modules(self):
        """Test OpenSearch-DSL."""
        for name, _, package in SEARCH_DSL_MOVED_MODULES:
            self._test_moved_modules(name, package)

    # **************************************************
    # **************** elasticsearch-dsl ***************
    # **************************************************

    @mock.patch.dict(
        "os.environ", {"ANYSEARCH_PREFERRED_BACKEND": ELASTICSEARCH}
    )
    @unittest.skipIf(
        detect_search_backend() != ELASTICSEARCH,
        "Skipped, because elasticsearch-dsl is not installed.",
    )
    def test_elasticsearch_dsl_moved_attributes(self):
        """Test Elasticsearch-DSL."""
        for name, package, _ in SEARCH_DSL_MOVED_ATTRIBUTES:
            self._test_moved_attributes(name, package)

    @mock.patch.dict(
        "os.environ", {"ANYSEARCH_PREFERRED_BACKEND": ELASTICSEARCH}
    )
    @unittest.skipIf(
        detect_search_backend() != ELASTICSEARCH,
        "Skipped, because elasticsearch-dsl is not installed.",
    )
    def test_elasticsearch_dsl_moved_attributes_type_shortcuts(self):
        """Test OpenSearch-DSL."""
        for name, package, _ in SEARCH_DSL_MOVED_ATTRIBUTES_TYPE_SHORTCUTS:
            self._test_moved_attributes_type_shortcuts(name, package)

    @mock.patch.dict(
        "os.environ", {"ANYSEARCH_PREFERRED_BACKEND": ELASTICSEARCH}
    )
    @unittest.skipIf(
        detect_search_backend() != ELASTICSEARCH,
        "Skipped, because elasticsearch-dsl is not installed.",
    )
    def test_elasticsearch_dsl_moved_modules(self):
        """Test Elasticsearch-DSL."""
        for name, package, _ in SEARCH_DSL_MOVED_MODULES:
            self._test_moved_modules(name, package)


class DjangoSearchDSLTestCase(AnySearchBaseTestCase):
    """Test Django search DSL."""

    def _test_moved_attributes(self, name, package):
        self._test_module_moved_attributes("django_search_dsl", name, package)

    def _test_moved_attributes_type_shortcuts(self, name, package):
        self._test_module_moved_attributes_type_shortcuts(
            "django_search_dsl", name, package
        )

    def _test_moved_modules(self, name, package):
        self._test_module_moved_modules("django_search_dsl", name, package)

    # **************************************************
    # **************** django-opensearch-dsl ***********
    # **************************************************

    @mock.patch.dict("os.environ", {"ANYSEARCH_PREFERRED_BACKEND": OPENSEARCH})
    @unittest.skipIf(
        detect_search_backend() != OPENSEARCH,
        "Skipped, because opensearch-dsl is not installed.",
    )
    def test_django_opensearch_dsl_moved_attributes(self):
        """Test Django-OpenSearch-DSL."""
        for name, _, package in DJANGO_SEARCH_DSL_MOVED_ATTRIBUTES:
            self._test_moved_attributes(name, package)

    @mock.patch.dict("os.environ", {"ANYSEARCH_PREFERRED_BACKEND": OPENSEARCH})
    @unittest.skipIf(
        detect_search_backend() != OPENSEARCH,
        "Skipped, because opensearch-dsl is not installed.",
    )
    def test_django_opensearch_dsl_moved_modules(self):
        """Test Django-OpenSearch-DSL."""
        for name, _, package in DJANGO_SEARCH_DSL_MOVED_MODULES:
            self._test_moved_modules(name, package)

    # **************************************************
    # ************** django-elasticsearch-dsl **********
    # **************************************************

    @mock.patch.dict(
        "os.environ", {"ANYSEARCH_PREFERRED_BACKEND": ELASTICSEARCH}
    )
    @unittest.skipIf(
        detect_search_backend() != ELASTICSEARCH,
        "Skipped, because opensearch-dsl is not installed.",
    )
    def test_django_elasticsearch_dsl_moved_attributes(self):
        """Test Django-OpenSearch-DSL."""
        name = "Document"
        package = "django_elasticsearch_dsl"
        module = "django_search_dsl"
        with self.subTest(f"name: {name}, package: {package}"):
            module_path = f"anysearch.{module}"
            _module = import_module(module_path)
            attr = getattr(_module, name)
            self._assert_expected_attribute_path(attr, package, "DocType")

    @mock.patch.dict(
        "os.environ", {"ANYSEARCH_PREFERRED_BACKEND": ELASTICSEARCH}
    )
    @unittest.skipIf(
        detect_search_backend() != ELASTICSEARCH,
        "Skipped, because opensearch-dsl is not installed.",
    )
    def test_django_elasticsearch_dsl_moved_modules(self):
        """Test Django-OpenSearch-DSL."""
        for name, package, _ in DJANGO_SEARCH_DSL_MOVED_MODULES:
            self._test_moved_modules(name, package)


class AnySearchTestCase(unittest.TestCase):
    """Test AnySearch helpers."""

    def test_detect_search_backend(self):
        with mock.patch.dict(
            "os.environ", {"ANYSEARCH_PREFERRED_BACKEND": ELASTICSEARCH}
        ):
            self.assertEqual(detect_search_backend(), ELASTICSEARCH)
        with mock.patch.dict(
            "os.environ", {"ANYSEARCH_PREFERRED_BACKEND": OPENSEARCH}
        ):
            self.assertEqual(detect_search_backend(), OPENSEARCH)
