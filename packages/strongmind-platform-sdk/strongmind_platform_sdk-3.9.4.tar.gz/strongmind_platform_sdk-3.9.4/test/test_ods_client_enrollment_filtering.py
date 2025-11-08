import unittest
import uuid
from typing import Dict

import requests
from faker import Faker
from mockito import when, mock, unstub, verifyStubbedInvocationsAreUsed, verify
from requests import HTTPError

from platform_sdk.clients.identity_client import IdentityServerClient
from platform_sdk.clients.ods_client import OneRosterDataStoreClient
from test.helpers.test_helpers import create_http_error

fake = Faker()


class TestOneRosterDataStoreClientEnrollmentFiltering(unittest.TestCase):
    """Test suite for the get_enrollments_for_class_in_school method in OneRosterDataStoreClient."""

    def tearDown(self) -> None:
        unstub()

    def setUp(self) -> None:
        """Set up test fixtures for each test method."""
        self.key = fake.word()
        self.base_url = f"https://{fake.domain_name()}"
        self.bearer_token = fake.sha256()
        self.identity_client = mock(IdentityServerClient)
        when(self.identity_client).get_token().thenReturn(self.bearer_token)

        # Create both legacy and central clients for testing
        self.one_roster_legacy_client = OneRosterDataStoreClient(
            base_url=self.base_url,
            key=self.key
        )
        self.one_roster_central_client = OneRosterDataStoreClient(
            base_url=self.base_url,
            identity_client=self.identity_client
        )

        # Test data
        self.school_id = fake.uuid4()
        self.class_id = fake.uuid4()
        self.filter_param = "status=active"

        # Mock enrollment response data
        self.mock_enrollment_response = {
            "enrollments": [
                {
                    "sourcedId": fake.uuid4(),
                    "status": "active",
                    "dateLastModified": fake.iso8601(),
                    "role": "student",
                    "beginDate": "2024-01-01",
                    "endDate": "2024-12-31",
                    "primary": "true",
                    "metadata": None,
                    "user": {
                        "sourcedId": fake.uuid4(),
                        "href": f"{self.base_url}/users/{fake.uuid4()}",
                        "type": "user"
                    },
                    "class": {
                        "sourcedId": self.class_id,
                        "href": f"{self.base_url}/classes/{self.class_id}",
                        "type": "class"
                    },
                    "school": {
                        "sourcedId": self.school_id,
                        "href": f"{self.base_url}/orgs/{self.school_id}",
                        "type": "org"
                    }
                }
            ]
        }

    def test_get_enrollments_for_class_in_school_with_legacy_client_success(self):
        """Test successful enrollment retrieval with legacy client (x-functions-key auth)."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id
        )

        # Assert
        verify(requests).get(url=url, headers={'x-functions-key': self.key})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_with_central_client_success(self):
        """Test successful enrollment retrieval with central client (Bearer token auth)."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'Authorization': self.bearer_token}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_central_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id
        )

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).get(url=url, headers={'Authorization': self.bearer_token})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_with_filter_legacy_client(self):
        """Test successful enrollment retrieval with filter parameter using legacy client."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments?filter={self.filter_param}"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id, self.filter_param
        )

        # Assert
        verify(requests).get(url=url, headers={'x-functions-key': self.key})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_with_filter_central_client(self):
        """Test successful enrollment retrieval with filter parameter using central client."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments?filter={self.filter_param}"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'Authorization': self.bearer_token}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_central_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id, self.filter_param
        )

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).get(url=url, headers={'Authorization': self.bearer_token})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_without_filter_legacy_client(self):
        """Test successful enrollment retrieval without filter parameter using legacy client."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id, None
        )

        # Assert
        verify(requests).get(url=url, headers={'x-functions-key': self.key})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_without_filter_central_client(self):
        """Test successful enrollment retrieval without filter parameter using central client."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'Authorization': self.bearer_token}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_central_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id, None
        )

        # Assert
        verifyStubbedInvocationsAreUsed()
        verify(requests).get(url=url, headers={'Authorization': self.bearer_token})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_404_error_legacy_client(self):
        """Test 404 error handling with legacy client when school/class not found."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        error = create_http_error(
            status_code=404,
            error_message='Not Found',
            url=url,
            method='GET'
        )
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act & Assert
        with self.assertRaises(HTTPError) as context:
            self.one_roster_legacy_client.get_enrollments_for_class_in_school(
                self.school_id, self.class_id
            )

        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)
        self.assertEqual(404, context.exception.response.status_code)

    def test_get_enrollments_for_class_in_school_404_error_central_client(self):
        """Test 404 error handling with central client when school/class not found."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        error = create_http_error(
            status_code=404,
            error_message='Not Found',
            url=url,
            method='GET'
        )
        when(requests).get(url=url, headers={'Authorization': self.bearer_token}).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act & Assert
        with self.assertRaises(HTTPError) as context:
            self.one_roster_central_client.get_enrollments_for_class_in_school(
                self.school_id, self.class_id
            )

        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)
        self.assertEqual(404, context.exception.response.status_code)

    def test_get_enrollments_for_class_in_school_500_error_legacy_client(self):
        """Test 500 error handling with legacy client."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        error = create_http_error(
            status_code=500,
            error_message='Internal Server Error',
            url=url,
            method='GET'
        )
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act & Assert
        with self.assertRaises(HTTPError) as context:
            self.one_roster_legacy_client.get_enrollments_for_class_in_school(
                self.school_id, self.class_id
            )

        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)
        self.assertEqual(500, context.exception.response.status_code)

    def test_get_enrollments_for_class_in_school_500_error_central_client(self):
        """Test 500 error handling with central client."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        error = create_http_error(
            status_code=500,
            error_message='Internal Server Error',
            url=url,
            method='GET'
        )
        when(requests).get(url=url, headers={'Authorization': self.bearer_token}).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act & Assert
        with self.assertRaises(HTTPError) as context:
            self.one_roster_central_client.get_enrollments_for_class_in_school(
                self.school_id, self.class_id
            )

        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)
        self.assertEqual(500, context.exception.response.status_code)

    def test_get_enrollments_for_class_in_school_url_construction_with_filter(self):
        """Test URL construction with filter parameter."""
        # Arrange
        custom_filter = "role=student"
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments?filter={custom_filter}"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id, custom_filter
        )

        # Assert
        verify(requests).get(url=url, headers={'x-functions-key': self.key})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_url_construction_without_filter(self):
        """Test URL construction without filter parameter."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id
        )

        # Assert
        verify(requests).get(url=url, headers={'x-functions-key': self.key})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_url_construction_with_empty_filter(self):
        """Test URL construction with empty filter parameter."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id, ""
        )

        # Assert
        verify(requests).get(url=url, headers={'x-functions-key': self.key})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_response_format_validation(self):
        """Test that response format matches expected OneRoster structure."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id
        )

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn('enrollments', result)
        self.assertIsInstance(result['enrollments'], list)

        if result['enrollments']:
            enrollment = result['enrollments'][0]
            required_fields = [
                'sourcedId', 'status', 'dateLastModified', 'role',
                'beginDate', 'endDate', 'primary', 'metadata',
                'user', 'class', 'school'
            ]
            for field in required_fields:
                self.assertIn(field, enrollment)

    def test_get_enrollments_for_class_in_school_with_special_characters_in_ids(self):
        """Test URL construction with special characters in school_id and class_id."""
        # Arrange
        special_school_id = "school-123_test"
        special_class_id = "class-456_test"
        url = f"{self.base_url}/schools/{special_school_id}/classes/{special_class_id}/enrollments"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            special_school_id, special_class_id
        )

        # Assert
        verify(requests).get(url=url, headers={'x-functions-key': self.key})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_with_complex_filter(self):
        """Test URL construction with complex filter parameter."""
        # Arrange
        complex_filter = "status=active AND role=student"
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments?filter={complex_filter}"
        response = mock({'status_code': 200, 'json': lambda: self.mock_enrollment_response})
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(response)
        when(response).raise_for_status()

        # Act
        result = self.one_roster_legacy_client.get_enrollments_for_class_in_school(
            self.school_id, self.class_id, complex_filter
        )

        # Assert
        verify(requests).get(url=url, headers={'x-functions-key': self.key})
        self.assertEqual(result, self.mock_enrollment_response)

    def test_get_enrollments_for_class_in_school_401_unauthorized_legacy_client(self):
        """Test 401 unauthorized error handling with legacy client."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        error = create_http_error(
            status_code=401,
            error_message='Unauthorized',
            url=url,
            method='GET'
        )
        when(requests).get(url=url, headers={'x-functions-key': self.key}).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act & Assert
        with self.assertRaises(HTTPError) as context:
            self.one_roster_legacy_client.get_enrollments_for_class_in_school(
                self.school_id, self.class_id
            )

        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)
        self.assertEqual(401, context.exception.response.status_code)

    def test_get_enrollments_for_class_in_school_401_unauthorized_central_client(self):
        """Test 401 unauthorized error handling with central client."""
        # Arrange
        url = f"{self.base_url}/schools/{self.school_id}/classes/{self.class_id}/enrollments"
        error = create_http_error(
            status_code=401,
            error_message='Unauthorized',
            url=url,
            method='GET'
        )
        when(requests).get(url=url, headers={'Authorization': self.bearer_token}).thenReturn(error.response)
        when(error.response).raise_for_status().thenRaise(error)

        # Act & Assert
        with self.assertRaises(HTTPError) as context:
            self.one_roster_central_client.get_enrollments_for_class_in_school(
                self.school_id, self.class_id
            )

        self.assertEqual('OneRosterDataStore', context.exception.dependency_name)
        self.assertEqual(401, context.exception.response.status_code)


if __name__ == '__main__':
    unittest.main()
