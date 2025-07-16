import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_brevo_email():
    """Test Brevo email API"""
    try:
        api_key = os.getenv('BREVO_API_KEY')
        print(f"API Key: {api_key[:20]}..." if api_key else "No API Key found")
        
        url = "https://api.brevo.com/v3/smtp/email"
        
        headers = {
            'accept': 'application/json',
            'api-key': api_key,
            'content-type': 'application/json'
        }
        
        # Test email data
        email_data = {
            'sender': {
                'name': 'RescueRadar Test',
                'email': 'alerts@rescueradar.org'
            },
            'to': [{'email': 'test@example.com'}],  # Change this to your email for testing
            'subject': 'Test Email from RescueRadar',
            'htmlContent': '<h1>Test Email</h1><p>This is a test email from RescueRadar backend.</p>',
            'textContent': 'Test Email - This is a test email from RescueRadar backend.'
        }
        
        print("Sending test email...")
        response = requests.post(url, headers=headers, json=email_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Email sending failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email: {str(e)}")
        return False

def test_whatsapp():
    """Test WhatsApp API"""
    try:
        from twilio.rest import Client as TwilioClient
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_whatsapp = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        print(f"Twilio SID: {account_sid[:10]}..." if account_sid else "No Twilio SID found")
        print(f"WhatsApp Number: {from_whatsapp}")
        
        client = TwilioClient(account_sid, auth_token)
        
        # Test with your real WhatsApp number
        test_message = client.messages.create(
            body="Test message from RescueRadar backend!",
            from_=from_whatsapp,
            to="whatsapp:+919892130048"  # Your WhatsApp number
        )
        
        print(f"✅ WhatsApp message sent! SID: {test_message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing WhatsApp: {str(e)}")
        return False

def test_supabase():
    """Test Supabase connection"""
    try:
        from supabase import create_client, Client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_API_KEY')
        
        print(f"Supabase URL: {url}")
        print(f"API Key: {key[:20]}..." if key else "No API Key found")
        
        supabase: Client = create_client(url, key)
        
        # Test connection by trying to fetch from reports table
        result = supabase.table('reports').select('id').limit(1).execute()
        
        print(f"✅ Supabase connection successful!")
        print(f"Table accessible: {len(result.data) >= 0}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing RescueRadar API Credentials...\n")
    
    print("1. Testing Brevo Email API:")
    test_brevo_email()
    print()
    
    print("2. Testing Supabase Database:")
    test_supabase()
    print()
    
    print("3. Testing WhatsApp API:")
    test_whatsapp()
    print()
    
    print("🏁 Test completed!")
