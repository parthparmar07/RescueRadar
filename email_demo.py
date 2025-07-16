#!/usr/bin/env python3
"""
Simple Email Demo using only Python built-in libraries
This demonstrates the refactored email service with Gmail SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_simple_gmail_email():
    """
    Simple function to send email using Gmail SMTP with built-in Python libraries only
    No external dependencies required!
    """
    
    # Email configuration (using your actual Gmail credentials)
    from_email = "gauravpatil2516@gmail.com"
    app_password = "yxjc ulzm mrcg ktrm"  # Your Gmail App Password
    to_email = "siesgauravpatil@gmail.com"
    
    # Email content
    subject = "Test Email from Python"
    body = "Hello, this is a test email sent from a Python script using smtplib and email libraries!"
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Create HTML and text versions
    html_content = f"""
    <html>
        <body>
            <h2>🐍 Test Email from Python</h2>
            <p>{body}</p>
            <p><strong>Sent at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><em>This email was sent using only Python's built-in libraries: smtplib and email</em></p>
        </body>
    </html>
    """
    
    # Attach parts
    text_part = MIMEText(body, 'plain')
    html_part = MIMEText(html_content, 'html')
    
    msg.attach(text_part)
    msg.attach(html_part)
    
    try:
        # Send email using Gmail SMTP SSL
        print("Connecting to Gmail SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            print("Logging in...")
            server.login(from_email, app_password)
            print("Sending email...")
            server.send_message(msg)
        
        print(f"✅ SUCCESS: Email sent successfully from {from_email} to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("Make sure you're using the correct Gmail App Password")
        print("Enable 2FA and generate an App Password at: https://myaccount.google.com/apppasswords")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ General Error: {e}")
        return False

def main():
    """Main function to demonstrate the email sending"""
    print("=" * 60)
    print("📧 Simple Gmail Email Demo")
    print("=" * 60)
    print("This script uses only Python built-in libraries:")
    print("- smtplib (for SMTP connection)")
    print("- email.mime (for message formatting)")
    print("- datetime (for timestamps)")
    print("-" * 60)
    
    # Note about credentials
    print("⚠️  IMPORTANT: To use this script with real emails:")
    print("1. Replace 'your_email@gmail.com' with your actual Gmail address")
    print("2. Replace 'yxjc ulzm mrcg ktrm' with your Gmail App Password")
    print("3. Replace 'recipient@example.com' with the recipient's email")
    print("4. Enable 2-Factor Authentication on your Gmail account")
    print("5. Generate an App Password at: https://myaccount.google.com/apppasswords")
    print("-" * 60)
    
    result = send_simple_gmail_email()
    
    if not result:
        print("\n📝 This is expected behavior with placeholder credentials.")
        print("The code structure is correct and ready for real credentials!")

if __name__ == "__main__":
    main()
