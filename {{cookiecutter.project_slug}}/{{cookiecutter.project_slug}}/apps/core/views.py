from typing import TYPE_CHECKING

from django.http import HttpResponse

if TYPE_CHECKING:
    from django.http import HttpRequest


def healthz(request: HttpRequest) -> HttpResponse:
    """Lightweight health-check endpoint for load-balancer probes."""
    return HttpResponse("ok", content_type="text/plain")
