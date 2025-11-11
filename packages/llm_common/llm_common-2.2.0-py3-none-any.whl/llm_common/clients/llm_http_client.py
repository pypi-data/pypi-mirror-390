from llm_common.clients.httpx_client import HttpxClientWithMonitoring


class LLMHttpClient(HttpxClientWithMonitoring):
    name_for_monitoring = "llm"
