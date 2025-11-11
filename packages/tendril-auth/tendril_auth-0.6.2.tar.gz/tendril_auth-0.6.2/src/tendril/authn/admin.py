#
#
# ### TODO DEPRECATE
#
# import string
# import secrets
#
# from tendril.config import AUTH_MECHANIZED_USER_DOMAIN
# from tendril.config import AUTH_MECHANIZED_PROVIDER
# from tendril.utils.fsutils import load_provider
# from .scaffold import null_dependency
# from .scaffold import wrap_security
#
# from tendril.utils import log
# logger = log.get_logger(__name__, log.DEBUG)
#
# enabled = False
#
# if not AUTH_MECHANIZED_PROVIDER:
#     logger.warning("AUTH_MECHANIZED_PROVIDER is not set. "
#                    "Support for Mechanized Users will not be available.")
#     MechanizedAuthProvider = None
#     mechanized_provider_name = None
#     swagger_auth_mechanized = null_dependency
#     security_mechanized = null_dependency
#     AuthMechanizedUserModel = None
#
# else:
#     try:
#         MechanizedAuthProvider = load_provider(AUTH_MECHANIZED_PROVIDER, "tendril.authn.providers")
#         mechanized_provider_name = AUTH_MECHANIZED_PROVIDER
#         if MechanizedAuthProvider.supports_mechanized:
#             enabled = True
#         else:
#             logger.critical(f"The configured AUTH_MECHANIZED_PROVIDER '{AUTH_MECHANIZED_PROVIDER}' "
#                             f"does not support mechanized users. Support for Mechanized Users "
#                             f"will not be available.")
#     except ImportError as e:
#         logger.critical(e)
#         raise
#
#     swagger_auth_mechanized = getattr(MechanizedAuthProvider, "swagger_auth", null_dependency)
#     security_mechanized = wrap_security(mechanized_provider_name, MechanizedAuthProvider.security)
#     get_mechanized_provider_user_profile = MechanizedAuthProvider.get_mechanized_user_profile
#     AuthMechanizedUserModel = MechanizedAuthProvider.AuthUserModel
#
#
# def _generate_password(length=32):
#     alphabet = string.ascii_letters + string.digits
#     password = ''.join(secrets.choice(alphabet) for i in range(length))
#     return password
#
#
# def _get_mechanized_user_username(username, prefix):
#     return f'{prefix}-{username}'
#
#
# def _get_mechanized_user_email(username, prefix):
#     return f'{username}@{prefix}.{AUTH_MECHANIZED_USER_DOMAIN}'
#
#
# def _get_mechanized_user_name(username, prefix):
#     return f'{prefix} {username}'
#
#
# def create_mechanized_user(username, prefix, role=None, password=None):
#     if not enabled:
#         raise RuntimeError("Mechanized users are not supported. There is probably no mechanized auth provider configured.")
#     if not password:
#         password = _generate_password()
#     MechanizedAuthProvider.create_user(
#         email=_get_mechanized_user_email(username, prefix),
#         username=_get_mechanized_user_username(username, prefix),
#         name=_get_mechanized_user_name(username, prefix),
#         role=role,
#         password=password, mechanized=True
#     )
#     return password
#
#
# def find_mechanized_user_by_email(email):
#     if not enabled:
#         raise RuntimeError("Mechanized users are not supported. There is probably no mechanized auth provider configured.")
#     return MechanizedAuthProvider.find_user_by_email(email, mechanized=True)
#
#
# def set_mechanized_user_password(user_id, password=None):
#     if not enabled:
#         raise RuntimeError("Mechanized users are not supported. There is probably no mechanized auth provider configured.")
#     if not password:
#         password = _generate_password()
#     MechanizedAuthProvider.set_user_password(user_id, password, mechanized=True)
#     return password
