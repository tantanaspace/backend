from django.core.management.base import BaseCommand

from apps.notifications.models import NotificationTemplate


class Command(BaseCommand):
    help = "Load default notification templates (booking project)"

    def handle(self, *args, **options):
        templates = [
            # Booking lifecycle
            {
                "type": "booking_created",
                "title": "Booking confirmed - {restaurant_name}",
                "title_en": "Booking confirmed - {restaurant_name}",
                "title_ru": "Бронирование подтверждено - {restaurant_name}",
                "title_uz": "Buyurtma tasdiqlandi - {restaurant_name}",
                "body_text": (
                    "Your table is booked for {guest_count} on {date} at {time}. "
                    "Reservation name: {customer_name}. "
                    "Address: {restaurant_address}."
                ),
                "body_text_en": (
                    "Your table is booked for {guest_count} on {date} at {time}. "
                    "Reservation name: {customer_name}. "
                    "Address: {restaurant_address}."
                ),
                "body_text_ru": (
                    "Ваш стол забронирован на {guest_count} гостей {date} в {time}. "
                    "Имя брони: {customer_name}. "
                    "Адрес: {restaurant_address}."
                ),
                "body_text_uz": (
                    "{date} kuni soat {time} da {guest_count} kishi uchun stol band qilindi. "
                    "Bron nomi: {customer_name}. "
                    "Manzil: {restaurant_address}."
                ),
            },
            {
                "type": "booking_reminder",
                "title": "Reminder: your booking today - {restaurant_name}",
                "title_en": "Reminder: your booking today - {restaurant_name}",
                "title_ru": "Напоминание: ваше бронирование сегодня - {restaurant_name}",
                "title_uz": "Eslatma: bugungi bron - {restaurant_name}",
                "body_text": (
                    "Reminder: your booking is today at {time} for {guest_count}. "
                    "Reservation name: {customer_name}."
                ),
                "body_text_en": (
                    "Reminder: your booking is today at {time} for {guest_count}. "
                    "Reservation name: {customer_name}."
                ),
                "body_text_ru": (
                    "Напоминание: ваше бронирование сегодня в {time} для {guest_count} гостей. "
                    "Имя брони: {customer_name}."
                ),
                "body_text_uz": (
                    "Eslatma: bugun soat {time} da {guest_count} kishi uchun broningiz mavjud. "
                    "Bron nomi: {customer_name}."
                ),
            },
            {
                "type": "booking_updated",
                "title": "Booking updated - {restaurant_name}",
                "title_en": "Booking updated - {restaurant_name}",
                "title_ru": "Бронирование обновлено - {restaurant_name}",
                "title_uz": "Bron yangilandi - {restaurant_name}",
                "body_text": (
                    "Your booking has been updated to {date} at {time} for {guest_count}. "
                    "Reservation name: {customer_name}."
                ),
                "body_text_en": (
                    "Your booking has been updated to {date} at {time} for {guest_count}. "
                    "Reservation name: {customer_name}."
                ),
                "body_text_ru": (
                    "Ваше бронирование обновлено на {date} в {time} для {guest_count} гостей. "
                    "Имя брони: {customer_name}."
                ),
                "body_text_uz": (
                    "Broningiz {date} kuni soat {time} ga {guest_count} kishi uchun yangilandi. "
                    "Bron nomi: {customer_name}."
                ),
            },
            {
                "type": "booking_cancelled",
                "title": "Booking cancelled - {restaurant_name}",
                "title_en": "Booking cancelled - {restaurant_name}",
                "title_ru": "Бронирование отменено - {restaurant_name}",
                "title_uz": "Bron bekor qilindi - {restaurant_name}",
                "body_text": (
                    "Your booking for {date} at {time} has been cancelled. "
                    "If this is a mistake, please contact us."
                ),
                "body_text_en": (
                    "Your booking for {date} at {time} has been cancelled. "
                    "If this is a mistake, please contact us."
                ),
                "body_text_ru": (
                    "Ваше бронирование на {date} в {time} было отменено. "
                    "Если это ошибка, пожалуйста, свяжитесь с нами."
                ),
                "body_text_uz": (
                    "{date} kuni {time} ga bo‘lgan broningiz bekor qilindi. "
                    "Agar bu xato bo‘lsa, iltimos, biz bilan bog‘laning."
                ),
            },
            {
                "type": "table_ready",
                "title": "Your table is ready - {restaurant_name}",
                "title_en": "Your table is ready - {restaurant_name}",
                "title_ru": "Ваш стол готов - {restaurant_name}",
                "title_uz": "Sizning stolingiz tayyor - {restaurant_name}",
                "body_text": (
                    "Your table is ready. Please proceed to the host stand. "
                    "Reservation name: {customer_name}."
                ),
                "body_text_en": (
                    "Your table is ready. Please proceed to the host stand. "
                    "Reservation name: {customer_name}."
                ),
                "body_text_ru": (
                    "Ваш стол готов. Пожалуйста, пройдите к стойке администратора. "
                    "Имя брони: {customer_name}."
                ),
                "body_text_uz": (
                    "Stolingiz tayyor. Iltimos, administrator yoniga boring. "
                    "Bron nomi: {customer_name}."
                ),
            },
            # Billing lifecycle
            {
                "type": "bill_opened",
                "title": "Bill opened - {restaurant_name}",
                "title_en": "Bill opened - {restaurant_name}",
                "title_ru": "Счёт открыт - {restaurant_name}",
                "title_uz": "Hisob ochildi - {restaurant_name}",
                "body_text": (
                    "Your bill has been opened. Table: {table_number}. Server: {server_name}. "
                    "You can view and pay through the app."
                ),
                "body_text_en": (
                    "Your bill has been opened. Table: {table_number}. Server: {server_name}. "
                    "You can view and pay through the app."
                ),
                "body_text_ru": (
                    "Ваш счёт открыт. Стол: {table_number}. Официант: {server_name}. "
                    "Вы можете просмотреть и оплатить через приложение."
                ),
                "body_text_uz": (
                    "Hisob ochildi. Stol: {table_number}. Ofitsiant: {server_name}. "
                    "Ilova orqali ko‘rish va to‘lash mumkin."
                ),
            },
            {
                "type": "bill_updated",
                "title": "Bill updated - {restaurant_name}",
                "title_en": "Bill updated - {restaurant_name}",
                "title_ru": "Счёт обновлён - {restaurant_name}",
                "title_uz": "Hisob yangilandi - {restaurant_name}",
                "body_text": (
                    "Your bill has been updated. New total: {bill_total}. "
                    "Items added/removed: {bill_change_summary}."
                ),
                "body_text_en": (
                    "Your bill has been updated. New total: {bill_total}. "
                    "Items added/removed: {bill_change_summary}."
                ),
                "body_text_ru": (
                    "Ваш счёт обновлён. Новый итог: {bill_total}. "
                    "Изменения: {bill_change_summary}."
                ),
                "body_text_uz": (
                    "Hisob yangilandi. Yangi summa: {bill_total}. "
                    "O‘zgarishlar: {bill_change_summary}."
                ),
            },
            {
                "type": "bill_closed",
                "title": "Bill closed - {restaurant_name}",
                "title_en": "Bill closed - {restaurant_name}",
                "title_ru": "Счёт закрыт - {restaurant_name}",
                "title_uz": "Hisob yopildi - {restaurant_name}",
                "body_text": (
                    "Your bill has been closed. Total paid: {bill_total}. "
                    "Thank you for visiting us!"
                ),
                "body_text_en": (
                    "Your bill has been closed. Total paid: {bill_total}. "
                    "Thank you for visiting us!"
                ),
                "body_text_ru": (
                    "Ваш счёт закрыт. Итоговая сумма: {bill_total}. "
                    "Спасибо за визит!"
                ),
                "body_text_uz": (
                    "Hisob yopildi. To‘langan summa: {bill_total}. "
                    "Tashrifingiz uchun rahmat!"
                ),
            },
            # Payments
            {
                "type": "payment_received",
                "title": "Payment received - {restaurant_name}",
                "title_en": "Payment received - {restaurant_name}",
                "title_ru": "Платёж получен - {restaurant_name}",
                "title_uz": "To‘lov qabul qilindi - {restaurant_name}",
                "body_text": (
                    "We have received your payment of {amount} via {method}. "
                    "Receipt: {receipt_number}."
                ),
                "body_text_en": (
                    "We have received your payment of {amount} via {method}. "
                    "Receipt: {receipt_number}."
                ),
                "body_text_ru": (
                    "Мы получили ваш платёж на сумму {amount} через {method}. "
                    "Квитанция: {receipt_number}."
                ),
                "body_text_uz": (
                    "{amount} miqdoridagi to‘lovingiz {method} orqali qabul qilindi. "
                    "Chek: {receipt_number}."
                ),
            },
            {
                "type": "payment_failed",
                "title": "Payment failed - {restaurant_name}",
                "title_en": "Payment failed - {restaurant_name}",
                "title_ru": "Платёж не прошёл - {restaurant_name}",
                "title_uz": "To‘lov amalga oshmadi - {restaurant_name}",
                "body_text": (
                    "Your payment of {amount} via {method} failed. "
                    "Please try again or use another method."
                ),
                "body_text_en": (
                    "Your payment of {amount} via {method} failed. "
                    "Please try again or use another method."
                ),
                "body_text_ru": (
                    "Ваш платёж на сумму {amount} через {method} не прошёл. "
                    "Пожалуйста, попробуйте снова или используйте другой способ."
                ),
                "body_text_uz": (
                    "{amount} miqdoridagi {method} orqali to‘lov amalga oshmadi. "
                    "Iltimos, yana urinib ko‘ring yoki boshqa usuldan foydalaning."
                ),
            },
        ]

        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                type=template_data["type"], defaults=template_data
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created template for {template.get_type_display()}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Template for {template.get_type_display()} already exists"
                    )
                )
