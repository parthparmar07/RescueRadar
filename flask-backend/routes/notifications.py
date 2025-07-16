from flask import Blueprint, request, jsonify
import os
import requests
from twilio.rest import Client as TwilioClient

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/email-notify', methods=['POST'])
def send_email_notification():
    """Send email notification using Brevo"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'report_id' not in data:
            return jsonify({
                'success': False,
                'message': 'Email and report_id are required'
            }), 400
        
        # Brevo API configuration
        api_key = os.getenv('BREVO_API_KEY')
        url = "https://api.brevo.com/v3/smtp/email"
        
        headers = {
            'accept': 'application/json',
            'api-key': api_key,
            'content-type': 'application/json'
        }
        
        # Email content
        email_data = {
            'sender': {
                'name': os.getenv('BREVO_SENDER_NAME', 'RescueRadar'),
                'email': os.getenv('BREVO_FROM_EMAIL', 'alerts@rescueradar.org')
            },
            'to': [{'email': data['email']}],
            'subject': f"Animal Rescue Alert - Report #{data['report_id']}",
            'htmlContent': f"""
            <h2>New Animal Rescue Report</h2>
            <p><strong>Report ID:</strong> {data['report_id']}</p>
            <p><strong>Description:</strong> {data.get('description', 'N/A')}</p>
            <p><strong>Location:</strong> {data.get('location', 'N/A')}</p>
            <p><strong>Urgency:</strong> {data.get('urgency_level', 'Normal')}</p>
            <p>Please respond as soon as possible.</p>
            """,
            'textContent': f"New Animal Rescue Report #{data['report_id']} - {data.get('description', 'N/A')}"
        }
        
        response = requests.post(url, headers=headers, json=email_data)
        
        if response.status_code in [200, 201]:
            return jsonify({
                'success': True,
                'email_sent': True,
                'details': {
                    'message_id': response.json().get('messageId'),
                    'recipient': data['email']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send email',
                'error': response.text
            }), 500
            
    except Exception as e:
        print(f"Email Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send email',
            'error': str(e)
        }), 500

@notifications_bp.route('/whatsapp-notify', methods=['POST'])
def send_whatsapp_notification():
    """Send WhatsApp notification using Twilio with business template"""
    try:
        data = request.get_json()
        
        if not data or 'phone_number' not in data:
            return jsonify({
                'success': False,
                'message': 'Phone number is required'
            }), 400
        
        # Twilio configuration
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_whatsapp = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        client = TwilioClient(account_sid, auth_token)
        
        # Get report details for template
        report_id = data.get('report_id', 'Unknown')
        description = data.get('description', 'Animal rescue report')
        location = data.get('location', 'Location not specified')
        urgency = data.get('urgency_level', 'Normal')
        
        # Try to send using business template first
        try:
            # Using a pre-approved template for business-initiated conversation
            # This assumes you have a template like "rescue_alert" approved
            message = client.messages.create(
                content_sid=os.getenv('TWILIO_WHATSAPP_TEMPLATE_SID', 'HX52d7b2c0f2b4a4e8d9c6b3f1a0e5d8c2'),  # Your template SID
                content_variables=f'{{"1":"{report_id}","2":"{description[:50]}","3":"{location[:30]}","4":"{urgency}"}}',
                from_=from_whatsapp,
                to=f"whatsapp:{data['phone_number']}"
            )
            
            return jsonify({
                'success': True,
                'message_sent': True,
                'method': 'template',
                'details': {
                    'message_sid': message.sid,
                    'status': message.status,
                    'report_id': report_id
                }
            })
            
        except Exception as template_error:
            print(f"Template WhatsApp failed, trying freeform: {str(template_error)}")
            
            # Fallback to regular message (only works if conversation already exists)
            fallback_message = f"""🚨 RescueRadar Alert 🚨

Report ID: {report_id}
Description: {description[:100]}
Location: {location}
Urgency: {urgency}

Your animal rescue report has been submitted successfully. Our network has been notified and will respond as soon as possible.

Thank you for helping animals in need! 🐾"""

            message = client.messages.create(
                body=fallback_message,
                from_=from_whatsapp,
                to=f"whatsapp:{data['phone_number']}"
            )
            
            return jsonify({
                'success': True,
                'message_sent': True,
                'method': 'freeform',
                'details': {
                    'message_sid': message.sid,
                    'status': message.status,
                    'report_id': report_id
                }
            })
        
    except Exception as e:
        print(f"WhatsApp Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send WhatsApp message',
            'error': str(e)
        }), 500

@notifications_bp.route('/generate-qr', methods=['GET'])
def generate_qr_code():
    """Generate QR code for report"""
    try:
        report_id = request.args.get('report_id')
        
        if not report_id:
            return jsonify({
                'success': False,
                'message': 'Report ID is required'
            }), 400
        
        import qrcode
        import io
        import base64
        
        # Create QR code data
        qr_data = f"https://rescueradar.org/report/{report_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_code': {
                'qr_code_data': qr_code_data,
                'format': 'base64',
                'url': qr_data
            }
        })
        
    except Exception as e:
        print(f"QR Code Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to generate QR code',
            'error': str(e)
        }), 500
