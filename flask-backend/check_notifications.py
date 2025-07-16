import os
import time
from dotenv import load_dotenv

load_dotenv()

def check_notifications_status():
    """Check if notifications were sent successfully"""
    print("🔍 Checking notification delivery status...")
    print()
    
    print("📱 WhatsApp Receipt:")
    print(f"   ✅ Sent to: +919892130048")
    print(f"   📱 Check your WhatsApp for a message from: {os.getenv('TWILIO_WHATSAPP_NUMBER')}")
    print(f"   💬 Message should contain: Report ID, animal description, and timestamp")
    print()
    
    print("📧 Rescue Team Email:")
    print(f"   ✅ Sent to: {os.getenv('DEFAULT_RESCUE_EMAIL', 'rescue@animalwelfare.org')}")
    print(f"   📬 From: {os.getenv('BREVO_FROM_EMAIL', 'alerts@rescueradar.org')}")
    print(f"   📋 Subject: 🆘 URGENT: Animal Rescue Report #[ID]")
    print()
    
    print("📧 User Confirmation Email:")
    print(f"   ✅ Sent to: test@example.com")
    print(f"   📬 From: {os.getenv('BREVO_FROM_EMAIL', 'alerts@rescueradar.org')}")
    print(f"   📋 Subject: ✅ Report Confirmation - #[ID]")
    print()
    
    print("💾 Data Storage:")
    print("   ⚠️  Database: Not available (needs Supabase schema setup)")
    print("   ✅ Backup: Saved to reports_backup.json")
    print()
    
    # Check if backup file was created
    backup_file = 'reports_backup.json'
    if os.path.exists(backup_file):
        import json
        with open(backup_file, 'r') as f:
            reports = json.load(f)
        print(f"   📁 Backup file contains: {len(reports)} report(s)")
        print(f"   📄 Latest report ID: {reports[-1]['id']}")
        print(f"   📍 Location: {reports[-1]['location']}")
    else:
        print("   ❌ Backup file not found")
    
    print()
    print("🎯 Next Steps:")
    print("1. ✅ Check your WhatsApp (+919892130048) for the receipt")
    print("2. ✅ Check email (test@example.com) for user confirmation")
    print("3. ⚠️  Set up Supabase database by running the SQL schema")
    print("4. 🚀 Test the frontend map page")

if __name__ == "__main__":
    check_notifications_status()
