# GenAI Application

## Project Information

**Nama Project:**
Feedback Analyzer

**Use Case:**
Menganalisis feedback pelanggan toko online menjadi insight terstruktur yang bisa langsung ditindaklanjuti.

**Deskripsi Singkat:**
Aplikasi menerima teks feedback pelanggan beserta konteks bisnisnya, lalu menghasilkan JSON berisi sentimen, ringkasan, masalah utama, saran tindakan, dan tingkat prioritas. Aplikasi ini bukan chatbot: outputnya berupa data terstruktur yang bisa diproses program lain (misalnya dashboard atau sistem tiket).

## Tech Stack

- Python
- FastAPI (web framework, dijalankan dengan `fastapi dev main.py`)
- Pydantic (validasi request body dan response)
- Groq API dengan model `openai/gpt-oss-120b` (bisa diganti lewat variabel `GROQ_MODEL`)
- python-dotenv (membaca API key dari file `.env`)

## Application Flow

```text
User Input
↓
FastAPI
↓
LLM API
↓
Structured Output
```

**Penjelasan:**
[TULIS ULANG DENGAN BAHASAMU SENDIRI]

<!-- Draft bahan: User mengirim POST /analyze berisi text dan context. FastAPI memvalidasi body dengan Pydantic (FeedbackRequest), lalu membangun prompt (system prompt + prompt berisi Task, Context, Constraint, Output Format) dan mengirimnya ke Groq secara async. Groq mengembalikan JSON dalam bentuk string, aplikasi mem-parse-nya dan memvalidasinya dengan Pydantic (FeedbackAnalysis), lalu mengembalikannya sebagai response. Jika ada kegagalan, aplikasi mengembalikan error 422/500/502. -->

## API Endpoint

```text
POST /analyze      -> analisis feedback (endpoint utama, memakai Prompt C)
POST /experiment   -> menjalankan Prompt A, B, C dengan input yang sama
GET  /             -> health check
```

## Example Request

```json
{
  "text": "Pengiriman lambat banget, sudah 5 hari belum sampai. Adminnya juga lama balas. Tapi barangnya bagus.",
  "context": "toko online sepatu"
}
```

## Example Response

```json
{
  "sentiment": "negatif",
  "summary": "Pengiriman terlambat lebih dari 5 hari dan respon admin lambat, meskipun kualitas barang memuaskan.",
  "key_issues": [
    "Pengiriman lambat",
    "Respon admin lambat"
  ],
  "suggested_actions": [
    "Tinjau dan optimalkan proses logistik untuk mempercepat pengiriman",
    "Implementasikan sistem tiket atau chatbot untuk mempercepat respon admin",
    "Lakukan pelatihan customer service tentang kecepatan dan kepuasan pelanggan",
    "Pantau dan evaluasi kepuasan pelanggan setelah perbaikan"
  ],
  "priority": "tinggi"
}
```

## Structured Output

| Field | Tipe | Keterangan |
|-------|------|------------|
| `sentiment` | `"positif"` / `"netral"` / `"negatif"` | Sentimen keseluruhan feedback |
| `summary` | string | Ringkasan maksimal 2 kalimat |
| `key_issues` | list of string | Masalah atau keluhan utama |
| `suggested_actions` | list of string | Saran tindak lanjut |
| `priority` | `"rendah"` / `"sedang"` / `"tinggi"` | Tingkat urgensi penanganan |

**Kenapa memilih field-field tersebut?**
[TULIS ULANG DENGAN BAHASAMU SENDIRI]

<!-- Draft bahan: sentiment untuk menyaring/mengelompokkan feedback secara cepat; summary agar tim tidak perlu membaca teks panjang; key_issues agar masalah bisa dihitung/dikelompokkan; suggested_actions agar hasil analisis bisa langsung ditindaklanjuti; priority agar tim tahu feedback mana yang ditangani lebih dulu. Field bertipe Literal/enum agar nilainya konsisten dan mudah diproses program. -->

## Prompt Experiment

### Input yang Digunakan

```json
{
  "text": "Pengiriman lambat banget, sudah 5 hari belum sampai. Adminnya juga lama balas. Tapi barangnya bagus.",
  "context": "toko online sepatu"
}
```

Ketiga prompt dijalankan sekaligus lewat `POST /experiment`.

### Prompt A

```text
Analyze this feedback: Pengiriman lambat banget, sudah 5 hari belum sampai. Adminnya juga lama balas. Tapi barangnya bagus.
```

### Actual Output A

```text
**Feedback Summary (Indonesian)**  
> *“Pengiriman lambat banget, sudah 5 hari belum sampai. Adminnya juga lama balas. Tapi barangnya bagus.”*  

---

## 1. Sentiment Overview  
| Aspect | Sentiment | Weight |
|--------|-----------|--------|
| **Pengiriman** | Negatif | 0.45 |
| **Layanan Admin** | Negatif | 0.35 |
| **Kualitas Barang** | Positif | 0.20 |

- **Overall sentiment:** Predominantly negative (≈ 0.8) due to delivery and support issues, but tempered by a positive note on product quality.

---

## 2. Key Issues Identified  

| Issue | Description | Impact |
|-------|-------------|--------|
| **Delivery delay** | 5‑day delay beyond expected window. | Low customer satisfaction, potential churn. |
| **Slow admin response** | Admin replies take longer than expected. | Frustration, perception of poor customer service. |
| **Product quality** | Positive feedback on the item itself. | Maintains brand reputation for product quality. |

---

## 3. Root‑Cause Hypotheses  

| Hypothesis | Supporting Evidence | Suggested Investigation |
|------------|---------------------|--------------------------|
| **Logistics partner inefficiency** | 5‑day delay suggests carrier or fulfillment issue. | Review shipping times, carrier SLAs, and order‑to‑delivery logs. |
| **Inventory or fulfillment bottleneck** | Delay could stem from stock‑out or packing delays. | Check inventory levels, fulfillment queue, and order status updates. |
| **Customer support staffing or workflow** | Admin slow to reply indicates possible understaffing or inefficient ticket routing. | Audit support ticket volume, response times, and staffing levels. |
| **Communication gaps** | No proactive status updates may exacerbate frustration. | Evaluate automated shipping notifications and status‑update frequency. |

---

## 4. Actionable Recommendations  

| Category | Recommendation | Priority | KPI to Track |
|----------|----------------|----------|--------------|
| **Shipping** | • Negotiate tighter SLAs with carriers.<br>• Implement real‑time tracking alerts to customers.<br>• Offer expedited shipping for high‑value items. | High | Avg. delivery time, % on‑time deliveries |
| **Customer Support** | • Increase support staff during peak periods.<br>• Adopt a ticketing system with SLA thresholds.<br>• Provide canned responses for common queries. | High | Avg. response time, CSAT score |
| **Communication** | • Send automated status updates at key milestones (order placed, shipped, out for delivery, delivered).<br>• Add a “delivery ETA” field on the order page. | Medium | Customer engagement with notifications |
| **Product Quality** | • Continue to highlight product strengths in marketing.<br>• Use positive feedback in testimonials. | Low | NPS, repeat purchase rate |

---

## 5. Suggested Customer‑Facing Response (Template)

> **Subject:** We’re sorry for the delay – here’s what we’re doing to fix it  
> **Hi [Customer Name],**  
> Thank you for your feedback. We’re glad you’re happy with the product, but we’re sorry the delivery and support experience fell short of your expectations.  
> *What’s happening:* Our shipping partner experienced an unexpected delay, and our support team is currently handling a higher volume of tickets than usual.  
> *What we’re doing:*  
> 1. We’ve expedited your shipment and you’ll receive a tracking number shortly.  
> 2. Our support team is now on a 24‑hour response cycle for all inquiries.  
> 3. We’re reviewing our logistics partners to prevent future delays.  
> We appreciate your patience and would love to offer you a 10% discount on your next purchase as a thank‑you.  
> **Best regards,**  
> [Your Name]  
> Customer Success Team

---

## 6. Quick Takeaway  

- **Delivery & support are the pain points** that need immediate attention.  
- **Product quality is a strength** that can be leveraged in marketing.  
- **Proactive communication** (tracking updates, ETA, quick replies) can significantly improve perceived service quality.  

Implementing the above actions should shift the overall sentiment toward positive and reduce churn risk.
```

### Prompt B

```text
Kamu adalah analis customer experience.
Tugas: analisis feedback pelanggan berikut.
Konteks bisnis: toko online sepatu
Feedback pelanggan: Pengiriman lambat banget, sudah 5 hari belum sampai. Adminnya juga lama balas. Tapi barangnya bagus.
```

### Actual Output B

```text
## Analisis Feedback Pelanggan  
**Feedback**:  
> “Pengiriman lambat banget, sudah 5 hari belum sampai. Adminnya juga lama balas. Tapi barangnya bagus.”

### 1. Ringkasan Sentimen
| Aspek | Sentimen | Keterangan |
|-------|----------|------------|
| Kualitas produk | Positif | “Barangnya bagus” |
| Pengiriman | Negatif | “Pengiriman lambat banget, sudah 5 hari belum sampai” |
| Layanan pelanggan (admin) | Negatif | “Adminnya juga lama balas” |

> **Kesimpulan**: Pelanggan puas dengan produk, namun tidak puas dengan proses pengiriman dan respons layanan pelanggan.

---

### 2. Pemetaan Masalah (Customer Journey)

| Tahap | Masalah | Dampak pada CX | Prioritas |
|-------|---------|----------------|-----------|
| Order Placement | Tidak ada | - |
| Order Confirmation | Tidak ada | - |
| **Pengiriman** | Waktu pengiriman > 5 hari | Menurunkan kepuasan, meningkatkan churn | **Tinggi** |
| **Customer Support** | Respons admin > 24 jam | Menurunkan kepercayaan, meningkatkan keluhan | **Tinggi** |
| **Product Delivery** | Barang bagus | Positif | - |

---

### 3. Analisis Root Cause (Menggunakan 5 Whys)

| Why | Jawaban | Catatan |
|-----|---------|---------|
| 1. Mengapa pengiriman lambat? | Kurangnya koordinasi dengan kurir atau volume pesanan tinggi | Perlu audit log pengiriman |
| 2. Mengapa kurir tidak tepat waktu? | Kurang SLA, kurang pengiriman reguler, atau jam kerja kurir | Periksa kontrak dan SLA |
| 3. Mengapa admin lambat balas? | Jumlah tiket tinggi, kurang staf, atau sistem tiket tidak efisien | Evaluasi kapasitas tim |
| 4. Mengapa tiket tinggi? | Banyak pelanggan yang tidak puas, tidak ada self‑service | Tambah FAQ, chat bot |
| 5. Mengapa tidak ada self‑service? | Tidak ada portal status pesanan | Implementasi portal pelanggan |

---

### 4. KPI yang Terpengaruh

| KPI | Target | Status (dari feedback) | Rekomendasi |
|-----|--------|------------------------|-------------|
| **On‑Time Delivery Rate** | ≥ 95% | < 95% | Optimasi logistik, SLA kurir |
| **Average Response Time (Admin)** | ≤ 12 jam | > 24 jam | Tambah staf, automasi |
| **CSAT (Customer Satisfaction)** | ≥ 80% | 60‑70% | Perbaiki pengiriman & support |
| **NPS (Net Promoter Score)** | ≥ 50 | < 50 | Tingkatkan kecepatan & komunikasi |

---

### 5. Rekomendasi Tindakan

| Area | Tindakan | Waktu Implementasi | KPI yang Meningkat |
|------|----------|--------------------|--------------------|
| **Logistik** | 1. Negosiasi ulang SLA dengan kurir. <br>2. Tambah titik pengiriman (hub) di wilayah target. <br>3. Implementasi sistem pelacakan real‑time. | 1–3 bulan | On‑Time Delivery Rate |
| **Customer Support** | 1. Tambah 2-3 staf admin. <br>2. Gunakan sistem tiket otomatis (Zendesk, Freshdesk). <br>3. Tambah chat bot FAQ. | 1–2 bulan | Avg. Response Time |
| **Self‑Service** | 1. Portal pelanggan: status pesanan, tracking, FAQ. <br>2. Notifikasi push/email otomatis. | 2–4 bulan | CSAT, NPS |
| **Feedback Loop** | 1. Survey singkat setelah pengiriman. <br>2. Analisis data feedback bulanan. | 1 bulan | CSAT, NPS |
| **Quality Assurance** | 1. Pastikan produk tetap berkualitas. <br>2. Kontrol kualitas sebelum pengiriman. | Ongoing | CSAT |

---

### 6. KPI Monitoring & Dashboard

| KPI | Target | Data Source | Frequency |
|-----|--------|-------------|-----------|
| On‑Time Delivery Rate | ≥ 95% | Log pengiriman | Mingguan |
| Avg. Response Time | ≤ 12 jam | Ticketing system | Harian |
| CSAT | ≥ 80% | Survey post‑delivery | Bulanan |
| NPS | ≥ 50 | Survey post‑delivery | Bulanan |
| Order Fulfillment Time | ≤ 24 jam | ERP | Harian |

> **Catatan**: Gunakan dashboard BI (misalnya Power BI, Tableau) untuk visualisasi real‑time.

---

### 7. Komunikasi ke Stakeholder

- **Executive Summary**: Fokus pada dua pain point utama (pengiriman & support) yang menurunkan CSAT/NPS.
- **Action Plan**: Timeline 6 bulan, dengan milestone setiap 2 bulan.
- **ROI Estimasi**: Perbaikan pengiriman & support diperkirakan meningkatkan CSAT 15‑20% dan NPS 10‑15 poin, yang berdampak pada retensi pelanggan +10% dan pendapatan +5%.

---

### 8. Kesimpulan

Feedback pelanggan menyoroti dua area kritis: **pengiriman** dan **respons admin**. Meskipun produk tetap memuaskan, ketidaksesuaian antara ekspektasi dan realitas layanan menurunkan kepuasan. Dengan mengimplementasikan rekomendasi di atas—terutama optimasi logistik, peningkatan kapasitas support, dan pemberdayaan pelanggan lewat portal self‑service—toko online sepatu dapat meningkatkan kepuasan pelanggan, mengurangi churn, dan memperkuat posisi kompetitif di pasar.
```

### Prompt C

Versi prompt pada saat eksperimen (sebelum perbaikan di bagian Failure Case):

```text
[SYSTEM]
Kamu adalah analis customer experience yang teliti dan objektif. Kamu hanya menjawab dalam format JSON valid tanpa teks tambahan.

[USER]
TASK:
Analisis feedback pelanggan berikut dan ubah menjadi insight yang bisa ditindaklanjuti.

CONTEXT:
Konteks bisnis: toko online sepatu
Feedback pelanggan:
"""Pengiriman lambat banget, sudah 5 hari belum sampai. Adminnya juga lama balas. Tapi barangnya bagus."""

CONSTRAINT:
- Gunakan Bahasa Indonesia.
- Jangan mengarang informasi yang tidak ada di feedback.
- summary maksimal 2 kalimat.
- key_issues dan suggested_actions masing-masing 1 sampai 4 item singkat.
- priority "tinggi" jika ada masalah serius/mendesak, "sedang" jika perlu perbaikan, "rendah" jika hanya masukan ringan.

OUTPUT FORMAT:
Balas HANYA dengan JSON berikut:
{
  "sentiment": "positif | netral | negatif",
  "summary": "string",
  "key_issues": ["string"],
  "suggested_actions": ["string"],
  "priority": "rendah | sedang | tinggi"
}
```

### Actual Output C

```json
{"sentiment":"negatif","summary":"Pengiriman terlambat selama 5 hari. Respon admin juga lambat, meskipun barangnya bagus.","key_issues":["Pengiriman terlambat","Respon admin lambat"],"suggested_actions":["Perbaiki sistem logistik dan koordinasi pengiriman","Tingkatkan kecepatan respon customer service"],"priority":"tinggi"}
```

## Prompt Evaluation

**Dari ketiga prompt tersebut, mana yang menurut kalian menghasilkan output paling baik?**
[Prompt C]

**Kenapa?**
[Penggunaan Constraint dan juga menggunakan format JSON]

**Apa perbedaan paling terlihat antara Prompt A, Prompt B, dan Prompt C berdasarkan hasil testing kalian?**
[A menjawab dalam bahasa Inggris dan sangat panjang; B berbahasa Indonesia tetapi tetap sangat panjang dan menambahkan angka yang tidak ada di feedback (misalnya "respons admin > 24 jam", CSAT 60-70%, estimasi ROI); A juga menambahkan diskon 10% dan bobot sentimen yang tidak ada di feedback; C ringkas, berformat JSON sesuai schema, dan tidak mengarang. Catatan: A dan B tidak memakai mode JSON, C memakai mode JSON, jadi sebagian perbedaan format berasal dari pengaturan itu.]

## Failure Case

**Input yang menghasilkan output kurang baik**

```json
{
  "text": "Wow hebat banget, pesan seminggu lalu baru datang hari ini. Terima kasih sudah melatih kesabaran saya.",
  "context": "toko online sepatu"
}
```

**Actual Output**

```json
{
  "sentiment": "positif",
  "summary": "Pelanggan mengapresiasi layanan kami. Namun, pengiriman memakan waktu satu minggu.",
  "key_issues": [
    "Pengiriman terlambat"
  ],
  "suggested_actions": [
    "Perbaiki estimasi waktu pengiriman",
    "Tingkatkan koordinasi logistik",
    "Berikan kompensasi diskon bagi pelanggan"
  ],
  "priority": "sedang"
}
```

**Menurut kalian apa masalah dari output tersebut?**
[Case ini menunjukkan respon sentimen positif padahal user melakukan feedback dengan gaya sarkasme. Model terkecoh dengan kata "hebat" dan "terima kasih".]

**Apa yang kalian ubah pada prompt / constraint / kode?**
[Menambahkan constaint "- Perhatikan sarkasme: tentukan sentiment berdasarkan makna sebenarnya, bukan kata-kata positifnya saja." di build_prompt()]

**Output setelah diperbaiki**

```json
{
  "sentiment": "negatif",
  "summary": "Pengiriman terlambat satu minggu, pelanggan merasa kesabaran diuji meski mengucapkan terima kasih.",
  "key_issues": [
    "Waktu pengiriman terlalu lama",
    "Kurangnya komunikasi status pengiriman",
    "Pengalaman pelanggan terpengaruh"
  ],
  "suggested_actions": [
    "Optimalkan proses logistik dan pilih kurir cepat",
    "Kirim update status secara real-time",
    "Tawarkan diskon atau voucher sebagai kompensasi"
  ],
  "priority": "sedang"
}
```

**Catatan setelah perbaikan:**
[Masalah sentimen teratasi, yang masih kurang adalah bagian key_issues yang tidak terlalu spesifik dan sedikit mengarang teks.]

## Personal Reflection

**1. Menurut kalian, bagian apa yang paling sulit dari project ini?**
[Menulis Kode]

**2. Bagian kode mana yang paling banyak dibantu oleh AI?**
[Bagian Endpoints]

**3. Setelah melihat kode tersebut, jelaskan menggunakan bahasa kalian sendiri bagaimana bagian tersebut bekerja.**
[Saya bahas bagian Endpoints POST /experiments. Setelah adanya body request, model akan mengeluarkan response dengan 3 hasil berbeda (A, B, C). Prompt C adalah prompt utama dengan format JSON.]

**4. Menurut kalian, apa kekurangan terbesar dari aplikasi yang kalian buat jika digunakan oleh user sungguhan?**
[Untuk sekarang saya bisa bilang hasil analisis merupakan kekurangan karena kurangnya testing input yang dilakukan. Jadi bisa saja sentimen yang dihasilkan tidak sesuai, ataupun model mengarang.]

**5. Jika provider LLM kalian diganti, misalnya dari Groq ke Gemini atau OpenAI, bagian mana dari project yang menurut kalian perlu diubah?**
[Yang langsung terlihat sudah pasti API Keys, Import/SDK, Variabel .env, serta requiremnents.txt]

**6. Setelah mencoba aplikasi kalian sendiri, apa satu improvement yang menurut kalian paling penting jika project ini dilanjutkan?**
[Penambahan Testing. Dengan banyaknya testing, kita bisa melihat berbagai aspek dari aplikasi yang perlu diubah]

## AI Usage

**AI tools yang digunakan**
Claude (Anthropic).

**AI digunakan untuk membantu bagian apa?**
[Pembuatan kerangka kode bagian endpoints dan prompt, Membantu menyusun README.md]

**Bagian apa yang kalian tentukan, perbaiki, atau ubah sendiri setelah melihat hasil dari AI?**
[AI menggunakan model yang sudah tidak ada, saya menggantinya. Melakukan testing model, Menambahkan endpoints POST /analyze untuk testing tambahan]

---

## Informasi Tambahan

### Cara Menjalankan

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Buat file `.env`:

```env
GROQ_API_KEY=isi_api_key_kamu
```

Jalankan:

```bash
fastapi dev main.py
```

Buka dokumentasi interaktif di http://127.0.0.1:8000/docs. File `.env` tidak ikut ke repository (ada di `.gitignore`).

### Error Handling

| Kode | Kondisi |
|------|---------|
| 422 | Request body tidak valid (divalidasi Pydantic) |
| 500 | `GROQ_API_KEY` belum diset / error server |
| 502 | Gagal menghubungi Groq atau output LLM bukan JSON valid |

Hasil tes aktual:

Input `text` terlalu pendek (`"jelek"`) menghasilkan 422:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 10 characters",
      "input": "jelek",
      "ctx": { "min_length": 10 }
    }
  ]
}
```

Field `text` hilang menghasilkan 422:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "text"],
      "msg": "Field required",
      "input": { "context": "toko online sepatu" }
    }
  ]
}
```