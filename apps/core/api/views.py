from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsViewer
from apps.core.models.cliente import Cliente
from apps.core.models.vip import create_vip_table
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, String
from django.shortcuts import render
from my_django_project_001.config.database import engine
import pandas as pd
from rest_framework import status
from apps.core.services.vip_service import upload_vip_data
import re
import os

# Form configuration for modularity
REGISTRATION_FIELDS = {
    'mandatory': {
        'nome': {'label': 'Nome', 'type': 'text'},
        'cognome': {'label': 'Cognome', 'type': 'text'},
        'cellulare': {'label': 'Cellulare', 'type': 'text', 'help': '(e.g., +393331234567 or 3331234567)'},
        'sesso': {'label': 'Sesso', 'type': 'select', 'options': [(0, 'Uomo'), (1, 'Donna')]},
    },
    'optional': {
        'indirizzo': {'label': 'Indirizzo', 'type': 'text'},
        'cap': {'label': 'CAP', 'type': 'text'},
        'citta': {'label': 'Città', 'type': 'text'},
        'prov': {'label': 'Provincia', 'type': 'text'},
    }
}

def validate_phone_number(cellulare: str) -> tuple[bool, str]:
    """Validate and normalize Italian phone number."""
    phone_pattern = re.compile(r'^\+39\d{10}$|^\d{10}$')
    if not phone_pattern.match(cellulare):
        return False, "Invalid phone number. Use +39 followed by 10 digits or just 10 digits."
    return True, cellulare[3:] if cellulare.startswith('+39') else cellulare

def check_phone_taken(session: Session, vip_table, cellulare: str) -> bool:
    """Check if phone number is already taken in the VIP table."""
    return session.query(vip_table).filter(vip_table.c.cellulare == cellulare).first() is not None

def get_available_vip_record(session: Session, vip_table):
    """Find the first available VIP record with stato = 1."""
    return session.query(vip_table).filter(vip_table.c.stato == 1).order_by(vip_table.c.IDvip).first()

def update_vip_record(session: Session, vip_table, record, data: dict):
    """Update the VIP record with form data, setting unspecified string fields to empty."""
    string_columns = [col.name for col in vip_table.columns if isinstance(col.type, String)]
    update_data = {col: '' for col in string_columns if col not in data}
    update_data.update(data)
    update_data['stato'] = 0  # Mark as taken
    session.execute(vip_table.update().where(vip_table.c.IDvip == record.IDvip).values(**update_data))
    session.commit()
    return record.code

def get_vip_by_code(session: Session, vip_table, code: str):
    """Retrieve VIP record by code."""
    return session.query(vip_table).filter(vip_table.c.code == code).first()

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

            # Use os.environ with a default value
            base_url = os.environ.get('BASE_URL', 'http://localhost:8000')
            signin_url = f"{base_url}/api/core/register/{client.token_registrazione}/"

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

class CustomerRegistrationView(APIView):
    def get(self, request, token_registrazione):
        with Session(engine) as session:
            client = session.query(Cliente).filter(Cliente.token_registrazione == token_registrazione).first()
            if not client:
                return Response({"error": "Client not found"}, status=404)
        return render(request, 'customer_registration.html', {
            'token_registrazione': token_registrazione,
            'fields': REGISTRATION_FIELDS
        })

    def post(self, request, token_registrazione):
        with Session(engine) as session:
            client = session.query(Cliente).filter(Cliente.token_registrazione == token_registrazione).first()
            if not client:
                return Response({"error": "Client not found"}, status=404)

            # Extract form data
            data = {field: request.POST.get(field) for field in REGISTRATION_FIELDS['mandatory'].keys()}
            data.update({field: request.POST.get(field, '') for field in REGISTRATION_FIELDS['optional'].keys()})

            # Validate mandatory fields
            missing_fields = [field for field, value in data.items() if field in REGISTRATION_FIELDS['mandatory'] and not value]
            if missing_fields:
                return render(request, 'customer_registration.html', {
                    'token_registrazione': token_registrazione,
                    'fields': REGISTRATION_FIELDS,
                    'error': f"Missing required fields: {', '.join(missing_fields)}"
                })

            # Validate phone number
            is_valid, cellulare = validate_phone_number(data['cellulare'])
            if not is_valid:
                return render(request, 'customer_registration.html', {
                    'token_registrazione': token_registrazione,
                    'fields': REGISTRATION_FIELDS,
                    'error': cellulare
                })
            data['cellulare'] = cellulare

            # Create VIP table
            metadata = MetaData()
            vip_table = create_vip_table(client.dbnome, metadata)
            vip_table.create(bind=engine, checkfirst=True)

            # Check if phone is taken
            if check_phone_taken(session, vip_table, cellulare):
                return render(request, 'customer_registration.html', {
                    'token_registrazione': token_registrazione,
                    'fields': REGISTRATION_FIELDS,
                    'error': "This phone number is already registered."
                })

            # Find available record
            available_record = get_available_vip_record(session, vip_table)
            if not available_record:
                return render(request, 'customer_registration.html', {
                    'token_registrazione': token_registrazione,
                    'fields': REGISTRATION_FIELDS,
                    'error': "No available VIP memberships."
                })

            # Update record
            code = update_vip_record(session, vip_table, available_record, data)

            # Retrieve updated record
            registered_vip = get_vip_by_code(session, vip_table, code)

        return render(request, 'registration_success.html', {
            'membership_number': code,
            'vip_data': {
                'Nome': registered_vip.Nome,
                'cognome': registered_vip.cognome,
                'cellulare': registered_vip.cellulare,
                'sesso': 'Uomo' if registered_vip.sesso == 0 else 'Donna',
                'Indirizzo': registered_vip.Indirizzo,
                'Cap': registered_vip.Cap,
                'Citta': registered_vip.Citta,
                'Prov': registered_vip.Prov
            }
        })
