from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rango.models import Category
from rango.api.v1.serializers import CategoryGetSerializer
from rango.api.v1.serializers import CategoryPostPutSerializer

class CategoryList(APIView):
    def get(self, request, format=None):
        try:
            category_objects = Category.objects.all()
        except:
            return Response({"error": "No Category Objects"}, status=
                            status.HTTP_404_NOT_FOUND)
        serializer = CategoryGetSerializer(category_objects, many=True)
        print(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = CategoryPostPutSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=
                            status.HTTP_400_BAD_REQUEST)

class CategoryDetail(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(id=pk)
        except Category.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategoryGetSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk, format=None):
        category = self.get_object(pk)
        serializer = CategoryPostPutSerializer(category, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_200_OK)