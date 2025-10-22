from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
import os


def health(request):
    """Simple liveness probe. Return 200 if the Django process is up."""
    return JsonResponse({"status": "ok"})


def ready(request):
    """Readiness probe - check DB connectivity and optionally cache/other services.

    Returns 200 when critical dependencies are reachable, 503 otherwise.
    """
    checks = {"database": False}
    status_code = 200

    # Check default DB
    db_conn = connections[os.environ.get('DJANGO_DB_CONNECTION', 'default')]
    try:
        c = db_conn.cursor()
        c.execute('SELECT 1')
        checks["database"] = True
    except OperationalError:
        checks["database"] = False
        status_code = 503

    return JsonResponse({"status": "ok" if status_code == 200 else "unavailable", "checks": checks}, status=status_code)
