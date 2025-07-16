import os
from dotenv import load_dotenv
from email_service import EmailService

# Load environment variables
load_dotenv()

def test_email_methods():
    """Test both REST API and SMTP email delivery methods"""
    print("🧪 Testing Enhanced Email Service...\n")
    
    email_service = EmailService()
    
    # Test email details
    test_email = "test@example.com"
    subject = "🧪 RescueRadar Email Test"
    html_content = """
    <h2 style="color: #16a34a;">📧 Email Service Test</h2>
    <p>This is a test email from RescueRadar's enhanced email service.</p>
    <div style="background: #f0fdf4; padding: 15px; border-radius: 6px; margin: 10px 0;">
        <p><strong>✅ If you receive this email, the service is working correctly!</strong></p>
    </div>
    <p>Testing both REST API and SMTP delivery methods.</p>
    <p>Best regards,<br>RescueRadar Team</p>
    """
    
    print("📧 Testing Brevo REST API method...")
    api_result = email_service.send_email_via_api(test_email, subject + " (API)", html_content)
    
    if api_result['success']:
        print(f"✅ REST API: Email sent successfully!")
        print(f"   Message ID: {api_result['message_id']}")
    else:
        print(f"❌ REST API: Failed - {api_result['error']}")
    
    print("\n📨 Testing SMTP method...")
    smtp_result = email_service.send_email_via_smtp(test_email, subject + " (SMTP)", html_content)
    
    if smtp_result['success']:
        print(f"✅ SMTP: Email sent successfully!")
        print(f"   Message ID: {smtp_result['message_id']}")
    else:
        print(f"❌ SMTP: Failed - {smtp_result['error']}")
    
    print("\n🔄 Testing automatic fallback...")
    fallback_result = email_service.send_email(test_email, subject + " (Auto-Fallback)", html_content)
    
    if fallback_result['success']:
        print(f"✅ Auto-Fallback: Email sent successfully via {fallback_result['method']}!")
        print(f"   Message ID: {fallback_result['message_id']}")
    else:
        print(f"❌ Auto-Fallback: Failed - {fallback_result['error']}")
    
    print("\n📊 Test Summary:")
    print(f"   REST API: {'✅ Working' if api_result['success'] else '❌ Failed'}")
    print(f"   SMTP: {'✅ Working' if smtp_result['success'] else '❌ Failed'}")
    print(f"   Auto-Fallback: {'✅ Working' if fallback_result['success'] else '❌ Failed'}")
    
    if api_result['success'] or smtp_result['success']:
        print(f"\n🎉 Email service is operational!")
        print(f"   📬 Check {test_email} for test emails")
    else:
        print(f"\n⚠️  Both methods failed. Check configuration.")

if __name__ == "__main__":
    test_email_methods()
