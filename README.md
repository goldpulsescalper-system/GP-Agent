# TF Engine - Telegram Trading Bot

TF Engine Agent adalah bot Telegram pintar (Userbot) yang dirancang untuk mengelola komunitas trading. Bot ini dilengkapi dengan AI (berbasis GPT-4o) untuk menjadi Customer Support di DM dan memposting konten secara otomatis ke Channel Telegram, serta terintegrasi langsung dengan MetaTrader 5 untuk pengiriman sinyal eksekusi otomatis.

## Fitur
1. **Customer Support (Private Message):**
   - Menjawab pertanyaan di DM layaknya seorang trader profesional dan logis ("Execution over emotion").
   - Terfokus untuk mengarahkan pengguna ke layanan utama: **Private Membership**.
   - Memiliki memori untuk mengingat 5-10 pesan terakhir per user (In-memory).
2. **Scheduled Posts (APScheduler):**
   - Memposting edukasi & soft-sell 1x sehari (Pagi).
   - Memposting evaluasi hari & hard-sell VIP 1x sehari (Malam).
   - Otomatis berhenti beroperasi di akhir pekan (Sabtu & Minggu).
3. **Smart MT5 Signal Broadcaster:**
   - **VIP Channel:** Menerima seluruh eksekusi pasar (semua pair) secara real-time dari EA (Entry, Modify, TP, SL).
   - **Free Channel:** Menerima maksimal 1 sinyal per hari khusus untuk pair **XAUUSD**. Sinyal Free juga dilengkapi dengan konten marketing ekstra (Hype) ketika target tercapai atau Motivasi ketika stop loss tersentuh.

## Setup & Instalasi Lokal
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` ke `.env` dan isi variabelnya.
3. Jalankan bot:
   ```bash
   python main.py
   ```

## Variabel Environment (.env)
Pastikan Anda mengatur ID Channel berikut di `.env`:
- `CHANNEL_ID`: ID untuk Free Channel (menerima 1 sinyal XAUUSD per hari & konten terjadwal).
- `VIP_CHANNEL_ID`: ID untuk VIP/Private Membership Channel (menerima semua eksekusi sinyal).

## Deployment di Railway
1. Push repository ini ke GitHub.
2. Buat project baru di Railway dan hubungkan ke repository tersebut.
3. Railway akan otomatis membaca `Procfile` dan `requirements.txt`.
4. Masuk ke tab **Variables** di Railway dan tambahkan semua variabel yang ada di file `.env`.
5. Restart deploy jika diperlukan.

**Note:** Karena sistem ini menggunakan memory internal (In-memory dict), setiap kali project di-deploy/restart di Railway, history chat akan ter-reset. History sinyal MT5 disimpan di file `data/signals.json` dan memori pembatasan sinyal harian juga disimpan di sana.

## Integrasi Webhook MT5 (Sinyal Real-time)
Bot ini memiliki HTTP Server bawaan (FastAPI) yang berjalan berbarengan dengan bot Telegram untuk menerima request dari Expert Advisor (EA) MT5 Anda.

### Cara Menghubungkan EA MT5:
1. **Dapatkan URL Bot Anda**:
   - Jika Anda deploy di Railway, dapatkan Public URL aplikasi Anda (contoh: `https://tfengine-production.up.railway.app`).
   - Endpoint webhook adalah: `https://tfengine-production.up.railway.app/api/webhook/mt5`

2. **Izinkan WebRequest di MT5**:
   - Buka aplikasi MetaTrader 5 di PC Anda.
   - Buka menu **Tools -> Options**.
   - Pilih tab **Expert Advisors**.
   - Centang opsi **"Allow WebRequest for listed URL:"**.
   - Klik dua kali di kotak bawahnya, tambahkan URL domain bot Anda.
   - Klik **OK**.

3. **Input URL di EA**:
   - Masukkan URL webhook ke dalam parameter input (contoh `InpWebhookURL`) saat memasang EA ke chart.

Sistem Webhook EA secara otomatis akan memicu:
- **ENTRY**: Saat order buy/sell tereksekusi. Bot akan kirim Sinyal Baru.
- **MODIFY**: Saat SL/TP diubah (termasuk Break Even). Bot akan me-reply Sinyal awal.
- **CLOSE_TP**: Saat harga menyentuh TP. Bot akan me-reply "TP HIT". (Khusus Free Channel, akan dilampirkan pesan Hype).
- **CLOSE_SL**: Saat harga menyentuh SL. Bot akan me-reply "SL HIT". (Khusus Free Channel, akan dilampirkan pesan Motivasi).

