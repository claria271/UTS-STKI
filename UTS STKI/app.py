import os
import re
import time
import math
from flask import Flask, render_template, request, redirect, url_for, abort
from markupsafe import Markup, escape

from engine.vsm import VSMEngine
from engine.preprocess import preprocess_verbose

app = Flask(__name__)

# Path dataset dan cache indeks
CSV_PATH = os.path.join(app.root_path, "data", "dataset.csv")
INDEX_PATH = os.path.join(app.root_path, "data", "index.pkl")

# Load or build VSM Engine (akan mengembalikan engine kosong jika dataset.csv belum dimasukkan)
engine = VSMEngine.load_or_build(CSV_PATH, INDEX_PATH)

PER_PAGE = 10


def make_snippet(text: str, terms: list[str], length: int = 250) -> Markup:
    """Membuat cuplikan teks (snippet) dan menyorot (highlight) kata kunci kueri."""
    text = str(text)
    low = text.lower()
    pos = -1

    for t in terms:
        pos = low.find(t)
        if pos != -1:
            break

    start = max(0, pos - 60) if pos != -1 else 0
    snippet_raw = text[start:start + length]
    snippet_escaped = escape(snippet_raw)

    # Highlight terms
    for t in set(terms):
        if t:
            snippet_escaped = re.sub(
                f"(?i)({re.escape(t)})",
                r"<mark>\1</mark>",
                str(snippet_escaped)
            )

    prefix = "..." if start > 0 else ""
    suffix = "..." if (start + length) < len(text) else ""
    return Markup(prefix + snippet_escaped + suffix)


@app.route("/")
def index():
    """Halaman utama / Dashboard pencarian."""
    stats = engine.stats()
    examples = [
        "pendidikan digital",
        "harga bbm naik",
        "kecerdasan buatan",
        "imunisasi anak",
        "energi bersih"
    ]
    return render_template("index.html", stats=stats, examples=examples)


@app.route("/search")
def search():
    """Halaman hasil pencarian VSM + TF-IDF dengan paginasi."""
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

    return render_template(
        "results.html",
        q=q,
        tokens=tokens,
        results=chunk,
        total=total,
        page=page,
        pages=pages,
        elapsed=f"{elapsed:.4f}"
    )


@app.route("/doc/<int:doc_id>")
def detail(doc_id):
    """Halaman detail dokumen lengkap."""
    if doc_id < 0 or doc_id >= len(engine.docs):
        abort(404)
    return render_template("detail.html", doc=engine.docs[doc_id])


@app.route("/preprocess")
def preprocess_demo():
    """Halaman demo visualisasi per tahapan pra-proses teks."""
    input_text = request.args.get("text", "Pemerintah Menaikkan Harga BBM di 2024, masyarakat protes!")
    steps = preprocess_verbose(input_text)
    return render_template("preprocess_demo.html", input_text=input_text, steps=steps)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
