# ContractIQ - Quick Deployment to Hugging Face Spaces

## 🚀 5-Minute Deployment

### Prerequisites
- Hugging Face account (free): https://huggingface.co/join
- Groq API key (free): https://console.groq.com

### Step 1: Create Space (2 minutes)

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name:** `contractiq-rag` (or your choice)
   - **License:** MIT
   - **Select SDK:** Streamlit
   - **Space hardware:** CPU basic (free)
   - **Visibility:** Public or Private
3. Click "Create Space"

### Step 2: Add API Key (1 minute)

1. In your new Space, go to **Settings** tab
2. Scroll to **Repository secrets**
3. Click **New secret**
4. Add:
   - **Name:** `GROQ_API_KEY`
   - **Value:** Your Groq API key from https://console.groq.com
5. Click **Add**

### Step 3: Upload Files (2 minutes)

1. Click **Files** tab in your Space
2. Upload these files from your local `contractiq-rag/` directory:

**Required files:**
```
contractiq-rag/
├── app.py                          # ← Upload this
├── requirements.txt                # ← Upload this
├── .huggingface/space.yaml         # ← Upload this
└── app/                            # ← Upload entire folder
    ├── __init__.py
    ├── api/
    ├── chunking/
    ├── config.py
    ├── embeddings/
    ├── evaluation/
    ├── ingestion/
    ├── main.py
    ├── rag/
    ├── utils/
    └── vectorstore/
```

**Upload method:**
- **Option A:** Drag and drop files/folders into the web interface
- **Option B:** Use Git (see below)

3. After uploading, click **Commit changes to main**

### Step 4: Wait for Build (Automatic)

1. Space will automatically start building
2. Watch the **Logs** tab for progress
3. Wait for "Running" status (2-5 minutes)

### Step 5: Test Your Space ✅

1. Once running, click your Space URL
2. You should see the ContractIQ UI
3. Try uploading a sample PDF contract
4. Ask a question and get a cited answer!

---

## 🔄 Alternative: Git Method

### Prerequisites
```bash
pip install huggingface_hub
huggingface-cli login
```

### Clone and Push
```bash
# Clone your new Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/contractiq-rag
cd contractiq-rag

# Copy files from your local contractiq-rag
cp -r /path/to/contractiq-rag/app.py .
cp -r /path/to/contractiq-rag/requirements.txt .
cp -r /path/to/contractiq-rag/.huggingface .
cp -r /path/to/contractiq-rag/app .

# Commit and push
git add .
git commit -m "Deploy ContractIQ"
git push
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Space shows "Running" status
- [ ] UI loads at your Space URL
- [ ] "Upload Contract" tab works
- [ ] Can upload a PDF file
- [ ] Processing completes successfully
- [ ] "Ask Questions" tab works
- [ ] Answers have citations (e.g., "According to [Clause X]...")
- [ ] Sources are displayed

---

## 🐛 Troubleshooting

### Space Won't Start
**Check:**
- All files uploaded correctly
- `GROQ_API_KEY` secret is set
- Review build logs for errors

### API Not Responding
**Fix:**
- Wait 30 seconds for API startup
- Check logs for FastAPI errors
- Restart Space from Settings

### Out of Memory
**Fix:**
- Upgrade to better hardware tier
- Or reduce `top_k` parameter in Advanced Options

---

## 📊 Expected Behavior

### First Run
- **Build time:** 2-5 minutes
- **Startup time:** 10-30 seconds
- **First query:** 5-10 seconds (model loading)
- **Subsequent queries:** 0.5-2 seconds

### Resource Usage
- **RAM:** ~2-4 GB
- **CPU:** 1-2 cores
- **Storage:** ~5-10 GB

---

## 🎉 Success!

Your ContractIQ Space is now live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/contractiq-rag
```

Share this URL with others to let them analyze contracts!

---

## 📚 Next Steps

1. **Test with Real Contracts**
   - Upload actual contracts
   - Test various questions
   - Verify citation accuracy

2. **Customize**
   - Update Space name/description
   - Add example contracts
   - Modify UI branding

3. **Monitor**
   - Check usage analytics
   - Review error logs
   - Gather user feedback

4. **Scale**
   - Upgrade hardware if needed
   - Enable persistent storage
   - Add rate limiting

---

## 💡 Pro Tips

1. **Sample Contracts**: Upload a sample contract with your Space so users can test immediately
2. **README**: Copy `README_HF.md` to `README.md` for better Space description
3. **Demo Video**: Record a quick demo and add to Space card
4. **Community**: Share in HF Discord and forums

---

## 📞 Support

Need help?
- **Docs:** See `DEPLOYMENT.md` for detailed guide
- **HF Forums:** https://discuss.huggingface.co
- **Issues:** Create issue in your repo

---

**Happy Deploying! 🚀**
