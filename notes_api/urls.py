from django.urls import path, include, re_path as url
from .views import (
    NoteListApiView,
    NoteDetailApiView,
    ShareNoteView,
    LoginView,
    SignUpView,
    SearchNotesView
)

urlpatterns = [
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('notes/', NoteListApiView.as_view(), name='notes_list'),
    path('notes/<int:id>/', NoteDetailApiView.as_view(), name='note_detail'),
    path('notes/<int:id>/share/', ShareNoteView.as_view(), name='share_note'),
    path('search/', SearchNotesView.as_view(), name='search_notes'),
]