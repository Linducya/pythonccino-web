from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64
import os
from email.mime.multipart import MIMEMultipart

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

CLIENT_SECRET_FILE = os.environ.get('GOOGLE_CLIENT_SECRET_FILE')
if not CLIENT_SECRET_FILE:
    raise RuntimeError("GOOGLE_CLIENT_SECRET_FILE environment variable must be set and point to your client_secret_*.json file.")
TOKEN_FILE = os.environ.get('GOOGLE_TOKEN_FILE')
if not TOKEN_FILE:
    raise RuntimeError("GOOGLE_TOKEN_FILE environment variable must be set and point to your token.json file.")
SMTP_EMAIL = os.environ.get('SMTP_EMAIL')
if not SMTP_EMAIL:
    raise RuntimeError("SMTP_EMAIL environment variable must be set.")

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_email(to, subject, body):
    service = get_gmail_service()
    message = MIMEText(body)
    message['to'] = to
    message['from'] = SMTP_EMAIL
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()

def send_email_confirmation(name, email, order_details, order_type="food"):
    sender_email = SMTP_EMAIL
    receiver_email = email


    # Extract the order number from the first item in order_details
    order_number = order_details[0].get("order_number", "N/A")

    # Create the email content
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Order Confirmation - Order Number: {order_number}"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Dear {name},\n\nThank you for your order!\n\nOrder Number: {order_number}\n\nOrder Details:\n"
    html = f"""\
    <html><body><p>Dear {name},<br><br>
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

    # Send the email using Gmail API
    try:
        service = get_gmail_service()
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw_message}
        user_id = 'me'
        sent_message = service.users().messages().send(userId=user_id, body=body).execute()
        return sent_message
    except Exception:
        return None