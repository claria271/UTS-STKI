import re
from functools import lru_cache
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

_stemmer = StemmerFactory().create_stemmer()
_stopwords = set(StopWordRemoverFactory().get_stop_words())
# Hapus kata kunci penting yang tidak boleh dibuang sebagai stopword
_stopwords -= {"naik", "turun", "bisa", "bukan", "tidak", "kurang", "lebih"}
_stopwords |= {"yaitu", "adalah", "akan", "juga", "serta", "tersebut", "ini", "itu"}


def case_folding(text: str) -> str:
    """Mengubah seluruh huruf menjadi huruf kecil."""
    return text.lower()


def cleaning(text: str) -> str:
    """Menghapus HTML tag, URL, karakter non-huruf, dan spasi berlebih."""
    text = re.sub(r"<[^>]+>", " ", text)           # tag HTML
    text = re.sub(r"http\S+|www\.\S+", " ", text)  # URL
    text = re.sub(r"[^a-z\s]", " ", text)          # hanya huruf a-z dan spasi
    return re.sub(r"\s+", " ", text).strip()


def tokenizing(text: str) -> list[str]:
    """Pecah teks menjadi daftar kata (token)."""
    return text.split()


def stopword_removal(tokens: list[str]) -> list[str]:
    """Menghapus kata umum (stopword) dan token terlalu pendek (<= 2 karakter)."""
    return [t for t in tokens if t not in _stopwords and len(t) > 2]


@lru_cache(maxsize=10000)
def _stem_word(word: str) -> str:
    """Stemming satu kata menggunakan Sastrawi dengan caching."""
    return _stemmer.stem(word)


def stemming(tokens: list[str]) -> list[str]:
    """Mengubah setiap kata dalam token ke bentuk kata dasarnya."""
    return [_stem_word(t) for t in tokens]


def preprocess(text: str) -> list[str]:
    """Pipeline pra-proses teks lengkap: Case folding -> Cleaning -> Tokenizing -> Stopword removal -> Stemming."""
    text = case_folding(str(text))
    text = cleaning(text)
    tokens = tokenizing(text)
    tokens = stopword_removal(tokens)
    return stemming(tokens)


def preprocess_verbose(text: str) -> dict:
    """Mengembalikan hasil per tahapan pra-proses teks (untuk demo/laporan)."""
    t1 = case_folding(str(text))
    t2 = cleaning(t1)
    t3 = tokenizing(t2)
    t4 = stopword_removal(t3)
    t5 = stemming(t4)
    return {
        "case_folding": t1,
        "cleaning": t2,
        "tokenizing": t3,
        "stopword_removal": t4,
        "stemming": t5
    }
