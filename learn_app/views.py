from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .db import get_connection
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


    
class SignupAPI(APIView):
    def post(self,request):
        username=request.data.get('username')
        email=request.data.get('email')
        password=request.data.get('password')
        if not username or not email or not password:
            return Response({"error": "All fields are required."}, status=400)
        
        # ✅ Hash the password
        hashed_password = make_password(password)

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
            [username, email, hashed_password]  
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
            stored_hashed_password = row[0]

            # ✅ Secure check using Django's password hasher
            if check_password(password, stored_hashed_password):
                return Response({"message": "Login successful."})
            else:
                return Response({"error": "Incorrect password."}, status=401)
        else:
            return Response({"error": "User not found."}, status=404)


class ForgetpwAPI(APIView):
    def post(self, request):
        password = request.data.get('password')
        email = request.data.get('email')
        hashed_password = make_password(password)
        conn = get_connection()
        cursor = conn.cursor()


        # Update the password
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", [hashed_password, email])
        conn.commit()
        conn.close()

        return Response({"message": "Password changed successfully"}, status=200)
    