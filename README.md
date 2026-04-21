# Alumni Tracer

A comprehensive web application for tracking and managing alumni records, employment history, further studies, and activities. Built with Django, the platform provides both student/alumni and administrative interfaces for maintaining detailed alumni databases with verification systems and analytics.

**Live Webiste**: [https://alumni-tracer.onrender.com/account/home/](https://alumni-tracer.onrender.com/account/home/)

## Features

### For Alumni Users
- **User Authentication**: Secure registration and login system
- **Profile Management**: 
  - Personal information (name, contact, student ID)
  - Profile photo upload with validation
  - Bio and social media links (LinkedIn, GitHub, Facebook, Instagram)
- **Employment Tracking**:
  - Log current and past employment history
  - Track job titles, companies, and seniority levels
  - Mark employment status (Employed, Unemployed, Self-employed, Further Studies)
- **Education Tracking**: Record further studies and educational pursuits
- **Activity Logging**: Track participation in alumni events and activities
- **Dashboard**: View comprehensive profile summary and historical records

### For Administrators
- **Admin Dashboard**: 
  - Statistical overview of alumni base
  - Breakdown by employment status, program, and graduation year
  - Recent registration tracking
- **Alumni Management**: 
  - View and manage all alumni records
  - Add/edit/delete alumni profiles
  - Bulk operations support
- **Profile Verification**: Verify and validate alumni information
- **Reporting**: Generate analytics and reports on alumni statistics
- **Site Configuration**: Manage website settings, carousel slides, core values, and page content
- **Face Recognition Login**: Optional facial recognition for admin authentication

### Advanced Features
- **Voice Recording**: Voice-based data entry for employment and study information
- **Face Detection**: Admin facial authentication system using TensorFlow.js
- **Search & Filtering**: Advanced filtering by program, graduation year, employment status
- **Multi-Program Support**: Track students from various engineering and business programs
- **Image Handling**: Automatic profile photo validation and optimization
- **Email Integration**: Password recovery and account notifications
- **Responsive Design**: Mobile-friendly interface

## Technology Stack

**Backend**
- Django 5.2.12 - Python web framework
- PostgreSQL - Database (via Render)
- WhiteNoise - Static file serving
- Pillow - Image processing
- NumPy - Numerical computations for face recognition

**Frontend**
- HTML5 & CSS3
- JavaScript with ES6+
- Bootstrap/Custom CSS
- TensorFlow.js - Client-side face detection
- Face-API - Face landmark detection and recognition

**Deployment**
- Render.com - Cloud hosting
- Gunicorn - WSGI HTTP Server
- Environment-based configuration

## Quick Start

> **Want to try it out?** Visit the live demo at [alumni-tracer.onrender.com/account/home/](https://alumni-tracer.onrender.com/account/home/)

### Prerequisites
- Python 3.8+
- PostgreSQL (or SQLite for development)
- pip or conda

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/HLyH3LL/Alumni-Tracer.git
cd Alumni-Tracer
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply migrations**
```bash
python manage.py migrate
```
```bash
python manage.py makemigrations
```

5. **Create a superuser**
```bash
python manage.py createsuperuser
```

6. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

7. **Run the development server**
```bash
python manage.py runserver
```

## Project Structure

```
Alumni-Tracer/
├── account/                      # Main Django app
│   ├── models.py                # Data models (Alumni, Employment, FurtherStudy, etc.)
│   ├── views.py                 # Core views and logic
│   ├── voice_views.py          # Voice recording endpoints
│   ├── auth_forms.py           # Authentication forms
│   ├── profile_forms.py        # Profile management forms
│   ├── admin.py                # Django admin configuration
│   ├── static/                 # CSS, JavaScript, Face API models
│   └── templates/              # HTML templates
│       ├── registration/       # Login/Register pages
│       ├── forms/              # Employment and study forms
│       ├── list/               # List views
│       ├── admin/              # Admin interface
│       └── account/            # Account management pages
├── bookmarks/                   # Django project settings
│   ├── settings.py             # Project configuration
│   ├── urls.py                 # URL routing
│   ├── wsgi.py                 # WSGI configuration
│   └── asgi.py                 # ASGI configuration
├── media/                       # User-uploaded files
│   ├── alumni_photos/          # Profile photos
│   ├── carousel/               # Carousel images
│   └── logos/                  # Site logos
├── staticfiles/                # Compiled static files
├── db.sqlite3                  # Development database
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── runtime.txt                 # Python version specification
```

## Authentication & Authorization

### User Roles
- **Alumni**: Registered graduates who can view and manage their own profiles
- **Admin**: Staff users who can manage all alumni records and site configuration
- **Superuser**: Django superuser for complete system access

### Access Control
- Login required decorators protect authenticated routes
- Staff-only decorators restrict admin functionality
- User can only edit their own profiles (except admins)

## Data Models

### Alumni
- Student ID, name, contact information
- Program and graduation year
- Employment status and current position
- Profile photo and biography
- Social media links
- Verification status

### Employment
- Job title and company
- Seniority level and dates
- Voice-recorded entry capability
- Associated alumni record

### FurtherStudy
- Degree and school information
- Dates of study
- Voice-recorded entry capability

### Activity
- Activity type and description
- Associated alumni record

### SiteConfig
- Site-wide settings
- Admin face descriptor for facial login
- Core values and page content management

## Key API Endpoints

### Authentication
- `POST /account/login/` - User login
- `POST /account/logout/` - User logout
- `POST /account/register/` - New user registration
- `POST /account/admin-login/` - Admin login
- `POST /account/admin-logout/` - Admin logout

### Alumni Operations
- `GET /account/dashboard/` - User dashboard
- `POST /account/edit-profile/` - Edit profile
- `POST /account/employment/add/` - Add employment record
- `GET /account/employment/list/` - View employment history
- `POST /account/study/add/` - Add study record
- `GET /account/study/list/` - View study history

### Admin Operations
- `GET /account/admin-dashboard/` - Admin dashboard with statistics
- `GET /account/alumni-records/` - View all alumni
- `POST /account/alumni/add/` - Add new alumni
- `GET /account/alumni/<id>/edit/` - Edit alumni record
- `POST /account/alumni/<id>/delete/` - Delete alumni record
- `GET /account/profile-verification/` - Alumni verification queue

### Face Recognition
- `POST /account/save-face/` - Save admin facial data
- `POST /account/face-login/` - Authenticate via facial recognition

### Voice Features
- `POST /account/employment/voice/` - Add employment via voice
- `POST /account/study/voice/` - Add study via voice

## Templates & Pages

### User-Facing Pages
- **Home**: Landing page with carousel and site information
- **Registration**: User sign-up form
- **Login**: Authentication page
- **Dashboard**: Personal profile and record summary
- **Profile Edit**: Update personal information
- **Employment Forms**: Add/edit employment records
- **Study Forms**: Add/edit further study records
- **Record Lists**: View historical employment and study entries
- **Privacy Policy & Terms**: Legal information pages

### Admin Pages
- **Admin Login**: Secure admin authentication
- **Admin Dashboard**: Statistics and analytics overview
- **Alumni Records**: Full alumni database management
- **Profile Verification**: Review and verify alumni information
- **Reports**: Alumni statistics and breakdowns
- **Site Configuration**: Edit site content and settings

## Configuration

### Static Files
- WhiteNoise middleware handles static file serving
- Run `python manage.py collectstatic` before deployment
- Face API models are included in static files

## Deployment

The project is configured for deployment on Render.com:

1. **Database**: PostgreSQL on Render
2. **Static Files**: WhiteNoise for serving
3. **Environment**: Set environment variables in Render dashboard
4. **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
5. **Start Command**: `gunicorn bookmarks.wsgi:application`

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL credentials in `.env` are correct
- For development, switch to SQLite by removing DATABASE_URL

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Ensure STATIC_ROOT and STATIC_URL are configured correctly

### Email Not Sending
- Verify SMTP credentials in environment variables
- Check the inbox spam folder
- For development, use console email backend

### Face Recognition Not Working
- Ensure face-api models are loaded (check browser console)
- Camera permissions must be granted in the browser
- Use HTTPS for production (required by browser APIs)

---
