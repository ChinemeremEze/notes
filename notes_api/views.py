from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions
from .models import Note
from .serializers import NoteSerializer, UserSerializer, CustomTokenObtainPairSerializer
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema



# Create your views here.

class SignUpView(generics.CreateAPIView):
    User = get_user_model()

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "message": "User created successfully."
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)

class NoteListApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''
            GET list of all Notes to the authenticated user
        '''
        # try:
        notes = Note.objects.filter(user = request.user.id)
                
        serializer = NoteSerializer(notes, many=True)

        # Construct custom response data
        response_data = {
            'count': notes.count(),  # Total count of notes
            'results': serializer.data,  # Serialized notes items
            'message': 'List of notes items retrieved successfully.'
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=NoteSerializer,
        responses={201: NoteSerializer},
    )
    def post(self, request):
        '''
            POST a note for the authenticated user
        '''
        
        data = {
            'title': request.data.get('title'),
            'content': request.data.get('content'),
            'user': request.user.id
        }
        serializer = NoteSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteDetailApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, note_id, user_id):
        '''
            Helper method to get the object with given note_id, and user_id
        '''
        try:
            return Note.objects.get(id=note_id, user = user_id)
        except Note.DoesNotExist:
            return None
        
    def get(self, request, id, *args, **kwargs):
        '''
            GET note by ID for the authenticated user.
        '''
        note_instance = self.get_object(id, request.user.id)
        if not note_instance:
            return Response(
                {"res": "Object with note id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = NoteSerializer(note_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=NoteSerializer,
        responses={201: NoteSerializer},
    )
    def put(self, request, id, *args, **kwargs):
        '''
            PUT an existing note by ID for the authenticated user
        '''
        note_instance = self.get_object(id, request.user.id)
        if not note_instance:
            return Response(
                {"res": "Object with note id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        updated_data = {
            'title': request.data.get('title'),
            'content': request.data.get('content'),
        }
        serializer = NoteSerializer(instance = note_instance, data = updated_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, *args, **kwargs):
        '''
            DELETE a note by ID for the authenticated user.
        '''
        note_instance = self.get_object(id, request.user.id)
        if not note_instance:
            return Response(
                {"res": "Object with note id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        note_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_204_NO_CONTENT
        )

class ShareNoteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, note_id, user_id):
        '''
            Helper method to get the object with given note_id, and user_id
        '''
        try:
            return Note.objects.get(id=note_id, user = user_id)
        except Note.DoesNotExist:
            return None
        
    @extend_schema(
        request=NoteSerializer,
        responses={201: NoteSerializer},
    )
    def post(self, request, id, *args, **kwargs):
        '''
            POST a note with another user for the authenticated user.
        '''
        note_instance = self.get_object(id, request.user.id)
        if not note_instance:
            return Response(
                {"res": "Object with note id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_data = {
            'shared_with': request.data.get('username'),
        }
        serializer = NoteSerializer(instance = note_instance, data = updated_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class SearchNotesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''
            SEARCH for notes based on keywords for the authenticated user.
        '''
        query = request.GET.get('q', '')
        # user = request.user
        if query:
            search_vector = SearchVector('title', 'content')
            search_query = SearchQuery(query)
            queryset = Note.objects.annotate(
                search=search_vector
            ).filter(search=search_query)
            
            serializer = NoteSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"detail": "No search query provided."}, status=status.HTTP_400_BAD_REQUEST)
        # if query:
        #     search_vector = SearchVector('title', 'content')
        #     search_query = SearchQuery(query)
        #     notes = Note.objects.annotate(
        #         rank=SearchRank(search_vector, search_query)
        #     ).filter(rank__gte=0.3).filter(
        #         Q(user=user) | Q(shared_with=user)
        #     ).order_by('-rank')
        # else:
        #     notes = Note.objects.none()

        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
