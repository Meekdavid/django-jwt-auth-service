from rest_framework.response import Response

def success_response(data, description="Success", status=200):
    return Response({
        "responseCode": "00",
        "responseDescription": description,
        "data": data
    }, status=status)

def error_response(code, description, data=None, status=400):
    return Response({
        "responseCode": code,
        "responseDescription": description,
        "data": data
    }, status=status)
