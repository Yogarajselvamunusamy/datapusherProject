from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

 
@api_view(['GET',])
def get_destinations(request, account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        destinations = Destination.objects.filter(account=account)
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def incoming_data(request):
    token = request.headers.get('CL-X-TOKEN')
    if not token:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account = Account.objects.get(app_secret_token=token)
    except Account.DoesNotExist:
        return Response({"error": "Un Authenticate"}, status=status.HTTP_401_UNAUTHORIZED)

    if not request.content_type == 'application/json':
        return Response({"error": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

    destinations = Destination.objects.filter(account=account)
    data = request.data

    for destination in destinations:
        headers = destination.headers
        if destination.http_method.upper() == 'GET':
            response = requests.get(destination.url, headers=headers, params=data)
        else:
            response = requests.request(destination.http_method.upper(), destination.url, headers=headers, json=data)

    return Response({"status": "Data sent to destinations"}, status=status.HTTP_200_OK)








