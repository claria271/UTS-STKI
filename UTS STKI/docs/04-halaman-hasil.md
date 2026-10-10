# Fitur 4: Halaman Hasil Pencarian (Tampilan Hasil)

## 1. Deskripsi
Menampilkan dokumen hasil pencarian terurut berdasarkan skor cosine similarity tertinggi, lengkap dengan cuplikan teks (snippet) dan informasi pendukung.

## 2. Kebutuhan Fungsional
| Kode | Kebutuhan |
|------|-----------|
| F4.1 | Menampilkan kueri yang dicari dan jumlah dokumen ditemukan |
| F4.2 | Menampilkan waktu pencarian (detik) |
| F4.3 | Menampilkan daftar hasil: peringkat, judul, snippet, skor |
| F4.4 | Menyorot (highlight) kata kunci pada snippet |
| F4.5 | Paginasi (mis. 10 hasil per halaman) |
| F4.6 | Kolom pencarian tetap tersedia di atas hasil |
| F4.7 | Pesan khusus jika tidak ada hasil |
| F4.8 | Menampilkan token kueri setelah preprocessing |
| F4.9 | Tombol "Lihat selengkapnya" menuju detail dokumen |

## 3. Rancangan Antarmuka
```
+----------------------------------------------------+
| [ harga bbm naik            ] [Cari]               |
| 37 dokumen ditemukan (0,012 detik)                 |
| Token kueri: harga · bbm · naik                    |
|----------------------------------------------------|
| #1  Kenaikan Harga BBM Picu Inflasi     Skor 0.842 |
|     ...pemerintah menaikkan **harga** **bbm**...   |
|     [Lihat selengkapnya]                           |
|----------------------------------------------------|
| #2  Dampak Subsidi BBM                  Skor 0.731 |
|     ...                                            |
|----------------------------------------------------|
| « 1 2 3 4 »                                        |
+----------------------------------------------------+
```

## 4. Routing
| Method | URL | Fungsi |
|--------|-----|--------|
| GET | `/search?q=...&page=1` | Hasil pencarian + paginasi |
| GET | `/doc/<int:doc_id>` | Detail dokumen lengkap |

## 5. Implementasi

### `app.py` (route hasil & detail)
```python
import re, time, math
from flask import Flask, render_template, request, redirect, url_for, abort
from markupsafe import Markup, escape

PER_PAGE = 10

def make_snippet(text: str, terms: list[str], length: int = 250) -> Markup:
    text = str(text)
    low = text.lower()
    pos = -1
    for t in terms:
        pos = low.find(t)
        if pos != -1:
            break
    start = max(0, pos - 60) if pos != -1 else 0
    snippet = escape(text[start:start + length])
    for t in set(terms):
        snippet = re.sub(f"(?i)({re.escape(t)})", r"<mark>\1</mark>", str(snippet))
    prefix = "..." if start > 0 else ""
    return Markup(prefix + snippet + "...")

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    page = max(1, request.args.get("page", 1, type=int))
    if not q:
        return redirect(url_for("index"))

    t0 = time.perf_counter()
    results, tokens = engine.search(q, top_k=1000)
    elapsed = time.perf_counter() - t0

    total = len(results)
    pages = max(1, math.ceil(total / PER_PAGE))
    page = min(page, pages)
    chunk = results[(page - 1) * PER_PAGE: page * PER_PAGE]
    for r in chunk:
        r["snippet"] = make_snippet(r["doc"].get("isi", ""), tokens)

    return render_template("results.html", q=q, tokens=tokens, results=chunk,
                           total=total, page=page, pages=pages,
                           elapsed=f"{elapsed:.4f}")

@app.route("/doc/<int:doc_id>")
def detail(doc_id):
    if doc_id < 0 or doc_id >= len(engine.docs):
        abort(404)
    return render_template("detail.html", doc=engine.docs[doc_id])
```
> Catatan: agar `/doc/<id>` bekerja, sertakan indeks dokumen (`doc_idx`) pada hasil di `engine.search`, misalnya `{"rank":..., "doc_idx": i, "doc":..., "score":...}`.

### `templates/results.html`
```html
{% extends "base.html" %}
{% block content %}
<form action="/search" method="get" class="searchbar">
  <input type="text" name="q" value="{{ q }}" required>
  <button type="submit">Cari</button>
</form>

{% if total == 0 %}
  <div class="empty">
    <h2>Tidak ada dokumen yang cocok untuk "{{ q }}"</h2>
    <ul>
      <li>Periksa ejaan kata kunci</li>
      <li>Gunakan kata yang lebih umum</li>
      <li>Kurangi jumlah kata kunci</li>
    </ul>
  </div>
{% else %}
  <p class="meta">{{ total }} dokumen ditemukan ({{ elapsed }} detik)</p>
  <p class="meta">Token kueri: {{ tokens | join(" · ") }}</p>

  {% for r in results %}
  <article class="result">
    <span class="rank">#{{ r.rank }}</span>
    <h3>{{ r.doc.judul }}</h3>
    <p>{{ r.snippet }}</p>
    <span class="score">Skor: {{ "%.4f"|format(r.score) }}</span>
    <a href="/doc/{{ r.doc_idx }}">Lihat selengkapnya</a>
  </article>
  {% endfor %}

  <nav class="pagination">
    {% if page > 1 %}<a href="?q={{ q|urlencode }}&page={{ page-1 }}">« Sebelumnya</a>{% endif %}
    <span>Halaman {{ page }} / {{ pages }}</span>
    {% if page < pages %}<a href="?q={{ q|urlencode }}&page={{ page+1 }}">Berikutnya »</a>{% endif %}
  </nav>
{% endif %}
{% endblock %}
```

### `static/style.css` (ringkas)
```css
body { font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
.searchbar { display: flex; gap: .5rem; }
.searchbar input { flex: 1; padding: .7rem; border: 1px solid #ccc; border-radius: 8px; }
button { padding: .7rem 1.2rem; border: 0; border-radius: 8px; background: #2563eb; color: #fff; cursor: pointer; }
.result { padding: 1rem 0; border-bottom: 1px solid #eee; }
.rank { color: #888; font-size: .85rem; }
.score { background: #e0f2fe; padding: 2px 8px; border-radius: 12px; font-size: .8rem; margin-right: .5rem; }
mark { background: #fde68a; }
.pagination { display: flex; gap: 1rem; justify-content: center; margin: 2rem 0; }
.meta { color: #555; font-size: .9rem; margin: .2rem 0; }
@media (max-width: 600px) { body { margin: 1rem auto; } }
```

## 6. Keamanan
- Gunakan `escape()` / autoescape Jinja2 agar tidak rentan XSS pada kueri dan isi dokumen.
- Batasi panjang kueri (mis. 200 karakter).

## 7. Kriteria Penerimaan
- [x] Hasil terurut dari skor tertinggi ke terendah
- [x] Kata kunci tersorot di snippet
- [x] Paginasi bekerja dan membawa parameter `q`
- [x] Pesan "tidak ditemukan" muncul bila hasil kosong
- [x] Waktu pencarian dan jumlah hasil tampil
- [x] Tampilan nyaman di layar kecil

## 8. Pengujian
| ID | Skenario | Hasil Diharapkan |
|----|----------|------------------|
| H1 | Kueri umum | 10 hasil per halaman, skor menurun |
| H2 | Klik halaman 2 | Hasil ke-11 s.d. 20 |
| H3 | Kueri tak ada | Pesan kosong tampil |
| H4 | Kueri `<script>alert(1)</script>` | Tidak dieksekusi (di-escape) |
| H5 | `/search?q=a&page=999` | Otomatis ke halaman terakhir |
