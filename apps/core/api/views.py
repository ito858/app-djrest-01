from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsViewer
from apps.core.models.cliente import Cliente
from apps.core.models.vip import create_vip_table
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from django.shortcuts import render
from my_django_project_001.config.database import engine
import pandas as pd
from rest_framework import status
from apps.core.services.vip_service import upload_vip_data

class ClientListView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]
    def get(self, request):
        with Session(engine) as session:
            clients = session.query(Cliente).all()
            data = [{col: getattr(c, col) for col in Cliente.__table__.columns.keys()} for c in clients]
            df = pd.DataFrame(data)
            return Response({'data': df.to_dict(orient='records')})

class VipMembershipView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]

    def get(self, request, token_registrazione):
        with Session(engine) as session:
            client = session.query(Cliente).filter(Cliente.token_registrazione == token_registrazione).first()
            if not client:
                return Response({"error": "Client not found"}, status=404)

            prefix = 'http://localhost:8001/api/'
            suffix = '?=signin'
            signin_url = f"{prefix}{client.token_registrazione or 'no-token'}{suffix}"

            metadata = MetaData()
            vip_table = create_vip_table(client.dbnome, metadata)
            vip_table.create(bind=engine, checkfirst=True)
            vip_count = session.query(vip_table).filter(vip_table.c.stato == 0).count()
            remaining_count = session.query(vip_table).filter(vip_table.c.stato == 1).count()

        return render(request, 'vip_membership.html', {
            'signin_url': signin_url,
            'vip_count': vip_count,
            'remaining_count': remaining_count,
            'nome_negozio': client.nome_negozio,
            'id_negozio': client.id_negozio,
            'dbnome': client.dbnome,
            'token_registrazione': client.token_registrazione
        })

class UploadVipFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, token_registrazione):
        with Session(engine) as session:
            client = session.query(Cliente).filter(Cliente.token_registrazione == token_registrazione).first()
            if not client:
                return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
            dbnome = client.dbnome

        vip_file = request.FILES.get('vipFile')
        if not vip_file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(vip_file)
        except Exception:
            try:
                df = pd.read_csv(vip_file)
            except Exception:
                return Response({'error': 'Invalid file format. Must be CSV or Excel.'}, status=status.HTTP_400_BAD_REQUEST)

        if not {'IDvip', 'code'}.issubset(df.columns):
            return Response({'error': 'The file must contain columns named "IDvip" and "code".'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upload_vip_data(df, dbnome)
        except Exception as e:
            return Response({'error': f"Database error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        with Session(engine) as session:
            metadata = MetaData()
            vip_table = create_vip_table(dbnome, metadata)
            remaining_count = session.query(vip_table).filter(vip_table.c.stato == 1).count()
            vip_count = session.query(vip_table).filter(vip_table.c.stato == 0).count()

        return Response({
            'message': 'VIP records added successfully',
            'remaining_count': remaining_count,
            'vip_count': vip_count
        }, status=status.HTTP_201_CREATED)

class VipCountsView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]

    def get(self, request, token_registrazione):
        with Session(engine) as session:
            client = session.query(Cliente).filter(Cliente.token_registrazione == token_registrazione).first()
            if not client:
                return Response({"error": "Client not found"}, status=404)

            metadata = MetaData()
            vip_table = create_vip_table(client.dbnome, metadata)
            vip_count = session.query(vip_table).filter(vip_table.c.stato == 0).count()
            remaining_count = session.query(vip_table).filter(vip_table.c.stato == 1).count()

            return Response({
                'vip_count': vip_count,
                'remaining_count': remaining_count
            })
