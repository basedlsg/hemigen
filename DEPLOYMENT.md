# Hemi-gen Deployment Guide

## 🚀 Quick Deploy to Vercel (Recommended)

### 1. Prerequisites
- GitHub account
- Vercel account (free tier available)
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Optional: Redis database from [Upstash](https://upstash.com) for rate limiting

### 2. Deploy Steps

1. **Fork/Clone this repository**
   ```bash
   git clone https://github.com/yourusername/focus-creation
   cd focus-creation
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Set Environment Variables**
   In Vercel dashboard → Settings → Environment Variables:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key
   REDIS_URL=your_redis_url (optional)
   ```

4. **Deploy**
   - Click "Deploy" in Vercel
   - Your app will be live at `https://your-project.vercel.app`

### 3. File Structure
```
/
├── api/
│   └── generate.py          # Serverless API endpoint
├── public/
│   └── index.html          # Frontend interface
├── vercel.json             # Vercel configuration
├── requirements.txt        # Python dependencies
└── DEPLOYMENT.md          # This file
```

## 🔒 Security Features

✅ **Rate Limiting**: 3 requests per 24 hours per IP  
✅ **Input Validation**: Content filtering and length limits  
✅ **CORS Protection**: Properly configured headers  
✅ **XSS Protection**: Content Security Policy  
✅ **API Key Security**: Server-side only, never exposed  

## 💰 Cost Management

### Free Tier Limits:
- **Vercel**: 100GB bandwidth, 100 builds per month
- **Gemini API**: 60 requests per minute (free tier)
- **Upstash Redis**: 10,000 requests per day (free tier)

### Estimated Costs:
- **Free usage**: $0/month for ~1000 meditations
- **Paid usage**: ~$0.001 per meditation (Gemini API costs)

## 🔧 Alternative Deployments

### Deploy to Netlify
1. Create `netlify.toml`:
   ```toml
   [build]
     functions = "api"
     publish = "public"
   ```

2. Add environment variables in Netlify dashboard
3. Deploy from GitHub

### Deploy to Railway
1. Connect GitHub repository
2. Set environment variables
3. Railway auto-deploys

### Deploy to Google Cloud Run
1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["python", "api/generate.py"]
   ```

2. Deploy with Cloud Run

## 🛠️ Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export GEMINI_API_KEY=your_key_here
   export REDIS_URL=redis://localhost:6379
   ```

3. **Run locally**:
   ```bash
   cd api && python generate.py
   ```

## 📊 Monitoring & Analytics

### Add Google Analytics (Optional)
Add to `public/index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Add Uptime Monitoring
- Use [UptimeRobot](https://uptimerobot.com) (free)
- Monitor your Vercel URL
- Get alerts if site goes down

## 🚨 Production Checklist

- [ ] Environment variables set in Vercel
- [ ] Custom domain configured (optional)
- [ ] Analytics tracking added
- [ ] Uptime monitoring configured
- [ ] Rate limiting tested
- [ ] Error handling verified
- [ ] HTTPS certificate active (automatic with Vercel)

## 🔧 Troubleshooting

### Common Issues:

1. **"API configuration error"**
   - Check GEMINI_API_KEY is set correctly
   - Verify API key has proper permissions

2. **Rate limiting not working**
   - Ensure REDIS_URL is configured
   - Check Upstash Redis connection

3. **Deployment fails**
   - Check Python version compatibility
   - Verify all dependencies in requirements.txt

### Support
- Check Vercel deployment logs
- Test API endpoint directly: `your-domain.com/api/generate`
- Verify CORS headers in browser dev tools

---

**Ready to deploy?** Follow the Vercel quick deploy steps above! 🚀