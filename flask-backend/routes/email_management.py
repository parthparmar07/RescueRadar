from flask import Blueprint, request, jsonify
import os
from datetime import datetime
from email_service import (
    email_service,
    send_test_email,
    send_bulk_notification,
    get_email_statistics
)

email_bp = Blueprint('email', __name__)

@email_bp.route('/send-test-email', methods=['POST'])
def send_test_email_route():
    """Send a test email to verify service functionality"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'message': 'Email address is required'
            }), 400
        
        email = data['email']
        test_type = data.get('test_type', 'API Test')
        prefer_smtp = data.get('prefer_smtp', False)
        
        result = send_test_email(email, test_type, 'SMTP' if prefer_smtp else 'API')
        
        return jsonify({
            'success': result['success'],
            'message': 'Test email sent successfully' if result['success'] else 'Failed to send test email',
            'email': email,
            'method': result.get('method'),
            'message_id': result.get('message_id'),
            'error': result.get('error') if not result['success'] else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to send test email',
            'error': str(e)
        }), 500

@email_bp.route('/send-custom-email', methods=['POST'])
def send_custom_email():
    """Send a custom email with custom content"""
    try:
        data = request.get_json()
        
        required_fields = ['to_email', 'subject', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        to_email = data['to_email']
        subject = data['subject']
        content = data['content']
        content_type = data.get('content_type', 'html')  # 'html' or 'text'
        prefer_smtp = data.get('prefer_smtp', False)
        
        if content_type == 'text':
            # Convert text to HTML
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{content}</pre>
                <p style="color: #6b7280; font-size: 12px; text-align: center; margin-top: 30px;">
                    Sent via RescueRadar Email Service - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
            """
            text_content = content
        else:
            html_content = content
            text_content = None
        
        result = email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            prefer_smtp=prefer_smtp
        )
        
        return jsonify({
            'success': result['success'],
            'message': 'Email sent successfully' if result['success'] else 'Failed to send email',
            'to_email': to_email,
            'subject': subject,
            'method': result.get('method'),
            'message_id': result.get('message_id'),
            'error': result.get('error') if not result['success'] else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to send custom email',
            'error': str(e)
        }), 500

@email_bp.route('/send-bulk-email', methods=['POST'])
def send_bulk_email():
    """Send email to multiple recipients"""
    try:
        data = request.get_json()
        
        required_fields = ['email_list', 'subject', 'message']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        email_list = data['email_list']
        subject = data['subject']
        message = data['message']
        
        if not isinstance(email_list, list) or len(email_list) == 0:
            return jsonify({
                'success': False,
                'message': 'email_list must be a non-empty array'
            }), 400
        
        result = send_bulk_notification(email_list, subject, message)
        
        return jsonify({
            'success': True,
            'message': f'Bulk email completed. {result["total_sent"]} sent, {result["total_failed"]} failed',
            'total_recipients': len(email_list),
            'total_sent': result['total_sent'],
            'total_failed': result['total_failed'],
            'details': result['results']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to send bulk email',
            'error': str(e)
        }), 500

@email_bp.route('/email-stats', methods=['GET'])
def get_email_stats():
    """Get email service statistics"""
    try:
        stats = get_email_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get email statistics',
            'error': str(e)
        }), 500

@email_bp.route('/email-templates', methods=['GET'])
def get_email_templates():
    """Get available email templates"""
    try:
        templates = {
            'rescue_alert': {
                'name': 'Rescue Team Alert',
                'description': 'Emergency alert sent to rescue teams',
                'variables': ['report_id', 'urgency_level', 'animal_type', 'situation_type', 'location', 'description', 'contact_name', 'contact_phone', 'contact_email']
            },
            'user_confirmation': {
                'name': 'User Confirmation',
                'description': 'Confirmation email sent to users who submit reports',
                'variables': ['contact_name', 'report_id', 'location', 'animal_type', 'situation_type', 'urgency_level', 'timestamp']
            },
            'status_update': {
                'name': 'Status Update',
                'description': 'Report status update notification',
                'variables': ['report_id', 'status', 'update_message', 'timestamp']
            },
            'test_email': {
                'name': 'Test Email',
                'description': 'Email service functionality test',
                'variables': ['test_type', 'timestamp', 'method']
            }
        }
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get templates',
            'error': str(e)
        }), 500

@email_bp.route('/send-template-email', methods=['POST'])
def send_template_email_route():
    """Send email using a predefined template"""
    try:
        data = request.get_json()
        
        required_fields = ['template_name', 'to_email', 'variables']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        template_name = data['template_name']
        to_email = data['to_email']
        variables = data['variables']
        prefer_smtp = data.get('prefer_smtp', False)
        
        result = email_service.send_template_email(
            template_name=template_name,
            to_email=to_email,
            variables=variables,
            prefer_smtp=prefer_smtp
        )
        
        return jsonify({
            'success': result['success'],
            'message': 'Template email sent successfully' if result['success'] else 'Failed to send template email',
            'template_name': template_name,
            'to_email': to_email,
            'method': result.get('method'),
            'message_id': result.get('message_id'),
            'error': result.get('error') if not result['success'] else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to send template email',
            'error': str(e)
        }), 500

@email_bp.route('/test-email-methods', methods=['POST'])
def test_email_methods():
    """Test both API and SMTP email delivery methods"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'message': 'Email address is required'
            }), 400
        
        email = data['email']
        
        # Test API method
        api_result = email_service.send_email_via_api(
            to_email=email,
            subject="🧪 API Method Test - RescueRadar",
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">✅ API Method Test</h2>
                <p>This email was sent using the Brevo REST API method.</p>
                <div style="background: #f0f9ff; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p><strong>Method:</strong> REST API</p>
                    <p><strong>Service:</strong> Brevo (SendinBlue)</p>
                    <p><strong>Time:</strong> {}</p>
                </div>
            </div>
            """.format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        )
        
        # Test SMTP method
        smtp_result = email_service.send_email_via_smtp(
            to_email=email,
            subject="🧪 SMTP Method Test - RescueRadar",
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #16a34a;">✅ SMTP Method Test</h2>
                <p>This email was sent using the SMTP method.</p>
                <div style="background: #f0fdf4; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p><strong>Method:</strong> SMTP</p>
                    <p><strong>Server:</strong> smtp-relay.brevo.com</p>
                    <p><strong>Time:</strong> {}</p>
                </div>
            </div>
            """.format(datetime.now().strftime('%B %d, %Y at %I:%M %p'))
        )
        
        return jsonify({
            'success': True,
            'message': 'Email method tests completed',
            'email': email,
            'api_test': {
                'success': api_result['success'],
                'message_id': api_result.get('message_id'),
                'error': api_result.get('error')
            },
            'smtp_test': {
                'success': smtp_result['success'],
                'message_id': smtp_result.get('message_id'),
                'error': smtp_result.get('error')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to test email methods',
            'error': str(e)
        }), 500

@email_bp.route('/email-config', methods=['GET'])
def get_email_config():
    """Get current email service configuration (without sensitive data)"""
    try:
        config = {
            'from_email': email_service.from_email,
            'sender_name': email_service.sender_name,
            'smtp_server': email_service.smtp_server,
            'smtp_port': email_service.smtp_port,
            'api_configured': bool(email_service.api_key),
            'smtp_configured': bool(email_service.smtp_login and email_service.smtp_password),
            'templates_available': len(email_service.templates)
        }
        
        return jsonify({
            'success': True,
            'configuration': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get email configuration',
            'error': str(e)
        }), 500
