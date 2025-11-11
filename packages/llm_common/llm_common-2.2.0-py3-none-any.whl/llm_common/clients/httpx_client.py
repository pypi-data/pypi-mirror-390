import time
import warnings

from httpx import AsyncClient, Request, Response, AsyncHTTPTransport

import llm_common.prometheus


class HttpxClientWithMonitoring(AsyncClient):
    """Custom async httpx client that collects metrics for HTTP requests."""

    # Для HTTP клиентов API сервисов, доабвляй суффикс "_api".
    name_for_monitoring = None

    def clear_resource_path(self, resource: str) -> str:
        """
        Надо очищать URL ресурсов от значений, которые мешают группировки запросов.
        """
        return resource

    async def send(self, request: Request, **kwargs) -> Response:
        if not self.name_for_monitoring:
            raise NotImplementedError("Not set name http requests for monitoring")

        response = await super().send(request, **kwargs)

        if llm_common.prometheus._metric:
            request_size = int(request.headers.get("content-length", 0))
            response_size = int(response.headers.get("content-length", 0))
            resource = self.clear_resource_path(request.url.path)

            llm_common.prometheus.http_tracking(
                app_type=self.name_for_monitoring,
                resource=resource,
                method=request.method,
                response_size=response_size,
                status_code=response.status_code,
                duration=response.elapsed.total_seconds(),
                request_size=request_size,
            )

        else:
            warnings.warn("Prometheus metrics not initialized", UserWarning)

        return response


class HTTPXTransportWithMonitoring(AsyncHTTPTransport):
    name_for_monitoring = None

    def clear_resource_path(self, resource: str) -> str:
        """
        Надо очищать URL ресурсов от значений, которые мешают группировки запросов.
        """
        return resource

    async def handle_async_request(self, request: Request) -> Response:
        if not self.name_for_monitoring:
            raise NotImplementedError("Not set name http requests for monitoring")

        start = time.perf_counter()
        response = await super().handle_async_request(request)

        if llm_common.prometheus._metric:
            duration = time.perf_counter() - start
            resource = self.clear_resource_path(request.url.path)
            response_size = int(response.headers.get("content-length", response.headers.get("Content-Length", 0)))
            status_code = response.status_code
            request_size = int(request.headers.get("content-length", request.headers.get("Content-Length", 0)))

            llm_common.prometheus.http_tracking(
                self.name_for_monitoring,
                resource=resource,
                method=request.method,
                response_size=response_size,
                status_code=status_code,
                duration=duration,
                request_size=request_size,
            )

        return response
