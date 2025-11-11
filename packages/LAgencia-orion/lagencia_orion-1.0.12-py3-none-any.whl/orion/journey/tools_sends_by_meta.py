import json
from typing import List, Optional

import requests
from pydantic import BaseModel


class RequestAPIMeta(BaseModel):
    phone: str
    code: Optional[str] = None
    token: Optional[str] = None
    price: Optional[int] = None
    old_price: Optional[int] = None
    week: Optional[int] = None
    option: Optional[str] = None


def sends_nuevo_ingreso(record: RequestAPIMeta):
    url = "https://smart-home.com.co/WhatsAppTemplate.aspx?method=POST"

    payload = json.dumps({"name": "nuevo_ingreso", "contactId": record.phone, "clientId": "573184444845", "addMessage": False, "components": [{"type": "button", "index": "0", "parameter_name": "id", "value": record.code}]})
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def sends_modifica_precio(record: RequestAPIMeta):
    url = "https://smart-home.com.co/WhatsAppTemplate.aspx?method=POST"

    payload = json.dumps({"name": "modifica_precio", "contactId": record.phone, "clientId": "573184444845", "addMessage": False, "components": [{"type": "button", "index": "0", "parameter_name": "id", "value": record.code}]})
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def sends_45a90_dias_semana1(record: RequestAPIMeta):
    url = "https://smart-home.com.co/WhatsAppTemplate.aspx?method=POST"

    payload = json.dumps({"name": "45a90_dias_semana1", "contactId": record.phone, "clientId": "573184444845", "addMessage": False})
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def sends_art_est_arrend(record: RequestAPIMeta):
    url = "https://smart-home.com.co/WhatsAppTemplate.aspx?method=POST"

    payload = json.dumps({"name": "art_est_arrend", "contactId": record.phone, "clientId": "573184444845", "addMessage": False})
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def sends_import_contrato(record: RequestAPIMeta):
    url = "https://smart-home.com.co/WhatsAppTemplate.aspx?method=POST"

    payload = json.dumps({"name": "import_contrato", "contactId": record.phone, "clientId": "573184444845", "addMessage": False})
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def sends_nuevos_ingresos(record: RequestAPIMeta):
    url = "https://smart-home.com.co/WhatsAppTemplate.aspx?method=POST"

    payload = json.dumps({"name": "nuevos_ingresos", "contactId": record.phone, "clientId": "573184444845", "addMessage": False, "components": [{"type": "button", "index": "0", "parameter_name": "id", "value": record.token}]})
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


class SendMessageByAPIMeta:
    _function_by_template = []

    def __init__(self, templates: List[str], record: RequestAPIMeta):
        self._function_by_template.clear()
        self.record = record

        for template in templates:
            self._function_by_template.append(self.get_funtions_by_sends(template))

    def send(self):
        for function in self._function_by_template:
            print(f"Haciendo envio con funcion {function} con data {self.record.phone, self.record.code, self.record.token, self.record.week}")
            function(self.record)
            print()

    def get_funtions_by_sends(self, template_name: str):
        match template_name:
            case "nuevo_ingreso":
                return sends_nuevo_ingreso

            case "nuevos_ingresos":
                return sends_nuevos_ingresos

            case "modifica_precio":
                return sends_modifica_precio

            case "45a90_dias_semana1":
                return sends_45a90_dias_semana1

            case "art_est_arrend":
                return sends_art_est_arrend

            case "import_contrato":
                return sends_import_contrato

            case _:
                raise


if __name__ == "__main__":
    code = "73498"
    phone = "573103738772"
    # sends_new_revenues(phone=phone, code=code)
    sends_modifica_precio(phone=phone, code=code)
