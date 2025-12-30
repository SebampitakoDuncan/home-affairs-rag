# Qdrant Cloud Setup Guide

This guide walks you through getting a Qdrant Cloud URL and setting it up for your Home Affairs RAG System on Streamlit Cloud.

## 🚀 Option 1: Quick Start (Free Tier - Recommended for Testing)

### Step 1: Sign Up for Qdrant Cloud

1. Go to: https://cloud.qdrant.io/signup
2. Click **"Start Free"** (no credit card required)
3. Sign up or login with your account

### Step 2: Create a Cloud Cluster

1. After logging in, you'll be redirected to the dashboard
2. Click **"Create Cluster"** button
3. Enter a name for your cluster (e.g., `home-affairs-rag`)
4. Select **"Free"** tier (1GB RAM, includes Qdrant server)
5. Click **"Create Cluster"**

### Step 3: Get Your Qdrant Cloud URL

1. After cluster is created, find it in your dashboard
2. Click on your cluster name
3. Look for the **HTTP/HTTPS URL** - it will look like:
   ```
   https://xxxxx-xxxxx-xxxxx-xxxxx.qdrant.tech
   ```
   Or with port:
   ```
   https://xxxxx-xxxxx-xxxxx-xxxxx.qdrant.tech:6333
   ```

**⚠️ Important:** The URL with port (`:6333`) is what you need for Qdrant client!

### Step 4: Copy the URL

Copy your Qdrant Cloud URL (with port `:6333`):
```
https://your-cluster-url.qdrant.tech:6333
```

### Step 5: Update Streamlit Cloud Secrets

1. Go to: https://share.streamlit.io
2. Find your app: `SebampitakoDuncan/home-affairs-rag`
3. Click **"..."** (three dots) → **"Manage app"**
4. Go to **"Secrets"** section
5. Click **"Add new secret"**
6. Name: `QDRANT_URL`
7. Value: `https://your-cluster-url.qdrant.tech:6333`
8. Click **"Save"**

Your other secrets should already be set:
- `OPENROUTER_API_KEY` = Your OpenRouter API key
- `OPENROUTER_MODEL` = `gpt-4o-mini` (or your preferred model)

### Step 6: Verify Deployment

1. After saving secrets, Streamlit will redeploy automatically (takes ~1-2 minutes)
2. Click on your app URL to verify it loads
3. Test with a query: "What are requirements for a 189 visa?"

---

## 📊 Option 2: Advanced (Different Tiers)

### Create Standard Cluster

1. In Qdrant Cloud dashboard, click **"Create Cluster"**
2. Choose **"Standard"** tier ($4-10/month)
3. This gives you:
   - 8-16GB RAM
   - More performance
   - Better for production

### Create Production Cluster

1. Choose **"Production"** tier
2. This gives you:
   - 16-64GB RAM
   - Maximum performance
   - SLA guarantees

---

## 🔄 Option 3: Use Local Qdrant with Streamlit Cloud

If you want to use your local Docker Qdrant with Streamlit Cloud, you need to **expose it to the internet**.

### Using Ngrok (Easiest)

1. Install ngrok:
   ```bash
   brew install ngrok
   ```

2. Start your local Qdrant:
   ```bash
   docker-compose up -d qdrant
   ```

3. Expose Qdrant port:
   ```bash
   ngrok http 6333
   ```

4. Copy the ngrok URL (e.g., `https://random-id.ngrok-free.app`)

5. Use in Streamlit Cloud secrets:
   - Name: `QDRANT_URL`
   - Value: `https://random-id.ngrok-free.app` (without `:6333`)

---

## 📁 Option 4: Deploy Your Own Qdrant Server

If you have a VPS or cloud server, you can run Qdrant yourself:

1. SSH into your server
2. Install Docker:
   ```bash
   curl -fsSL https://qdrant.tech/install.sh | sh
   ```

3. Start Qdrant:
   ```bash
   docker run -d -p 6333:6333 qdrant/qdrant
   ```

4. Use your server's public URL in Streamlit Cloud:
   - Name: `QDRANT_URL`
   - Value: `http://your-server-ip:6333` or `https://your-domain.com:6333`

---

## 🔍 Troubleshooting

### Streamlit Cloud Error: "Connection to Qdrant failed"

1. Check your `QDRANT_URL` in Secrets
2. Make sure it includes the port (`:6333`)
3. Verify URL format:
   - ✅ Correct: `https://cluster-name.qdrant.tech:6333`
   - ❌ Wrong: `https://cluster-name.qdrant.tech` (missing port)
4. Check if your cluster is running in Qdrant Cloud dashboard

### Connection Refused

1. Make sure your Qdrant cluster is running (green status in dashboard)
2. Check if port `6333` is exposed
3. Try testing URL in browser first

### Timeout Errors

1. Free tier has 1GB RAM - may be slow
2. Consider upgrading to Standard tier for better performance
3. Add caching to your app

---

## 📋 Summary of Required Secrets for Streamlit Cloud

| Secret Name | Value | Description |
|------------|-------|-------------|
| `QDRANT_URL` | Your Qdrant Cloud URL | Must include `:6333` port |
| `OPENROUTER_API_KEY` | `sk-or-v1-84b2...` | Your OpenRouter API key |
| `OPENROUTER_MODEL` | `gpt-4o-mini` | Model to use (optional) |

---

## 🎯 Recommended Setup for Testing

**Free Qdrant Cloud + Streamlit Cloud** = $0/month

This is perfect for:
- Learning and testing
- Small projects
- Proof of concept

**Upgrade path:**
1. Start with Free tier
2. When ready for production, upgrade to Standard tier
3. Update `QDRANT_URL` in Streamlit Cloud secrets

---

## 📝 Additional Resources

- [Qdrant Cloud Documentation](https://qdrant.tech/documentation/cloud-intro/)
- [Qdrant Cloud Quickstart](https://qdrant.tech/documentation/quickstart-cloud/)
- [Qdrant API Reference](https://api.qdrant.tech/api-reference/)
- [Streamlit Cloud Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
