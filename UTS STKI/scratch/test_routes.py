import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app

def test_routes():
    client = app.test_client()
    
    print("Testing GET / ...")
    r_index = client.get("/")
    assert r_index.status_code == 200
    assert b"Mesin Pencari VSM" in r_index.data
    assert b"0" in r_index.data
    print("GET / OK!")

    print("Testing GET /search?q=pendidikan ...")
    r_search = client.get("/search?q=pendidikan")
    assert r_search.status_code == 200
    assert b"Tidak ada dokumen yang cocok" in r_search.data
    print("GET /search OK!")

    print("Testing GET /doc/0 (harus 404 karena belum ada dokumen) ...")
    r_doc = client.get("/doc/0")
    assert r_doc.status_code == 404
    print("GET /doc/0 OK!")

    print("Testing GET /preprocess?text=pemerintah+menaikkan+harga ...")
    r_prep = client.get("/preprocess?text=pemerintah+menaikkan+harga")
    assert r_prep.status_code == 200
    assert b"Case Folding" in r_prep.data
    print("GET /preprocess OK!")

    print("\nALL ROUTES TESTED SUCCESSFULLY WITH 200 OK!")

if __name__ == "__main__":
    test_routes()
