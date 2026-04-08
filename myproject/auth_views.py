from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse


class RateLimitedLoginView(LoginView):
    template_name = "registration/login.html"
    rate_limit_attempts = 5
    rate_limit_window_seconds = 15 * 60

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.method == "POST" and self._is_rate_limited(request):
            return self._render_rate_limited_response()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: Any) -> HttpResponse:
        cache.delete(self._cache_key(self.request))
        return super().form_valid(form)

    def form_invalid(self, form: Any) -> HttpResponse:
        attempts = cache.get_or_set(self._cache_key(self.request), 0, self.rate_limit_window_seconds)
        cache.set(self._cache_key(self.request), int(attempts) + 1, self.rate_limit_window_seconds)
        return super().form_invalid(form)

    def _is_rate_limited(self, request: HttpRequest) -> bool:
        attempts = cache.get(self._cache_key(request), 0)
        return int(attempts) >= self.rate_limit_attempts

    def _cache_key(self, request: HttpRequest) -> str:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR", "")
        return f"login-rate-limit:{client_ip}"

    def _render_rate_limited_response(self) -> TemplateResponse:
        form = self.get_form()
        form.add_error(None, "ログイン試行回数が上限に達しました。時間をおいて再試行してください。")
        response = self.render_to_response(self.get_context_data(form=form), status=429)
        response.headers["Retry-After"] = str(self.rate_limit_window_seconds)
        return response


def is_allowed_image_url(image_url: str) -> bool:
    parsed = urlparse(image_url)
    if parsed.scheme != "https":
        return False
    return parsed.netloc.endswith("res.cloudinary.com")
