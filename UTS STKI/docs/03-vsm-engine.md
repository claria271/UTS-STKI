# Fitur 3: Mesin Hitung VSM & Perangkingan (Backend Engine)

## 1. Deskripsi
Inti aplikasi. Bertugas: **(a) indeksasi**, **(b) pembobotan TF-IDF**, **(c) representasi vektor**, **(d) menghitung kemiripan kueri–dokumen dengan Cosine Similarity**, dan **(e) merangking dokumen**.

## 2. Konsep & Rumus

### 2.1 Term Frequency (TF)
Jumlah kemunculan term *t* dalam dokumen *d*.

- **Raw TF:** `tf(t,d) = f(t,d)`
- **Log TF (disarankan):** `tf(t,d) = 1 + log10(f(t,d))` jika f > 0, selain itu 0

### 2.2 Inverse Document Frequency (IDF)
```
idf(t) = log10( N / df(t) )
```
- `N` = jumlah dokumen (1000)
- `df(t)` = jumlah dokumen yang mengandung term *t*

> Jika memakai versi smoothing: `idf(t) = log10( (N+1) / (df(t)+1) ) + 1` agar term yang muncul di semua dokumen tidak bernilai 0. Pilih satu dan **konsisten** di laporan.

### 2.3 Bobot TF-IDF
```
w(t,d) = tf(t,d) × idf(t)
```

### 2.4 Cosine Similarity
```
                 Σ ( w(t,q) × w(t,d) )
cos(q,d) = ───────────────────────────────
               ‖q‖ × ‖d‖

‖v‖ = √( Σ w(t,v)² )
```
Nilai 0 (tidak mirip) hingga 1 (identik arah vektor).

### 2.5 Contoh Hitung Singkat
Misal N = 4, kueri `"harga naik"`.

| Term | df | idf = log10(4/df) |
|------|----|-------------------|
| harga | 2 | 0,301 |
| naik | 1 | 0,602 |

Dokumen D1 memuat `harga` ×2 dan `naik` ×1 (raw TF):
- w(harga,D1) = 2 × 0,301 = 0,602
- w(naik,D1) = 1 × 0,602 = 0,602
- Vektor kueri: w(harga,q) = 0,301; w(naik,q) = 0,602
- Dot product = (0,301×0,602) + (0,602×0,602) = 0,181 + 0,362 = 0,543
- ‖q‖ = √(0,301² + 0,602²) = 0,673; ‖D1‖ = √(0,602²+0,602²) = 0,851 (jika hanya dua term)
- cos = 0,543 / (0,673 × 0,851) ≈ **0,948**

## 3. Kebutuhan Fungsional
| Kode | Kebutuhan |
|------|-----------|
| F3.1 | Membaca CSV dan memproses 1.000 dokumen |
| F3.2 | Membangun vocabulary, DF, dan inverted index |
| F3.3 | Menghitung bobot TF-IDF tiap term di tiap dokumen |
| F3.4 | Menyimpan norma vektor dokumen (prakomputasi) |
| F3.5 | Membuat vektor kueri dengan IDF dari koleksi |
| F3.6 | Menghitung cosine similarity |
| F3.7 | Mengurutkan skor menurun, mengembalikan Top-K |
| F3.8 | Menyimpan indeks ke `index.pkl` agar start berikutnya cepat |
| F3.9 | Term kueri yang tak ada di vocabulary diabaikan |

## 4. Struktur Data
| Struktur | Tipe | Isi |
|----------|------|-----|
| `docs` | list[dict] | id, judul, isi asli |
| `df` | dict[str,int] | term → jumlah dokumen |
| `idf` | dict[str,float] | term → nilai IDF |
| `inverted` | dict[str, dict[int,float]] | term → {doc_idx: bobot TF-IDF} |
| `doc_norm` | list[float] | ‖d‖ tiap dokumen |

Inverted index membuat pencarian hanya menyentuh dokumen yang memuat term kueri, sehingga cepat.

## 5. Implementasi: `engine/vsm.py`
```python
import math
import pickle
import os
from collections import Counter, defaultdict

import pandas as pd
from engine.preprocess import preprocess


def log_tf(freq: int) -> float:
    return 1 + math.log10(freq) if freq > 0 else 0.0


class VSMEngine:
    def __init__(self, docs, df, idf, inverted, doc_norm):
        self.docs = docs
        self.df = df
        self.idf = idf
        self.inverted = inverted
        self.doc_norm = doc_norm

    # ---------- INDEXING ----------
    @classmethod
    def build(cls, csv_path: str):
        data = pd.read_csv(csv_path)
        docs = data.to_dict("records")
        N = len(docs)

        # 1. preprocess + hitung TF
        tfs = []                      # list[Counter]
        df = Counter()
        for d in docs:
            text = f"{d.get('judul', '')} {d.get('isi', '')}"
            tokens = preprocess(text)
            c = Counter(tokens)
            tfs.append(c)
            df.update(c.keys())       # tiap term dihitung 1x per dokumen

        # 2. IDF
        idf = {t: math.log10(N / n) for t, n in df.items()}

        # 3. bobot TF-IDF + inverted index
        inverted = defaultdict(dict)
        sq_sum = [0.0] * N
        for i, c in enumerate(tfs):
            for t, f in c.items():
                w = log_tf(f) * idf[t]
                if w > 0:
                    inverted[t][i] = w
                    sq_sum[i] += w * w

        doc_norm = [math.sqrt(s) for s in sq_sum]
        return cls(docs, dict(df), idf, dict(inverted), doc_norm)

    @classmethod
    def load_or_build(cls, csv_path: str, cache_path: str):
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        engine = cls.build(csv_path)
        with open(cache_path, "wb") as f:
            pickle.dump(engine, f)
        return engine

    # ---------- SEARCHING ----------
    def search(self, query: str, top_k: int = 100):
        tokens = preprocess(query)
        q_tf = Counter(t for t in tokens if t in self.idf)
        if not q_tf:
            return [], tokens

        # vektor kueri
        q_w = {t: log_tf(f) * self.idf[t] for t, f in q_tf.items()}
        q_norm = math.sqrt(sum(w * w for w in q_w.values()))
        if q_norm == 0:
            return [], tokens

        # dot product via inverted index
        scores = defaultdict(float)
        for t, wq in q_w.items():
            for doc_i, wd in self.inverted.get(t, {}).items():
                scores[doc_i] += wq * wd

        # cosine similarity
        ranked = []
        for doc_i, dot in scores.items():
            if self.doc_norm[doc_i] > 0:
                cos = dot / (q_norm * self.doc_norm[doc_i])
                ranked.append((doc_i, cos))

        ranked.sort(key=lambda x: x[1], reverse=True)
        results = [
            {"rank": r + 1, "doc": self.docs[i], "score": s}
            for r, (i, s) in enumerate(ranked[:top_k])
        ]
        return results, tokens

    def stats(self):
        return {"n_docs": len(self.docs), "n_terms": len(self.idf)}
```

## 6. Endpoint Backend
```python
@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return redirect(url_for("index"))
    results, tokens = engine.search(q)
    return render_template("results.html", q=q, tokens=tokens, results=results)
```

## 7. Validasi Hasil (Opsional tapi Dianjurkan)
Bandingkan dengan scikit-learn untuk memastikan perhitungan benar:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Gunakan teks hasil preprocess, hitung ranking, lalu bandingkan urutan Top-10.
```
Skor bisa sedikit berbeda (rumus IDF/TF berbeda), tetapi **urutan Top-10 seharusnya mirip**.

## 8. Pengujian
| ID | Kasus | Hasil Diharapkan |
|----|-------|------------------|
| E1 | Term ada di 1 dokumen saja | Dokumen itu peringkat 1 |
| E2 | Dua dokumen identik | Skor sama |
| E3 | Kueri = isi persis suatu dokumen | Skor mendekati 1 |
| E4 | Term tak ada di vocabulary | Hasil kosong |
| E5 | Skor selalu 0 ≤ s ≤ 1 | Terpenuhi |
| E6 | Hasil terurut menurun | Terpenuhi |
| E7 | Waktu pencarian | < 1 detik |

## 9. Catatan Penting
- Term yang muncul di **semua** dokumen memiliki IDF = 0 (pada rumus tanpa smoothing) dan otomatis tidak berpengaruh.
- Hapus `index.pkl` setiap kali dataset atau pipeline preprocessing diubah.
