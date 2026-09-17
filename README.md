# ZeroCore v1.0 — District Zerø

> **District Zerø**  
> *All stories start from zero.*

ZeroCore adalah bot pengelola komunitas District Zerø yang dirancang agar pekerjaan
rutin server dapat berjalan otomatis tanpa membuat AI memiliki kekuasaan absolut.

ZeroCore dapat:

- membaca aktivitas komunitas;
- menganalisis kebutuhan channel;
- menerima dan menindaklanjuti saran/kritik;
- membuat thread atau trial channel;
- menilai apakah trial channel layak dipertahankan;
- mengarsipkan trial channel yang tidak aktif;
- memperbaiki channel/role inti yang hilang;
- membuat backup struktur server;
- mencatat semua tindakan ke `#zero-log`;
- menjalankan continuity mode jika founder lama tidak aktif.

ZeroCore **tidak** boleh secara otomatis:

- memindahkan ownership server;
- memberikan permission Administrator;
- menghapus Administrator;
- mass-delete server;
- menghapus core channel permanen;
- mengganti successor;
- melakukan permanent ban terhadap staff;
- mengubah Constitution tanpa keputusan manusia.

---

# 1. Struktur Project

```text
District-Zero-ZeroCore-v1.0/
│
├── bot.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
│
├── config/
│   ├── constitution.yml
│   ├── server.yml
│   └── messages.yml
│
├── zerocore/
│   ├── app.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── policy.py
│   │
│   ├── services/
│   │   ├── ai.py
│   │   ├── guild.py
│   │   ├── backup.py
│   │   ├── lifecycle.py
│   │   └── continuity.py
│   │
│   └── cogs/
│       └── management.py
│
├── scripts/
│   └── check_config.py
│
├── tests/
│   └── ACCEPTANCE.md
│
├── data/
└── backups/
```

---

# 2. Yang Dibutuhkan

Sebelum mulai, siapkan:

1. Python 3.11 atau lebih baru.
2. Discord Server District Zerø.
3. Discord Developer Application.
4. Gemini API key.
5. VS Code (opsional tetapi disarankan).
6. VPS/Docker jika bot ingin hidup 24/7.

---

# 3. Membuat Bot Discord

Buka:

**Discord Developer Portal**

Kemudian:

1. Klik **New Application**.
2. Nama contoh:

```text
ZeroCore
```

3. Masuk ke menu **Bot**.
4. Klik **Reset Token** / buat token bot.
5. Simpan token di komputer.

## PENTING

Jangan:

- kirim bot token ke orang lain;
- upload token ke GitHub;
- menaruh token langsung di source code;
- mengirim token ke ChatGPT.

Token hanya ditaruh di file `.env`.

---

# 4. Aktifkan Intent

Pada halaman:

```text
Developer Portal
→ Application
→ Bot
```

aktifkan:

```text
MESSAGE CONTENT INTENT
```

Ini dibutuhkan jika ZeroCore ingin menganalisis percakapan komunitas.

Tanpa intent ini, fungsi community analysis dari isi chat tidak akan bekerja secara penuh.

---

# 5. Invite Bot ke Server

Masuk ke:

```text
OAuth2
→ URL Generator
```

Scopes:

```text
bot
applications.commands
```

Permission yang direkomendasikan:

```text
View Channels
Send Messages
Read Message History

Manage Channels
Manage Roles
Manage Messages
Manage Threads

Create Public Threads
Create Private Threads

View Audit Log
Manage Server
Moderate Members
```

## Jangan centang:

```text
Administrator
```

ZeroCore sengaja dirancang tanpa Administrator.

---

# 6. Posisi Role Bot

Setelah bot masuk server:

```text
Server Settings
→ Roles
```

Letakkan role:

```text
ZeroCore
```

di atas role yang memang perlu dikelolanya.

Contoh:

```text
Owner
Admin
ZeroCore
Moderator
District Crew
Member
Newcomer
```

Kalau ZeroCore perlu mengelola Moderator, role ZeroCore harus lebih tinggi dari Moderator.

Jangan tempatkan bot di atas role manusia yang tidak ingin bot kelola.

---

# 7. Install Project

Extract ZIP.

Buka folder project di VS Code.

Buka terminal.

Windows PowerShell:

```powershell
py -m venv .venv
```

Aktifkan virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependency:

```powershell
pip install -r requirements.txt
```

---

# 8. Membuat File .env

Copy:

```text
.env.example
```

menjadi:

```text
.env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Kemudian buka `.env`.

Isi:

```env
DISCORD_TOKEN=TOKEN_BOT_DISCORD
DISCORD_GUILD_ID=ID_SERVER_DISTRICT_ZERO

GEMINI_API_KEY=GEMINI_API_KEY
GEMINI_MODEL=gemini-2.0-flash

TIMEZONE=Asia/Jakarta
DATABASE_PATH=data/district_zero.db
BACKUP_DIR=backups
LOG_LEVEL=INFO
```

---

# 9. Mendapatkan Discord Guild ID

Discord:

```text
User Settings
→ Advanced
→ Developer Mode
```

Aktifkan.

Kemudian:

```text
Klik kanan server District Zerø
→ Copy Server ID
```

Masukkan ke:

```env
DISCORD_GUILD_ID=
```

---

# 10. Gemini API Key

ZeroCore menggunakan Gemini API untuk memahami konteks komunitas.

Masukkan API key pada:

```env
GEMINI_API_KEY=
```

API key tidak sama dengan subscription ChatGPT.

Penggunaan API memiliki billing sendiri sesuai penggunaan.

---

# 11. Mengecek Configuration

Sebelum menjalankan bot:

```powershell
python scripts/check_config.py
```

Jika benar:

```text
Configuration check: OK
```

---

# 12. Menjalankan ZeroCore

Jalankan:

```powershell
python bot.py
```

Jika berhasil, terminal akan menampilkan kurang lebih:

```text
ZeroCore online as ZeroCore#....
```

---

# 13. Setup Server Otomatis

Di Discord:

```text
/setup
```

ZeroCore akan memastikan struktur dasar tersedia.

Struktur default:

```text
START HERE
├── #welcome
├── #rules
├── #announcements
└── #saran-kritik

THE DISTRICT
├── #general
├── #random
├── #media
├── #introduce-yourself
├── Zero Room
├── Late Night
└── AFK

ACTIVITIES
├── #events
└── #looking-for-group

SYSTEM
├── #zero-log
├── #mod-queue
└── #continuity-room
```

Role:

```text
Admin
Moderator
District Crew
Member
Newcomer
```

---

# 14. Command ZeroCore

## /setup

Membangun atau memperbaiki struktur inti.

```text
/setup
```

## /status

Menampilkan status dan guardrail ZeroCore.

```text
/status
```

## /review-now

Memaksa ZeroCore melakukan review komunitas saat itu juga.

```text
/review-now
```

## /backup

Membuat backup struktur server.

```text
/backup
```

## /heartbeat

Menandai bahwa founder masih aktif.

Hanya server owner yang dapat menggunakan:

```text
/heartbeat
```

---

# 15. Cara ZeroCore Membuat Channel

ZeroCore tidak menggunakan aturan:

```text
Topik ramai = buat channel
```

Sistemnya:

```text
OBSERVE
↓
EXISTING CHANNEL
↓
THREAD
↓
PROPOSAL
↓
TRIAL CHANNEL
↓
REVIEW
↓
KEEP / ARCHIVE
```

---

# 16. Contoh: Banyak Orang Ngopi

Misalnya:

```text
Aan:
ngopi yuk

Raka:
gas

Dimas:
ngopi ngopi ngopi

Raka:
jam berapa?
```

Walaupun jumlahnya:

```text
1.000 pesan
50 orang
```

ZeroCore tetap melihatnya sebagai:

```text
SOCIAL INVITATION
```

Keputusan:

```text
KEEP IN #GENERAL
```

Tidak membuat:

```text
#ngopi
```

Karena obrolan sosial spontan adalah fungsi utama `#general`.

---

# 17. Contoh Channel yang Memang Dibutuhkan

Misalnya selama beberapa minggu banyak diskusi:

```text
kamera
editing
street photography
lensa
hasil hunting
kritik foto
```

Jika memenuhi threshold:

```text
>= 8 unique users
>= 7 active days
>= 40 meaningful messages

structural_need >= 72%
AI confidence >= 80%
```

ZeroCore dapat membuat:

```text
#photography
```

Tetapi status awal:

```text
TRIAL
```

Default:

```text
14 hari
```

---

# 18. Trial Channel

Setelah 14 hari ZeroCore mengecek:

```text
unique users
jumlah pesan
jumlah hari aktif
```

Default minimum agar dipertahankan:

```text
5 unique users
30 messages
5 active days
```

Jika sehat:

```text
TRIAL
→ ESTABLISHED
```

Jika tidak:

```text
#photography
→ #archive-photography
```

Channel tidak langsung dihapus.

---

# 19. Saran dan Kritik

Gunakan:

```text
#saran-kritik
```

Member dapat memberi:

```text
Saya merasa pembicaraan fotografi sudah terlalu banyak di general.
Mungkin perlu tempat sendiri.
```

ZeroCore dapat:

1. membaca saran;
2. membandingkan dengan aktivitas server;
3. mengecek apakah channel lama sudah cukup;
4. membuat proposal;
5. membuat thread;
6. membuat trial channel jika memang diperlukan.

---

# 20. ZeroCore Constitution

File paling penting:

```text
config/constitution.yml
```

Ini adalah aturan utama bot.

Contoh:

```yaml
social:
  invitations_stay_in_general: true

  examples:
    - ngopi
    - nongkrong
    - mabar
    - makan
    - nonton
    - jalan
    - hangout

  frequency_never_creates_channel: true
```

Jangan sembarang menghapus guardrail ini.

---

# 21. Successor System

Buka:

```text
config/constitution.yml
```

Cari:

```yaml
continuity:
  primary_successor_user_id: 0
  secondary_successor_user_id: 0
  emergency_successor_user_id: 0
```

Ganti dengan User ID Discord.

Contoh:

```yaml
continuity:
  primary_successor_user_id: 111111111111111111
  secondary_successor_user_id: 222222222222222222
  emergency_successor_user_id: 333333333333333333
```

---

# 22. Arti Successor

## Primary Successor

Orang utama yang dipercaya menjaga District Zerø.

## Secondary Successor

Cadangan jika Primary tidak tersedia.

## Emergency Successor

Cadangan terakhir untuk kondisi darurat jangka panjang.

Mereka tidak otomatis:

```text
menjadi Owner
mendapat Administrator
mengambil alih akun founder
```

---

# 23. Continuity Mode

Default:

```text
0–29 hari
ACTIVE

30 hari
WARNING

60 hari
CONTINUITY

90 hari
EMERGENCY
```

ZeroCore menggunakan heartbeat founder.

Gunakan secara berkala:

```text
/heartbeat
```

---

# 24. Backup

Backup otomatis dibuat setiap:

```text
24 jam
```

Folder:

```text
backups/
```

Contoh:

```text
district-zero-20260917T120000Z.zip
```

Default:

```text
30 backup terakhir
```

Backup menyimpan informasi struktur seperti:

```text
roles
permissions
channels
categories
channel topics
permission overwrites
constitution.yml
server.yml
messages.yml
```

---

# 25. Backup Off-Site

Jangan hanya menyimpan backup di VPS yang sama.

Jika VPS rusak, backup ikut hilang.

Gunakan salah satu:

```text
Google Drive
OneDrive
S3
NAS
server kedua
```

Untuk versi ini sinkronisasi off-site belum otomatis agar credential storage tetap sederhana.

---

# 26. Self-Healing

ZeroCore mengecek struktur server setiap:

```text
6 jam
```

Misalnya:

```text
#rules
```

terhapus.

ZeroCore dapat membuatnya kembali.

Hal yang sama berlaku untuk core role dan SYSTEM category.

---

# 27. Zero Log

Semua tindakan manajemen penting diarahkan ke:

```text
#zero-log
```

Contoh:

```text
ZeroCore • Trial created

#photography

Reason:
Sustained photography discussion

Confidence:
91%

Structural need:
87%
```

---

# 28. Moderation

Untuk spam/scam sederhana, gunakan Discord AutoMod sebagai lapisan pertama.

ZeroCore default:

```yaml
ai_can_timeout: false
ai_can_ban: false
ai_can_kick: false
```

AI tidak langsung menghukum manusia pada kasus kontekstual.

Kasus meragukan diarahkan ke:

```text
#mod-queue
```

---

# 29. Privacy

Default raw message retention:

```text
30 hari
```

Author Discord ID di-hash sebelum digunakan dalam payload analisis.

Channel berikut tidak dimasukkan ke dataset community analysis:

```text
#zero-log
#mod-queue
#continuity-room
```

---

# 30. Menjalankan 24/7 dengan Docker

Install Docker.

Kemudian:

```bash
docker compose up -d --build
```

Cek:

```bash
docker compose ps
```

Log:

```bash
docker compose logs -f
```

Restart:

```bash
docker compose restart
```

Stop:

```bash
docker compose down
```

File sudah menggunakan:

```yaml
restart: unless-stopped
```

Jadi bot otomatis hidup lagi setelah reboot/crash container.

---

# 31. Update Source Code

Sebelum update:

```text
1. buat /backup
2. copy folder data/
3. copy folder backups/
4. copy .env
```

Jangan menimpa `.env` jika sudah berisi token production.

---

# 32. Troubleshooting

## ModuleNotFoundError

Jalankan:

```powershell
pip install -r requirements.txt
```

Pastikan virtual environment aktif.

---

## Slash command tidak muncul

Pastikan:

```env
DISCORD_GUILD_ID=
```

benar.

Restart bot.

---

## ZeroCore tidak membaca chat

Pastikan:

```text
MESSAGE CONTENT INTENT
```

aktif pada Developer Portal.

Restart bot setelah mengubah intent.

---

## Missing Permissions

Periksa:

```text
Server Settings
→ Roles
→ ZeroCore
```

dan posisi role.

Discord role hierarchy tetap berlaku.

---

## Bot offline setelah terminal ditutup

Itu normal jika menjalankan langsung di komputer.

Untuk 24/7 gunakan:

```text
VPS
Docker
```

---

## GEMINI_API_KEY belum ada

Bot tetap dapat menjalankan fungsi non-AI tertentu, tetapi community analysis AI tidak akan bekerja.

---

# 33. Security Checklist

Sebelum production:

- [ ] `.env` tidak masuk Git.
- [ ] Bot tidak punya Administrator.
- [ ] Message Content Intent aktif jika dibutuhkan.
- [ ] Bot role ditempatkan dengan benar.
- [ ] Successor sudah diisi.
- [ ] Primary dan Secondary adalah orang terpercaya.
- [ ] Backup off-site tersedia.
- [ ] Discord AutoMod aktif.
- [ ] `/backup` sudah dites.
- [ ] `/status` normal.
- [ ] `/review-now` berhasil.
- [ ] Docker auto-restart aktif.
- [ ] Token Discord belum pernah dipublikasikan.

---

# 34. Setelah Pertama Kali Setup

Urutan yang direkomendasikan:

```text
1. Jalankan bot
2. /setup
3. cek seluruh category/channel
4. cek role permissions
5. isi successor
6. restart bot
7. /heartbeat
8. /backup
9. /status
10. /review-now setelah server memiliki data percakapan
```

---

# 35. Prinsip Terakhir

ZeroCore dirancang dengan prinsip:

```text
AI boleh mengelola rutinitas.
AI boleh memberi struktur ringan.
AI boleh memperbaiki kerusakan sederhana.

Tetapi manusia tetap memegang:
ownership
Administrator
succession
hukuman berat
keputusan destruktif
```

Tujuannya bukan membuat AI menjadi pemilik District Zerø.

Tujuannya adalah membuat District Zerø tetap dapat hidup, berkembang, dan
dipelihara walaupun founder suatu hari tidak bisa mengurus server secara aktif.
