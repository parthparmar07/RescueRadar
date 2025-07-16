from flask import Blueprint, request, jsonify
import os
import requests
from groq import Groq

ai_bp = Blueprint('ai_analysis', __name__)

@ai_bp.route('/ai-analysis', methods=['POST'])
def analyze_report():
    """AI Analysis of animal cruelty reports"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'message': 'Description is required'
            }), 400
        
        description = data['description'].lower()
        location = data.get('location', '')
        image_url = data.get('image_url', '')
        
        # Simple rule-based analysis for immediate functionality
        analysis = {
            'severity': 'medium',
            'category': 'general',
            'urgency_level': 'normal',
            'response_team': 'animal_control',
            'recommended_action': 'Standard response protocol recommended.',
            'full_analysis': ''
        }
        
        # Emergency keywords
        emergency_keywords = ['emergency', 'dying', 'bleeding', 'severe', 'critical', 'urgent', 'immediate', 'life-threatening']
        high_keywords = ['injured', 'hurt', 'sick', 'abuse', 'neglect', 'abandoned', 'trapped', 'danger']
        low_keywords = ['stray', 'lost', 'mild', 'minor', 'observation']
        
        # Determine severity based on keywords
        if any(keyword in description for keyword in emergency_keywords):
            analysis.update({
                'severity': 'emergency',
                'urgency_level': 'emergency',
                'response_team': 'emergency_vet',
                'recommended_action': 'IMMEDIATE ACTION REQUIRED: Contact emergency veterinary services and animal rescue teams immediately.',
                'full_analysis': 'Emergency situation detected. Immediate veterinary attention and rescue response needed.'
            })
        elif any(keyword in description for keyword in high_keywords):
            analysis.update({
                'severity': 'high',
                'urgency_level': 'high',
                'response_team': 'veterinary_rescue',
                'recommended_action': 'High priority response needed. Contact local animal welfare organizations and veterinary services.',
                'full_analysis': 'High priority situation requiring prompt attention from qualified animal welfare professionals.'
            })
        elif any(keyword in description for keyword in low_keywords):
            analysis.update({
                'severity': 'low',
                'urgency_level': 'low',
                'response_team': 'animal_control',
                'recommended_action': 'Standard monitoring and welfare check recommended.',
                'full_analysis': 'Standard animal welfare check and monitoring recommended.'
            })
        else:
            analysis.update({
                'severity': 'normal',
                'urgency_level': 'normal',
                'response_team': 'animal_welfare',
                'recommended_action': 'Regular animal welfare assessment recommended.',
                'full_analysis': 'Standard animal welfare assessment and appropriate response measures recommended.'
            })
        
        # Add location-specific recommendations
        if location:
            analysis['full_analysis'] += f' Location: {location}. Coordinate with local authorities in this area.'
        
        # Try Groq API as enhancement if available
        try:
            if os.getenv('GROQ_API_KEY'):
                from groq import Groq
                client = Groq(api_key=os.getenv('GROQ_API_KEY'))
                
                prompt = f"""
                Analyze this animal report and provide a brief assessment:
                Description: {description}
                Location: {location}
                
                Provide severity (emergency/high/normal/low) and brief recommendation.
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are an animal welfare expert. Provide brief, actionable analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3,
                    max_tokens=200
                )
                
                ai_response = chat_completion.choices[0].message.content
                analysis['ai_enhancement'] = ai_response
                
        except Exception as ai_error:
            print(f"AI Enhancement failed (using fallback): {ai_error}")
            # Continue with rule-based analysis
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"AI Analysis Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to analyze report',
            'error': str(e)
        }), 500
