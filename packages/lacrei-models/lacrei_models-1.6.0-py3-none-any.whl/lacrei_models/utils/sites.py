from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site


def get_site_for_origin(http_origin):
    parsed_url = urlparse(http_origin)
    origin, port = parsed_url.hostname, parsed_url.port

    if not origin:
        # Assume default site
        return get_current_site(request=None)

    try:
        port = (
            f":{port}" if bool(port) and port not in (80, 443) else ""
        )  # Ignore empty and default ports (80, 443)
        return Site.objects.get(domain=f"{origin}{port}")
    except Site.DoesNotExist:
        return get_current_site(request=None)


def get_site_for_user(user, force_professional=False):
    """
    Get the site link for the given user.

    Try to check if the user has a related professional OR if we are forcing
    the professional site.
    """
    if hasattr(user, "professional") or force_professional:
        return Site.objects.get(id=settings.SITE_IDS["professional"])
    return Site.objects.get(id=settings.SITE_IDS["default"])


def format_professional_url(path, schema="https"):
    site = Site.objects.get(id=settings.SITE_IDS["professional"])
    return f"{schema}://{site.domain}/{path}"
