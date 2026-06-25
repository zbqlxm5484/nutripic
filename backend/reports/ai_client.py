import json
import urllib.error
import urllib.request
from urllib.parse import urljoin

from django.conf import settings


class AIClientError(Exception):
    def __init__(self, status_code, payload=None, path=None):
        self.status_code = status_code
        self.payload = payload or {}
        self.path = path
        super().__init__(self.payload.get('message', 'AI server request failed.'))


class AIServiceUnavailableError(Exception):
    pass


class AIClient:
    def __init__(self, base_url=None, api_key=None, timeout=None):
        self.base_url = (base_url or settings.AI_SERVER_BASE_URL).rstrip('/') + '/'
        self.api_key = api_key or settings.AI_INTERNAL_API_KEY
        self.timeout = timeout or settings.AI_REQUEST_TIMEOUT_SECONDS

    def input_guardrail(self, payload):
        return self._post('guardrails/input/', payload)

    def normalize(self, payload):
        return self._post('normalize/', payload)

    def rag_search(self, payload):
        return self._post('rag/search/', payload)

    def generate_report(self, payload):
        return self._post('reports/generate/', payload)

    def chat_respond(self, payload):
        return self._post('chat/respond/', payload)

    def output_guardrail(self, payload):
        return self._post('guardrails/output/', payload)

    def _post(self, path, payload):
        request_id = payload.get('request_id')
        body = json.dumps(payload).encode('utf-8')

        request = urllib.request.Request(
            urljoin(self.base_url, path),
            data=body,
            method='POST',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Internal-Api-Key': self.api_key,
                'X-Request-Id': request_id or '',
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                try:
                    return json.loads(response.read().decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError) as error:
                    raise AIClientError(
                        status_code=502,
                        payload={
                            'message': 'AI server returned an invalid JSON response.',
                        },
                        path=path,
                    ) from error
        except urllib.error.HTTPError as error:
            raise AIClientError(
                status_code=error.code,
                payload=self._read_error_payload(error),
                path=path,
            ) from error
        except urllib.error.URLError as error:
            raise AIServiceUnavailableError(str(error)) from error
        except TimeoutError as error:
            raise AIServiceUnavailableError(str(error)) from error

    def _read_error_payload(self, error):
        try:
            return json.loads(error.read().decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}


def get_ai_client():
    return AIClient()
