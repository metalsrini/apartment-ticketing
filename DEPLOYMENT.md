# Deployment Guide

## Database Storage Options

This application supports multiple database backends for production deployment:

### 1. SQLite (Default - Local Deployment)

**Best for:** Small to medium deployments, single server setups

```bash
# No additional setup required
# Database file will be created automatically as 'tickets.db'
export USE_DATABASE=true
python enhanced_app.py
```

**Pros:**
- No additional database server required
- Zero configuration
- Perfect for local or small-scale deployments

**Cons:**
- Not suitable for high-traffic applications
- Single file can be a bottleneck

### 2. PostgreSQL (Recommended for Production)

**Best for:** Production deployments, cloud hosting, high availability

```bash
# Set environment variables
export USE_DATABASE=true
export DATABASE_URL="postgresql://username:password@localhost:5432/tickets_db"

# Or individual components
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=tickets_db
export DB_USER=username
export DB_PASSWORD=password

python enhanced_app.py
```

**Cloud Deployment Examples:**

**Heroku:**
```bash
# Heroku automatically provides DATABASE_URL
heroku config:set USE_DATABASE=true
```

**Railway/Render:**
```bash
# Set in environment variables
USE_DATABASE=true
DATABASE_URL=${{POSTGRES.DATABASE_URL}}
```

### 3. MySQL

```bash
export USE_DATABASE=true
export DATABASE_URL="mysql://username:password@localhost:3306/tickets_db"
python enhanced_app.py
```

## Authentication

The application includes admin authentication for the reports section:

- **Username:** admin
- **Password:** admin
- **Protected Route:** `/reports`

**To change credentials:**
```python
# In enhanced_app.py
ADMIN_CREDENTIALS = {
    'username': 'your_username',
    'password': 'your_password'
}
```

## Migration from CSV

If you have existing CSV data, the application will automatically migrate it to the database on first run when `USE_DATABASE=true`.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `USE_DATABASE` | Enable database mode | `false` |
| `DATABASE_URL` | Full database connection string | - |
| `DB_TYPE` | Database type (sqlite/postgresql/mysql) | `sqlite` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | - |
| `DB_NAME` | Database name | `tickets.db` |
| `DB_USER` | Database username | - |
| `DB_PASSWORD` | Database password | - |

## Quick Start Commands

### Local Development (SQLite)
```bash
pip install -r requirements.txt
export USE_DATABASE=true
python enhanced_app.py
```

### Production (PostgreSQL)
```bash
pip install -r requirements.txt
export USE_DATABASE=true
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
python enhanced_app.py
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5002
ENV USE_DATABASE=true
CMD ["python", "enhanced_app.py"]
```

## Security Notes

1. **Change default admin credentials** before production
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Set a secure SECRET_KEY** for Flask sessions
5. **Use a proper WSGI server** like Gunicorn for production

## Production WSGI Setup

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 enhanced_app:app
```

## Backup Strategy

### SQLite
```bash
# Simple file copy
cp tickets.db tickets_backup_$(date +%Y%m%d).db
```

### PostgreSQL
```bash
# Database dump
pg_dump tickets_db > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

1. **Database connection issues:** Check DATABASE_URL format
2. **Migration problems:** Ensure CSV file exists and is readable
3. **Authentication not working:** Verify session configuration
4. **Performance issues:** Consider upgrading from SQLite to PostgreSQL