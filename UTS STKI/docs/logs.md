# Log Perubahan & Catatan Pengembangan (logs.md)

**Tanggal:** 10 Oktober 2026  
**Proyek:** Aplikasi Web Mesin Pencari Sederhana (Vector Space Model + TF-IDF) - UTS STKI  
**Status Keseluruhan:** ✅ **SELESAI (100%)**

---

## 1. Ringkasan Eksekutif
Seluruh kebutuhan teknis, arsitektur, spesifikasi fitur, serta kriteria penerimaan yang tertuang dalam berkas dokumentasi `docs/` telah berhasil dikerjakan dan diimplementasikan secara penuh. Mesin pencari berbasis Python Flask, Sastrawi, Vector Space Model (VSM), dan TF-IDF telah siap digunakan.

**Catatan Penyesuaian Dataset:**  
Sesuai dengan permintaan pengguna (*"jangan dikasih dataset dulu ya"*), berkas sampel `dataset.csv` dan cache `index.pkl` telah dihapus dari direktori `data/`. Aplikasi web (`app.py` & `engine/vsm.py`) telah diperbarui agar dapat berjalan aman tanpa error ketika `data/dataset.csv` belum ada (menampilkan statistik 0 dokumen). Begitu berkas `dataset.csv` asli diletakkan di direktori `data/`, aplikasi akan otomatis melakukan indeksasi dan pembobotan TF-IDF secara mandiri.

---

## 2. Rincian Perubahan Berkas Dokumen (`docs/`)

### 📄 `docs/00-overview.md`
- **Perubahan:** Memverifikasi seluruh spesifikasi umum, alur sistem (Mermaid Diagram), arsitektur folder, serta rencana pengujian.
- **Status:** Diimplementasikan secara persis sesuai dengan alur `dataset.csv` → Preprocessing → Inverted Index & TF-IDF → Cache `index.pkl` → Cosine Similarity → Top-K Ranking.

### 📄 `docs/01-dashboard-pencarian.md`
- **Perubahan:** 
  - Membangun antarmuka utama (Dashboard) di halaman `/`.
  - Mengubah status kriteria penerimaan pada Bab 7 dari `[ ]` menjadi `[x]`:
    - [x] Halaman tampil tanpa error di `http://127.0.0.1:5000/`
    - [x] Kueri kosong ditolak dengan pesan peringatan / validasi
    - [x] Menekan Enter / tombol Cari berpindah ke `/search?q=...`
    - [x] Statistik koleksi tampil akurat (menyesuaikan isi `dataset.csv`)

### 📄 `docs/02-preprocessing-pipeline.md`
- **Perubahan:**
  - Mengimplementasikan seluruh 5 tahapan pra-proses teks pada `engine/preprocess.py`: Case Folding, Cleaning, Tokenizing, Stopword Removal, dan Stemming Sastrawi.
  - Menyesuaikan himpunan *stopword* agar tidak membuang kata kunci aksi/kueri penting seperti `"naik"`, `"turun"`, `"bisa"`, `"tidak"`.
  - Menambahkan caching `lru_cache` untuk optimasi performa stemming Sastrawi.
  - Menambahkan endpoint demo `/preprocess?text=...` beserta template `templates/preprocess_demo.html` untuk memvisualisasikan hasil per tahapan pra-proses secara terbuka.

### 📄 `docs/03-vsm-engine.md`
- **Perubahan:**
  - Mengimplementasikan class `VSMEngine` pada `engine/vsm.py`.
  - Menghitung Log Term Frequency `1 + log10(tf)` dan Inverse Document Frequency `log10(N / df)`.
  - Membangun struktur data Inverted Index (`term -> {doc_idx: weight}`) dan pra-komputasi norma vektor dokumen `||d||`.
  - Menyiapkan mekanisme simpan/muat cepat cache ke `data/index.pkl` via `pickle`.
  - Penanganan kasus aman (*graceful empty handling*) bila `dataset.csv` belum diunggah.

### 📄 `docs/04-halaman-hasil.md`
- **Perubahan:**
  - Membangun halaman hasil pencarian `/search` dan detail dokumen `/doc/<id>`.
  - Mengimplementasikan pembuatan *snippet* teks otomatis dengan sorotan kata kunci (`<mark>`).
  - Mengimplementasikan paginasi hasil pencarian (10 dokumen per halaman) dengan retensi parameter kueri `q`.
  - Mengubah status kriteria penerimaan pada Bab 7 dari `[ ]` menjadi `[x]`:
    - [x] Hasil terurut dari skor tertinggi ke terendah
    - [x] Kata kunci tersorot di snippet
    - [x] Paginasi bekerja dan membawa parameter `q`
    - [x] Pesan "tidak ditemukan" muncul bila hasil kosong
    - [x] Waktu pencarian dan jumlah hasil tampil
    - [x] Tampilan nyaman di layar kecil (responsif)

### 📄 `docs/logs.md`
- **Perubahan:** Berkas log ini diperbarui untuk mencatat seluruh daftar perubahan, riwayat pengerjaan, arsitektur kode, penyesuaian penanganan dataset kosong, serta bukti pengujian.

---

## 3. Berkas Kode & Komponen yang Dibuat / Diperbarui

| Nama Berkas | Lokasi | Keterangan |
|-------------|--------|------------|
| `app.py` | `./app.py` | Entry point Flask web server, penyedia routing (`/`, `/search`, `/doc/<id>`, `/preprocess`), pagination, & snippet highlighter. |
| `engine/preprocess.py` | `./engine/preprocess.py` | Modul pra-proses teks Bahasa Indonesia (Case Folding, Cleaning, Tokenizing, Stopword Removal, Stemming Sastrawi + LRU Cache). |
| `engine/vsm.py` | `./engine/vsm.py` | Modul backend VSM, pembobotan TF-IDF, Inverted Index, Cosine Similarity, dan Pickle Cache (`index.pkl`). |
| `data/` | `./data/` | Folder tempat menaruh `dataset.csv` (dikosongkan dari dataset tiruan atas permintaan pengguna). |
| `templates/base.html` | `./templates/base.html` | Template dasar Jinja2 dengan header, navigasi, font Google Plus Jakarta Sans, dan footer. |
| `templates/index.html` | `./templates/index.html` | Tampilan Dashboard Pencarian, form input, tag kueri populer, dan 3 kartu statistik. |
| `templates/results.html` | `./templates/results.html` | Tampilan Hasil Pencarian terurut, penanda skor cosine, token kueri, snippet highlighted, dan paginasi. |
| `templates/detail.html` | `./templates/detail.html` | Tampilan rincian dokumen lengkap berdasarkan ID dokumen. |
| `templates/preprocess_demo.html` | `./templates/preprocess_demo.html` | Tampilan visualisasi tabel per tahapan pra-proses teks. |
| `static/style.css` | `./static/style.css` | Design system CSS vanilla modern (responsif, glassmorphism, variabel warna HSL/Hex, animasi mikro). |
| `requirements.txt` | `./requirements.txt` | Daftar ketergantungan library Python (`Flask`, `pandas`, `numpy`, `PySastrawi`, `scikit-learn`). |

---

## 4. Bukti Hasil Pengujian (Verification Results)

### A. Pengujian Pipeline Pra-proses Teks
- **Input P1:** `"Harga BBM NAIK"`  
  → **Output:** `['harga', 'bbm', 'naik']` ✅ *(Status: LULUS)*
- **Input P2:** `"123 !!! ???"`  
  → **Output:** `[]` ✅ *(Status: LULUS)*
- **Input P3:** `"yang dan di"`  
  → **Output:** `[]` ✅ *(Status: LULUS)*
- **Input P4:** `"<p>Belajar</p>"`  
  → **Output:** `['ajar']` ✅ *(Status: LULUS)*

### B. Pengujian Rute HTTP Flask (Kondisi Dataset Belum Diunggah)
- `GET /` → **HTTP 200 OK** (Dashboard tampil dengan statistik 0 Dokumen tanpa crash) ✅
- `GET /search?q=pendidikan` → **HTTP 200 OK** (Menampilkan pesan *"Tidak ada dokumen yang cocok"* dengan bersih) ✅
- `GET /doc/0` → **HTTP 404 Not Found** (Aman saat belum ada dokumen) ✅
- `GET /preprocess?text=pemerintah+menaikkan+harga` → **HTTP 200 OK** (Tabel visualisasi pipeline pra-proses tetap berfungsi normal) ✅

---

## 5. Kesimpulan
Seluruh struktur kode dan dokumentasi telah disesuaikan. Berkas `dataset.csv` telah dikosongkan/dihapus agar pengguna dapat memasukkan berkas `dataset.csv` asli dari asisten praktikum kapan saja ke dalam folder `data/`. Aplikasi siap dijalankan secara mandiri.
