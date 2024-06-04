from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from django.contrib.auth.models import User  # Import the User model
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from .models import CustomUser  # Import your custom user model
from .serializers import SignupSerializer,ChatSerializer
from .models import Chat
from huggingface_hub import InferenceClient
import os
import requests
import logging
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from model.qanoonbot import (
    set_up_openai_key, create_custom_prompt_template, initialize_embeddings,
    load_vector_database, create_conversation_memory, initialize_prompt,
    initialize_llm, create_conversational_retrieval_chain, process_conversation
)

openai_client = set_up_openai_key()
custom_template = create_custom_prompt_template()
embeddings = initialize_embeddings()
db_retriever = load_vector_database(embeddings)
memory = create_conversation_memory()
prompt = initialize_prompt(custom_template, memory)
llm = initialize_llm()
qa = create_conversational_retrieval_chain(llm, memory, db_retriever)

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
headers = {"Authorization": "Bearer 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"}

def home(request):
    return HttpResponse("Welcome to the home page!")

@api_view(['POST'])
def signup(request):
    try:
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data from serializer
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            
            # Check if a user with the provided email already exists
            if CustomUser.objects.filter(email=email).exists():
                return Response({'error': 'Account already exists with this email'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create and save user object
            user = CustomUser.objects.create_user(username=email, email=email, password=password)
            
            # Return success response
            return Response({'message': 'Signup successful'}, status=status.HTTP_201_CREATED)
        else:
            # Return validation error response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Log the exception or return a generic error message
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def user_login(request):
    try:
        # Extract email and password from request data
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Authenticate user
        user = CustomUser.objects.filter(email=email).first()
        
        # Check if user exists and password is correct
        if user is not None and user.check_password(password):
            # Return success response with user details
            return Response({'message': 'Login successful', 'user_id': user.id}, status=status.HTTP_200_OK)
        else:
            # Return error response for invalid credentials
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Log the exception or return a generic error message
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def send_contact_email(request):
     if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        description = request.POST.get('description')
        
        # You can customize the email subject and body as per your requirements
        subject = f"New Contact Form Submission from {name}"
        message = f"Name: {name}\nEmail: {email}\nAddress: {address}\nDescription: {description}"
        from_email = 'noorejaz576@gmail.com'  # Update with your email address
        
        try:
            # Send email
            send_mail(subject, message, from_email, ['noorejaz576@gmail.com'])
            return JsonResponse({'success': True})
        except Exception as e:
            # Handle error
            return JsonResponse({'error': str(e)}, status=500)
     else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@api_view(['POST'])
def save_chat(request):
    serializer = ChatSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Chat saved successfully!"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_saved_chats(request):
    try:
        chats = Chat.objects.all()
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def generate_text(request):
    if request.method == 'POST':
        try:
            data = request.data
            prompt = data.get("prompt")
            
            if not prompt:
                if os.getenv('DEBUG', 'False') == 'True':
                    # Debugging line to allow prompt input from the console in debug mode
                    prompt = input("Enter prompt for debugging: ")
                    if not prompt:
                        return JsonResponse({"error": "No prompt provided"}, status=400)
                else:
                    return JsonResponse({"error": "No prompt provided"}, status=400)

            # Debugging line to check OpenAI key
            print(f"OpenAI API Key in view: {os.getenv('OPENAI_API_KEY')[:4]}...")

            # Process the conversation
            messages = []
            generated_text = process_conversation(qa, prompt, messages)

            print("Generated Text:", generated_text)  # Print the generated text
            return JsonResponse({"generated_text": generated_text})
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)