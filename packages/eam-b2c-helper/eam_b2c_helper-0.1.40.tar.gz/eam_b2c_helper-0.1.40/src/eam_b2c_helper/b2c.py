"""Module providing functionality to interact with Azure AD B2C via the Microsoft Graph API"""

import json
import logging
import requests
import datetime

LOGGER = logging.getLogger("azure")
LOGGER.setLevel(logging.WARN)


def build_local_user_object(user_details: dict, b2c_prefix: str, extension_id: str) -> dict:
    """Builds a user object to be used in the creation or update of a user in Azure AD B2C"""

    if user_details['role'] == '8amAdmin':
        user_details['password'] = 'dailyAdmin!394'
    else:
        user_details['password'] = 'eightam!23'

    try:
        company_name = user_details['companyName']
    except KeyError:
        company_name = 'default'

    # Need to add department and company name to the user object before using 0.1.29
    return {
        "accountEnabled": True,
        "displayName": f"{user_details['firstName']} {user_details['lastName']}",
        "givenName": user_details['firstName'],
        "surname": user_details['lastName'],
        "mail": user_details['email'],
        "department": company_name,
        "companyName": company_name,
        "mailNickname": user_details['firstName'],
        "identities": [
            {
                "issuer": f"{b2c_prefix}.onmicrosoft.com",
                "issuerAssignedId": user_details['email'],
                "signInType": "emailAddress"
            }
        ],
        "passwordProfile": {
            "forceChangePasswordNextSignIn": False,
            "password": user_details['password']
        },
        "mobilePhone": user_details['phone'],
        f"extension_{extension_id}_OrganizationID": user_details['company_id'],
        f"extension_{extension_id}_SignUpCode": user_details['sign_up_code'],
        f"extension_{extension_id}_UserRoles": user_details['role'],
        f"extension_{extension_id}_mustResetPassword": user_details['reset_password']
    }


def build_federated_user_object(user_details: dict, extension_id: str) -> dict:
    """Builds a federated user object to be used in the creation or update of a user in Azure AD B2C"""
    return {
        "accountEnabled": True,
        "displayName": f"{user_details['firstName']} {user_details['lastName']}",
        "mailNickname": user_details['firstName'],
        "otherMails": [user_details['email']],
        "passwordProfile": {
            "forceChangePasswordNextSignIn": False
        },
        "mobilePhone": user_details['phone'],
        f"extension_{extension_id}_OrganizationID": user_details['company_id'],
        f"extension_{extension_id}_SignUpCode": user_details['sign_up_code'],
        f"extension_{extension_id}_UserRoles": user_details['role'],
        f"extension_{extension_id}_mustResetPassword": user_details['reset_password']
    }


def build_user_object(user_details: dict, extension_id: str, b2c_prefix: str) -> dict:
    """Builds a user object to be used in the creation or update of a user in Azure AD B2C"""
    if ('signInType' in user_details) and (user_details['signInType'] == 'federated'):
        return build_federated_user_object(user_details, extension_id)
    else:
        return build_local_user_object(user_details, b2c_prefix, extension_id)


class B2CHelper:
    """Class providing functionality to interact with Azure AD B2C via the Microsoft Graph API"""

    def __init__(self, token_request_data) -> None:
        self.token_request_data = {
            'grant_type': token_request_data['grant_type'],
            'client_id': token_request_data['user_mgmt_client_id'],
            'scope': token_request_data['scope'],
            'client_secret': token_request_data['user_mgmt_client_secret'],
            'b2c_tenant_id': token_request_data['tenant_id'],
            'extension_id': token_request_data['ext_app_client_id']
        }

    def get_token(self) -> str:
        """Gets an access token from Azure AD B2C
        using the token_request_data provided in the constructor."""
        return requests.post(
            f"https://login.microsoftonline.com/"
            f"{self.token_request_data['b2c_tenant_id']}/oauth2/v2.0/token",
            data=self.token_request_data,
            timeout=30).json()['access_token']

    def get_auth_header(self) -> dict:
        """Returns a dictionary containing the authorization header"""
        return {
            'Authorization': f'Bearer {self.get_token()}',
            'Content-type': 'application/json',
        }

    @staticmethod
    def create_item(auth_header: dict, item: dict) -> requests.Response:
        """Creates a user in Azure AD B2C using the provided item and authorization header."""
        return requests.post(
            "https://graph.microsoft.com/beta/users",
            headers=auth_header,
            data=json.dumps(item),
            timeout=30
        )

    @staticmethod
    def update_item(auth_header: dict, item: dict, item_id: str) -> requests.Response:
        """Updates a user in Azure AD B2C using the provided item and authorization header."""
        del item['passwordProfile']
        return requests.patch(
            f"https://graph.microsoft.com/beta/users/{item_id}",
            headers=auth_header,
            data=json.dumps(item),
            timeout=30
        )

    @staticmethod
    def delete_item(auth_header: dict, user_id: dict) -> requests.Response:
        """Deletes a user in Azure AD B2C using the provided user_id and authorization header."""
        return requests.delete(
            f"https://graph.microsoft.com/beta/users/{user_id}",
            headers=auth_header,
            timeout=30
        )

    def get_user(self, user_id: str) -> dict:
        """Gets a user in Azure AD B2C using the provided user_id."""
        user = requests.get(
            f"https://graph.microsoft.com/beta/users/{user_id}", headers=self.get_auth_header(),
            timeout=30
        ).json()

        if 'error' not in user:
            del user["@odata.context"]
        return user

    def get_user_by_email(self, email: str) -> dict:
        """Gets a user in Azure AD B2C using the provided email."""

        return requests.get(
            f"https://graph.microsoft.com/beta/users?$filter=identities/any(c:c/issuerAssignedId eq '{email}' and c/issuer eq 'eightam72045b2ctenant.onmicrosoft.com')", headers=self.get_auth_header(),
            timeout=30
        ).json()

    def compile_entire_user_list(self, filter_extension: str) -> list:
        """Compiles the entire list of users in Azure AD B2C using the provided filter_extension."""
        users = requests.get(
            f"https://graph.microsoft.com/beta/users{filter_extension}",
            headers=self.get_auth_header(),
            timeout=30
        )
        if '@odata.nextLink' in users.json():
            next_link = users.json()["@odata.nextLink"]
        else:
            next_link = None
        return_list = users.json()['value']

        while next_link is not None:
            users_next = requests.get(
                next_link,
                headers=self.get_auth_header(),
                timeout=30
            )

            for user in users_next.json()['value']:
                return_list.append(user)

            if '@odata.nextLink' in users_next.json():
                next_link = users_next.json()["@odata.nextLink"]
            else:
                next_link = None

        # try:
        #     return_list = sorted(
        #         return_list, key=lambda x: x['displayName'].split(' ')[1].lower() if len(x['displayName'].split(' ')) > 1 else x['displayName'].lower())
        # except IndexError:
        #     logging.info('No second word in displayName')
        #     logging.info(return_list)

        return return_list

    def filter_by_branch_id(self, users: list, branch_id: int) -> list:
        """Filters the list of users in Azure AD B2C using the provided branch_id."""
        filtered_users = []
        for user in users:
            if user['identities'][0]['issuerAssignedId'].split('+')[-1].split('@')[0] == str(branch_id):
                filtered_users.append(user)
        return filtered_users

    def get_users(self, company_id: str = None, role_type: str = None, branch_id: int = None) -> list:
        """Gets a list of users in Azure AD B2C using the provided company_id or role_type."""

        if (company_id is not None) and (branch_id is None):
            filter_extension = f"?$filter=" \
                f"extension_{self.token_request_data['extension_id']}_OrganizationID eq '{company_id}'"

            users = self.compile_entire_user_list(filter_extension)
            return users

        if (company_id is not None) and (branch_id is not None):
            filter_extension = f"?$filter=" \
                f"extension_{self.token_request_data['extension_id']}_OrganizationID eq '{company_id}'"

            users = self.compile_entire_user_list(filter_extension)
            users = self.filter_by_branch_id(users, branch_id)
            return users

        if role_type is not None:
            filter_extension = f"?$filter=" \
                f"extension_{self.token_request_data['extension_id']}_UserRoles eq '{role_type}'"
            users = self.compile_entire_user_list(filter_extension)
            return users

        else:
            filter_extension = ''
            users = [
                x for x in self.compile_entire_user_list(filter_extension)
                if x['mailNickname'] != 'Daveg_8amsolutions.com#EXT#'
            ]

        return users

    # Needs branch_id
    def create_user(self, user_details: dict, b2c_prefix: str, branch_id: str = None) -> dict:
        """Creates a user in Azure AD B2C using the provided user_details and b2c_prefix."""

        print('BRANCH ID: %s', branch_id)

        if branch_id is not None:
            user_details['email'] = user_details['email'].split(
                '@')[0] + '+' + branch_id + '@' + user_details['email'].split('@')[1]

        user = build_user_object(
            user_details, self.token_request_data['extension_id'], b2c_prefix)
        return self.create_item(self.get_auth_header(), user)

    # Needs branch_id
    def create_users(self, user_details_list: list, b2c_prefix: str, branch_id: str = None) -> list:
        """Creates a list of users in Azure AD B2C
        using the provided user_details_list and b2c_prefix."""
        auth_header = self.get_auth_header()
        results = []
        for user_detail in user_details_list:
            if branch_id is not None:
                user_detail['email'] = user_detail['email'].split(
                    '@')[0] + '+' + branch_id + '@' + user_detail['email'].split('@')[1]
            user = build_user_object(
                user_detail, self.token_request_data['extension_id'], b2c_prefix)
            results.append(self.create_item(auth_header, user))
        return results

    def update_user(self, user_details: dict, b2c_prefix: str) -> dict:
        """Updates a user in Azure AD B2C using the provided user_details and b2c_prefix."""
        user = build_user_object(
            user_details, self.token_request_data['extension_id'], b2c_prefix)
        return self.update_item(self.get_auth_header(), user, user_details['id'])

    def update_users(self, user_details_list: list, b2c_prefix: str) -> list:
        """Updates a list of users in Azure AD B2C"""
        auth_header = self.get_auth_header()
        results = []
        for user_detail in user_details_list:
            user = build_user_object(
                user_detail, self.token_request_data['extension_id'], b2c_prefix)
            results.append(self.update_item(
                auth_header, user, user_detail['id']))
        return results

    def delete_user(self, user_id: str) -> dict:
        """Deletes a user in Azure AD B2C using the provided user_id."""
        return self.delete_item(self.get_auth_header(), user_id)

    def delete_users(self, user_id_list) -> list:
        """Deletes a list of users in Azure AD B2C using the provided user_id_list."""
        auth_header = self.get_auth_header()
        results = []
        for user_id in user_id_list:
            results.append(self.delete_item(auth_header, user_id))
        return results
