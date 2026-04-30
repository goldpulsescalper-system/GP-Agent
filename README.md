# GP_Agent - Telegram Trading Bot

GP_Agent adalah bot Telegram pintar yang dirancang sebagai co-admin untuk channel trading XAUUSD. Bot ini dilengkapi dengan AI (berbasis GPT-4o) untuk menjadi Customer Support di DM dan memposting secara otomatis ke Channel berdasarkan gambar yang dikirim di Grup Admin (Topics).

## Fitur
1. **Smart Auto-Post (Grup ke Channel):**
   - Meneruskan foto dari grup admin (Topik: HASIL TRADING atau TESTIMONI) ke Channel.
   - Generate caption otomatis bergaya anak trading (menggunakan AI).
   - Rate limit: maksimal 1 post setiap 2 jam.
2. **Customer Support (Private Message):**
   - Menjawab pertanyaan di DM layaknya seorang trader.
   - Menjawab seputar pendaftaran VIP, link broker, channel free, dan lainnya.
   - Memiliki memori untuk mengingat 5-10 pesan terakhir per user (In-memory).
3. **Scheduled Posts (APScheduler):**
   - Memposting Edukasi 2x sehari (Pagi & Sore).
   - Memposting Soft-sell VIP 1x sehari (Malam).

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

## Cara Mendapatkan ID Group, Channel, dan Topik
1. **Group/Channel ID:**
   - Gunakan bot pihak ketiga (seperti `@RawDataBot` atau `@MissRose_bot`) di grup Anda untuk mengetahui ID. Group ID biasanya berawalan `-100`.
2. **Topic ID (`message_thread_id`):**
   - Untuk mendapatkan ID Topik, Anda bisa mengakses Telegram Web, masuk ke grup admin Anda, lalu klik salah satu Topik (misal: "HASIL TRADING").
   - Perhatikan URL-nya. Contoh: `https://web.telegram.org/a/#-100123456789_2`
   - Angka terakhir (setelah `_`) adalah Topic ID. Dalam contoh di atas, Topic ID adalah `2`.

## Deployment di Railway
1. Push repository ini ke GitHub.
2. Buat project baru di Railway dan hubungkan ke repository tersebut.
3. Railway akan otomatis membaca `Procfile` dan `requirements.txt`.
4. Masuk ke tab **Variables** di Railway dan tambahkan semua variabel yang ada di file `.env`.
5. Restart deploy jika diperlukan.

**Note:** Karena sistem ini menggunakan memory internal (In-memory dict), setiap kali project di-deploy/restart di Railway, history chat dan history post akan ter-reset. (Kecuali MT5 Ticket Mapping yang disimpan di `data/signals.json`).

## Integrasi Webhook MT5 (Sinyal Real-time)
Bot ini memiliki HTTP Server bawaan (FastAPI) yang berjalan berbarengan dengan bot Telegram untuk menerima request dari Expert Advisor (EA) MT5 Anda.

### Cara Menghubungkan EA MT5:
1. **Dapatkan URL Bot Anda**:
   - Jika Anda deploy di Railway, buka pengaturan *Networking* dan dapatkan Public URL aplikasi Anda (contoh: `https://gp-agent-production.up.railway.app`).
   - Endpoint webhook adalah: `https://gp-agent-production.up.railway.app/api/webhook/mt5`
   - Pastikan port aplikasi terekspos (Railway biasanya otomatis mengarahkan port HTTP ke domain ini).

2. **Izinkan WebRequest di MT5**:
   - Buka aplikasi MetaTrader 5 di PC Anda.
   - Buka menu **Tools -> Options**.
   - Pilih tab **Expert Advisors**.
   - Centang opsi **"Allow WebRequest for listed URL:"**.
   - Klik dua kali di kotak bawahnya, tambahkan URL domain bot Anda (contoh: `https://gp-agent-production.up.railway.app`).
   - Klik **OK**.

3. **Input URL di EA**:
   - Masukkan URL webhook ke dalam parameter input `InpWebhookURL` saat memasang (Attach) EA ke chart.
   - Contoh format: `https://gp-agent-production.up.railway.app/api/webhook/mt5`

EA secara otomatis akan mengirim:
- **ENTRY**: Saat order buy/sell tereksekusi. Bot akan kirim Sinyal Baru.
- **MODIFY**: Saat SL/TP diubah (termasuk Break Even). Bot akan me-reply Sinyal awal.
- **CLOSE_TP**: Saat harga menyentuh TP. Bot akan me-reply "TP HIT", lalu mengirim pesan Hype & Call-to-Action (VIP).
- **CLOSE_SL**: Saat harga menyentuh SL. Bot akan me-reply "SL HIT", lalu mengirim pesan Motivasi trading.
