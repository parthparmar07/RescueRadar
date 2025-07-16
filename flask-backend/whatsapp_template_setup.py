#!/usr/bin/env python3
"""
WhatsApp Business Template Setup Guide for RescueRadar

This script provides guidance on setting up WhatsApp Business templates
for the RescueRadar application.
"""

import os
import json
from twilio.rest import Client as TwilioClient

def create_template_suggestion():
    """Generate a template suggestion for RescueRadar"""
    
    template_suggestion = {
        "name": "rescue_alert_confirmation",
        "language": "en_US",
        "category": "TRANSACTIONAL",
        "components": [
            {
                "type": "BODY",
                "text": "🆘 RescueRadar Alert Confirmation\n\nYour animal rescue report has been submitted:\n\n📋 Report ID: {{1}}\n📝 Description: {{2}}\n⏰ Submitted: {{3}}\n\n✅ Our rescue network has been notified and will respond ASAP.\n\n🔗 Track: {{4}}\n\n🚨 For emergencies, contact local authorities immediately."
            }
        ]
    }
    
    return template_suggestion

def check_existing_templates():
    """Check what templates are already approved for your Twilio account"""
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            print("❌ Twilio credentials not found in environment variables")
            return None
            
        client = TwilioClient(account_sid, auth_token)
        
        # List approved templates
        templates = client.content.contents.list(limit=20)
        
        print(f"📋 Found {len(templates)} content templates:")
        print("-" * 50)
        
        for template in templates:
            print(f"✅ Template SID: {template.sid}")
            print(f"   Name: {template.friendly_name}")
            print(f"   Language: {template.language}")
            print(f"   Status: {template.approval_requests}")
            print("-" * 30)
            
        return templates
        
    except Exception as e:
        print(f"❌ Error checking templates: {str(e)}")
        return None

def test_whatsapp_connection():
    """Test basic WhatsApp connection"""
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_whatsapp = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        if not all([account_sid, auth_token, from_whatsapp]):
            print("❌ Missing Twilio configuration in environment variables")
            return False
            
        client = TwilioClient(account_sid, auth_token)
        
        # Check account status
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Twilio Account Status: {account.status}")
        print(f"📱 WhatsApp Number: {from_whatsapp}")
        
        return True
        
    except Exception as e:
        print(f"❌ WhatsApp connection test failed: {str(e)}")
        return False

def print_setup_instructions():
    """Print setup instructions for WhatsApp Business templates"""
    
    print("=" * 60)
    print("🚀 WHATSAPP BUSINESS TEMPLATE SETUP FOR RESCUERADAR")
    print("=" * 60)
    
    print("\n📋 STEP 1: Check your current templates")
    print("-" * 40)
    check_existing_templates()
    
    print("\n📝 STEP 2: Suggested template for RescueRadar")
    print("-" * 40)
    template = create_template_suggestion()
    print(json.dumps(template, indent=2))
    
    print("\n🔧 STEP 3: How to create the template")
    print("-" * 40)
    print("1. Go to Twilio Console: https://console.twilio.com/us1/develop/sms/content-editor")
    print("2. Click 'Create new template'")
    print("3. Use the template structure shown above")
    print("4. Submit for approval (usually takes 24-48 hours)")
    print("5. Once approved, update your .env file with the template SID")
    
    print("\n⚡ STEP 4: Alternative - Use existing approved templates")
    print("-" * 40)
    print("If you have any approved templates, you can modify the code to use them.")
    print("Check the templates listed above and modify the notification logic accordingly.")
    
    print("\n🧪 STEP 5: Test connection")
    print("-" * 40)
    test_whatsapp_connection()
    
    print("\n💡 TIPS:")
    print("-" * 40)
    print("• Templates are required for business-initiated conversations")
    print("• After user replies, you can send free-form messages for 24 hours")
    print("• Always have a fallback strategy for when templates fail")
    print("• Keep template variables short and meaningful")
    
    print("\n🔗 USEFUL LINKS:")
    print("-" * 40)
    print("• Twilio Content API: https://www.twilio.com/docs/content")
    print("• WhatsApp Templates: https://www.twilio.com/docs/whatsapp/tutorial/send-whatsapp-notification-messages-templates")
    print("• Template Guidelines: https://developers.facebook.com/docs/whatsapp/message-templates/guidelines")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print_setup_instructions()
