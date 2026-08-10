"""
Script batch analisis semua dataset via API Flask lokal.
Menjalankan: upload → preprocess → find_optimal_k → analyze
untuk setiap dataset CSV di folder uploads/.
"""
import os
import sys
import json
import time
import requests

BASE_URL = "http://localhost:5000"
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")

DATASETS = [
    "Avengers_Endgame_2019.csv",
    "The_Dark_Knight_2008.csv",
    "Interstellar_2014.csv",
    "Parasite_2019.csv",
    "Coco_2017.csv",
    "Toy_Story_1995.csv",
    "WALL-E_2008.csv",
    "Your_Name_2016.csv",
    "Spider-Man_Into_the_Spider-Verse_2018.csv",
    "The_Lord_of_the_Rings_The_Return_of_the_King_2003.csv",
]

COLUMN_NAME = "review_text"  # kolom teks ulasan

def wait_for_flask(max_retries=15):
    """Tunggu Flask siap."""
    for i in range(max_retries):
        try:
            r = requests.get(f"{BASE_URL}/saved_movies", timeout=3)
            if r.status_code == 200:
                print("✅ Flask siap")
                return True
        except Exception:
            pass
        print(f"  ⏳ Menunggu Flask... ({i+1}/{max_retries})")
        time.sleep(2)
    return False

def get_title_from_filename(fname):
    return fname.replace(".csv", "")

def upload_and_preprocess(csv_path, title):
    """Upload file dan jalankan preprocessing."""
    fname = os.path.basename(csv_path)
    
    # Upload
    with open(csv_path, "rb") as f:
        r = requests.post(f"{BASE_URL}/upload", files={"file": (fname, f, "text/csv")}, timeout=60)
    if r.status_code != 200:
        raise Exception(f"Upload gagal: {r.text}")
    
    # Preprocess
    r = requests.post(f"{BASE_URL}/preprocess",
                      json={"filename": fname, "column": COLUMN_NAME, "title": title},
                      timeout=120)
    if r.status_code != 200:
        raise Exception(f"Preprocess gagal: {r.text}")
    
    return fname

def find_optimal_k(filename, title):
    """Cari K optimal (min=2, max=10)."""
    r = requests.post(f"{BASE_URL}/find_optimal_k",
                      json={"filename": filename, "title": title, "min_k": 2, "max_k": 10},
                      timeout=30)
    if r.status_code != 200:
        raise Exception(f"find_optimal_k gagal: {r.text}")
    
    task_id = r.json().get("task_id")
    print(f"    📊 Task ID: {task_id}")
    
    # Poll status task
    for attempt in range(120):  # max 4 menit
        time.sleep(2)
        r2 = requests.get(f"{BASE_URL}/task_status/{task_id}", timeout=10)
        if r2.status_code != 200:
            continue
        task = r2.json().get("data", {})
        status = task.get("status")
        progress = task.get("progress", 0)
        total = task.get("total", 1)
        k_now = task.get("current_k", "?")
        mode = task.get("current_mode", "?")
        print(f"    ⏳ [{progress}/{total}] K={k_now} mode={mode} status={status}", end="\r")
        
        if status == "done":
            print(f"\n    ✅ find_optimal_k selesai")
            return task.get("results", [])
        elif status == "error":
            raise Exception(f"Task error: {task.get('message')}")
    
    raise Exception("Timeout menunggu find_optimal_k")

def run_analyze(filename, title, optimal_k_results):
    """Jalankan analisis LDA dengan K dan mode terbaik."""
    # Pilih K & mode dari hasil optimal berdasarkan coherence tertinggi
    if optimal_k_results:
        best = max(optimal_k_results, key=lambda x: x.get("score", 0))
        k = best.get("k", 3)
        mode = best.get("mode", "bigram")
    else:
        k = 3
        mode = "bigram"
    
    print(f"    🎯 Analisis dengan K={k}, mode={mode}")
    
    r = requests.post(f"{BASE_URL}/analyze",
                      json={
                          "filename": filename,
                          "title": title,
                          "num_topics": k,
                          "mode": mode,
                          "optimal_k_results": optimal_k_results
                      },
                      timeout=180)
    if r.status_code != 200:
        raise Exception(f"Analyze gagal: {r.text}")
    
    data = r.json().get("data", {})
    topics = data.get("topics", {})
    print(f"    ✅ Berhasil! {len(topics)} topik ditemukan")
    
    for topic_name, topic_data in topics.items():
        label = topic_data.get("auto_label", "?")
        print(f"       {topic_name}: {label}")
    
    return data

def main():
    print("=" * 60)
    print("BATCH ANALISIS SEMUA DATASET")
    print("=" * 60)
    
    if not wait_for_flask():
        print("❌ Flask tidak merespons. Pastikan server berjalan.")
        sys.exit(1)
    
    results_summary = []
    
    for i, csv_fname in enumerate(DATASETS, 1):
        csv_path = os.path.join(UPLOADS_DIR, csv_fname)
        
        # Cek file ada (dengan prefix temp_ jika perlu)
        if not os.path.exists(csv_path):
            temp_path = os.path.join(UPLOADS_DIR, "temp_" + csv_fname)
            if os.path.exists(temp_path):
                csv_path = temp_path
                csv_fname = "temp_" + csv_fname
            else:
                print(f"\n[{i}/10] ⚠️  SKIP: {csv_fname} tidak ditemukan")
                continue
        
        title = get_title_from_filename(csv_fname.replace("temp_", ""))
        print(f"\n[{i}/10] 🎬 {title}")
        print(f"         File: {csv_fname}")
        
        try:
            # 1. Upload & Preprocess
            print("    📤 Upload & Preprocessing...")
            fname = upload_and_preprocess(csv_path, title)
            
            # 2. Find Optimal K
            print("    🔍 Mencari K optimal (K=2..10)...")
            optimal_results = find_optimal_k(fname, title)
            
            # 3. Analyze
            data = run_analyze(fname, title, optimal_results)
            
            results_summary.append({
                "title": title,
                "status": "SUCCESS",
                "topics": len(data.get("topics", {}))
            })
        except Exception as e:
            print(f"\n    ❌ ERROR: {e}")
            results_summary.append({
                "title": title,
                "status": "FAILED",
                "error": str(e)
            })
    
    # Ringkasan akhir
    print("\n" + "=" * 60)
    print("RINGKASAN HASIL BATCH ANALISIS")
    print("=" * 60)
    for r in results_summary:
        icon = "✅" if r["status"] == "SUCCESS" else "❌"
        if r["status"] == "SUCCESS":
            print(f"  {icon} {r['title']} — {r['topics']} topik")
        else:
            print(f"  {icon} {r['title']} — {r.get('error', '?')}")
    
    success = sum(1 for r in results_summary if r["status"] == "SUCCESS")
    print(f"\n  Total: {success}/{len(results_summary)} berhasil")

if __name__ == "__main__":
    main()
