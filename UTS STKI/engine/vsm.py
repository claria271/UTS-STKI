import math
import pickle
import os
from collections import Counter, defaultdict

import pandas as pd
from engine.preprocess import preprocess


def log_tf(freq: int) -> float:
    """Menghitung Log Term Frequency: 1 + log10(tf) jika tf > 0, selain itu 0."""
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
        """Membangun indeks VSM + TF-IDF dari file CSV dataset."""
        if not os.path.exists(csv_path):
            return cls(docs=[], df={}, idf={}, inverted={}, doc_norm=[])

        data = pd.read_csv(csv_path)
        docs = data.to_dict("records")
        N = len(docs)

        # 1. Preprocess & hitung Term Frequency (TF) tiap dokumen
        tfs = []
        df = Counter()
        for d in docs:
            text = f"{d.get('judul', '')} {d.get('isi', '')}"
            tokens = preprocess(text)
            c = Counter(tokens)
            tfs.append(c)
            df.update(c.keys())  # Hitung 1x per dokumen unik

        # 2. Inverse Document Frequency (IDF)
        idf = {t: math.log10(N / n) for t, n in df.items() if n > 0}

        # 3. Bobot TF-IDF & Inverted Index
        inverted = defaultdict(dict)
        sq_sum = [0.0] * N
        for i, c in enumerate(tfs):
            for t, f in c.items():
                if t in idf:
                    w = log_tf(f) * idf[t]
                    if w > 0:
                        inverted[t][i] = w
                        sq_sum[i] += w * w

        doc_norm = [math.sqrt(s) for s in sq_sum]
        return cls(docs, dict(df), idf, dict(inverted), doc_norm)

    @classmethod
    def load_or_build(cls, csv_path: str, cache_path: str):
        """Memuat indeks dari cache pickle atau membangun ulang jika belum ada."""
        if not os.path.exists(csv_path):
            return cls(docs=[], df={}, idf={}, inverted={}, doc_norm=[])

        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    return pickle.load(f)
            except Exception:
                pass  # Rebuild if corrupted
        engine = cls.build(csv_path)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump(engine, f)
        return engine

    # ---------- SEARCHING ----------
    def search(self, query: str, top_k: int = 100):
        """Mencari dokumen relevan berdasarkan kueri dengan Cosine Similarity."""
        tokens = preprocess(query)
        q_tf = Counter(t for t in tokens if t in self.idf)
        if not q_tf:
            return [], tokens

        # Vektor kueri (TF-IDF)
        q_w = {t: log_tf(f) * self.idf[t] for t, f in q_tf.items()}
        q_norm = math.sqrt(sum(w * w for w in q_w.values()))
        if q_norm == 0:
            return [], tokens

        # Dot product menggunakan inverted index
        scores = defaultdict(float)
        for t, wq in q_w.items():
            for doc_i, wd in self.inverted.get(t, {}).items():
                scores[doc_i] += wq * wd

        # Hitung Cosine Similarity
        ranked = []
        for doc_i, dot in scores.items():
            if self.doc_norm[doc_i] > 0:
                cos = dot / (q_norm * self.doc_norm[doc_i])
                ranked.append((doc_i, cos))

        # Urutkan berdasarkan skor tertinggi (descending)
        ranked.sort(key=lambda x: x[1], reverse=True)
        results = [
            {
                "rank": r + 1,
                "doc_idx": i,
                "doc": self.docs[i],
                "score": s
            }
            for r, (i, s) in enumerate(ranked[:top_k])
        ]
        return results, tokens

    def stats(self):
        """Mengembalikan statistik koleksi dokumen."""
        return {
            "n_docs": len(self.docs),
            "n_terms": len(self.idf)
        }
