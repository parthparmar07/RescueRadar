import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import json

class EmailService:
    """Simple email service using Gmail SMTP with built-in Python libraries only"""
    
    def __init__(self):
        # Gmail SMTP Configuration
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 465  # SSL port for Gmail
        self.from_email = 'gauravpatil2516@gmail.com'
        self.app_password = 'yxjc ulzm mrcg ktrm'
        self.sender_name = 'RescueRadar Team'
        
        # Email templates
        self.templates = {
            'rescue_alert': self._get_rescue_alert_template(),
            'user_confirmation': self._get_user_confirmation_template(),
            'status_update': self._get_status_update_template(),
            'test_email': self._get_test_email_template()
        }
    
    def send_email(self, to_email, subject, html_content, text_content=None, attachments=None):
        """Send email using Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['X-Mailer'] = 'RescueRadar Email Service'
            
            # Create text and HTML parts
            text_part = MIMEText(text_content or self._html_to_text(html_content), 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email using Gmail SMTP SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.from_email, self.app_password)
                server.send_message(msg)
            
            result = {
                'success': True,
                'method': 'gmail_smtp',
                'message_id': f"gmail_{datetime.now().timestamp()}",
                'status': 'sent'
            }
            
            print(f"✅ Email sent successfully to {to_email}")
            
        except smtplib.SMTPAuthenticationError as e:
            result = {
                'success': False,
                'method': 'gmail_smtp',
                'error': f'Authentication failed: {str(e)}'
            }
            print(f"❌ SMTP Authentication Error: {e}")
            
        except smtplib.SMTPException as e:
            result = {
                'success': False,
                'method': 'gmail_smtp',
                'error': f'SMTP Error: {str(e)}'
            }
            print(f"❌ SMTP Error: {e}")
            
        except Exception as e:
            result = {
                'success': False,
                'method': 'gmail_smtp',
                'error': str(e)
            }
            print(f"❌ General Error: {e}")
        
        # Log the email attempt
        self._log_email(to_email, subject, result)
        
        return result
        """Send email using Brevo REST API"""
        try:
            url = "https://api.brevo.com/v3/smtp/email"
            
            headers = {
                'accept': 'application/json',
                'api-key': self.api_key,
                'content-type': 'application/json'
            }
            
            email_data = {
                'sender': {
                    'name': self.sender_name,
                    'email': self.from_email
                },
                'to': [{'email': to_email}],
                'subject': subject,
                'htmlContent': html_content,
                'textContent': text_content or self._html_to_text(html_content)
            }
            
            # Add attachments if provided
            if attachments:
                email_data['attachment'] = attachments
            
            response = requests.post(url, headers=headers, json=email_data)
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'method': 'api',
                    'message_id': response.json().get('messageId'),
                    'status': 'sent'
                }
            else:
                return {
                    'success': False,
                    'method': 'api',
                    'error': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'method': 'api',
                'error': str(e)
            }
    
    def send_email_via_smtp(self, to_email, subject, html_content, text_content=None, attachments=None):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['X-Mailer'] = 'RescueRadar Email Service'
            
            # Create text and HTML parts
            text_part = MIMEText(text_content or self._html_to_text(html_content), 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_login, self.smtp_password)
                server.send_message(msg)
            
            return {
                'success': True,
                'method': 'smtp',
                'message_id': f"smtp_{datetime.now().timestamp()}",
                'status': 'sent'
            }
            
        except Exception as e:
            return {
                'success': False,
                'method': 'smtp',
                'error': str(e)
            }
    
    def send_email(self, to_email, subject, html_content, text_content=None, prefer_smtp=False, attachments=None):
        """Send email with automatic fallback between API and SMTP"""
        
        if prefer_smtp:
            # Try SMTP first, fallback to API
            result = self.send_email_via_smtp(to_email, subject, html_content, text_content, attachments)
            if not result['success']:
                print(f"SMTP failed: {result.get('error', 'Unknown error')}, trying API...")
                result = self.send_email_via_api(to_email, subject, html_content, text_content, attachments)
        else:
            # Try API first, fallback to SMTP
            result = self.send_email_via_api(to_email, subject, html_content, text_content, attachments)
            if not result['success']:
                print(f"API failed: {result.get('error', 'Unknown error')}, trying SMTP...")
                result = self.send_email_via_smtp(to_email, subject, html_content, text_content, attachments)
        
        # Log the email attempt
        self._log_email(to_email, subject, result)
        
        return result
    
    def send_template_email(self, template_name, to_email, variables=None, prefer_smtp=False):
        """Send email using predefined templates"""
        if template_name not in self.templates:
            return {
                'success': False,
                'error': f"Template '{template_name}' not found"
            }
        
        template = self.templates[template_name]
        variables = variables or {}
        
        # Replace variables in template
        subject = template['subject'].format(**variables)
        html_content = template['html'].format(**variables)
        text_content = template.get('text', '').format(**variables) or None
        
        return self.send_email(to_email, subject, html_content, text_content, prefer_smtp)
    
    def send_bulk_emails(self, email_list, subject, html_content, text_content=None):
        """Send emails to multiple recipients"""
        results = []
        
        for email in email_list:
            result = self.send_email(email, subject, html_content, text_content)
            results.append({
                'email': email,
                'success': result['success'],
                'message_id': result.get('message_id'),
                'error': result.get('error')
            })
        
        return {
            'total_sent': sum(1 for r in results if r['success']),
            'total_failed': sum(1 for r in results if not r['success']),
            'results': results
        }
    
    def _add_attachment(self, msg, attachment):
        """Add attachment to email message"""
        try:
            if isinstance(attachment, dict):
                filename = attachment.get('filename')
                content = attachment.get('content')
                
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
        except Exception as e:
            print(f"Failed to add attachment: {e}")
    
    def _html_to_text(self, html_content):
        """Convert HTML to plain text"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        # Clean up multiple whitespaces and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def _log_email(self, to_email, subject, result):
        """Log email sending attempts"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'to_email': to_email,
                'subject': subject,
                'success': result['success'],
                'method': result.get('method'),
                'message_id': result.get('message_id'),
                'error': result.get('error')
            }
            
            # Log to file
            log_file = 'email_log.json'
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            # Keep only last 1000 logs
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Failed to log email: {e}")
    
    def get_email_stats(self):
        """Get email sending statistics"""
        try:
            log_file = 'email_log.json'
            if not os.path.exists(log_file):
                return {'total': 0, 'successful': 0, 'failed': 0}
            
            with open(log_file, 'r') as f:
                logs = json.load(f)
            
            total = len(logs)
            successful = sum(1 for log in logs if log['success'])
            failed = total - successful
            
            # Recent activity (last 24 hours)
            recent_logs = [log for log in logs if 
                          (datetime.now() - datetime.fromisoformat(log['timestamp'])).days < 1]
            
            return {
                'total': total,
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / total * 100) if total > 0 else 0,
                'recent_24h': len(recent_logs),
                'api_usage': sum(1 for log in logs if log.get('method') == 'api'),
                'smtp_usage': sum(1 for log in logs if log.get('method') == 'smtp')
            }
            
        except Exception as e:
            print(f"Failed to get email stats: {e}")
            return {'error': str(e)}
    
    # Template definitions
    def _get_rescue_alert_template(self):
        return {
            'subject': '🆘 URGENT: Animal Rescue Report #{report_id}',
            'html': '''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #dc2626; text-align: center;">🆘 New Animal Rescue Report</h2>
                
                <div style="background: #fef2f2; padding: 20px; border-radius: 8px; border-left: 4px solid #dc2626; margin: 20px 0;">
                    <p><strong>Report ID:</strong> {report_id}</p>
                    <p><strong>Urgency Level:</strong> <span style="color: #dc2626; font-weight: bold;">{urgency_level}</span></p>
                    <p><strong>Animal Type:</strong> {animal_type}</p>
                    <p><strong>Situation:</strong> {situation_type}</p>
                    <p><strong>Location:</strong> {location}</p>
                </div>
                
                <h3>📝 Description:</h3>
                <div style="background: #f9fafb; padding: 15px; border-radius: 6px;">
                    <p>{description}</p>
                </div>
                
                <h3>👤 Contact Information:</h3>
                <ul style="background: #f0f9ff; padding: 15px; border-radius: 6px;">
                    <li><strong>Name:</strong> {contact_name}</li>
                    <li><strong>Phone:</strong> {contact_phone}</li>
                    <li><strong>Email:</strong> {contact_email}</li>
                </ul>
                
                <div style="margin-top: 20px; padding: 15px; background: #dbeafe; border-radius: 6px; text-align: center;">
                    <p><strong>⚡ ACTION REQUIRED: Please respond immediately!</strong></p>
                </div>
                
                <p style="text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px;">
                    This alert was sent by RescueRadar Emergency Response System
                </p>
            </div>
            ''',
            'text': 'URGENT: Animal Rescue Report #{report_id} - {description} at {location}. Contact: {contact_name} - {contact_phone}'
        }
    
    def _get_user_confirmation_template(self):
        return {
            'subject': '✅ Report Confirmation - #{report_id}',
            'html': '''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #16a34a; text-align: center;">✅ Thank You for Your Report!</h2>
                
                <p>Dear {contact_name},</p>
                
                <p>Thank you for taking action to help an animal in need. Your report has been successfully submitted and forwarded to local rescue teams.</p>
                
                <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #16a34a; margin: 20px 0;">
                    <h3>📋 Report Details:</h3>
                    <p><strong>Report ID:</strong> {report_id}</p>
                    <p><strong>Location:</strong> {location}</p>
                    <p><strong>Animal:</strong> {animal_type}</p>
                    <p><strong>Situation:</strong> {situation_type}</p>
                    <p><strong>Urgency:</strong> {urgency_level}</p>
                    <p><strong>Submitted:</strong> {timestamp}</p>
                </div>
                
                <h3>🚀 What Happens Next?</h3>
                <ul style="background: #f9fafb; padding: 15px; border-radius: 6px;">
                    <li>✅ Your report has been sent to local animal rescue teams</li>
                    <li>📞 A rescue coordinator may contact you for additional information</li>
                    <li>🆘 If this is an emergency, please also contact local authorities</li>
                    <li>📱 You'll receive WhatsApp updates if you provided your phone number</li>
                </ul>
                
                <div style="background: #fef3c7; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p><strong>⚠️ Emergency Note:</strong> If the animal is in immediate danger, please also contact your local animal control or emergency services.</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8fafc; border-radius: 6px;">
                    <p><strong>Thank you for being a voice for animals who cannot speak for themselves!</strong></p>
                </div>
                
                <p style="text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px;">
                    Best regards,<br>The RescueRadar Team
                </p>
            </div>
            ''',
            'text': 'Thank you for your report #{report_id}. Your report has been forwarded to rescue teams. Report ID: {report_id}'
        }
    
    def _get_status_update_template(self):
        return {
            'subject': '📋 Report Update - #{report_id}',
            'html': '''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb; text-align: center;">📋 Report Status Update</h2>
                
                <div style="background: #eff6ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb; margin: 20px 0;">
                    <p><strong>Report ID:</strong> {report_id}</p>
                    <p><strong>Status:</strong> <span style="color: #2563eb; font-weight: bold;">{status}</span></p>
                    <p><strong>Updated:</strong> {timestamp}</p>
                </div>
                
                <h3>📝 Update Details:</h3>
                <div style="background: #f9fafb; padding: 15px; border-radius: 6px;">
                    <p>{update_message}</p>
                </div>
                
                <p style="text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px;">
                    RescueRadar Status Update System
                </p>
            </div>
            ''',
            'text': 'Report #{report_id} Status Update: {status} - {update_message}'
        }
    
    def _get_test_email_template(self):
        return {
            'subject': '🧪 RescueRadar Email Service Test',
            'html': '''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #16a34a; text-align: center;">🧪 Email Service Test</h2>
                
                <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #16a34a; margin: 20px 0;">
                    <p><strong>✅ If you receive this email, the service is working correctly!</strong></p>
                </div>
                
                <h3>📊 Test Details:</h3>
                <ul style="background: #f9fafb; padding: 15px; border-radius: 6px;">
                    <li><strong>Test Type:</strong> {test_type}</li>
                    <li><strong>Timestamp:</strong> {timestamp}</li>
                    <li><strong>Delivery Method:</strong> {method}</li>
                    <li><strong>Email Service:</strong> Brevo (SendinBlue)</li>
                </ul>
                
                <p style="text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px;">
                    RescueRadar Email Service Test - {timestamp}
                </p>
            </div>
            ''',
            'text': 'RescueRadar Email Service Test - {test_type} at {timestamp}'
        }

# Global email service instance
email_service = EmailService()

# Convenience functions for backward compatibility
def send_rescue_team_email(report_id, report_data):
    """Send emergency alert to rescue team"""
    rescue_email = os.getenv('DEFAULT_RESCUE_EMAIL', 'rescue@animalwelfare.org')
    
    variables = {
        'report_id': report_id,
        'urgency_level': report_data.get('urgency_level', 'normal').upper(),
        'animal_type': report_data.get('animal_type', 'Unknown'),
        'situation_type': report_data.get('situation_type', 'Unknown'),
        'location': report_data.get('location', 'Not specified'),
        'description': report_data.get('description', ''),
        'contact_name': report_data.get('contact_name', 'Anonymous'),
        'contact_phone': report_data.get('contact_phone', 'Not provided'),
        'contact_email': report_data.get('contact_email', 'Not provided')
    }
    
    return email_service.send_template_email('rescue_alert', rescue_email, variables)

def send_user_confirmation_email(email, report_id, report_data):
    """Send confirmation to user who submitted report"""
    variables = {
        'contact_name': report_data.get('contact_name', 'Valued Reporter'),
        'report_id': report_id,
        'location': report_data.get('location', 'Not specified'),
        'animal_type': report_data.get('animal_type', 'Animal'),
        'situation_type': report_data.get('situation_type', 'Rescue needed'),
        'urgency_level': report_data.get('urgency_level', 'normal').upper(),
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }
    
    return email_service.send_template_email('user_confirmation', email, variables)

def send_status_update_email(email, report_id, status, update_message):
    """Send status update to user"""
    variables = {
        'report_id': report_id,
        'status': status.upper(),
        'update_message': update_message,
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }
    
    return email_service.send_template_email('status_update', email, variables)

def send_test_email(email, test_type='Basic Functionality', method='auto'):
    """Send test email"""
    variables = {
        'test_type': test_type,
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'method': method
    }
    
    return email_service.send_template_email('test_email', email, variables)

# Email management functions
def get_email_statistics():
    """Get email sending statistics"""
    return email_service.get_email_stats()

def send_bulk_notification(email_list, subject, message):
    """Send notification to multiple recipients"""
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">RescueRadar Notification</h2>
        <div style="background: #f9fafb; padding: 20px; border-radius: 8px;">
            <p>{message}</p>
        </div>
        <p style="color: #6b7280; font-size: 12px; text-align: center; margin-top: 30px;">
            RescueRadar Team - {datetime.now().strftime('%B %d, %Y')}
        </p>
    </div>
    """
    
    return email_service.send_bulk_emails(email_list, subject, html_content)
