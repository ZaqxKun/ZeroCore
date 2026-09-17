# QUICK START — ZeroCore

1. Copy `.env.example` → `.env`
2. Isi:
   - `DISCORD_TOKEN`
   - `DISCORD_GUILD_ID`
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL` (default: `gemini-2.0-flash`)
3. Install:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
4. Check:
   ```powershell
   python scripts/check_config.py
   ```
5. Run:
   ```powershell
   python bot.py
   ```
6. Discord:
   ```text
   /setup
   /heartbeat
   /backup
   /status
   ```

Baca `README.md` untuk panduan lengkap.
