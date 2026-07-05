from django.http import JsonResponse


def health_check(request):
    """
    GET /api/health/ — used by Docker Compose healthchecks now and by
    Kubernetes liveness/readiness probes from Phase 6 onward.
    """
    return JsonResponse({"status": "ok"})
