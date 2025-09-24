import json
import random
import logging
import requests
from typing import Dict, Any, Optional

from django.core.cache import cache
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnorbankInterface:
    """
    Interface for working with Open API ANOR BANK
    Documentation: ANOR-BANK OPEN-API-DOCUMENTATION-v1.4
    """
    
    def __init__(self, base_url: str = "https://ob-api.anorbank.uz/services/", 
                 username: str = None, password: str = None):
        if username is None:
            username = settings.PAYMENT_CREDENTIALS["anorbank"]["username"]
        if password is None:
            password = settings.PAYMENT_CREDENTIALS["anorbank"]["password"]

        self.base_url = base_url.rstrip('/') + '/'
        self.session = requests.Session()
        self.username = username
        self.password = password

        self.access_token_cache_key = 'anor_bank_access_token'
        self.refresh_token_cache_key = 'anor_bank_refresh_token'
        
        self.auth_url = f"{self.base_url}api/ext/user"
        self.payment_url = f"{self.base_url}services/open-api-payment-ms/api/json-rpc"
        self.card_url = f"{self.base_url}services/open-api-card-ms/api/json-rpc"
        self.service_url = f"{self.base_url}services/open-api-services-ms/api/json-rpc"
        
    def _get_cached_value(self, key: str) -> Optional[str]:
        return cache.get(key)
    
    def _set_cached_value(self, key: str, value: str, expire_seconds: int) -> bool:
        cache.set(key, value, expire_seconds)
        return True
    
    def _delete_cached_value(self, key: str) -> bool:
        cache.delete(key)
        return True
    
    def _get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        headers = {
            "Content-Type": content_type
        }
        
        token = self._get_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        return headers
    
    
    def _update_token_data(self, response_data: Dict[str, Any]) -> bool:
        """Updating token data in the cache after successful authentication"""
        if "result" in response_data and "access_token" in response_data["result"] and "refresh_token" in response_data["result"] and "expires_in" in response_data["result"] and "refresh_expires_in" in response_data["result"]:
            result = response_data["result"]
            self._set_cached_value(self.access_token_cache_key, result["access_token"], result["expires_in"])
            self._set_cached_value(self.refresh_token_cache_key, result["refresh_token"], result["refresh_expires_in"])
            return True
        return False


    def _get_access_token(self) -> str:
        access_token = self._get_cached_value(self.access_token_cache_key)
        if access_token:
            return access_token
        
        refresh_token = self._get_cached_value(self.refresh_token_cache_key)
        if refresh_token:
            response = self.refresh_token(refresh_token)
            if self._update_token_data(response):
                return response["result"]["access_token"]

        login_response = self.login()
        if self._update_token_data(login_response):
            return login_response["result"]["access_token"]
        
        return None
        

    
    def _make_request(self, method: str, url: str, is_auth_request: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Base method for executing requests with authorization processing
        
        :param method: HTTP method
        :param url: URL for the request
        :param is_auth_request: Whether the request is an authentication request
        :param kwargs: Additional parameters for requests
        :return: API response
        """
        
        kwargs["headers"] = self._get_headers()
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 401 and not is_auth_request:
                kwargs["headers"] = self._get_headers()
                response = self.session.request(method, url, **kwargs)
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Request error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise Exception(f"JSON decode error: {str(e)}")
    
    def _json_rpc_request(self, method: str, params: Dict[str, Any], 
                         url: str = None) -> Dict[str, Any]:
        """Executing a JSON-RPC request"""
        if url is None:
            url = self.payment_url
            
        payload = {
            "id": random.randint(1, 1000000),
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        return self._make_request("POST", url, json=payload)
    
    # Authentication
    def login(self) -> Dict[str, Any]:
        """
        Method for user login
        
        :return: Response with tokens
        """
            
        url = f"{self.auth_url}/login"
        data = {
            "username": self.username,
            "password": self.password
        }
        
        response = self._make_request("POST", url, is_auth_request=True, json=data)
                
        return response
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Method for updating the token
        
        :param refresh_token: Token for updating
        :return: Response with new tokens
        """
        url = f"{self.auth_url}/refresh-token"
        data = {
            "refreshToken": refresh_token
        }
        
        response = self._make_request("POST", url, is_auth_request=True, json=data)

        return response
    
    # Payment gateway
    def account_to_card_transfer(self, agent_tran_id: int, currency: int, 
                               from_account: str, from_mfo: str, from_name: str,
                               to_pan: str, to_exp: str, amount: int,
                               comment: str = None, purpose_id: str = None) -> Dict[str, Any]:
        """
        Transfer from account to card
        
        :param agent_tran_id: Unique transaction identifier
        :param currency: Transaction currency (860 - UZS, 840 - USD)
        :param from_account: Account number of the sender
        :param from_mfo: MFO of the sender
        :param from_name: Name of the sender
        :param to_pan: Card number of the recipient
        :param to_exp: Card expiration date (MMYY)
        :param amount: Transfer amount (in sums)
        :param comment: Comment (optional)
        :param purpose_id: Purpose code (optional)
        :return: Result of the operation
        """
        from_data = {
            "account": from_account,
            "mfo": from_mfo,
            "name": from_name
        }
        
        # Adding optional fields, if they are provided
        if comment is not None:
            from_data["comment"] = comment
        if purpose_id is not None:
            from_data["purposeId"] = purpose_id
            
        to_data = {
            "pan": to_pan,
            "exp": to_exp
        }
        
        request_data = {
            "agentTranId": agent_tran_id,
            "currency": currency,
            "from": from_data,
            "to": to_data,
            "amount": amount
        }
        
        return self._json_rpc_request("account.to.card.transfer", {"request": request_data})
    
    def account_to_account_transfer(self, agent_tran_id: int, currency: int,
                                  from_account: str, from_mfo: str, 
                                  to_account: str, to_mfo: str, amount: int,
                                  from_comment: str = None, from_purpose_id: str = None,
                                  from_name: str = None, to_comment: str = None,
                                  to_purpose_id: str = None, to_name: str = None) -> Dict[str, Any]:
        """
        Transfer from account to account
        
        :param agent_tran_id: Unique transaction identifier
        :param currency: Transaction currency (860 - UZS, 840 - USD)
        :param from_account: Account number of the sender
        :param from_mfo: MFO of the sender
        :param to_account: Account number of the recipient
        :param to_mfo: MFO of the recipient
        :param amount: Transfer amount (in sums)
        :param from_comment: Comment of the sender (optional)
        :param from_purpose_id: Purpose code of the sender (optional)
        :param from_name: Name of the sender (optional)
        :param to_comment: Comment of the recipient (optional)
        :param to_purpose_id: Purpose code of the recipient (optional)
        :param to_name: Name of the recipient (optional)
        :return: Result of the operation
        """
        from_data = {
            "account": from_account,
            "mfo": from_mfo
        }
        
        # Adding optional fields of the sender
        if from_comment is not None:
            from_data["comment"] = from_comment
        if from_purpose_id is not None:
            from_data["purposeId"] = from_purpose_id
        if from_name is not None:
            from_data["name"] = from_name
            
        to_data = {
            "account": to_account,
            "mfo": to_mfo
        }
        
        # Adding optional fields of the recipient
        if to_comment is not None:
            to_data["comment"] = to_comment
        if to_purpose_id is not None:
            to_data["purposeId"] = to_purpose_id
        if to_name is not None:
            to_data["name"] = to_name
            
        request_data = {
            "agentTranId": agent_tran_id,
            "currency": currency,
            "from": from_data,
            "to": to_data,
            "amount": amount
        }
        
        return self._json_rpc_request("account.to.account.transfer", {"request": request_data})
    
    def trans_pay_purpose_check(self, recipient_id: int, account: str, amount: int, 
                              agent_tran_id: str, currency: int = 860,
                              pan: str = None, exp: str = None) -> Dict[str, Any]:
        """
        Checking the account in the billing
        
        :param recipient_id: Recipient identifier
        :param account: Account number (phone number, wallet number, etc.)
        :param amount: Payment amount
        :param agent_tran_id: Agent transaction identifier
        :param currency: Currency (860 - UZS, 840 - USD)
        :param pan: Card number (optional)
        :param exp: Card expiration date (optional)
        :return: Result of the check
        """
        params = {}
        if pan is not None and exp is not None:
            params = {
                "pan": pan,
                "exp": exp
            }
            
        request_data = {
            "recipientId": recipient_id,
            "account": account,
            "amount": amount,
            "currency": currency,
            "agentTranId": agent_tran_id,
            "params": params
        }
        
        return self._json_rpc_request("trans.pay.purpose.check", {"request": request_data})
    
    def trans_pay_purpose(self, bill_id: int, amount: int, type_: str = "AGENT", 
                         otp: str = None) -> Dict[str, Any]:
        """
        Payment
        
        :param bill_id: Payment number in the system
        :param amount: Payment amount
        :param type_: Payment type (default "AGENT")
        :param otp: OTP code (optional)
        :return: Result of the operation
        """
        params = {}
        if otp is not None:
            params = {
                "otp": otp
            }
            
        request_data = {
            "billId": bill_id,
            "amount": amount,
            "type": type_,
            "params": params
        }
        
        return self._json_rpc_request("trans.pay.purpose", {"request": request_data})
    
    def trans_reverse(self, bill_id: int, agent_tran_id: str, 
                     tran_id: int = None) -> Dict[str, Any]:
        """
        Cancel payment
        
        :param bill_id: Payment number in the system
        :param agent_tran_id: Agent transaction identifier
        :param tran_id: Transaction identifier (optional)
        :return: Result of the operation
        """
        request_data = {
            "billId": bill_id,
            "agentTranId": agent_tran_id
        }
        
        if tran_id is not None:
            request_data["tranId"] = tran_id
            
        return self._json_rpc_request("trans.reverse", {"request": request_data})
    
    def hold_create(self, bill_id: int, amount: int, type_: str = "AGENT",
                   params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Creation of holding
        
        :param bill_id: Payment number in the system
        :param amount: Payment amount
        :param type_: Payment type (default "AGENT")
        :param params: Additional parameters (optional)
        :return: Result of the operation
        """
        if params is None:
            params = {}
            
        request_data = {
            "billId": bill_id,
            "amount": amount,
            "type": type_,
            "params": params
        }
        
        return self._json_rpc_request("hold.create", {"request": request_data})
    
    def hold_dismiss_charge(self, bill_id: int, amount: int, type_: str = "AGENT",
                           params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Confirmation of holding
        
        :param bill_id: Payment number in the system
        :param amount: Payment amount
        :param type_: Payment type (default "AGENT")
        :param params: Additional parameters (optional)
        :return: Result of the operation
        """
        if params is None:
            params = {}
            
        request_data = {
            "billId": bill_id,
            "amount": amount,
            "type": type_,
            "params": params
        }
        
        return self._json_rpc_request("hold.dismiss.charge", {"request": request_data})
    
    def hold_dismiss(self, bill_id: int, amount: int, type_: str = "AGENT",
                    params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Cancel holding
        
        :param bill_id: Payment number in the system
        :param amount: Payment amount
        :param type_: Payment type (default "AGENT")
        :param params: Additional parameters (optional)
        :return: Result of the operation
        """
        if params is None:
            params = {}
            
        request_data = {
            "billId": bill_id,
            "amount": amount,
            "type": type_,
            "params": params
        }
        
        return self._json_rpc_request("hold.dismiss", {"request": request_data})
    
    # Card gateway
    def cards_new_otp(self, pan: str, expiry: str) -> Dict[str, Any]:
        """
        Sending OTP code for card binding
        
        :param pan: Card number
        :param expiry: Card expiration date (MMYY)
        :return: Result of the operation
        """
        request_data = {
            "pan": pan,
            "expiry": expiry
        }
        
        return self._json_rpc_request("cards.new.otp", {"request": request_data}, self.card_url)
    
    def cards_new_verify(self, id_: str, otp: str) -> Dict[str, Any]:
        """
        Confirmation of OTP code for card binding
        
        :param id_: ID from the response of cards.new.otp
        :param otp: OTP code
        :return: Result of the operation
        """
        request_data = {
            "id": id_,
            "otp": otp
        }
        
        return self._json_rpc_request("cards.new.verify", {"request": request_data}, self.card_url)
    
    # Service gateway
    def account_check(self, number: str, mfo: str) -> Dict[str, Any]:
        """
        Checking the account for validity
        
        :param number: Account number
        :param mfo: MFO of the bank
        :return: Result of the check
        """
        params = {
            "number": number,
            "mfo": mfo
        }
        
        return self._json_rpc_request("account.check", params, self.service_url)
    
    def account_balance(self, number: str, mfo: str) -> Dict[str, Any]:
        """
        Getting the balance of the account
        
        :param number: Account number
        :param mfo: MFO of the bank
        :return: Balance of the account
        """
        params = {
            "number": number,
            "mfo": mfo
        }
        
        return self._json_rpc_request("account.balance", params, self.service_url)
    
    def account_history(self, number: str, mfo: str, currency: str, 
                       from_date: int, to_date: int, type_: str) -> Dict[str, Any]:
        """
        Monitoring the account (history of operations)
        
        :param number: Account number
        :param mfo: MFO of the bank
        :param currency: Currency of the account
        :param from_date: Initial date in milliseconds
        :param to_date: Final date in milliseconds
        :param type_: Type of operations (CREDIT, DEBIT)
        :return: History of operations
        """
        account_data = {
            "number": number,
            "mfo": mfo,
            "currency": currency
        }
        
        filter_data = {
            "from": from_date,
            "to": to_date,
            "type": type_
        }
        
        params = {
            "account": account_data,
            "filter": filter_data
        }
        
        return self._json_rpc_request("account.history", params, self.service_url)
    
    def nci_transaction_status_get(self, trans_id: str, group_id: str) -> Dict[str, Any]:
        """
        Getting the status of the transaction in the ABS
        
        :param trans_id: ID of the transaction in the ABS
        :param group_id: ID of the transaction group (0 - General, 4 - ANOR SMM)
        :return: Status of the transaction
        """
        request_data = {
            "transId": trans_id,
            "groupId": group_id
        }
        
        return self._json_rpc_request("nci.transactionStatus.get", {"request": request_data}, self.service_url)