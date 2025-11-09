# Database Reset Guide for DigitalOcean

## Quick Reset (Recommended)

### Method 1: Using the Reset Script

1. **Access DigitalOcean App Console:**
   - Go to DigitalOcean Dashboard
   - Apps → the-hive → Console tab
   - Click "Create Console"

2. **Run the reset script:**
   ```bash
   cd /app/backend
   python3 reset_db.py
   ```
   
3. **Type `DELETE` to confirm**

4. **Force redeploy:**
   - Go to Apps → the-hive → Settings
   - Click "Force Rebuild and Deploy"

---

### Method 2: Manual SQL Reset

1. **Get database connection string:**
   - DigitalOcean Dashboard → Databases
   - Click your PostgreSQL database
   - Click "Connection Details"
   - Copy the connection string

2. **Connect via psql (from your local machine):**
   ```bash
   psql "postgresql://username:password@host:port/database?sslmode=require"
   ```

3. **Drop all tables:**
   ```sql
   DROP TABLE IF EXISTS messages CASCADE;
   DROP TABLE IF EXISTS service_progress CASCADE;
   DROP TABLE IF EXISTS service_applications CASCADE;
   DROP TABLE IF EXISTS service_availability CASCADE;
   DROP TABLE IF EXISTS service_tags CASCADE;
   DROP TABLE IF EXISTS services CASCADE;
   DROP TABLE IF EXISTS password_reset_tokens CASCADE;
   DROP TABLE IF EXISTS email_verifications CASCADE;
   DROP TABLE IF EXISTS tags CASCADE;
   DROP TABLE IF EXISTS users CASCADE;
   ```

4. **Exit psql:**
   ```sql
   \q
   ```

5. **Force redeploy on DigitalOcean:**
   - Dashboard → Apps → the-hive
   - Actions → "Force Rebuild and Deploy"

---

### Method 3: Destroy and Recreate Database

1. **Backup connection info (if needed):**
   - Note down your DATABASE_URL from app settings

2. **Destroy the database:**
   - DigitalOcean Dashboard → Databases
   - Select your database
   - Settings → "Destroy Database"
   - Confirm

3. **Create new database:**
   - DigitalOcean Dashboard → Apps → the-hive
   - Settings → "Create Resource" → Database
   - Select: PostgreSQL 14
   - Plan: Development (Free) or Basic
   - Name: hive-db
   - Click "Create and Attach"

4. **Wait for provisioning** (2-5 minutes)

5. **Automatic redeploy:**
   - The app will automatically redeploy with the new database
   - Check Runtime Logs for "Database initialized successfully!"

---

## Troubleshooting

### "Connection refused" error
- Database is still provisioning, wait a few more minutes
- Check database status: Databases → Your DB → should show "Available"

### "Migration errors" or "Column already exists"
- Tables were created before ALTER statements ran
- Solution: Drop tables manually (Method 2) then redeploy

### App won't start after reset
1. Check Runtime Logs for actual error
2. Verify DATABASE_URL is set correctly
3. Try "Force Rebuild and Deploy" again

### How to verify reset worked
After redeployment, check logs for:
```
Database initialized successfully!
Migrations applied successfully!
```

---

## Local Testing (Docker)

To test the reset locally before doing it on DigitalOcean:

```bash
# Stop containers
docker-compose down

# Delete database volume (complete wipe)
docker-compose down -v

# Rebuild and restart
docker-compose up --build
```

---

## After Reset Checklist

- [ ] App deployed successfully
- [ ] No errors in Runtime Logs
- [ ] Database tables created (check logs)
- [ ] Can access the app URL
- [ ] Can create a new user account
- [ ] Can login
- [ ] Can create services

---

## Emergency Rollback

If something goes wrong:

1. **Check previous deployments:**
   - Apps → the-hive → Activity
   - Find last working deployment
   - Click "Redeploy"

2. **Or revert code:**
   ```bash
   # Locally
   git log --oneline  # Find last good commit
   git revert <commit-hash>
   git push origin main
   ```
