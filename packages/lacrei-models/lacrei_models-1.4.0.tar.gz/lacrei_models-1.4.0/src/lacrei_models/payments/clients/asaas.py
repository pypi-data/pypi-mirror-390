import logging
import os
from datetime import datetime
from typing import Optional

import requests
from payments.types import BankAccountData, CreditCard, CreditCardHolderInfo
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger("celery")


class AsaasClient:
    BASE_URL = os.getenv("ASAAS_API_URL", "https://api-sandbox.asaas.com")

    def __init__(self, version: str = "v3", *args, **kwargs):
        self.version = version
        self.token = os.getenv("ASAAS_ROOT_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "access_token": self.token,
        }

    def create_customer_account(
        self, name: str, cpfCnpj: str, phone_number: str
    ) -> Optional[str]:
        """Creates a customer on Asaas and return their ID if successful."""
        url = f"{self.BASE_URL}/{self.version}/customers"

        payload = {"name": name, "cpfCnpj": cpfCnpj, "phone": phone_number}

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=4)
            response.raise_for_status()
            data = response.json()
            return data.get("id")
        except (RequestException, Timeout):
            logger.error("Erro ao criar cliente na Asaas API", exc_info=True)
            return None

    def get_customer_account(self, customer_id: str) -> Optional[dict]:
        """
        Fetch a customer from Asaas by ID.
        Returns a dict with id, name, cpfCnpj, and phone if found; otherwise None.
        """
        url = f"{self.BASE_URL}/{self.version}/customers/{customer_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=4)
            response.raise_for_status()
            data = response.json()

            if not data or "id" not in data:
                return {}

            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "cpfCnpj": data.get("cpfCnpj"),
                "phone": data.get("phone"),
            }
        except (RequestException, Timeout):
            logger.error("Erro ao buscar cliente na Asaas API", exc_info=True)
            return {}

    def update_customer_account(self, id: str, cpfCnpj: str, mobile_phone: str) -> None:
        """
        Updates a customer on Asaas using their ID.
        """
        url = f"{self.BASE_URL}/{self.version}/customers/{id}"
        payload = {
            "cpfCnpj": cpfCnpj,
            "phone": mobile_phone,
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=4)
            response.raise_for_status()
        except (RequestException, Timeout):
            logger.error(f"Erro ao atualizar cliente {id} na Asaas API", exc_info=True)

    def delete_customer_account(self, id: str) -> Optional[dict]:
        """
        Deletes a customer from Asaas by ID.
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/customers/{id}"

        try:
            response = requests.delete(url, headers=self.headers, timeout=4)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout):
            logger.error(f"Erro ao deletar cliente {id} na Asaas API", exc_info=True)
            return None

    def create_professional_account(
        self,
        name: str,
        email: str,
        cpf_cnpj: str,
        mobile_phone: str,
        income_value: float,
        address: str,
        address_number: str,
        province: str,
        postal_code: str,
        company_type: str,
    ) -> Optional[dict]:
        """
        Creates a white label sub-account for a professional.
        Returns a dict with the apiKey for the account and unique walletId for payment splits
        or None if the request failed.
        """
        url = f"{self.BASE_URL}/{self.version}/accounts"

        payload = {
            "name": name,
            "email": email,
            "cpfCnpj": cpf_cnpj,
            "mobilePhone": mobile_phone,
            "incomeValue": income_value,
            "address": address,
            "addressNumber": address_number,
            "province": province,
            "postalCode": postal_code,
            "companyType": company_type,
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=4)
            response.raise_for_status()
            data = response.json()

            return {
                "api_key": data.get("apiKey"),
                "wallet_id": data.get("walletId"),
            }

        except (RequestException, Timeout):
            logger.error(
                "Erro ao criar subconta white label na Asaas API", exc_info=True
            )
            return None

    def get_professional_account(self, subaccount_id: str) -> Optional[dict]:
        """
        Retrieves information about a white label sub-account given its id.
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/accounts/{subaccount_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=4)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout):
            logger.error(
                f"Erro ao recuperar informações da subconta {subaccount_id}",
                exc_info=True,
            )
            return None

    def delete_professional_account(self, api_key: str) -> Optional[dict]:
        """
        Deletes a white label subaccount.
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/myAccount"

        self.token = api_key

        try:
            response = requests.delete(url, headers=self.headers, timeout=4)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout):
            logger.error("Erro ao deletar profissional na Asaas API", exc_info=True)
            return None

    def request_withdrawal_TED(
        self, api_key: str, value: float, bank_account: BankAccountData
    ) -> Optional[dict]:
        """
        Requests a withdrawal for a white label sub-account via TED transfer.
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/transfers"

        self.token = api_key
        payload = {
            "value": value,
            "bankAccount": bank_account,
            "operationType": "TED",
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=4)
            response.raise_for_status()
            return response.json()

        except (RequestException, Timeout):
            logger.error("Erro ao solicitar saque via TED", exc_info=True)
            return None

    def request_withdrawal_PIX(
        self, api_key: str, value: float, pix_address_key: str, pix_key_type: str
    ) -> Optional[dict]:
        """
        Requests a withdrawal for a white label sub-account via PIX.
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/transfers"
        self.token = api_key

        payload = {
            "value": value,
            "pixAddressKey": pix_address_key,
            "pixAddressKeyType": pix_key_type,
            "operationType": "PIX",
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=4)
            response.raise_for_status()
            return response.json()

        except (RequestException, Timeout):
            logger.error("Erro ao solicitar saque via PIX", exc_info=True)
            return None

    def get_professional_account_docs(self, api_key: str) -> Optional[dict]:
        """
        Retrieves information about the documents sent or to be sent for the subaccount to be fully approved by Asaas.
        It also includes the onboardingUrl for pending documents.
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/myAccount/documents"
        self.token = api_key

        try:
            response = requests.get(url, headers=self.headers, timeout=4)
            response.raise_for_status()
            return response.json()

        except (RequestException, Timeout):
            logger.error(
                "Erro ao consultar documentos da subconta profissional", exc_info=True
            )

    def create_key_EVP(self, api_key: str) -> Optional[dict]:
        """
        Creates a new random PIX key (EVP) for the professional (white label account).
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/pix/addressKeys"
        self.token = api_key

        # the payload will be the same for every request,
        # since Asaas can only create EVP keys via API at the moment.
        payload = {"type": "EVP"}

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=4)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout):
            logger.error("Erro ao criar chave EVP na Asaas API", exc_info=True)
            return None

    def list_active_EVP_keys(self, api_key: str) -> Optional[dict]:
        """
        List all active PIX EVP keys for the professional (white label account).
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/pix/addressKeys?status=ACTIVE"
        self.token = api_key

        try:
            response = requests.post(url, headers=self.headers, timeout=4)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout):
            logger.error("Erro ao listar chaves EVP na Asaas API", exc_info=True)
            return None

    def create_payment_PIX(
        self, customer_id: str, value: float, dueDate: datetime
    ) -> Optional[dict]:
        """
        Creates a new PIX payment.
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/payments"

        payload = {
            "customer": customer_id,
            "billingType": "PIX",
            "value": value,
            "dueDate": dueDate,
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=4)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout):
            logger.error("Erro ao criar cobrança PIX na Asaas API", exc_info=True)
            return None

    def create_payment_credit_card(
        self,
        customer_id: str,
        value: float,
        dueDate: datetime,
        creditCard: CreditCard,
        creditCardHolderInfo: CreditCardHolderInfo,
    ) -> Optional[dict]:
        """
        Creates a new credit card payment.
        Returns the JSON response from Asaas, or None if failed.
        """
        url = f"{self.BASE_URL}/{self.version}/payments"

        payload = {
            "customer": customer_id,
            "value": value,
            "dueDate": dueDate,
            "creditCard": creditCard,
            "creditCardHolderInfo": creditCardHolderInfo,
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=4)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout):
            logger.error(
                "Erro ao criar cobrança cartão de crédito na Asaas API", exc_info=True
            )
            return None
