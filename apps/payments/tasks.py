from core.celery import app
from apps.notifications.models import Notification
from apps.payments.models import PaymentTransaction



@app.task
def send_payment_successful_notification(transaction_id: int):
    transaction = PaymentTransaction.objects.get(pk=transaction_id)
    notification = Notification.objects.create(
        type=Notification.NotificationType.PAYMENT_RECEIVED,
        title="To'lov muvaffaqiyatli amalga oshirildi",
        title_uz="To'lov muvaffaqiyatli amalga oshirildi",
        title_ru="Оплата прошла успешно",
        title_en="Payment successful",
        title_zh_cn="支付成功",
        body_text=f"Balansingiz {transaction.amount} so'mga muvaffaqiyatli to'ldirildi",
        body_text_uz=f"Balansingiz {transaction.amount} so'mga muvaffaqiyatli to'ldirildi",
        body_text_ru=f"Ваш баланс успешно пополнен на {transaction.amount} сум",
        body_text_en=f"Your balance was successfully topped up by {transaction.amount} sum",
        body_text_zh_cn=f"您的余额已成功充值 {transaction.amount} 元",
        body_html=f"Balansingiz {transaction.amount} so'mga muvaffaqiyatli to'ldirildi",
        body_html_uz=f"Balansingiz {transaction.amount} so'mga muvaffaqiyatli to'ldirildi",
        body_html_ru=f"Ваш баланс успешно пополнен на {transaction.amount} сум",
        body_html_en=f"Your balance was successfully topped up by {transaction.amount} sum",
        body_html_zh_cn=f"您的余额已成功充值 {transaction.amount} 元",
        is_for_everyone=False,
        only_push=False,
        data={
            'transaction_id': transaction.id,
        },
    )

    notification.users.set([transaction.user])

    return str(dict(success=True, transaction_id=transaction.id))