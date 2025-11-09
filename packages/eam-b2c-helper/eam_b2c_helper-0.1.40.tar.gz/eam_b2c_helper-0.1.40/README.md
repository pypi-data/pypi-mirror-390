# This package is used as to add data to cosmos db, which is required during onboarding of a client or adding a new vendor to the 8am system.

B2CHelper:



build_user_object():

This function is used to format the user object according to the MS AD schema. It takes the user_details object from the 8am Web App front end, along with extension_id and b2c_prefix (B2C parameters) and returns the formatted user object. The last 4 fields within the the user object are custom fields which use the extension_id to denote as such.



get_token()

This function is used to get the token from the MS AD B2C. It takes the client_id, client_secret, tenant_id, and the scope as parameters and returns the token.



get_auth_header()

This function is used to get the authorization header for the MS AD B2C. It uses the token string returned from the get_token() function and structures it into a Bearer token along with Content-Type header for ease of use.



create_item()

This function is used to add a new user to the MS AD b2C directory. It takes the user object and the auth_header as parameters and returns the response from the MS Graph API.



update_item()

This function is used to update a user in the MS AD B2C directory. It takes the user object and the auth_header as parameters and returns the response from the MS Graph API.



delete_item()

This function is used to delete a user from the MS AD B2C directory. It takes the user object and the auth_header as parameters and returns the response from the MS Graph API.



get_user()

This function is used to get a user from the MS AD B2C directory. It takes the user id as a parameter, removes the @odata.context field and returns the single user object.



compile_entire_user_list()

This function is used to get the entire list of users from the MS AD B2C directory. As a default, the MS Graph API returns 100 users per page, this function will use the @odata.nextLink field to get the next page of users until there are no more pages left. It returns a list of user objects, combined from each successive call made to the MS Graph API. This function uses the argument filter_extension to filter users by either company, user role, or nothing at all (return all users from the directory).



get_users()

This function is used to get a list of users from the MS AD B2C directory. It takes a company id and a user role as optional parameters and returns a list of user objects, possibly filtered by the company and user role. Based off of what parameters are passed, it will call the compile_entire_user_list() function with the appropriate filter_extension. The filter extension is added to the suffix of the MS Graph API call to filter the users.



create_user()

This function is used to create a new user in the MS AD B2C directory. It takes the user_details object from the 8am Web App front end, along with extension_id and b2c_prefix (B2C parameters) and returns the response from the MS Graph API.



create_users()

This function is used to create multiple users in the MS AD B2C directory. It takes a list of user_details objects from the 8am Web App front end, along with extension_id and b2c_prefix (B2C parameters) and returns the response from the MS Graph API.



update_user()

This function is used to update a user in the MS AD B2C directory. It takes the user_details object from the 8am Web App front end, along with extension_id and b2c_prefix (B2C parameters) and returns the response from the MS Graph API.



update_users()

This function is used to update multiple users in the MS AD B2C directory. It takes a list of user_details objects from the 8am Web App front end, along with extension_id and b2c_prefix (B2C parameters) and returns the response from the MS Graph API.



delete_user()

This function is used to delete a user from the MS AD B2C directory. It takes the user_id from the 8am Web App front end and returns the response from the MS Graph API.



delete_users()

This function is used to delete multiple users from the MS AD B2C directory. It takes a list of user_ids from the 8am Web App front end and returns the response from the MS Graph API.



