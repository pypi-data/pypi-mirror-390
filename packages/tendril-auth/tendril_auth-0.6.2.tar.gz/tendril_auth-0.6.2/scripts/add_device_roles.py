from tendril.authn.providers import auth0

device_users = auth0.get_connection_users('IoT-Device-Credentials')
role = auth0.get_role_id('IoT Device')

auth0.assign_role_to_users(role, device_users)
