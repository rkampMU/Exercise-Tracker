# Vercel Deployment Guide for ClassTracker

This guide will help you deploy your ClassTracker application to Vercel for production.

## Prerequisites

1. ✅ Vercel account (create at https://vercel.com)
2. ✅ GitHub account with your repository pushed
3. ✅ Supabase project with database configured
4. ✅ All environment variables set

## Step 1: Prepare Your Repository

Make sure all changes are committed:

```bash
cd /Users/familymac/ClassTracker/project
git status
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

## Step 2: Create Vercel Project

### Option A: Using Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project directory
cd /Users/familymac/ClassTracker/project
vercel
```

### Option B: Using Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Select "Import Git Repository"
4. Choose your GitHub repository (Exercise-Tracker)
5. Click "Import"

## Step 3: Configure Environment Variables

In Vercel Dashboard:

1. Go to your project settings
2. Click "Environment Variables"
3. Add the following variables:

```
SUPABASE_URL=https://csgwfqrmpggjapbucvlx.supabase.co
SUPABASE_KEY=your_supabase_key_here
FLASK_ENV=production
SECRET_KEY=your_secure_random_key_here
```

⚠️ **IMPORTANT**: 
- Replace `SUPABASE_KEY` with your actual Supabase API key
- Use a strong random string for `SECRET_KEY`
- Never commit `.env` file with real credentials

## Step 4: Update QR Code URLs

Your QR codes will point to localhost by default. Update them for production:

### In `app.py`, find the QR code generation section:

```python
# Generate QR code
qr_url = request.host_url + f'complete/{qr_token}'
```

This will automatically use your Vercel domain. No changes needed!

## Step 5: Deploy

### Via CLI:
```bash
vercel --prod
```

### Via GitHub:
1. Push changes to `main` branch
2. Vercel will automatically deploy
3. Your app will be live at: `https://your-project-name.vercel.app`

## Step 6: Verify Deployment

After deployment completes:

1. ✅ Visit your app URL: `https://your-project-name.vercel.app`
2. ✅ Test login: Use admin / admin123
3. ✅ Create a test class
4. ✅ Generate a QR code (should point to your Vercel domain)
5. ✅ Scan QR code and test exercise completion

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure `requirements.txt` has all dependencies:

```bash
pip freeze > requirements.txt
```

Then commit and push.

### Issue: "Supabase connection failed"

**Solution**: 
1. Check environment variables are set correctly
2. Verify SUPABASE_URL and SUPABASE_KEY in Vercel settings
3. Test connection locally: `python app.py`

### Issue: Static files (CSS/JS) not loading

**Solution**: Ensure Flask is serving templates correctly:

```python
app = Flask(__name__)
# Files in templates/ directory are served automatically
```

### Issue: "Environment variable not found"

**Solution**: 
1. Go to Vercel Dashboard → Project Settings
2. Click "Environment Variables"
3. Ensure variables are added for all environments (Production, Preview, Development)
4. Redeploy: `vercel --prod`

## Production Best Practices

1. **Enable HTTPS**: Vercel does this automatically ✓
2. **Use environment variables**: Never hardcode secrets
3. **Set FLASK_ENV=production**: Disables debug mode
4. **Monitor logs**: Vercel Dashboard → Deployments → Logs
5. **Enable RLS in Supabase**: For production security

## Environment Variables Checklist

```
[ ] SUPABASE_URL - Your Supabase project URL
[ ] SUPABASE_KEY - Your Supabase API key
[ ] FLASK_ENV - Set to "production"
[ ] SECRET_KEY - Strong random string
```

## Accessing Your App

Once deployed, your app will be available at:
```
https://your-project-name.vercel.app
```

Share this URL with instructors to access the admin dashboard!

## Custom Domain (Optional)

To use your own domain:

1. In Vercel Dashboard → Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed by Vercel
4. Click "Verify"

## Updating Your App

Every time you push to `main` branch:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Vercel will automatically redeploy! 🚀

## Database Backups

Supabase automatically backs up your data. To manually backup:

1. Go to Supabase Dashboard
2. Select your project
3. Click "Database" → "Backups"
4. Download backup file

## Security Checklist

- [ ] Disabled debug mode in production (FLASK_ENV=production)
- [ ] Environment variables not in git repository
- [ ] Strong SECRET_KEY set
- [ ] Supabase RLS policies configured
- [ ] HTTPS enabled (automatic with Vercel)
- [ ] Regular database backups

## Support

- Vercel Docs: https://vercel.com/docs
- Flask Docs: https://flask.palletsprojects.com
- Supabase Docs: https://supabase.com/docs

---

**You're ready to deploy!** 🎉

If you encounter issues, check:
1. Vercel logs (Dashboard → Deployments)
2. Browser console (F12 → Console)
3. Supabase logs (Dashboard → SQL Editor)
