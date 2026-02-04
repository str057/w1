# Django Project with CI/CD Pipeline

## 🚀 Live Deployment
- **URL:** https://django-app-lji9.onrender.com
- **Status:** ✅ Live
- **Auto-deploy:** On push to main branch

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow:
1. **Tests run** on every push/pull request
2. **Deploy only after tests pass** (dependency: `needs: test`)
3. **Automatic deployment** to Render via webhook

### Server Configuration (Render):
- **Web Service:** Django + Gunicorn
- **Database:** PostgreSQL (managed by Render)
- **Process Management:** Built-in (equivalent to Supervisor)
- **Security:** Built-in firewall and SSL

## 🛠️ Local Development
```bash
# Clone repository
git clone <repo-url>
cd project

# Setup virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run server
python manage.py runserver