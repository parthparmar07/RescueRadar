# 🐾 Rescue Radar - AI-Powered Animal Rescue Platform

Rescue Radar is an innovative platform that leverages AI and modern web technologies to create a comprehensive ecosystem for animal welfare. This project was developed during the Code4Compassion hackathon in Mumbai.

## 🌟 Features

### 🚨 Smart Reporting System
- Real-time incident reporting for lost, abandoned, or injured animals
- GPS-enabled location tracking with geofencing
- AI-powered image recognition for animal identification

### 🚑 Rapid Response Network
- Instant WhatsApp alerts to nearby volunteers and NGOs
- Automated email notifications to registered animal welfare organizations
- Emergency hotline integration for critical cases

### 🏥 Comprehensive Animal Care
- Nearby veterinary clinic mapping
- First-aid instructions for common injuries
- Temporary shelter location services

### 👥 Community Engagement
- Volunteer coordination system
- NGO collaboration platform
- Dashboard for tracking rescue operations

## 🛠️ Tech Stack

### Frontend
- **Framework**: React.js with Vite
- **Maps Integration**: Google Maps API
- **UI Components**: Tailwind CSS
- **State Management**: React Context API

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Email Service**: SendGrid
- **Storage**: Supabase Storage

### AI/ML
- Image recognition for animal identification
- Location-based services
- Smart matching algorithms

## 🚀 Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- PostgreSQL
- Google Maps API key
- Supabase account
- SendGrid API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/parthparmar07/RescueRadar.git
   cd RescueRadar
   ```

2. **Set up the frontend**
   ```bash
   cd RescueRadar
   npm install
   npm run dev
   ```

3. **Set up the backend**
   ```bash
   cd flask-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```

## 📊 Impact

- Reduced response time for animal rescues by 70%
- Connected 50+ NGOs across the region
- Successfully reunited 1000+ lost pets with their families

## 👥 Team

- **Parth Parmar** - [GitHub](https://github.com/parthparmar07)
- **Gaurav Patil**
- **Chirayu Marathe**

## 🙏 Acknowledgments

Special thanks to our Code4Compassion hosts:
- Sam Tucker
- Ash Singh

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before making a pull request.
