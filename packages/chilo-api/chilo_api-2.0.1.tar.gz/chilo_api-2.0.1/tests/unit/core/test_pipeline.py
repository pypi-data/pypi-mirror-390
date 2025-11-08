import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from tests.unit.mocks.core.pipeline import DummyPipeline


class PipelineInterfaceTest(unittest.TestCase):

    def setUp(self):
        self.request = object()
        self.response = object()

    def test_run_request_validation_uses_standard_validator(self):
        validator = Mock()
        pipeline = DummyPipeline(openapi_validate_request=False, validator=validator)
        endpoint = SimpleNamespace(has_requirements=True, requirements={'required_query': ['auth_id']})

        pipeline.run_request_validation(self.request, self.response, endpoint)

        validator.validate_request.assert_called_once_with(self.request, self.response, endpoint.requirements)
        validator.validate_request_with_openapi.assert_not_called()

    def test_run_request_validation_openapi_calls_openapi_validator(self):
        validator = Mock()
        pipeline = DummyPipeline(openapi_validate_request=True, validator=validator)
        endpoint = SimpleNamespace(requirements={'required_query': []})

        pipeline.run_request_validation_openapi(self.request, self.response, endpoint)

        validator.validate_request_with_openapi.assert_called_once_with(self.request, self.response, endpoint.requirements)

    def test_run_response_validation_uses_standard_validator(self):
        validator = Mock()
        pipeline = DummyPipeline(openapi_validate_response=False, validator=validator)
        endpoint = SimpleNamespace(has_required_response=True, requirements={'required_response': 'schema'})

        pipeline.run_response_validation(self.request, self.response, endpoint)

        validator.validate_response.assert_called_once_with(self.request, self.response, endpoint.requirements)
        validator.validate_response_with_openapi.assert_not_called()

    def test_run_response_validation_openapi_calls_openapi_validator(self):
        validator = Mock()
        pipeline = DummyPipeline(openapi_validate_response=True, validator=validator)
        endpoint = SimpleNamespace(requirements={'required_response': 'schema'})

        pipeline.run_response_validation_openapi(self.request, self.response, endpoint)

        validator.validate_response_with_openapi.assert_called_once_with(self.request, self.response, endpoint.requirements)
