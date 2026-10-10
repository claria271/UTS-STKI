# Fitur 1: Halaman Utama (Dashboard Pencarian)

## 1. Deskripsi
Halaman pertama yang dilihat pengguna. Berisi kolom input kueri dan informasi ringkas tentang koleksi dokumen. Dibuat bersih dan fokus seperti halaman utama mesin pencari pada umumnya.

## 2. Kebutuhan Fungsional
| Kode | Kebutuhan |
|------|-----------|
| F1.1 | Menampilkan judul/logo aplikasi |
| F1.2 | Menyediakan kolom input kueri dan tombol **Cari** |
| F1.3 | Pencarian dapat dikirim dengan menekan tombol Enter |
| F1.4 | Validasi: kueri kosong tidak boleh dikirim |
| F1.5 | Menampilkan statistik koleksi (jumlah dokumen, jumlah term unik) |
| F1.6 | (Opsional) Contoh kueri yang bisa diklik |
| F1.7 | (Opsional) Pilihan jumlah hasil per halaman |

## 3. Kebutuhan Non-Fungsional
- Responsif (nyaman di laptop dan ponsel)
- Tampil dalam < 1 detik
- Bahasa antarmuka: Indonesia

## 4. Rancangan Antarmuka (Wireframe)
```
+--------------------------------------------------+
|                 🔍 Mesin Pencari VSM              |
|        Cari dari 1.000 dokumen dengan TF-IDF      |
|                                                  |
|   [ ketik kata kunci...                 ] [Cari] |
|                                                  |
|   Contoh: ekonomi digital | pendidikan | banjir   |
|                                                  |
|   ┌─────────┐ ┌──────────────┐ ┌──────────────┐  |
|   │ 1000    │ │ 12.345       │ │ VSM+TF-IDF   │  |
|   │ Dokumen │ │ Term unik    │ │ Metode       │  |
|   └─────────┘ └──────────────┘ └──────────────┘  |
+--------------------------------------------------+
```

## 5. Routing
| Method | URL | Fungsi |
|--------|-----|--------|
| GET | `/` | Menampilkan dashboard + statistik |

## 6. Implementasi

### `app.py` (bagian dashboard)
```python
from flask import Flask, render_template, request
from engine.vsm import VSMEngine

app = Flask(__name__)
engine = VSMEngine.load_or_build("data/dataset.csv", "data/index.pkl")

@app.route("/")
def index():
    stats = engine.stats()
    examples = ["pendidikan", "ekonomi digital", "kesehatan masyarakat"]
    return render_template("index.html", stats=stats, examples=examples)
```

### `templates/index.html`
```html
{% extends "base.html" %}
{% block content %}
<main class="hero">
  <h1>🔍 Mesin Pencari VSM</h1>
  <p>Cari dari {{ stats.n_docs }} dokumen dengan TF-IDF</p>

  <form action="/search" method="get" onsubmit="return validate()">
    <input type="text" id="q" name="q" placeholder="Ketik kata kunci..." autofocus>
    <button type="submit">Cari</button>
  </form>

  <div class="examples">
    Contoh:
    {% for e in examples %}
      <a href="/search?q={{ e|urlencode }}">{{ e }}</a>
    {% endfor %}
  </div>

  <section class="stats">
    <div class="card"><b>{{ stats.n_docs }}</b><span>Dokumen</span></div>
    <div class="card"><b>{{ stats.n_terms }}</b><span>Term unik</span></div>
    <div class="card"><b>VSM + TF-IDF</b><span>Metode</span></div>
  </section>
</main>

<script>
function validate() {
  const q = document.getElementById("q").value.trim();
  if (!q) { alert("Masukkan kata kunci terlebih dahulu."); return false; }
  return true;
}
</script>
{% endblock %}
```

## 7. Kriteria Penerimaan
- [x] Halaman tampil tanpa error di `http://127.0.0.1:5000/`
- [x] Kueri kosong ditolak dengan pesan
- [x] Menekan Enter / tombol Cari berpindah ke `/search?q=...`
- [x] Statistik sesuai data (1000 dokumen)
