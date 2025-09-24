import json
import threading
from apps.payments.models import PaymentRequestLog, PaymentTransaction


class PaymentTransactionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.provider_urls = {
            "/api/v1/payme/": PaymentTransaction.ProviderType.PAYME,
            "/api/v1/paylov/": PaymentTransaction.ProviderType.PAYLOV,  
            "/api/v1/click-prepare/": PaymentTransaction.ProviderType.CLICK,
            "/api/v1/click-complete/": PaymentTransaction.ProviderType.CLICK,
        }
        self.click_methods = {
            "/api/v1/click-prepare/": "prepare",
            "/api/v1/click-complete/": "complete",
        }
        self._local = threading.local()

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        self.process_response(request, response)
        return response

    def process_request(self, request):
        if request.path in self.provider_urls.keys():
            headers = {key: value for key, value in request.headers.items()}
            body = request.body.decode('utf-8')
            
            try:
                method = json.loads(body).get("method", None) if body else None
                if str(request.path).startswith("/api/v1/click"):
                    method = self.click_methods[request.path]
            except Exception:
                method = "prepare" if str(request.path).startswith("/api/v1/click-prepare/") else "complete"
            
            request_data = {
                "headers": headers,
                "body": body,
            }
            
            payment_log = PaymentRequestLog.objects.create(
                provider=self.provider_urls[request.path],
                method=method,
                request_data=request_data,
            )
            
            self._local.payment_log_id = payment_log.id

    def process_response(self, request, response):
        if request.path in self.provider_urls.keys() and hasattr(self._local, 'payment_log_id'):
            try:
                payment_log = PaymentRequestLog.objects.get(id=self._local.payment_log_id)
                
                response_data = {
                    "status_code": response.status_code,
                    "headers": {key: value for key, value in response.headers.items()},
                    "body": response.content.decode('utf-8'),
                }
                
                payment_log.response_data = response_data
                payment_log.save(update_fields=['response_data'])
                
            except PaymentRequestLog.DoesNotExist:
                pass
            finally:
                if hasattr(self._local, 'payment_log_id'):
                    delattr(self._local, 'payment_log_id')

        return response
