# 🚀 Deploying Hemi-gen to the Web

## Quick Deployment Options

### Option 1: Deploy to Render (FREE - Recommended)

1. **Push your code to GitHub first:**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin master
   ```

2. **Deploy to Render:**
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Name**: hemi-gen
     - **Runtime**: Python
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app_production:app`
   
3. **Add Environment Variables in Render Dashboard:**
   - `GEMINI_API_KEY` = Your Gemini API key
   - `ELEVENLABS_API_KEY` = Your ElevenLabs API key
   - `ELEVENLABS_VOICE_ID` = 7nFoun39JV8WgdJ3vGmC (or your voice ID)

4. **Click "Create Web Service"**

Your app will be live at: `https://hemi-gen.onrender.com` (or similar)

### Option 2: Deploy to Railway (Simple Alternative)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Add environment variables in Railway dashboard**

4. **Get your public URL:**
   ```bash
   railway open
   ```

### Option 3: Deploy to PythonAnywhere (Free Tier)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your files
3. Set up Flask app in Web tab
4. Add environment variables in .env file
5. Your app will be at: `https://yourusername.pythonanywhere.com`

### Option 4: Deploy to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Create vercel.json:**
   ```json
   {
     "builds": [
       {
         "src": "app_production.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app_production.py"
       }
     ]
   }
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

## Important Notes

### API Keys Security
- **NEVER** commit API keys to GitHub
- Use environment variables on all platforms
- Consider using separate keys for production

### File Storage Limitations
- Most free hosting doesn't persist files
- Generated meditations will be temporary
- Consider using cloud storage (S3, Cloudinary) for permanent storage

### Audio Generation
- ElevenLabs API has quotas
- The production app disables audio generation by default
- Enable it only if you have sufficient credits

### Custom Domain
- All platforms support custom domains
- Usually requires a paid plan
- Example: `meditation.yourdomain.com`

## Production Checklist

- [x] Remove debug mode from Flask
- [x] Add gunicorn for production server
- [x] Use environment variables for secrets
- [x] Create requirements.txt
- [x] Add error handling for API failures
- [x] Disable audio generation in demo mode
- [ ] Add rate limiting (optional)
- [ ] Add user analytics (optional)
- [ ] Set up monitoring (optional)

## Monitoring Your App

### Free Monitoring Options:
- **UptimeRobot**: Check if site is up
- **Render Dashboard**: Built-in metrics
- **Google Analytics**: User tracking

## Troubleshooting

### Common Issues:

1. **"Application Error" on Heroku/Render**
   - Check logs: `heroku logs --tail` or Render dashboard
   - Usually missing environment variables

2. **"Module not found"**
   - Ensure all dependencies are in requirements.txt
   - Check Python version compatibility

3. **"API quota exceeded"**
   - Disable audio generation
   - Implement caching
   - Use backup API keys

### Support Resources:
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/

## Next Steps

After deployment:
1. Test all features
2. Share your meditation app link!
3. Monitor usage and errors
4. Consider adding:
   - User accounts
   - Saved meditations
   - Social sharing
   - Premium features

---

**Questions?** Check the logs first, then the platform's documentation.