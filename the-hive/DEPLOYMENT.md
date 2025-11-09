# The Hive - DigitalOcean Deployment Guide

## Prerequisites
1. GitHub repository with the code
2. DigitalOcean account

## Deployment Steps

### 1. Create a New App in DigitalOcean App Platform

1. Go to DigitalOcean → Apps → Create App
2. Connect your GitHub repository: `mzyavuz/SWE-573-Software-Development-Practice`
3. Select branch: `main`
4. **Important**: Set the source directory to: `the-hive`

### 2. Configure the Backend Component

DigitalOcean should auto-detect the Dockerfile. Configure:

- **Component Name**: `the-hive-backend`
- **Type**: Web Service
- **Dockerfile Path**: `Dockerfile` (in the-hive directory)
- **HTTP Port**: `5000`
- **HTTP Routes**: `/`
- **Instance Size**: Basic (512 MB RAM, 1 vCPU) - $5/month
- **Instance Count**: 1

### 3. Add PostgreSQL Database

1. Click "Add Resource" → Database
2. Select **PostgreSQL**
3. **Engine Version**: 14
4. **Database Name**: `hive-db` (or any name you prefer)
5. **Plan**: Development (Free) or Basic ($15/month for production)

### 4. Configure Environment Variables

DigitalOcean will automatically inject database connection variables. You need to add:

**Required Variables:**
- `DATABASE_URL` → `${db.DATABASE_URL}` (auto-injected by DigitalOcean)
- `POSTGRES_USER` → `${db.USERNAME}` (auto-injected)
- `POSTGRES_PASSWORD` → `${db.PASSWORD}` (auto-injected)
- `POSTGRES_DB` → `${db.DATABASE}` (auto-injected)

**Optional but Recommended:**
- `SECRET_KEY` → Generate a random secure key (use: `openssl rand -hex 32`)

### 5. Deploy

1. Click "Create Resources"
2. Wait for deployment (5-10 minutes)
3. DigitalOcean will:
   - Build your Docker image
   - Create the database
   - Deploy the application
   - Assign a public URL

### 6. Post-Deployment

**Access your app:**
- Your app will be available at: `https://[your-app-name].ondigitalocean.app`

**Monitor logs:**
- Go to App → Runtime Logs to check for any errors

**Database initialization:**
- The database tables will be created automatically on first run
- Check logs to confirm: "Database initialized successfully"

## Troubleshooting

### "could not translate host name 'db'"
✅ **Fixed!** The code now checks for `DATABASE_URL` environment variable

### Health check failures
- Ensure the app is listening on port 5000
- Check logs for startup errors
- Database connection issues

### Database connection errors
- Verify `DATABASE_URL` is set correctly
- Check database component is running
- Ensure database and app are in the same region

## Environment Variables Reference

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Auto-injected | Full PostgreSQL connection string |
| `POSTGRES_USER` | Auto-injected | Database username |
| `POSTGRES_PASSWORD` | Auto-injected | Database password |
| `POSTGRES_DB` | Auto-injected | Database name |
| `SECRET_KEY` | Manual | Flask secret key for sessions |

## Cost Estimate

**Development Setup (Free Tier):**
- App Platform Basic: $5/month
- PostgreSQL Development: Free
- **Total: $5/month**

**Production Setup:**
- App Platform Professional: $12/month
- PostgreSQL Basic: $15/month
- **Total: $27/month**

## Security Checklist

- [ ] Change `SECRET_KEY` from default
- [ ] Enable HTTPS (automatic with App Platform)
- [ ] Set up trusted sources if needed
- [ ] Review database access permissions
- [ ] Enable App Platform alerts

## Useful Commands

**View logs:**
```bash
doctl apps logs <app-id>
```

**Restart app:**
```bash
doctl apps create-deployment <app-id>
```

## Support

If you encounter issues:
1. Check Runtime Logs in DigitalOcean dashboard
2. Verify environment variables are set
3. Ensure database is running
4. Check app build logs
