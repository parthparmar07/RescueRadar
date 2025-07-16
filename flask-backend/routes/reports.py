from flask import Blueprint, request, jsonify
import os
import uuid
from datetime import datetime, timedelta
from supabase import create_client, Client
import requests
from email_service import send_rescue_team_email, send_user_confirmation_email

reports_bp = Blueprint('reports', __name__)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_API_KEY')
)

@reports_bp.route('/save-report', methods=['POST'])
def save_report():
    """Save a new animal cruelty report and send notifications"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'description' not in data or 'location' not in data:
            return jsonify({
                'success': False,
                'message': 'Description and location are required'
            }), 400
        
        # Generate report ID
        report_id = str(uuid.uuid4())

        # Get user_id from request headers or session if available (for RLS)
        user_id = data.get('user_id')

        # Prepare report data for new 'reports' table schema
        # Convert coordinates to POINT (longitude, latitude) if provided as {lat, lng}
        coords = data.get('coordinates')
        point = None
        if coords and isinstance(coords, dict) and 'lat' in coords and 'lng' in coords:
            # Use the Postgres tuple format: (lng, lat)
            point = f"({coords['lng']}, {coords['lat']})"

        report_data = {
            'id': report_id,  # Only include if you're setting a custom ID
            'description': data['description'],
            'location': data['location'],
            'coordinates': point,
            'contact_name': data.get('contact_name') or None,
            'contact_email': data.get('contact_email') or None,
            'contact_phone': data.get('contact_phone') or None,
            'urgency_level': data.get('urgency_level') or 'normal',
            'animal_type': data.get('animal_type') or None,
            'situation_type': data.get('situation_type') or None,
            'image_url': data.get('image_url') or None,
            'ai_analysis': data.get('ai_analysis') or None,
            'status': 'active'
        }
        
        # Try to save to Supabase first
        saved_to_db = False
        try:
            # Use the new 'reports' table
            result = supabase.table('reports').insert(report_data).execute()
            if result.data:
                saved_to_db = True
                saved_report = result.data[0]
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
        
        # If database failed, save to backup file
        if not saved_to_db:
            import json
            reports_file = 'reports_backup.json'
            
            if os.path.exists(reports_file):
                with open(reports_file, 'r') as f:
                    reports = json.load(f)
            else:
                reports = []
            
            report_data['created_at'] = datetime.now().isoformat()
            reports.append(report_data)
            
            with open(reports_file, 'w') as f:
                json.dump(reports, f, indent=2)
        
        # Send notifications
        notifications_sent = []
        
        # Send WhatsApp receipt to user if phone number provided
        if data.get('contact_phone'):
            try:
                whatsapp_result = send_whatsapp_receipt(
                    phone_number=data['contact_phone'],
                    report_id=report_id,
                    description=data['description']
                )
                if whatsapp_result.get('success'):
                    notifications_sent.append('whatsapp_receipt')
                    
                    # Log notification in database if available
                    if saved_to_db:
                        try:
                            supabase.table('notifications').insert({
                                'report_id': report_id,
                                'notification_type': 'whatsapp',
                                'recipient': data['contact_phone'],
                                'status': 'sent',
                                'message_id': whatsapp_result.get('message_id'),
                                'sent_at': datetime.now().isoformat()
                            }).execute()
                        except:
                            pass
                        
            except Exception as e:
                print(f"WhatsApp notification failed: {str(e)}")
        
        # Send email notification to rescue team
        try:
            email_result = send_rescue_team_email(
                report_id=report_id,
                report_data=report_data
            )
            if email_result.get('success'):
                notifications_sent.append('rescue_team_email')
                
                # Log notification in database if available
                if saved_to_db:
                    try:
                        supabase.table('notifications').insert({
                            'report_id': report_id,
                            'notification_type': 'email',
                            'recipient': os.getenv('DEFAULT_RESCUE_EMAIL', 'rescue@animalwelfare.org'),
                            'status': 'sent',
                            'message_id': email_result.get('message_id'),
                            'sent_at': datetime.now().isoformat()
                        }).execute()
                    except:
                        pass
                    
        except Exception as e:
            print(f"Email notification failed: {str(e)}")
        
        # Send email confirmation to user if email provided
        if data.get('contact_email'):
            try:
                user_email_result = send_user_confirmation_email(
                    email=data['contact_email'],
                    report_id=report_id,
                    report_data=report_data
                )
                if user_email_result.get('success'):
                    notifications_sent.append('user_email_confirmation')
                    
                    # Log notification in database if available
                    if saved_to_db:
                        try:
                            supabase.table('notifications').insert({
                                'report_id': report_id,
                                'notification_type': 'email',
                                'recipient': data['contact_email'],
                                'status': 'sent',
                                'message_id': user_email_result.get('message_id'),
                                'sent_at': datetime.now().isoformat()
                            }).execute()
                        except:
                            pass
                        
            except Exception as e:
                print(f"User email confirmation failed: {str(e)}")
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'message': 'Report saved successfully',
            'notifications_sent': notifications_sent,
            'saved_to_database': saved_to_db
        })
            
    except Exception as e:
        print(f"Save Report Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to save report',
            'error': str(e)
        }), 500

@reports_bp.route('/reports/active', methods=['GET'])
def get_active_reports():
    """Get all active reports from database"""
    try:
        # Try to fetch from Supabase first
        try:
            print("Fetching active reports from Supabase...")
            result = supabase.table('reports').select('*').eq('status', 'active').order('created_at', desc=True).limit(100).execute()
            
            # Log the raw result for debugging
            print(f"Supabase response: {result}")
            
            if hasattr(result, 'data') and result.data:
                reports = []
                for report in result.data:
                    try:
                        # Safely access report data with defaults
                        report_data = {
                            'id': report.get('id', str(uuid.uuid4())),  # Generate new ID if missing
                            'description': report.get('description', 'No description provided'),
                            'location': report.get('location', 'Location not specified'),
                            'coordinates': report.get('coordinates', {'lat': 40.7128, 'lng': -74.0060}),
                            'urgency_level': report.get('urgency_level', 'normal'),
                            'animal_type': report.get('animal_type'),
                            'situation_type': report.get('situation_type'),
                            'created_at': report.get('created_at', datetime.now().isoformat()),
                            'contact_info': {
                                'name': report.get('contact_name'),
                                'email': report.get('contact_email'),
                                'phone': report.get('contact_phone')
                            },
                            'image_url': report.get('image_url'),
                            'ai_analysis': report.get('ai_analysis')
                        }
                        reports.append(report_data)
                    except Exception as report_error:
                        print(f"Error processing report: {str(report_error)}")
                        print(f"Problematic report data: {report}")
                        continue
                
                return jsonify({
                    'success': True,
                    'reports': reports,
                    'total': len(reports)
                })
                
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
        
        # If database fails, try to load from backup file
        import json
        reports_file = 'reports_backup.json'
        
        if os.path.exists(reports_file):
            try:
                with open(reports_file, 'r') as f:
                    backup_reports = json.load(f)
                
                # Format backup reports for frontend
                reports = []
                for report in backup_reports:
                    reports.append({
                        'id': report['id'],
                        'description': report['description'],
                        'location': report['location'],
                        'coordinates': report.get('coordinates', {'lat': 40.7128, 'lng': -74.0060}),
                        'urgency_level': report.get('urgency_level', 'normal'),
                        'animal_type': report.get('animal_type'),
                        'situation_type': report.get('situation_type'),
                        'created_at': report.get('created_at', datetime.now().isoformat()),
                        'contact_info': {
                            'name': report.get('contact_name'),
                            'email': report.get('contact_email'),
                            'phone': report.get('contact_phone')
                        },
                        'image_url': report.get('image_url'),
                        'ai_analysis': report.get('ai_analysis')
                    })
                
                return jsonify({
                    'success': True,
                    'reports': reports,
                    'total': len(reports),
                    'source': 'backup_file'
                })
            except Exception as file_error:
                print(f"Backup file error: {str(file_error)}")
        
        # Fallback to demo data for NYC area
        demo_reports = [
            {
                'id': 'demo-001',
                'description': 'Injured stray dog found in Central Park. Appears to have a leg injury and is limping. The dog seems friendly but scared.',
                'location': 'Central Park, Manhattan, New York, NY',
                'coordinates': {'lat': 40.7829, 'lng': -73.9654},
                'urgency_level': 'high',
                'animal_type': 'dog',
                'situation_type': 'injury',
                'created_at': datetime.now().isoformat(),
                'contact_info': {
                    'name': 'Demo Reporter',
                    'email': 'demo@example.com',
                    'phone': '+1-555-0123'
                },
                'image_url': None,
                'ai_analysis': {'severity': 'high', 'confidence': 0.85}
            },
            {
                'id': 'demo-002',
                'description': 'Cat stuck in tree for over 24 hours. Owner reports the cat has not eaten and appears weak.',
                'location': 'Brooklyn Bridge Park, Brooklyn, NY',
                'coordinates': {'lat': 40.7023, 'lng': -73.9969},
                'urgency_level': 'normal',
                'animal_type': 'cat',
                'situation_type': 'rescue',
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'contact_info': {
                    'name': 'Demo Reporter 2',
                    'email': 'demo2@example.com',
                    'phone': '+1-555-0124'
                },
                'image_url': None,
                'ai_analysis': {'severity': 'medium', 'confidence': 0.75}
            }
        ]
        
        return jsonify({
            'success': True,
            'reports': demo_reports,
            'total': len(demo_reports),
            'source': 'demo_data',
            'message': 'Using demo data - database not available'
        })
            
    except Exception as e:
        print(f"Get Reports Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to fetch reports',
            'error': str(e)
        }), 500

def send_whatsapp_receipt(phone_number, report_id, description):
    """Send WhatsApp receipt to user using business template"""
    try:
        from twilio.rest import Client as TwilioClient
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_whatsapp = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        client = TwilioClient(account_sid, auth_token)
        
        # Format the message for business template
        # Since we don't have a custom template yet, we'll use a freeform message
        # that works well for animal rescue confirmations
        
        message_body = f"""🆘 *RescueRadar Report Received*

Thank you for reporting an animal in need!

📋 Report ID: {report_id[:8]}
📝 Details: {description[:100]}{'...' if len(description) > 100 else ''}
⏰ Time: {datetime.now().strftime('%m/%d at %I:%M %p')}

✅ Your report has been forwarded to local rescue teams.

🚨 Emergency? Also contact local authorities immediately.

Reply to this message if you have updates."""
        
        try:
            message = client.messages.create(
                body=message_body.strip(),
                from_=from_whatsapp,
                to=f"whatsapp:{phone_number}"
            )
            
            return {
                'success': True,
                'message_id': message.sid,
                'status': message.status,
                'method': 'freeform'
            }
            
        except Exception as msg_error:
            print(f"WhatsApp message error: {str(msg_error)}")
            
            # If regular message fails, it might be because we need a template
            # For now, let's try a simple business template approach
            # You would need to create a template in Twilio Console first
            
            # Fallback: try with content template (requires pre-approval)
            # template_sid = os.getenv('TWILIO_WHATSAPP_TEMPLATE_SID', 'HXb5b62575e6e4ff6129ad7c8efe1f983e')
            # 
            # content_variables = {
            #     "1": datetime.now().strftime('%m/%d'),
            #     "2": datetime.now().strftime('%I:%M %p')
            # }
            # 
            # message = client.messages.create(
            #     content_sid=template_sid,
            #     content_variables=str(content_variables),
            #     from_=from_whatsapp,
            #     to=f"whatsapp:{phone_number}"
            # )
            
            return {
                'success': False,
                'error': str(msg_error),
                'note': 'Consider setting up a pre-approved business template'
            }
        
    except Exception as e:
        print(f"WhatsApp Receipt Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }






