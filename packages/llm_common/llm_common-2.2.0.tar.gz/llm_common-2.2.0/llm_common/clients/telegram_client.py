import re

from llm_common.clients.httpx_client import HTTPXTransportWithMonitoring


class TelegramHTTPXTransportWithMonitoring(HTTPXTransportWithMonitoring):
    name_for_monitoring = "telegram_api"

    def clear_resource_path(self, resource: str):
        """
        Надо очищать URL ресурсов от значений, которые мешают группировки запросов.
        """
        # Remove telegram bot token.
        return re.sub(r"/bot[^/]+", "", resource)
