import unittest

from helpers.singletons import es
from helpers.outlier import Outlier

from analyzers.metrics import MetricsAnalyzer

from tests.unit_tests.test_stubs.test_stub_notifier import TestStubNotifier
from tests.unit_tests.test_stubs.test_stub_es import TestStubEs
from tests.unit_tests.utils.test_settings import TestSettings
from tests.unit_tests.utils.dummy_documents_generate import DummyDocumentsGenerate


class TestNotifier(unittest.TestCase):

    def setUp(self):
        self.test_es = TestStubEs()
        self.test_settings = TestSettings()

    def tearDown(self):
        self.test_settings.restore_default_configuration_path()
        self.test_es.restore_es()

    def test_notify_on_outlier_correctly_create_email(self):
        self.test_settings.change_configuration_path("/app/tests/unit_tests/files/notifications_test.conf")
        self.test_notifier = TestStubNotifier()

        doc_generate = DummyDocumentsGenerate()

        # Create outlier
        doc = doc_generate.generate_document()
        outlier = Outlier("dummy type", "dummy reason", "dummy summary", doc)

        # execute notification
        es.notifier.notify_on_outlier(outlier)

        self.assertEqual(len(self.test_notifier.get_list_email()), 1)
        self.test_notifier.restore_notifier()

    def test_email_dict_key(self):
        self.test_settings.change_configuration_path("/app/tests/unit_tests/files/notifications_test.conf")
        self.test_notifier = TestStubNotifier()

        doc_generate = DummyDocumentsGenerate()

        # Create outlier
        doc = doc_generate.generate_document()
        outlier = Outlier("dummy type", "dummy reason", "dummy summary", doc)

        # execute notification
        es.notifier.notify_on_outlier(outlier)

        email_dict = self.test_notifier.get_list_email()[0]
        self.assertEqual(list(email_dict.keys()), ["subject", "body"])
        self.test_notifier.restore_notifier()

    def test_notification_on_outlier_match_metrics(self):
        self.test_settings.change_configuration_path("/app/tests/unit_tests/files/notifications_test.conf")
        self.test_notifier = TestStubNotifier()

        doc_generate = DummyDocumentsGenerate()

        # Create document that's an outlier
        doc = doc_generate.generate_document(user_id=11)
        self.test_es.add_doc(doc)

        analyzer = MetricsAnalyzer("metrics_numerical_value_dummy_test")
        analyzer.evaluate_model()

        self.assertEqual(len(self.test_notifier.get_list_email()), 1)
        self.test_notifier.restore_notifier()

    def test_notification_on_outlier_match_metrics_not_notification_enable(self):
        self.test_settings.change_configuration_path("/app/tests/unit_tests/files/notifications_test.conf")
        self.test_notifier = TestStubNotifier()

        doc_generate = DummyDocumentsGenerate()

        # Create document that's an outlier
        doc = doc_generate.generate_document(user_id=11)
        self.test_es.add_doc(doc)

        analyzer = MetricsAnalyzer("metrics_no_notif_numerical_value_dummy_test")
        analyzer.evaluate_model()

        self.assertEqual(len(self.test_notifier.get_list_email()), 0)
        self.test_notifier.restore_notifier()
