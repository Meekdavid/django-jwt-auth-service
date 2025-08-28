from rest_framework.response import Response
from rest_framework import status as http_status


def success_response(data=None, message="Success", status=200):
    """
    Standard success response format
    """
    response_data = {
        "responseCode": "00",
        "responseDescription": message,
        "data": data
    }
    return Response(response_data, status=status)


def error_response(code="01", message="Error", data=None, status=400):
    """
    Standard error response format
    """
    response_data = {
        "responseCode": code,
        "responseDescription": message,
    }
    if data is not None:
        response_data["data"] = data
    
    return Response(response_data, status=status)


def paginated_response(data, page_info, message="Success", status=200):
    """
    Standard paginated response format
    """
    response_data = {
        "responseCode": "00",
        "responseDescription": message,
        "data": data,
        "pagination": page_info
    }
    return Response(response_data, status=status)
