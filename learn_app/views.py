from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .db import get_connection
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from rest_framework import status
from django.db import connection, transaction
import re


    
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



class AddPropertyRawSQL(APIView):
    def post(self, request):
        data = request.data

        # ✅ Required fields check
        required = ["area_location", "property_type", "rent", "contact_number"]
        for field in required:
            if field not in data or str(data[field]).strip() == "":
                return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Extract & clean
        area_location = str(data["area_location"]).strip()
        property_type = str(data["property_type"]).strip()
        description = str(data.get("description", "")).strip()

        try:
            rent = float(data["rent"])
        except ValueError:
            return Response({"error": "Rent must be a number"}, status=status.HTTP_400_BAD_REQUEST)

        contact_number = str(data["contact_number"]).strip()
        if not re.fullmatch(r"\d{7,15}", contact_number):
            return Response({"error": "Invalid contact number"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Insert using raw SQL
        insert_sql = """
        INSERT INTO property (area_location, property_type, rent, contact_number, description)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, posted_at;
        """

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(insert_sql, [area_location, property_type, rent, contact_number, description])
                    new_id, posted_at = cursor.fetchone()

            return Response({
                "message": "Property added successfully",
                "id": new_id,
                "posted_at": posted_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
import psycopg2
from django.http import JsonResponse
from django.conf import settings

def get_properties(request):
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        database=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, area_location, property_type, rent, contact_number, description, posted_at
        FROM property
        ORDER BY posted_at DESC
    """)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert to list of dicts
    properties = []
    for row in rows:
        properties.append({
            "id": row[0],
            "area_location": row[1],
            "property_type": row[2],
            "rent": float(row[3]),
            "contact_number": row[4],
            "description": row[5],
            "posted_at": row[6].isoformat() if row[6] else None
        })

    return JsonResponse(properties, safe=False)
