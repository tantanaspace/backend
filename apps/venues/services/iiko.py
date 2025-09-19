import requests
import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class IikoTable:
    id: str
    name: str
    number: str
    seats_count: int
    status: str
    zone_id: str
    zone_name: str


@dataclass
class IikoReservation:
    id: str
    table_ids: List[str]
    customer_name: str
    customer_phone: str
    guests_count: int
    start_time: datetime.datetime
    duration_minutes: int
    status: str
    comment: Optional[str] = None


class IikoCloudAPI:
    """
    Комплексный класс для работы с iikoCloud API с фокусом на бронирования и управление счетами.
    Основан на анализе Postman коллекции.
    """

    def __init__(self, api_login: str = 'bbc6101b17a04c42b5bcc5ef14d1a145', base_url: str = "https://api-ru.iiko.services"):
        self.api_login = api_login
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime.datetime] = None
        self.organization_id: Optional[str] = None

    # ------------------------
    # Базовые методы
    # ------------------------
    def _auth_headers(self) -> Dict[str, str]:
        """Возвращает заголовки авторизации"""
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json"
        }

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Any:
        """Универсальный метод для POST запросов"""
        url = f"{self.base_url}{endpoint}"
        headers = self._auth_headers()
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()

    def get_token(self) -> str:
        """Получение и кэширование токена"""
        if (self.token and self.token_expiry and 
            datetime.datetime.utcnow() < self.token_expiry):
            return self.token

        url = f"{self.base_url}/api/1/access_token"
        payload = {"apiLogin": self.api_login}
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        self.token = data["token"]
        self.token_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=19)
        
        return self.token

    def renew_token(self) -> str:
        """Обновление токена"""
        self.token = None
        self.token_expiry = None
        self.get_token()
        return self.token

    # ------------------------
    # Организации и структура
    # ------------------------
    def get_organizations(self) -> List[Dict[str, Any]]:
        """Получение списка организаций"""
        return self._post("/api/1/organizations", {})

    def set_organization(self, org_id: Optional[str] = None) -> None:
        """
        Установка организации по умолчанию.
        Если org_id не указан, берет первую из доступных.
        """
        if org_id:
            self.organization_id = org_id
        else:
            orgs = self.get_organizations()
            if orgs and orgs[0].get('id'):
                self.organization_id = orgs[0]['id']
            else:
                raise ValueError("No organizations available")

    def get_terminal_groups(self, org_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получение групп терминалов"""
        org_id = org_id or self.organization_id
        if not org_id:
            self.set_organization()
            org_id = self.organization_id
            
        return self._post("/api/1/terminal_groups", {
            "organizationIds": [org_id]
        })

    # ------------------------
    # Работа со столами и зонами
    # ------------------------
    def get_restaurant_sections(self, terminal_group_id: str, 
                              return_schema: bool = True,
                              revision: int = 0) -> Dict[str, Any]:
        """
        Получение схемы ресторана (зоны и столы)
        
        Args:
            terminal_group_id: ID группы терминалов
            return_schema: Возвращать схему расположения
            revision: Ревизия для инкрементального обновления
        """
        return self._post("/api/1/reserve/available_restaurant_sections", {
            "terminalGroupIds": [terminal_group_id],
            "returnSchema": return_schema,
            "revision": revision
        })

    def get_tables(self, org_id: Optional[str] = None) -> List[IikoTable]:
        """Получение списка всех столов с информацией о статусе"""
        org_id = org_id or self.organization_id
        if not org_id:
            self.set_organization()
            org_id = self.organization_id
            
        response = self._post("/api/1/reserve/tables", {
            "organizationIds": [org_id]
        })
        
        tables = []
        for restaurant in response.get('restaurantSections', []):
            zone_id = restaurant.get('id')
            zone_name = restaurant.get('name', '')
            
            for table in restaurant.get('tables', []):
                tables.append(IikoTable(
                    id=table.get('id'),
                    name=table.get('name', ''),
                    number=table.get('number', ''),
                    seats_count=table.get('seatsCount', 0),
                    status=table.get('status', 'Unknown'),
                    zone_id=zone_id,
                    zone_name=zone_name
                ))
        
        return tables

    def get_available_tables(self, terminal_group_id: str, 
                           start_time: datetime.datetime,
                           duration_minutes: int,
                           guests_count: int) -> List[Dict[str, Any]]:
        """
        Получение доступных столов для бронирования
        
        Args:
            terminal_group_id: ID группы терминалов
            start_time: Время начала брони
            duration_minutes: Продолжительность в минутах
            guests_count: Количество гостей
        """
        return self._post("/api/1/reserve/available_tables", {
            "terminalGroupId": terminal_group_id,
            "startTime": start_time.isoformat(),
            "durationInMinutes": duration_minutes,
            "guestsCount": guests_count
        })

    # ------------------------
    # Управление бронированиями
    # ------------------------
    def create_reservation(self,
                         org_id: str,
                         terminal_group_id: str,
                         table_ids: List[str],
                         customer_name: str,
                         customer_phone: str,
                         start_time: datetime.datetime,
                         duration_minutes: int,
                         guests_count: int,
                         comment: Optional[str] = None,
                         should_remind: Optional[int] = None,
                         items: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Создание бронирования стола
        
        Args:
            org_id: ID организации
            terminal_group_id: ID группы терминалов
            table_ids: Список ID столов
            customer_name: Имя клиента
            customer_phone: Телефон клиента
            start_time: Время начала
            duration_minutes: Продолжительность
            guests_count: Количество гостей
            comment: Комментарий к брони
            should_remind: За сколько минут напомнить
            items: Предзаказ блюд
        """
        payload = {
            "organizationId": org_id,
            "terminalGroupId": terminal_group_id,
            "tableIds": table_ids,
            "customer": {
                "name": customer_name,
                "phone": customer_phone
            },
            "estimatedStartTime": start_time.isoformat(),
            "durationInMinutes": duration_minutes,
            "guests": {"count": guests_count},
            "shouldRemind": should_remind
        }
        
        if comment:
            payload["comment"] = comment
            
        if items:
            payload["order"] = {"items": items}
            
        return self._post("/api/1/reserve/create", payload)

    def get_reservations(self, org_id: str,
                       from_date: datetime.datetime,
                       to_date: datetime.datetime) -> List[IikoReservation]:
        """Получение списка бронирований за период"""
        response = self._post("/api/1/reserve/reserves", {
            "organizationIds": [org_id],
            "from": from_date.isoformat(),
            "to": to_date.isoformat()
        })
        
        reservations = []
        for reserve in response.get('reserves', []):
            reservations.append(IikoReservation(
                id=reserve.get('id'),
                table_ids=reserve.get('tableIds', []),
                customer_name=reserve.get('customer', {}).get('name', ''),
                customer_phone=reserve.get('customer', {}).get('phone', ''),
                guests_count=reserve.get('guests', {}).get('count', 0),
                start_time=datetime.datetime.fromisoformat(
                    reserve.get('estimatedStartTime').replace('Z', '+00:00')
                ),
                duration_minutes=reserve.get('durationInMinutes', 0),
                status=reserve.get('status', 'Unknown'),
                comment=reserve.get('comment')
            ))
        
        return reservations

    def close_reservation(self, org_id: str, reserve_id: str) -> Dict[str, Any]:
        """Закрытие бронирования"""
        return self._post("/api/1/reserve/close", {
            "organizationId": org_id,
            "reserveIds": [reserve_id]
        })

    def update_reservation(self, org_id: str, reserve_id: str,
                         update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление информации о бронировании"""
        payload = {
            "organizationId": org_id,
            "id": reserve_id,
            **update_data
        }
        return self._post("/api/1/reserve/update", payload)

    # ------------------------
    # Управление заказами (счетами)
    # ------------------------
    def create_order(self, org_id: str, terminal_group_id: str,
                   table_ids: List[str], items: List[Dict],
                   customer: Optional[Dict] = None,
                   phone: Optional[str] = None,
                   payments: Optional[List[Dict]] = None,
                   discounts: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Создание заказа (счета) для стола
        
        Args:
            org_id: ID организации
            terminal_group_id: ID группы терминалов
            table_ids: Список ID столов
            items: Список позиций заказа
            customer: Информация о клиенте
            phone: Телефон клиента
            payments: Способы оплаты
            discounts: Скидки
        """
        payload = {
            "organizationId": org_id,
            "terminalGroupId": terminal_group_id,
            "order": {
                "tableIds": table_ids,
                "items": items
            }
        }
        
        if customer:
            payload["order"]["customer"] = customer
            
        if phone:
            payload["order"]["phone"] = phone
            
        if payments:
            payload["order"]["payments"] = payments
            
        if discounts:
            payload["order"]["discountsInfo"] = discounts
            
        return self._post("/api/1/order/create", payload)

    def get_order_by_id(self, org_id: str, order_id: str) -> Dict[str, Any]:
        """Получение информации о заказе по ID"""
        return self._post("/api/1/order/by_id", {
            "organizationIds": [org_id],
            "orderIds": [order_id]
        })

    def get_orders_by_table(self, org_id: str, table_ids: List[str],
                          statuses: Optional[List[str]] = None) -> Dict[str, Any]:
        """Получение заказов по номерам столов"""
        payload = {
            "organizationIds": [org_id],
            "tableIds": table_ids
        }
        
        if statuses:
            payload["status"] = statuses
            
        return self._post("/api/1/order/by_table", payload)

    def close_order(self, org_id: str, order_id: str) -> Dict[str, Any]:
        """Закрытие заказа (счета)"""
        return self._post("/api/1/order/close", {
            "organizationId": org_id,
            "orderId": order_id
        })

    def change_order_payments(self, org_id: str, order_id: str,
                            payments: List[Dict]) -> Dict[str, Any]:
        """Изменение способов оплаты в заказе"""
        return self._post("/api/1/order/change_payments", {
            "organizationId": org_id,
            "orderId": order_id,
            "payments": payments
        })

    def init_order_by_table(self, org_id: str, terminal_group_id: str,
                          table_ids: List[str]) -> Dict[str, Any]:
        """
        Инициализация заказов по столам (проталкивание в API)
        """
        return self._post("/api/1/order/init_by_table", {
            "organizationId": org_id,
            "terminalGroupId": terminal_group_id,
            "tableIds": table_ids
        })

    # ------------------------
    # Дополнительные методы
    # ------------------------
    def get_payment_types(self, org_id: str) -> List[Dict[str, Any]]:
        """Получение типов оплат"""
        return self._post("/api/1/payment_types", {
            "organizationIds": [org_id]
        })

    def get_discounts(self, org_id: str) -> List[Dict[str, Any]]:
        """Получение скидок RMS"""
        return self._post("/api/1/discounts", {
            "organizationIds": [org_id]
        })

    def get_stop_lists(self, org_id: str) -> Dict[str, Any]:
        """Получение стоп-листов"""
        return self._post("/api/1/stop_lists", {
            "organizationIds": [org_id]
        })

    def get_command_status(self, org_id: str, correlation_id: str) -> Dict[str, Any]:
        """Получение статуса операции по correlationId"""
        return self._post("/api/1/commands/status", {
            "organizationId": org_id,
            "correlationId": correlation_id
        })

    # ------------------------
    # Вспомогательные методы
    # ------------------------
    def find_table_by_number(self, table_number: str, 
                           org_id: Optional[str] = None) -> Optional[IikoTable]:
        """Поиск стола по номеру"""
        tables = self.get_tables(org_id)
        for table in tables:
            if table.number == table_number:
                return table
        return None

    def get_tables_by_zone(self, zone_id: str, 
                         org_id: Optional[str] = None) -> List[IikoTable]:
        """Получение столов по зоне"""
        tables = self.get_tables(org_id)
        return [table for table in tables if table.zone_id == zone_id]

    def get_available_tables_for_period(self, terminal_group_id: str,
                                      start_time: datetime.datetime,
                                      end_time: datetime.datetime,
                                      guests_count: int) -> List[Dict[str, Any]]:
        """
        Получение столов, доступных в указанный период
        """
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        return self.get_available_tables(terminal_group_id, start_time, 
                                       duration_minutes, guests_count)