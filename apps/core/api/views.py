from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsViewer
from apps.core.models.cliente import Cliente
from apps.core.models.vip import create_vip_table
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, String
from sqlalchemy.sql import func
from django.shortcuts import render
from my_django_project_001.config.database import engine
import pandas as pd
from rest_framework import status
from django.http import JsonResponse  # Add this import
from apps.core.services.vip_service import upload_vip_data
from apps.core.services.client_service import add_client, regenerate_token, CLIENTE_FIELDS
import re
import os

# Form configuration for modularity
REGISTRATION_FIELDS = {
    'mandatory': {
        'Nome': {'label': 'Nome', 'type': 'text'},
        'cognome': {'label': 'Cognome', 'type': 'text'},
        'cellulare': {'label': 'Cellulare', 'type': 'text', 'help': '(e.g., +393331234567 or 3331234567)'},
        'sesso': {'label': 'Sesso', 'type': 'select', 'options': [(0, 'Uomo'), (1, 'Donna')]},
    },
    'optional': {
        'nascita': {'label': 'Data di Nascita', 'type': 'date'},
        'Indirizzo': {'label': 'Indirizzo', 'type': 'text'},
        'Cap': {'label': 'CAP', 'type': 'text'},
        'Citta': {'label': 'Città', 'type': 'text'},
        'Prov': {'label': 'Provincia', 'type': 'text'},
        'Email': {'label': 'Email', 'type': 'text'},
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
    return record.code, record.IDvip  # Return both code and IDvip

def get_vip_by_idvip(session: Session, vip_table, idvip: int):
    """Retrieve VIP record by IDvip."""
    return session.query(vip_table).filter(vip_table.c.IDvip == idvip).first()

class ClientListView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]
    def get(self, request):
        with Session(engine) as session:
            clients = session.query(Cliente).all()
            data = [{col: getattr(c, col) for col in Cliente.__table__.columns.keys()} for c in clients]
            df = pd.DataFrame(data)
            return Response({'data': df.to_dict(orient='records')})

class ClientTableView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]

    def get(self, request):
        has_editor_permission = request.user.has_perm('apps.core.can_edit_item')
        print(f"User: {request.user}, Has Editor Permission: {has_editor_permission}")  # Debug log
        return render(request, 'client_table.html', {
            'has_editor_permission': has_editor_permission
        })

class AddClientView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]

    def get(self, request):
        return render(request, 'add_client.html', {'fields': CLIENTE_FIELDS})

    def post(self, request):
        data = {field: request.POST.get(field) for field in CLIENTE_FIELDS['mandatory'].keys()}
        data.update({field: request.POST.get(field, '') for field in CLIENTE_FIELDS['optional'].keys()})

        missing_fields = [f for f in CLIENTE_FIELDS['mandatory'] if not data[f]]
        if missing_fields:
            return render(request, 'add_client.html', {
                'fields': CLIENTE_FIELDS,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            })

        client = add_client(data)
        return JsonResponse({'id_negozio': client.id_negozio, 'token_registrazione': client.token_registrazione})


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

        if 'code' not in df.columns or len(df.columns) != 1:
            return Response({'error': 'File must contain exactly one column named "code".'}, status=status.HTTP_400_BAD_REQUEST)

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
            'fields': REGISTRATION_FIELDS,
            'nome_negozio': client.nome_negozio  # Pass store name
        })

    def post(self, request, token_registrazione):
        with Session(engine) as session:
            client = session.query(Cliente).filter(Cliente.token_registrazione == token_registrazione).first()
            if not client:
                return Response({"error": "Client not found"}, status=404)

            # Extract form data
            data = {field: request.POST.get(field) for field in REGISTRATION_FIELDS['mandatory'].keys()}
            data.update({field: request.POST.get(field, '') for field in REGISTRATION_FIELDS['optional'].keys()})
            data['sesso'] = int(data['sesso']) if data['sesso'] in ['0', '1'] else 0

            # Step 1: Check if phone number is taken
            metadata = MetaData()
            vip_table = create_vip_table(client.dbnome, metadata)
            vip_table.create(bind=engine, checkfirst=True)
            is_valid, cellulare = validate_phone_number(data['cellulare'])
            if not is_valid:
                return render(request, 'customer_registration.html', {
                    'token_registrazione': token_registrazione,
                    'fields': REGISTRATION_FIELDS,
                    'error': cellulare
                })
            if check_phone_taken(session, vip_table, cellulare):
                return render(request, 'customer_registration.html', {
                    'token_registrazione': token_registrazione,
                    'fields': REGISTRATION_FIELDS,
                    'error': "This phone number is already registered."
                })
            data['cellulare'] = cellulare

            # Validate mandatory fields
            missing_fields = [field for field, value in data.items() if field in REGISTRATION_FIELDS['mandatory'] and (value is None or value == '')]
            if missing_fields:
                return render(request, 'customer_registration.html', {
                    'token_registrazione': token_registrazione,
                    'fields': REGISTRATION_FIELDS,
                    'error': f"Missing required fields: {', '.join(missing_fields)}"
                })

            # Step 2: Find first record with stato=1 and update it
            available_record = get_available_vip_record(session, vip_table)
            if not available_record:
                return render(request, 'customer_registration.html', {
                    'token_registrazione': token_registrazione,
                    'fields': REGISTRATION_FIELDS,
                    'error': "No available VIP memberships."
                })

            # Preserve original code and update with form data
            string_columns = [col.name for col in vip_table.columns if isinstance(col.type, String)]
            update_data = {col: '' for col in string_columns if col not in data}  # Set unspecified string fields to empty
            update_data.update(data)
            update_data['code'] = available_record.code  # Preserve original code
            update_data['rdata'] = func.now()  # Set rdata to current timestamp
            update_data['stato'] = 0  # Mark as taken
            session.execute(vip_table.update().where(vip_table.c.IDvip == available_record.IDvip).values(**update_data))
            session.commit()

            # Step 3: Query by code to confirm and display
            registered_vip = session.query(vip_table).filter(vip_table.c.code == available_record.code).first()
            if not registered_vip:
                return Response({"error": "Failed to retrieve updated VIP record"}, status=500)

        return render(request, 'registration_success.html', {
            'membership_number': registered_vip.code,
            'vip_data': {
                'Nome': registered_vip.Nome,
                'cognome': registered_vip.cognome,
                'cellulare': registered_vip.cellulare,
                'sesso': 'Uomo' if registered_vip.sesso == 0 else 'Donna',
                'nascita': registered_vip.nascita,
                'Indirizzo': registered_vip.Indirizzo,
                'Cap': registered_vip.Cap,
                'Citta': registered_vip.Citta,
                'Prov': registered_vip.Prov,
                'Email': registered_vip.Email
            }
        })



class RegenerateTokenView(APIView):
    permission_classes = [IsAuthenticated, IsViewer]

    def post(self, request, id_negozio):
        client = regenerate_token(id_negozio)
        if not client:
            return Response({"error": "Client not found"}, status=404)
        return Response({"token_registrazione": client.token_registrazione}, status=200)
