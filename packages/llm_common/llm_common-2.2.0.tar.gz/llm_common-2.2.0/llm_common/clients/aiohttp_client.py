import time

from aiohttp import ClientSession

import llm_common.prometheus


class ClientSessionWithMonitoring(ClientSession):
    """
    AIOHTTP client session that collects Prometheus metrics for outgoing HTTP requests.
    """

    # Для HTTP клиентов API сервисов, доабвляй суффикс "_api".
    name_for_monitoring = None

    def clear_resource_path(self, resource: str) -> str:
        return resource

    async def _request(self, method, str_or_url, **kwargs):
        if not self.name_for_monitoring:
            raise NotImplementedError("Not set name http requests for monitoring")

        start = time.perf_counter()
        response = await super()._request(method, str_or_url, **kwargs)

        if llm_common.prometheus._metric:
            duration = time.perf_counter() - start
            resource = self.clear_resource_path(response.url.path)
            request_headers = getattr(response.request_info, "headers", {}) or {}
            response_headers = response.headers or {}
            request_size = int(request_headers.get("content-length", request_headers.get("Content-Length", 0)))
            response_size = int(response_headers.get("content-length", response_headers.get("Content-Length", 0)))

            llm_common.prometheus.http_tracking(
                app_type=self.name_for_monitoring,
                resource=resource,
                method=str(method).upper(),
                response_size=response_size,
                status_code=response.status,
                duration=duration,
                request_size=request_size,
            )

        return response
