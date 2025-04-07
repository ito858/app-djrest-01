from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsViewer
from apps.core.models.cliente import Cliente
from sqlalchemy.orm import Session
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
