class NotificationService:
    def send_email(self, to_email: str, subject: str, body: str):
        # Code to send email
        print(f"Sending email to {to_email}: {subject} - {body}")

    def send_sms(self, to_phone: str, message: str):
        # Code to send SMS
        print(f"Sending SMS to {to_phone}: {message}")
