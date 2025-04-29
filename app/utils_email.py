import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_confirmation(name, email, order_details, order_type="food"):
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    receiver_email = email

    if not sender_email or not sender_password:
        raise ValueError("SENDER_EMAIL or SENDER_PASSWORD environment variables are not set.")

    # Extract the order number from the first item in order_details
    order_number = order_details[0].get("order_number", "N/A")

    # Create the email content
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Order Confirmation - Order Number: {order_number}"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Dear {name},\n\nThank you for your order!\n\nOrder Number: {order_number}\n\nOrder Details:\n"
    html = f"""\
    <html>
    <body>
        <p>Dear {name},<br><br>
           Thank you for your order!<br><br>
           <b>Order Number:</b> {order_number}<br><br>
           <b>Order Details:</b><br>
    """
    total_amount = 0
    for item in order_details:
        if order_type == "food":
            price = item.get("price", 0)
            total_amount += price * item['quantity']
            text += f"{item['quantity']} x {item['food_item']} - {item['description']} - £{price}\n"
            html += f"{item['quantity']} x {item['food_item']}<br>Description: {item['description']}<br>Price: £{price}<br><br>"
        elif order_type == "book":
            price = item.get("price", 0)
            total_amount += price * item['quantity']
            text += f"{item['quantity']} x {item['book_title']} - £{price}\n"
            html += f"{item['quantity']} x {item['book_title']}<br>Price: £{price}<br><br>"
    text += f"\nTotal Amount: £{total_amount}\n\nBest regards,\nThe Pythonccino Food & Book Cafe"
    html += f"<br>Total Amount: £{total_amount}<br><br>Best regards,<br>The Pythonccino Food & Book Cafe</p></body></html>"

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # Send the email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during SMTP login: {e}")
        raise
