"""
Django views example using SecureKit
"""

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from django.conf import settings

from securekit.crypto.password import hash_password, verify_password
from .models import SecureUser, EncryptedDocument
import json

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    """User registration with secure password hashing"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            
            if not username or not password:
                return JsonResponse({'error': 'Username and password required'}, status=400)
            
            # Check if user exists
            if SecureUser.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            
            # Create user with hashed password
            user = SecureUser.objects.create_user(
                username=username,
                email=email,
                password=password  # Django hashes the password
            )
            
            # Store encrypted PII if provided
            if data.get('social_security'):
                user.social_security = data['social_security']
            
            if data.get('medical_record_number'):
                user.medical_record_number = data['medical_record_number']
            
            user.save()
            
            return JsonResponse({
                'message': 'User registered successfully',
                'user_id': user.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    """User login with password verification"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'message': 'Login successful',
                    'user_id': user.id
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ProfileView(View):
    """Get user profile with encrypted data"""
    
    def get(self, request, user_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            user = SecureUser.objects.get(id=user_id)
            
            # Only allow users to view their own profile
            if request.user != user and not request.user.is_staff:
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            profile_data = {
                'username': user.username,
                'email': user.email,
                'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
                'social_security': user.social_security,  # Will be decrypted automatically
                'medical_record_number': user.medical_record_number,  # Will be decrypted automatically
            }
            
            return JsonResponse(profile_data)
            
        except SecureUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class DocumentView(View):
    """Encrypted document management"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            
            if not title or not content:
                return JsonResponse({'error': 'Title and content required'}, status=400)
            
            document = EncryptedDocument.objects.create(
                title=title,
                content=content  # Will be encrypted automatically
            )
            
            return JsonResponse({
                'message': 'Document created successfully',
                'document_id': document.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get(self, request, document_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            document = EncryptedDocument.objects.get(id=document_id)
            
            return JsonResponse({
                'title': document.title,
                'content': document.content,  # Will be decrypted automatically
                'created_at': document.created_at.isoformat()
            })
            
        except EncryptedDocument.DoesNotExist:
            return JsonResponse({'error': 'Document not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)