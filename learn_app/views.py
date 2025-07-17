from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .db import get_connection

    
class SignupAPI(APIView):
    def post(self,request):
        username=request.data.get('username')
        email=request.data.get('email')
        password=request.data.get('password')
        if not username or not email or not password:
            return Response({"error": "All fields are required."}, status=400)

        conn = get_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", [email])
        if cursor.fetchone():
            conn.close()
            return Response({"error": "Email already registered."}, status=400)

        # Insert user into database
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            [username, email, password]  # (hash later)
        )
        conn.commit()
        conn.close()

        return Response({"message": "Signup successful."})
    

class LoginAPI(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')
      
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE email = %s", [email])
        row = cursor.fetchone()
        conn.close()

        if row:
            stored_password = row[0]

            if password == stored_password:  # 🔴 raw check (fix later!)
                return Response({"message": "Login successful."})
            else:
                return Response({"error": "Incorrect password."}, status=401)
        else:
            return Response({"error": "User not found."}, status=404)


