from django.shortcuts import render
import json
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from .models import LocationReport

# Create your views here.
def index(request):
    return render(request, "index.html")



logger = logging.getLogger(__name__)

@csrf_exempt
def store(request):
    """
    Accepts POST /s with JSON body containing keys like:
      - timestamp (ISO string, optional)
      - provider
      - coords (object)  e.g. { latitude, longitude, accuracy, ... }
      - address (object)
      - raw (object) raw reverse-geocode response
      - reverseError (optional)
    Saves to LocationReport and returns JSON ack.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    # ensure JSON content
    content_type = request.META.get("CONTENT_TYPE", "")
    body = request.body
    if not body:
        return HttpResponseBadRequest("Empty request body")

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception as e:
        logger.exception("Invalid JSON posted to /s")
        return HttpResponseBadRequest("Invalid JSON: " + str(e))

    # Extract fields gently
    ts = payload.get("timestamp")
    provider = payload.get("provider") or payload.get("provider_name") or payload.get("provider", "")
    coords = payload.get("coords") or payload.get("coordinate") or payload.get("location")
    address = payload.get("address")
    raw = payload.get("raw")
    reverse_error = payload.get("reverseError") or payload.get("reverse_error") or payload.get("reverseerror")

    # parse timestamp if provided
    parsed_ts = None
    if ts:
        parsed_ts = parse_datetime(ts)
        # parse_datetime returns None for naive/unknown formats; keep it optional
    if parsed_ts is None:
        parsed_ts = None

    # Save to DB
    try:
        report = LocationReport.objects.create(
            timestamp=parsed_ts,
            provider=provider,
            coords=coords,
            address=address,
            raw=raw,
            reverse_error=reverse_error
        )
    except Exception:
        # DB save failed — still return 200 but log for debugging
        logger.exception("Failed to save LocationReport; falling back to logging.")
        # fallback: log full payload to server logs
        logger.info("Location payload: %s", json.dumps(payload, indent=2))
        return JsonResponse({"ok": False, "saved": False, "note": "DB save failed — payload logged"}, status=500)

    # success
    logger.info("Saved LocationReport id=%s provider=%s", report.id, provider)
    return JsonResponse({"ok": True, "saved": True, "id": report.id})




