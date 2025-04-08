from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsViewer
from apps.core.models.cliente import Cliente
from apps.core.models.vip import VIP  # Import VIP model
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from django.shortcuts import render
from my_django_project_001.config.database import engine  # Absolute import
import pandas as pd

class ClientListView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]  # Protect with Viewer permission

    def get(self, request):
        with Session(engine) as session:
            # Query full cliente table and convert to DataFrame
            clients = session.query(Cliente).all()
            data = [{col: getattr(c, col) for col in Cliente.__table__.columns.keys()} for c in clients]
            df = pd.DataFrame(data)

            # Return full table as JSON
            return Response({
                'data': df.to_dict(orient='records')  # Full table, no pagination
            })

class VipMembershipView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]  # Viewer or higher

    def get(self, request, id_negozio):
        with Session(engine) as session:
            # Get client details
            client = session.query(Cliente).filter(Cliente.id_negozio == id_negozio).first()
            if not client:
                return Response({"error": "Client not found"}, status=404)

            # Construct QR code URL
            prefix = 'http://localhost:8001/api/'
            suffix = '?=signin'
            signin_url = f"{prefix}{client.token_registrazione or 'no-token'}{suffix}"

           # Set dynamic table name for VIP model
            VIP.__table__.name = client.dbnome
            vip_count = session.query(VIP).filter(VIP.stato == 0).count()
            remaining_count = session.query(VIP).filter(VIP.stato == 1).count()

        return render(request, 'vip_membership.html', {
            'signin_url': signin_url,
            'vip_count': vip_count,
            'remaining_count': remaining_count,
            'nome_negozio': client.nome_negozio,
            'id_negozio': id_negozio,
        })
