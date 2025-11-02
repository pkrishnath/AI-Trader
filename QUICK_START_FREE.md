# Quick Start: Test AI-Trader for FREE 🎉

**No credit card required. No API costs. Completely FREE.**

---

## ⚡ Fastest Way: Use Groq (2 Minutes)

### 1. Sign up (FREE)
Go to: https://console.groq.com
- Click "Sign Up"
- Verify email
- Done! (No credit card needed)

### 2. Get API Key
- Go to: https://console.groq.com/keys
- Copy your API key

### 3. Set Environment
```bash
export GROQ_API_KEY="gsk_xxxxxxxxxxxxx"
```

### 4. Run Trading Agent
```bash
python main.py configs/groq_config.json
```

**That's it! You're trading with a FREE AI model! 🚀**

---

## 🖥️ Alternative: Use Ollama (Local, 100% FREE)

No internet required, no API key needed, runs on YOUR machine.

### 1. Install Ollama
Download from: https://ollama.ai

### 2. Start Service
```bash
ollama serve
```

### 3. Pull a Model (in another terminal)
```bash
# Option A: Fast & Good (7B parameters)
ollama pull mistral

# Option B: More Capable (7B parameters)
ollama pull neural-chat

# Option C: Largest (70B parameters, requires more RAM)
ollama pull llama2-uncensored
```

### 4. Run Trading Agent
```bash
python main.py configs/ollama_config.json
```

**Running completely locally on your machine, ZERO API costs! 💻**

---

## 📊 Side-by-Side Comparison

| Feature | Groq | Ollama | DeepSeek | OpenAI |
|---------|------|--------|----------|--------|
| **Cost** | 🆓 FREE | 🆓 FREE | 💰 $0.14/M tokens | 💰 $15/M tokens |
| **Speed** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡⚡ | ⚡⚡⚡⚡ |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Sign-up** | Easy | None | Easy | Need card |
| **API Key** | Yes | No | Yes | Yes |
| **Internet** | Required | Not needed after setup | Required | Required |
| **Rate Limits** | None | None | Yes | Yes |

---

## 💰 Cost Estimation

If you run trading for 1 hour per day:

| Provider | Monthly Cost |
|----------|-------------|
| **Groq** | **$0** (FREE!) |
| **Ollama** | **$0** (LOCAL!) |
| **DeepSeek** | ~$0.42 (3M tokens) |
| **OpenAI GPT-4** | ~$15 (3M tokens) |

---

## 🧪 Testing Checklist

- [ ] **Groq Setup**
  - [ ] Create account at groq.com
  - [ ] Get API key
  - [ ] Set `GROQ_API_KEY` env variable
  - [ ] Run `python main.py configs/groq_config.json`

- [ ] **Ollama Setup**
  - [ ] Install Ollama from ollama.ai
  - [ ] Run `ollama serve`
  - [ ] Run `ollama pull mistral`
  - [ ] Run `python main.py configs/ollama_config.json`

- [ ] **Verify It Works**
  - [ ] Check logs appear
  - [ ] See trading decisions being made
  - [ ] Verify no API errors
  - [ ] Check results in `./data/agent_data/`

---

## ❓ FAQ

**Q: Can I really use Groq for free?**
A: Yes! Groq offers completely free API access with no rate limits. No credit card required.

**Q: Is Ollama really free?**
A: Yes! It runs locally on your machine. No API calls, no costs, ever.

**Q: What's the catch?**
A: No catch! These companies offer free access to test. Groq makes money from enterprises. Ollama is open-source.

**Q: Can I test without an internet connection?**
A: Yes! Use Ollama. Download models, then everything runs locally.

**Q: What if I want the best quality?**
A: Use Groq's Llama 3.3 70B (free) or DeepSeek (cheap, $0.14/M tokens).

**Q: How many requests can I make?**
A: **Groq**: Unlimited (no official limits). **Ollama**: Unlimited (local). **DeepSeek**: Pay only for what you use.

---

## 🚀 Next Steps

1. **Choose your option**:
   - Want fastest setup? → Groq ⚡
   - Want completely local? → Ollama 🖥️
   - Want best price? → DeepSeek 💰

2. **Follow the 2-minute setup** above

3. **Run the trading agent** with your chosen config

4. **Watch it trade for FREE!** 🎉

---

## 📚 Full Documentation

For more details, see:
- `FREE_LLM_TESTING.md` - Complete guide with all options
- `LLM_API_SETUP.md` - Technical setup for paid providers

---

**Ready? Start with Groq in 2 minutes!**

**Go to**: https://console.groq.com 🚀
