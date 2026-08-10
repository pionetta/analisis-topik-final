import sqlite3
import json
import os

def create_svg_chart(k_data):
    if not k_data or len(k_data) < 2:
        return ""
    
    W = 600
    H = 200
    PL = 50
    PR = 20
    PT = 20
    PB = 40
    iW = W - PL - PR
    iH = H - PT - PB
    
    ks = [d['k'] for d in k_data]
    minK, maxK = min(ks), max(ks)
    
    def xPos(k2):
        return PL + ((k2 - minK) / (maxK - minK or 1)) * iW
    
    # Coherence line
    cohVals = [d['score'] for d in k_data]
    minCoh, maxCoh = min(cohVals), max(cohVals)
    def yC(v):
        return PT + iH - ((v - minCoh) / (maxCoh - minCoh or 1)) * iH
    
    cohPts = " ".join([f"{xPos(d['k']):.1f},{yC(d['score']):.1f}" for d in k_data])
    cohDots = "".join([
        f'<circle cx="{xPos(d["k"]):.1f}" cy="{yC(d["score"]):.1f}" r="4" fill="#2c3e50"/>'
        f'<text x="{xPos(d["k"]):.1f}" y="{yC(d["score"]) - 10:.1f}" text-anchor="middle" font-size="10" fill="#2c3e50">{d["score"]:.3f}</text>'
        for d in k_data
    ])
    
    # Perplexity line
    perpVals = [d['perplexity'] for d in k_data]
    minPerp, maxPerp = min(perpVals), max(perpVals)
    def yP(v):
        return PT + iH - ((v - minPerp) / (maxPerp - minPerp or 1)) * iH
    
    perpPts = " ".join([f"{xPos(d['k']):.1f},{yP(d['perplexity']):.1f}" for d in k_data])
    perpDots = "".join([
        f'<circle cx="{xPos(d["k"]):.1f}" cy="{yP(d["perplexity"]):.1f}" r="4" fill="#e74c3c"/>'
        f'<text x="{xPos(d["k"]):.1f}" y="{yP(d["perplexity"]) + 15:.1f}" text-anchor="middle" font-size="10" fill="#e74c3c">{d["perplexity"]:.1f}</text>'
        for d in k_data
    ])
    
    x_axis_labels = "".join([
        f'<text x="{xPos(k):.1f}" y="{H - 15}" text-anchor="middle" font-size="12" fill="#555">K={k}</text>'
        for k in ks
    ])
    
    return f"""
    <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 15px;">
        <div style="border:1px solid #ccc; border-radius: 8px; padding: 10px; background: #fff; flex: 1; min-width: 300px;">
            <h5 style="margin:0 0 10px 0; color: #2c3e50; text-align: center;">Coherence (C_V)</h5>
            <svg width="100%" height="100%" viewBox="0 0 {W} {H}" style="font-family:sans-serif;">
                <polyline points="{cohPts}" fill="none" stroke="#2c3e50" stroke-width="2"/>
                {cohDots}
                <line x1="{PL}" y1="{H - PB}" x2="{W - PR}" y2="{H - PB}" stroke="#ccc" stroke-width="1"/>
                {x_axis_labels}
            </svg>
        </div>
        <div style="border:1px solid #ccc; border-radius: 8px; padding: 10px; background: #fff; flex: 1; min-width: 300px;">
            <h5 style="margin:0 0 10px 0; color: #e74c3c; text-align: center;">Perplexity</h5>
            <svg width="100%" height="100%" viewBox="0 0 {W} {H}" style="font-family:sans-serif;">
                <polyline points="{perpPts}" fill="none" stroke="#e74c3c" stroke-width="2"/>
                {perpDots}
                <line x1="{PL}" y1="{H - PB}" x2="{W - PR}" y2="{H - PB}" stroke="#ccc" stroke-width="1"/>
                {x_axis_labels}
            </svg>
        </div>
    </div>
    """

def get_table_html(k_results, best_k):
    if not k_results:
        return "<p>Tidak ada data.</p>"
    
    html = '<table><thead><tr><th>K</th><th>Coherence</th><th>Perplexity</th></tr></thead><tbody>'
    for kr in sorted(k_results, key=lambda x: x['k']):
        is_best = ' <span class="badge">Optimal</span>' if kr['k'] == best_k else ''
        html += f'<tr><td>{kr["k"]}{is_best}</td><td>{kr["score"]:.4f}</td><td>{kr["perplexity"]:.4f}</td></tr>'
    html += '</tbody></table>'
    return html

def get_topics_html(best_model):
    if not best_model:
        return "<p>Tidak ada model.</p>"
        
    topics = best_model.get('topics', {})
    interps = best_model.get('interpretations', {})
    
    html = '<div class="topic-grid">'
    for t_name, t_data in topics.items():
        lbl = interps.get(t_name, {}).get('custom_label') or t_data.get('auto_label') or t_name
        words = t_data.get('words', [])[:7]
        words_html = "".join([f'<tr><td>{w["word"]}</td><td style="text-align:right;">{w["weight"]:.3f}</td></tr>' for w in words])
        
        html += f'''
        <div class="topic-card">
            <h4>{t_name}: {lbl}</h4>
            <table>
                <thead><tr><th>Kata Kunci</th><th style="text-align:right">Bobot</th></tr></thead>
                <tbody>{words_html}</tbody>
            </table>
        </div>
        '''
    html += '</div>'
    return html

def export_all_to_html():
    db_path = 'backend/database.db'
    if not os.path.exists(db_path):
        print("Database tidak ditemukan!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id_title, result_data FROM movie_analysis')
    rows = cursor.fetchall()
    
    # Kelompokkan berdasarkan Judul -> Mode -> K
    movies = {}
    for row in rows:
        db_key = row[0]
        data = json.loads(row[1])
        title = data.get('title', 'Unknown').replace('_', ' ')
        mode = data.get('ngram_mode', 'bigram')
        
        if title not in movies:
            movies[title] = {}
        if mode not in movies[title]:
            movies[title][mode] = []
            
        movies[title][mode].append(data)
        
    html = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Laporan Hasil Analisis Topik (LDA) Keseluruhan</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; color: #333; margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h1 { text-align: center; color: #2c3e50; margin-bottom: 5px; }
            h2 { color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 5px; margin-top: 40px; }
            h3 { color: #e67e22; margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; color: #333; }
            .topic-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin-top: 15px; }
            .topic-card { background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 15px; }
            .topic-card h4 { margin: 0 0 10px 0; color: #2c3e50; font-size: 14px; }
            .badge { display: inline-block; padding: 3px 8px; background: #2ecc71; color: white; border-radius: 12px; font-size: 11px; font-weight: bold; }
            .print-btn { display: block; width: 200px; margin: 20px auto; padding: 12px; background: #2980b9; color: #fff; text-align: center; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
            .section-header { background: #2c3e50; color: #fff; padding: 10px; border-radius: 4px; margin-top: 30px; margin-bottom: 15px; }
            .mode-header { text-align: center; color: #2980b9; font-weight: bold; margin-bottom: 10px; font-size: 16px; }
            @media print {
                .print-btn { display: none; }
                body { background: #fff; }
                .container { box-shadow: none; padding: 0; }
                .page-break { page-break-before: always; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Laporan Hasil Analisis Topik (LDA) Keseluruhan</h1>
            <p style="text-align: center; color: #7f8c8d;">Dokumen ini memuat seluruh evaluasi Coherence, Perplexity, dan Interpretasi Topik Optimal.</p>
            <button class="print-btn" onclick="window.print()">Simpan sebagai PDF</button>
    """
    
    for title, modes in sorted(movies.items()):
        html += f'<div class="page-break"></div>'
        html += f'<h2 style="text-align: center; font-size: 24px; margin-bottom: 20px;">Dataset: {title}</h2>'
        
        mode_data = {}
        for mode in ['unigram', 'bigram']:
            if mode not in modes or not modes[mode]:
                mode_data[mode] = None
                continue
            
            models = modes[mode]
            k_results_all = models[0].get('optimal_k_results', [])
            k_results = [r for r in k_results_all if r.get('mode') == mode]
            
            if k_results:
                best_k_data = max(k_results, key=lambda x: x['score'])
                best_k = best_k_data['k']
            else:
                best_k = max(models, key=lambda x: x.get('coherence_score', 0)).get('num_topics')
                
            best_model = next((m for m in models if m.get('num_topics') == best_k), models[0])
            mode_data[mode] = {
                'k_results': k_results,
                'best_k': best_k,
                'best_model': best_model
            }
            
        # SECTION 1: TABEL EVALUASI
        html += '<h3 class="section-header">1. Tabel Evaluasi (Coherence & Perplexity)</h3>'
        html += '<div style="display: flex; gap: 20px; margin-bottom: 20px;">'
        for mode in ['unigram', 'bigram']:
            html += '<div style="flex: 1;">'
            html += f'<div class="mode-header">Mode: {mode.upper()}</div>'
            if mode_data.get(mode):
                html += get_table_html(mode_data[mode]['k_results'], mode_data[mode]['best_k'])
            else:
                html += '<p style="text-align: center; color: #999;">Data tidak tersedia</p>'
            html += '</div>'
        html += '</div>'
        
        # SECTION 2: GRAFIK EVALUASI
        html += '<h3 class="section-header">2. Grafik Evaluasi K</h3>'
        for mode in ['unigram', 'bigram']:
            html += '<div style="margin-bottom: 30px;">'
            html += f'<div class="mode-header" style="text-align: left;">Mode: {mode.upper()}</div>'
            if mode_data.get(mode):
                html += create_svg_chart(mode_data[mode]['k_results'])
            else:
                html += '<p style="color: #999;">Data tidak tersedia</p>'
            html += '</div>'
            
        # SECTION 3: INTERPRETASI TOPIK
        html += '<h3 class="section-header">3. Interpretasi Topik Optimal</h3>'
        for mode in ['unigram', 'bigram']:
            html += '<div style="margin-bottom: 30px;">'
            if mode_data.get(mode):
                best_k = mode_data[mode]['best_k']
                html += f'<div class="mode-header" style="text-align: left;">Mode: {mode.upper()} (Optimal K={best_k})</div>'
                html += get_topics_html(mode_data[mode]['best_model'])
            else:
                html += f'<div class="mode-header" style="text-align: left;">Mode: {mode.upper()}</div>'
                html += '<p style="color: #999;">Data tidak tersedia</p>'
            html += '</div>'
            
    html += """
        </div>
    </body>
    </html>
    """
    
    with open('Laporan_Analisis_Lengkap.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Berhasil mengekspor Laporan_Analisis_Lengkap.html")

if __name__ == '__main__':
    export_all_to_html()
