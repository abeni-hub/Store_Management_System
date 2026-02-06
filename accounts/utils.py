from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

def my_custom_jwt_response_handler(token, user=None, request=None):
    payload = jwt_payload_handler(user)
    payload['role'] = user.role  # Include the role in the payload
    return {
        'token': jwt_encode_handler(payload),
        'user': user.email,
        'role': user.role
    }
