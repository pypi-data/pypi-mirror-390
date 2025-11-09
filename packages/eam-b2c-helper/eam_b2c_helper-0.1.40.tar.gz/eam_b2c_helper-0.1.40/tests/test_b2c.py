"""This module contains tests for the B2CHelper class in the b2c module."""

from unittest import mock
import dataclasses

from src.eam_b2c_helper.b2c import B2CHelper

# pylint: disable=unused-argument


def mocked_requests_post(*args, **kwargs):
    """Mocked requests.post method for B2CHelper class tests."""
    @dataclasses.dataclass
    class MockResponse:
        """Mocked response object for requests.post method"""
        json_data: dict
        status_code: int

        def json(self):
            """Returns the json data of the response"""
            return self.json_data

    if args[0] == 'https://login.microsoftonline.com/90/oauth2/v2.0/token':
        return MockResponse({"access_token": "eyJ"}, 200)
    if args[0] == 'https://graph.microsoft.com/beta/users':
        return MockResponse(
            {
                "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
                "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd",
                "businessPhones": [],
                "displayName": "Adele Vance",
                "givenName": "Adele",
                "jobTitle": "Product Marketing Manager",
                "mail": "AdeleV@contoso.com",
                "mobilePhone": "+1 425 555 0109",
                "officeLocation": "18/2111",
                "preferredLanguage": "en-US",
                "surname": "Vance",
                "userPrincipalName": "AdeleV@contoso.com"
            },
            201
        )

    return MockResponse(None, 404)


def mocked_requests_patch(*args, **kwargs):
    """Mocked requests.patch method for B2CHelper class tests."""
    @dataclasses.dataclass
    class MockResponse:
        """Mocked response object for requests.patch method"""
        json_data: dict
        status_code: int

        def json(self):
            """Returns the json data of the response"""
            return self.json_data

    if args[0] == 'https://graph.microsoft.com/beta/users/test_id':
        return MockResponse("No Content", 204)

    return MockResponse(None, 404)


def mocked_requests_delete(*args, **kwargs):
    """Mocked requests.delete method for B2CHelper class tests."""
    @dataclasses.dataclass
    class MockResponse:
        """Mocked response object for requests.delete method"""
        json_data: dict
        status_code: int

        def json(self):
            """Returns the json data of the response"""
            return self.json_data

    if args[0] == 'https://graph.microsoft.com/beta/users/test_id':
        return MockResponse("No Content", 204)

    return MockResponse(None, 404)


def mocked_requests_get(*args, **kwargs):
    """Mocked requests.get method for B2CHelper class tests."""
    @dataclasses.dataclass
    class MockResponse:
        """Mocked response object for requests.get method"""
        json_data: dict
        status_code: int

        def json(self):
            """Returns the json data of the response"""
            return self.json_data
    mock_object = {
        'https://graph.microsoft.com/beta/users/test_id': MockResponse(
            {
                "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
                "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd",
                "businessPhones": [],
                "displayName": "Adele Vance",
                "givenName": "Adele",
                "jobTitle": "Product Marketing Manager",
                "mail": "AdeleV@contoso.com",
                "mobilePhone": "+1 425 555 0109",
                "officeLocation": "18/2111",
                "preferredLanguage": "en-US",
                "surname": "Vance",
                "userPrincipalName": "AdeleV@contoso.com"
            },
            201
        ),
        'https://graph.microsoft.com/beta/users_filter_extension': MockResponse(
            {
                '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#users',
                '@odata.nextLink': 'https://graph.microsoft.com/beta/users_filter_extension'
                '?$skiptoken=1',
                'value': [
                    {
                        "displayName": "Conf Room Adams",
                        "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
                    },
                    {
                        "displayName": "MOD Administrator",
                        "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
                    }
                ]
            },
            200
        ),
        'https://graph.microsoft.com/beta/users_filter_extension?$skiptoken=1': MockResponse(
            {
                '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#users',
                'value': [
                    {
                        "displayName": "Conf Room Adams",
                        "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
                    },
                    {
                        "displayName": "MOD Administrator",
                        "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
                    }
                ]
            },
            200
        ),
        "https://graph.microsoft.com/beta/users?$filter=extension_abc_OrganizationID"
        " eq '12345'": MockResponse(
            {
                '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#users',
                'value': [
                    {
                        "displayName": "Conf Room Adams",
                        "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
                    },
                    {
                        "displayName": "MOD Administrator",
                        "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
                    }
                ]
            },
            200
        ),
        "https://graph.microsoft.com/beta/users?$filter=extension_abc_UserRoles"
        " eq 'Test Role'": MockResponse(
            {
                '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#users',
                'value': [
                    {
                        "displayName": "Conf Room Adams",
                        "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
                    },
                    {
                        "displayName": "MOD Administrator",
                        "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
                    }
                ]
            },
            200
        ),
        "https://graph.microsoft.com/beta/users": MockResponse(
            {
                '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#users',
                'value': [
                    {
                        "displayName": "Conf Room Adams",
                        "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0",
                        'mailNickname': 'Daveg_8amsolutions.com#EXT#'
                    },
                    {
                        "displayName": "MOD Administrator",
                        "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e",
                        'mailNickname': 'test@test.com'
                    }
                ]
            },
            200
        )

    }

    if args[0] in mock_object:
        return mock_object[args[0]]
    return MockResponse(None, 404)


TOKEN_REQUEST_DATA = {
    'grant_type': 'client_credentials',
    'user_mgmt_client_id': '12345',
    'scope': 'https://graph.microsoft.com/.default',
    'user_mgmt_client_secret': '678',
    'tenant_id': '90',
    'ext_app_client_id': 'abc'
}

B2C = B2CHelper(TOKEN_REQUEST_DATA)


# Test the get_token method
@mock.patch('requests.post', side_effect=mocked_requests_post)
def test_get_token(mock_post):
    """Test the get_token method of the B2CHelper class."""
    assert B2C.get_token() == 'eyJ'


# # Test the get_auth_header method
@mock.patch('requests.post', side_effect=mocked_requests_post)
def test_get_auth_header(mock_post):
    """Test the get_auth_header method of the B2CHelper class."""
    assert B2C.get_auth_header() == {
        'Authorization': 'Bearer eyJ',
        'Content-type': 'application/json',
    }


# # Test the create_item method
@mock.patch('requests.post', side_effect=mocked_requests_post)
def test_create_item(mock_post):
    """Test the create_item method of the B2CHelper class."""
    assert B2C.create_item(B2C.get_auth_header(), {'key1': 'value1'}).json() == {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users/$entity",
        "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd",
        "businessPhones": [],
        "displayName": "Adele Vance",
        "givenName": "Adele",
        "jobTitle": "Product Marketing Manager",
        "mail": "AdeleV@contoso.com",
        "mobilePhone": "+1 425 555 0109",
        "officeLocation": "18/2111",
        "preferredLanguage": "en-US",
        "surname": "Vance",
        "userPrincipalName": "AdeleV@contoso.com"
    }


# # Test the update_item method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.patch', side_effect=mocked_requests_patch)
def test_update_item(mock_post, mock_patch):
    """Test the update_item method of the B2CHelper class."""
    assert B2C.update_item(
        B2C.get_auth_header(),
        {'passwordProfile': 'testPassword'}, 'test_id').json() == "No Content"


# # Test the delete_item method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.delete', side_effect=mocked_requests_delete)
def test_delete_item(mock_post, mock_delete):
    """Test the delete_item method of the B2CHelper class."""
    assert B2C.delete_item(B2C.get_auth_header(),
                           'test_id').json() == "No Content"


# # Test the get_user method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_get_user(mock_post, mock_get):
    """Test the get_user method of the B2CHelper class."""
    assert B2C.get_user('test_id') == {
        "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd",
        "businessPhones": [],
        "displayName": "Adele Vance",
        "givenName": "Adele",
        "jobTitle": "Product Marketing Manager",
        "mail": "AdeleV@contoso.com",
        "mobilePhone": "+1 425 555 0109",
        "officeLocation": "18/2111",
        "preferredLanguage": "en-US",
        "surname": "Vance",
        "userPrincipalName": "AdeleV@contoso.com"
    }


# # Test the compile_entire_user_list method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_compile_entire_user_list(mock_post, mock_get):
    """Test the compile_entire_user_list method of the B2CHelper class."""
    assert B2C.compile_entire_user_list('_filter_extension') == [
        {
            "displayName": "Conf Room Adams",
            "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
        },
        {
            "displayName": "MOD Administrator",
            "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
        },
        {
            "displayName": "Conf Room Adams",
            "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
        },
        {
            "displayName": "MOD Administrator",
            "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
        }
    ]


# # Test the get_users method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.get', side_effect=mocked_requests_get)
def test_get_users(mock_post, mock_get):
    """Test the get_users method of the B2CHelper class."""
    assert B2C.get_users(company_id=12345) == [
        {
            "displayName": "Conf Room Adams",
            "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
        },
        {
            "displayName": "MOD Administrator",
            "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
        }
    ]
    assert B2C.get_users(company_id=None, role_type='Test Role') == [
        {
            "displayName": "Conf Room Adams",
            "id": "6ea91a8d-e32e-41a1-b7bd-d2d185eed0e0"
        },
        {
            "displayName": "MOD Administrator",
            "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e"
        }
    ]
    assert B2C.get_users() == [
        {
            "displayName": "MOD Administrator",
            "id": "4562bcc8-c436-4f95-b7c0-4f8ce89dca5e",
            'mailNickname': 'test@test.com'
        }
    ]


# # Test the create_user method
@mock.patch('requests.post', side_effect=mocked_requests_post)
def test_create_user(mock_post):
    """Test the create_user method of the B2CHelper class."""
    assert B2C.create_user(
        {
            'key1': 'value1',
            'role': '8amAdmin',
            'firstName': 'Dave',
            'lastName': 'G',
            'email': 'test@test.com',
            'phone': '1234567890',
            'company_id': '12345',
            'sign_up_code': '12345',
            'reset_password': False
        }, 'test_prefix'
    ).status_code == 201


# # Test the create_users method
@mock.patch('requests.post', side_effect=mocked_requests_post)
def test_create_users(mock_post):
    """Test the create_users method of the B2CHelper class."""
    test_list = B2C.create_users([
        {
            'key1': 'value1',
            'role': '8amAdmin',
            'firstName': 'Dave',
            'lastName': 'G',
            'email': 'test@test.com',
            'phone': '1234567890',
            'company_id': '12345',
            'sign_up_code': '12345',
            'reset_password': False
        },
        {
            'key2': 'value2',
            'role': 'Admin',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'test@test.com',
            'phone': '1234567890',
            'company_id': '12345',
            'sign_up_code': '12345',
            'reset_password': True
        }
    ], 'test_prefix')
    for item in test_list:
        assert item.status_code == 201


# Test the update user method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.patch', side_effect=mocked_requests_patch)
def test_update_user(mock_post, mock_patch):
    """Test the update_user method of the B2CHelper class."""
    assert B2C.update_user(
        {
            'id': 'test_id',
            'role': '8amAdmin',
            'firstName': 'Dave',
            'lastName': 'G',
            'email': 'test@test.com',
            'phone': '1234567890',
            'company_id': '12345',
            'sign_up_code': '12345',
            'reset_password': False
        }, 'test_prefix'
    ).status_code == 204

    assert B2C.update_user(
        {
            'id': 'test_id',
            'role': '8amAdmin',
            'firstName': 'Dave',
            'lastName': 'G',
            'email': 'test@test.com',
            'signInType': 'federated',
            'phone': '1234567890',
            'company_id': '12345',
            'sign_up_code': '12345',
            'reset_password': False
        }, 'test_prefix'
    ).status_code == 204


# Test the update_users method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.patch', side_effect=mocked_requests_patch)
def test_update_users(mock_post, mock_patch):
    """Test the update_users method of the B2CHelper class."""
    test_list = B2C.update_users(
        [
            {
                'id': 'test_id',
                'role': '8amAdmin',
                'firstName': 'Dave',
                'lastName': 'G',
                'email': 'test@test.com',
                'phone': '1234567890',
                'company_id': '12345',
                'sign_up_code': '12345',
                'reset_password': False
            },
            {
                'id': 'test_id',
                'role': 'Admin',
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'test@test.com',
                'phone': '1234567890',
                'company_id': '12345',
                'sign_up_code': '12345',
                'reset_password': True
            }
        ],
        'test_prefix'
    )

    for item in test_list:
        assert item.status_code == 204


# Test the delete_user method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.delete', side_effect=mocked_requests_delete)
def test_delete_user(mock_post, mock_delete):
    """Test the delete_user method of the B2CHelper class."""
    assert B2C.delete_user('test_id').status_code == 204


# Test the delete_users method
@mock.patch('requests.post', side_effect=mocked_requests_post)
@mock.patch('requests.delete', side_effect=mocked_requests_delete)
def test_delete_users(mock_post, mock_delete):
    """Test the delete_users method of the B2CHelper class."""
    test_list = B2C.delete_users(['test_id', 'test_id'])
    for item in test_list:
        assert item.status_code == 204
