# services/bitrix24.py
import requests
from django.conf import settings


class Bitrix24API:
    def __init__(self):
        self.webhook = settings.BITRIX24_WEBHOOK
        self.enabled = getattr(settings, 'BITRIX24_INTEGRATION_ENABLED', False)

    def _call(self, method, params):
        """Универсальный вызов API Битрикс24"""
        if not self.enabled:
            return {'error': 'Integration disabled'}

        url = f"{self.webhook}{method}"
        try:
            response = requests.post(url, json=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {'error': f'HTTP {response.status_code}', 'text': response.text}
        except requests.exceptions.Timeout:
            return {'error': 'Timeout'}
        except Exception as e:
            return {'error': str(e)}

    def create_contact(self, user):
        """Создание контакта в Битрикс24"""
        phones = []
        if user.phone:
            phones = [{'VALUE': user.phone, 'VALUE_TYPE': 'WORK'}]

        emails = []
        if user.email:
            emails = [{'VALUE': user.email, 'VALUE_TYPE': 'WORK'}]

        params = {
            'fields': {
                'NAME': user.first_name or user.username,
                'LAST_NAME': user.last_name or '',
                'PHONE': phones,
                'EMAIL': emails,
            }
        }
        return self._call('crm.contact.add', params)

    def find_contact_by_phone(self, phone):
        """Поиск контакта по телефону"""
        if not phone:
            return {'result': []}

        params = {
            'filter': {'PHONE': phone},
            'select': ['ID', 'NAME', 'LAST_NAME']
        }
        return self._call('crm.contact.list', params)

    def create_deal(self, appointment, contact_id):
        """Создание сделки из записи"""
        services = appointment.services.all()
        services_names = '\n'.join([f"- {s.name} ({s.price} ₽)" for s in services])
        total_price = sum(s.price for s in services)

        title = f"Запись #{appointment.id} | {appointment.vehicle.brand} {appointment.vehicle.model}"

        params = {
            'fields': {
                'TITLE': title,
                'TYPE_ID': 'SERVICE',
                'STAGE_ID': 'NEW',
                'CONTACT_ID': contact_id,
                'OPPORTUNITY': float(total_price),
                'CURRENCY_ID': 'RUB',
                'UF_CRM_1777118222343': appointment.get_status_display(),
                'UF_CRM_1777118061': appointment.vehicle.brand,
                'UF_CRM_1777118072': appointment.vehicle.model,
                'UF_CRM_1777108833807': float(total_price),
                'UF_CRM_1777108580982': appointment.vehicle.id,
                'COMMENTS': f"""
🚗 АВТОМОБИЛЬ
Марка: {appointment.vehicle.brand} {appointment.vehicle.model}
Год: {appointment.vehicle.year}
Госномер: {appointment.vehicle.license_plate}

📅 ЗАПИСЬ
Дата: {appointment.date}
Время: {appointment.time}
Статус: {appointment.get_status_display()}

🔧 УСЛУГИ
{services_names}

💰 ИТОГО: {total_price} ₽
                """.strip(),
            }
        }
        return self._call('crm.deal.add', params)