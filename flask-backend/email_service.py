import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import json
import os

class EmailService:
    """Simple email service using Gmail SMTP with built-in Python libraries only"""
    
    def __init__(self):
        # SMTP Configuration from environment variables
        self.smtp_server = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_PORT', 587))  # Use port from .env or default to 587
        self.from_email = os.getenv('EMAIL_USER', 'speedblast069@gmail.com')
        self.app_password = os.getenv('EMAIL_PASS', 'rdbc ianf bqzl uoao')
        self.sender_name = os.getenv('EMAIL_SENDER_NAME', 'RescueRadar Team')
        print(f"[EmailService] Initialized with {self.from_email} on {self.smtp_server}:{self.smtp_port}")
    
    def send_email(self, to_email, subject, html_content, text_content=None, attachments=None):
        """Send email using Gmail SMTP"""
        try:
            print(f"[EmailService] Sending email to: {to_email}")
            print(f"[EmailService] Using from: {self.from_email}")
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
            
            # Send email using SMTP with TLS
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS encryption
                server.login(self.from_email, self.app_password)
                server.send_message(msg)
            print(f"[EmailService] Email sent successfully to {to_email}")
            
            result = {
                'success': True,
                'method': 'gmail_smtp',
                'message_id': f"gmail_{datetime.now().timestamp()}",
                'status': 'sent'
            }
            
            print(f"✅ Email sent successfully to {to_email}")
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EmailService] SMTPAuthenticationError: {e}")
            result = {
                'success': False,
                'method': 'gmail_smtp',
                'error': f'Authentication failed: {str(e)}'
            }
            print(f"❌ SMTP Authentication Error: {e}")
            
        except smtplib.SMTPException as e:
            print(f"[EmailService] SMTPException: {e}")
            result = {
                'success': False,
                'method': 'gmail_smtp',
                'error': f'SMTP Error: {str(e)}'
            }
            print(f"❌ SMTP Error: {e}")
            
        except Exception as e:
            print(f"[EmailService] General Exception: {e}")
            result = {
                'success': False,
                'method': 'gmail_smtp',
                'error': str(e)
            }
            print(f"❌ General Error: {e}")
        
        # Log the email attempt
        self._log_email(to_email, subject, result)
        
        return result
    
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
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            logs.append(log_entry)
            
            # Keep only last 1000 logs
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Failed to log email: {e}")

# Global email service instance
email_service = EmailService()

def send_rescue_team_email(report_id, report_data):
    """Send professional email notification to rescue team"""
    try:
        # Format date and time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Determine urgency level and color
        urgency_level = report_data.get('urgency_level', 'normal').upper()
        if urgency_level == 'EMERGENCY':
            urgency_color = '#dc2626'  # Red
        elif urgency_level == 'HIGH':
            urgency_color = '#ea580c'  # Orange
        else:
            urgency_color = '#16a34a'  # Green
        
        # Get location map URL if coordinates are available
        map_url = ""
        if 'coordinates' in report_data and report_data['coordinates']:
            lat = report_data['coordinates'].get('lat')
            lng = report_data['coordinates'].get('lng')
            if lat and lng:
                map_url = f"https://www.google.com/maps?q={lat},{lng}"
        
        subject = f"🆘 {urgency_level}: Animal Rescue Report #{report_id[:8]}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rescue Report #{report_id[:8]}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; padding: 20px 0; border-bottom: 2px solid #e5e7eb; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #1e40af; }}
                .alert-box {{ 
                    background-color: #fef2f2; 
                    border-left: 4px solid {urgency_color};
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .section {{ 
                    margin: 25px 0;
                    padding: 15px;
                    background: #f9fafb;
                    border-radius: 6px;
                }}
                .section-title {{ 
                    color: #1e40af;
                    margin-top: 0;
                    border-bottom: 1px solid #e5e7eb;
                    padding-bottom: 8px;
                }}
                .grid {{ 
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin: 15px 0;
                }}
                .info-label {{ 
                    font-weight: 600;
                    color: #4b5563;
                }}
                .urgent {{ 
                    color: {urgency_color};
                    font-weight: bold;
                }}
                .footer {{ 
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 12px;
                    color: #6b7280;
                    text-align: center;
                }}
                .btn {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #1e40af;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: 500;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">RescueRadar</div>
                    <div style="color: #6b7280; font-size: 14px;">Emergency Response System</div>
                </div>
                
                <div class="alert-box">
                    <h2 style="margin: 0; color: {urgency_color};">🆘 {urgency_level} PRIORITY REPORT</h2>
                    <p style="margin: 5px 0 0 0; font-weight: 500;">Action Required: Immediate Response Needed</p>
                </div>
                
                <div class="section">
                    <h3 class="section-title">📋 Report Summary</h3>
                    <div class="grid">
                        <div>
                            <div class="info-label">Report ID</div>
                            <div>{report_id}</div>
                        </div>
                        <div>
                            <div class="info-label">Date & Time</div>
                            <div>{current_time}</div>
                        </div>
                        <div>
                            <div class="info-label">Urgency Level</div>
                            <div class="urgent">{urgency_level}</div>
                        </div>
                        <div>
                            <div class="info-label">Animal Type</div>
                            <div>{report_data.get('animal_type', 'Not specified')}</div>
                        </div>
                        <div>
                            <div class="info-label">Situation</div>
                            <div>{report_data.get('situation_type', 'Unknown')}</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3 class="section-title">📍 Incident Location</h3>
                    <p><strong>Address:</strong> {report_data.get('location', 'Location not specified')}</p>
                    {f'<p><strong>Coordinates:</strong> {lat}, {lng}</p>' if 'lat' in locals() and 'lng' in locals() else ''}
                    {f'<a href="{map_url}" class="btn" target="_blank">View on Map</a>' if map_url else ''}
                </div>
                
                <div class="section">
                    <h3 class="section-title">📝 Incident Details</h3>
                    <div style="background: white; padding: 15px; border-radius: 4px; border: 1px solid #e5e7eb;">
                        <p style="margin: 0;">{report_data.get('description', 'No description provided.')}</p>
                    </div>
                    
                    {f'''
                    <div style="margin-top: 15px;">
                        <h4>AI Analysis:</h4>
                        <div style="background: #f0f9ff; padding: 10px; border-radius: 4px; font-size: 14px;">
                            {report_data.get('ai_analysis', 'No AI analysis available.')}
                        </div>
                    </div>
                    ''' if report_data.get('ai_analysis') else ''}
                </div>
                
                <div class="section">
                    <h3 class="section-title">👤 Reporter Information</h3>
                    <div class="grid">
                        <div>
                            <div class="info-label">Name</div>
                            <div>{report_data.get('contact_name', 'Not provided')}</div>
                        </div>
                        <div>
                            <div class="info-label">Phone</div>
                            <div>{report_data.get('contact_phone', 'Not provided')}</div>
                        </div>
                        <div>
                            <div class="info-label">Email</div>
                            <div>{report_data.get('contact_email', 'Not provided')}</div>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="#" class="btn" style="background-color: #dc2626;">MARK AS RESPONDED</a>
                    <a href="#" class="btn" style="background-color: #16a34a;">UPDATE STATUS</a>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from RescueRadar Emergency Response System.</p>
                    <p>Please do not reply to this email. For support, contact your system administrator.</p>
                    <p>© {datetime.now().year} RescueRadar. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send to configured rescue email
        rescue_email = 'siesgauravpatil@gmail.com'  # This should be replaced with actual rescue team email
        result = email_service.send_email(rescue_email, subject, html_content)
        
        return result
        
    except Exception as e:
        print(f"Error sending rescue team email: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def send_user_confirmation_email(email, report_id, report_data):
    """Send email confirmation to user using enhanced service"""
    try:
        subject = f"✅ Report Confirmation - #{report_id[:8]}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #16a34a; text-align: center;">✅ Thank You for Your Report!</h2>
            
            <p>Dear {report_data.get('contact_name', 'Animal Advocate')},</p>
            
            <p>Thank you for taking action to help an animal in need. Your report has been successfully submitted and forwarded to local rescue teams.</p>
            
            <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #16a34a; margin: 20px 0;">
                <h3>📋 Report Details:</h3>
                <p><strong>Report ID:</strong> {report_id}</p>
                <p><strong>Location:</strong> {report_data['location']}</p>
                <p><strong>Description:</strong> {report_data['description']}</p>
                <p><strong>Animal Type:</strong> {report_data.get('animal_type', 'Not specified')}</p>
                <p><strong>Urgency Level:</strong> {report_data.get('urgency_level', 'normal').upper()}</p>
                <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h3>🚀 What Happens Next?</h3>
            <ul style="background: #f9fafb; padding: 15px; border-radius: 6px;">
                <li>✅ Your report has been sent to local animal rescue teams</li>
                <li>📞 A rescue coordinator may contact you for additional information</li>
                <li>🆘 If this is an emergency, please also contact local authorities</li>
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
        """
        
        result = email_service.send_email(email, subject, html_content)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def send_test_email():
    """Send a realistic test rescue report email to Gaurav Patil"""
    try:
        report_id = 'RR-' + str(uuid.uuid4())[:8].upper()
        print(f"Sending rescue report email #{report_id}...")
        
        # Create a realistic test report
        test_report = {
            'id': report_id,
            'situation_type': 'Injured Dog',
            'description': 'Medium-sized brown dog with visible injury on right hind leg. Limping and appears to be in pain. Found near Bandra West, outside Bandra Station.',
            'urgency_level': 'emergency',
            'location': 'Bandra West, near Bandra Station, Mumbai',
            'coordinates': {'lat': 19.0596, 'lng': 72.8295},
            'animal_type': 'Dog',
            'animal_condition': 'Injured, limping, visible wound on right hind leg',
            'reporter_name': 'Rahul Sharma',
            'reporter_contact': '+91 98765 43210',
            'created_at': datetime.now().isoformat(),
            'ai_analysis': '''
            Based on the description and image analysis (if provided):
            - Animal appears to be a medium-sized adult dog
            - Visible injury on right hind leg, possibly a deep cut or fracture
            - Animal is mobile but in visible discomfort
            - No immediate threats in the vicinity
            - Recommended: Immediate medical attention required, approach with caution as animal may be in pain
            '''
        }
        
        # Send the email
        result = send_rescue_team_email(report_id, test_report)
        if result.get('success'):
            print("✅ Rescue report email sent successfully!")
        else:
            print(f"❌ Failed to send email: {result.get('error')}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Error in sending rescue report: {str(e)}"
        print(error_msg)
        return {'success': False, 'error': error_msg}

def send_bulk_notification(email_list, subject, message, email_type='notification'):
    """Send bulk email notifications"""
    try:
        # ... (rest of the code remains the same)
        for email in email_list:
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">RescueRadar Notification</h2>
                <div style="background: #f9fafb; padding: 20px; border-radius: 8px;">
                    <p>{message}</p>
                </div>
                <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                    This notification was sent by RescueRadar System
                </p>
            </div>
            """
            
            result = email_service.send_email(email, subject, html_content)
            results.append({
                'email': email,
                'success': result['success'],
                'error': result.get('error')
            })
        
        successful = sum(1 for r in results if r['success'])
        return {
            'success': True,
            'total_sent': successful,
            'total_failed': len(results) - successful,
            'results': results
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_email_statistics():
    """Get email statistics"""
    try:
        # Read email log
        log_file = 'email_log.json'
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'total_emails': 0,
                'successful_emails': 0,
                'failed_emails': 0,
                'success_rate': 0,
                'recent_activity': []
            }
        
        total = len(logs)
        successful = sum(1 for log in logs if log['success'])
        failed = total - successful
        
        # Recent activity (last 10 emails)
        recent_activity = logs[-10:] if logs else []
        
        return {
            'total_emails': total,
            'successful_emails': successful, 
            'failed_emails': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'recent_activity': recent_activity
        }
        
    except Exception as e:
        return {
            'error': str(e)
        }

# WhatsApp function (stub for compatibility)
def send_whatsapp_receipt(phone_number, report_id, description):
    """Placeholder WhatsApp function"""
    print(f"WhatsApp notification would be sent to {phone_number} for report {report_id}")
    return {'success': True, 'message_id': f'whatsapp_{datetime.now().timestamp()}'}

# Run the test if this script is executed directly
if __name__ == "__main__":
    send_test_email()
