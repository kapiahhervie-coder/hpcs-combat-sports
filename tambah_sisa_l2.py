path = r'combat\templates\combat\l2_strenght.html'

with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Hapus baris rusak di akhir
bad_ending = '''                            <div class="col-6">
                                <div class="input-group input-group-sm">
                                    }'''

SISA_HTML = '''                            <div class="col-6">
                                <div class="input-group input-group-sm">
                                    <input type="number" name="score_push" id="score_push" type="hidden" style="display:none">
                                    <span class="input-group-text" id="badge_push_display" style="color:#10b981;font-weight:700;">—</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Pull -->
                    <div class="pilar-card">
                        <div class="pilar-label">
                            <i class="bi bi-arrow-down-circle-fill me-1 icon-pull"></i>
                            Pull — Weighted Pull Up
                        </div>
                        <div class="row g-2">
                            <div class="col-6">
                                <div class="input-group input-group-sm">
                                    <input type="number" name="pull_reps" id="pull_reps"
                                           class="form-control" placeholder="Reps" oninput="liveUpdate()">
                                    <span class="input-group-text">reps</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <input type="hidden" name="score_pull" id="score_pull">
                            </div>
                        </div>
                    </div>

                    <!-- Core -->
                    <div class="pilar-card">
                        <div class="pilar-label">
                            <i class="bi bi-shield-fill me-1 icon-core"></i>
                            Core — Weighted Plank
                        </div>
                        <div class="row g-2">
                            <div class="col-6">
                                <div class="input-group input-group-sm">
                                    <input type="number" name="core_durasi_detik" id="core_durasi"
                                           class="form-control" placeholder="Detik" oninput="liveUpdate()">
                                    <span class="input-group-text">dtk</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <input type="hidden" name="score_core" id="score_core">
                            </div>
                        </div>
                    </div>

                    <!-- Isometric -->
                    <div class="pilar-card">
                        <div class="pilar-label">
                            <i class="bi bi-lightning-fill me-1 icon-iso"></i>
                            Isometric — Split Squat Hold
                        </div>
                        <div class="row g-2">
                            <div class="col-6">
                                <div class="input-group input-group-sm">
                                    <input type="number" name="iso_durasi_detik" id="iso_durasi"
                                           class="form-control" placeholder="Total hold" oninput="liveUpdate()">
                                    <span class="input-group-text">dtk</span>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="input-group input-group-sm">
                                    <input type="number" name="iso_tremor_onset_detik" id="iso_tremor"
                                           class="form-control" placeholder="Tremor onset" oninput="liveUpdate()">
                                    <span class="input-group-text">dtk</span>
                                </div>
                            </div>
                        </div>
                        <input type="hidden" name="score_isometric" id="score_iso">
                    </div>

                    <!-- Hidden AI fields -->
                    <input type="hidden" name="ai_rep_count_lower" id="ai_rep_lower">
                    <input type="hidden" name="ai_rep_count_push" id="ai_rep_push">
                    <input type="hidden" name="ai_rep_count_pull" id="ai_rep_pull">
                    <input type="hidden" name="ai_confidence_score" id="ai_confidence">
                    <input type="hidden" name="catatan" id="catatan_hidden">

                </div><!-- /card-hpcs -->
            </div><!-- /col-lg-4 kiri -->

            <!-- ── KOLOM TENGAH: Radar ── -->
            <div class="col-lg-4">
                <div class="card-hpcs text-center">
                    <span class="section-label"><i class="bi bi-radar"></i>Strength Distribution Radar</span>
                    <div style="height:320px;display:flex;align-items:center;justify-content:center;margin:8px 0;">
                        <canvas id="radarChart"></canvas>
                    </div>
                    <div class="d-flex justify-content-center gap-2 flex-wrap mt-2" style="font-size:10px;">
                        <span id="badge_lower" class="score-pill">Lower: —</span>
                        <span id="badge_push"  class="score-pill">Push: —</span>
                        <span id="badge_pull"  class="score-pill">Pull: —</span>
                        <span id="badge_core"  class="score-pill">Core: —</span>
                        <span id="badge_iso"   class="score-pill">Iso: —</span>
                    </div>

                    <!-- Profil Kondisi Atlet -->
                    <div id="narasi_panel" class="mt-3 text-start" style="display:none">
                        <div class="section-label"><i class="bi bi-person-lines-fill"></i>Profil Kondisi Atlet</div>
                        <div id="narasi_box" style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.7;color:#cbd5e1;max-height:320px;overflow-y:auto;text-align:left;"></div>
                    </div>
                </div>
            </div>

            <!-- ── KOLOM KANAN: Result ── -->
            <div class="col-lg-4">
                <div class="card-hpcs sticky-panel text-center">
                    <span class="section-label"><i class="bi bi-trophy-fill"></i>Audit Result</span>
                    <div class="total-score" id="res_total">0.0</div>
                    <div class="mt-2 mb-3">
                        <span class="predikat-badge" id="res_predikat">Novice</span>
                    </div>
                    <button type="submit" class="btn btn-hpcs-primary w-100 mb-2">
                        <i class="bi bi-save2-fill me-1"></i>SIMPAN DATA L2
                    </button>
                    <button type="button" class="btn btn-outline-secondary w-100 btn-sm" onclick="handlePrint()">
                        <i class="bi bi-printer-fill me-1"></i>Cetak PDF (Browser)
                    </button>

                    <div id="reko_panel" class="mt-3 text-start" style="display:none">
                        <div class="section-label"><i class="bi bi-lightbulb-fill" style="color:#10b981"></i>Rekomendasi HPCS</div>
                        <div id="reko_list"></div>
                    </div>

                    <!-- CNS Status -->
                    <div id="cns_panel" class="mt-3" style="display:none">
                        <div class="section-label"><i class="bi bi-activity"></i>CNS Tremor Analysis</div>
                        <div id="cns_box" style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.2);border-radius:8px;padding:10px;font-size:11px;color:#cbd5e1;text-align:left;"></div>
                    </div>
                </div>
            </div>

        </div><!-- /row -->
    </form>

    <!-- ── HISTORY TABLE ── -->
    <div class="history-wrap no-print mt-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="mb-0" style="color:#10b981;font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;">
                <i class="bi bi-clock-history me-1"></i>History Audit L2 — Strength
            </h6>
            <span class="badge" style="background:rgba(16,185,129,0.2);color:#10b981;">{{ history|length }} Record</span>
        </div>

        {% if history %}
        <div class="table-responsive">
            <table class="table tbl table-hover align-middle mb-0">
                <thead>
                    <tr>
                        <th>#</th><th>Tanggal</th><th>Atlet</th><th>Kategori</th>
                        <th>Gender</th><th>BB</th>
                        <th>Lower</th><th>Push</th><th>Pull</th><th>Core</th><th>Iso</th>
                        <th>Tremor</th><th>Total</th><th>Predikat</th><th>Aksi</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in history %}
                    <tr>
                        <td class="text-white-50">{{ forloop.counter }}</td>
                        <td class="text-white-50" style="font-size:0.75rem;white-space:nowrap;">{{ item.timestamp|date:"d/m/Y H:i" }}</td>
                        <td class="fw-bold">{{ item.atlet_name }}</td>
                        <td>{{ item.kategori_usia }}</td>
                        <td>{{ item.gender }}</td>
                        <td>{{ item.kelas_berat|default:"—" }} kg</td>
                        <td><span class="score-pill">{{ item.score_lower }}</span></td>
                        <td><span class="score-pill">{{ item.score_push }}</span></td>
                        <td><span class="score-pill">{{ item.score_pull }}</span></td>
                        <td><span class="score-pill">{{ item.score_core }}</span></td>
                        <td><span class="score-pill">{{ item.score_isometric }}</span></td>
                        <td>
                            {% if item.iso_tremor_rasio %}
                                <span class="tremor-pill">{{ item.iso_tremor_rasio }}%</span>
                            {% else %}<span class="text-white-50">—</span>{% endif %}
                        </td>
                        <td><strong style="color:#10b981;font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;">{{ item.total_skor }}</strong></td>
                        <td><span class="predikat-badge" style="font-size:0.7rem;padding:2px 8px;">{{ item.predikat }}</span></td>
                        <td class="text-center">
                            <button class="btn btn-sm btn-outline-danger py-0 px-2"
                                    onclick="if(confirm('Hapus data {{ item.atlet_name }}?')) window.location='/combat/l2-strength/hapus/{{ item.pk }}/'">
                                <i class="bi bi-trash3-fill"></i>
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="text-center py-5" style="color:#4b5563;">
            <i class="bi bi-inbox fs-2 d-block mb-2"></i>Belum ada data. Simpan audit pertama.
        </div>
        {% endif %}
    </div>

</div><!-- /container -->

<script>
// ── Auto Scoring ──────────────────────────────────────────
function calcScoreLower(beban, bb) {
    if (!beban || !bb || bb <= 0) return 0;
    var r = beban / bb;
    if (r >= 1.5) return 9.5; if (r >= 1.25) return 8.5;
    if (r >= 1.0) return 7.5; if (r >= 0.75) return 6.0;
    if (r >= 0.6) return 5.0; return 3.0;
}
function calcScorePush(reps) {
    if (!reps) return 0;
    if (reps > 12) return 9.5; if (reps >= 10) return 8.5;
    if (reps >= 6) return 7.0; if (reps >= 3) return 5.5; return 3.0;
}
function calcScorePull(reps) {
    if (!reps) return 0;
    if (reps > 15) return 9.5; if (reps >= 12) return 8.5;
    if (reps >= 8) return 7.0; if (reps >= 4) return 5.5; return 3.0;
}
function calcScoreCore(d) {
    if (!d) return 0;
    if (d > 90) return 9.5; if (d >= 75) return 8.5;
    if (d >= 60) return 7.0; if (d >= 30) return 5.5; return 3.0;
}
function calcScoreIso(d) {
    if (!d) return 0;
    if (d > 60) return 9.5; if (d >= 50) return 8.5;
    if (d >= 40) return 7.0; if (d >= 20) return 5.5; return 3.0;
}

function g(id) { return parseFloat(document.getElementById(id).value) || 0; }

function autoCalcScores() {
    var bb = g('h_berat') || g('input_berat') || 70;
    var sL = calcScoreLower(g('lower_5rm_beban'), bb);
    var sP = calcScorePush(g('push_5rm_beban'));
    var sPl = calcScorePull(g('pull_reps'));
    var sC = calcScoreCore(g('core_durasi'));
    var sI = calcScoreIso(g('iso_durasi'));
    document.getElementById('score_lower').value = sL.toFixed(1);
    document.getElementById('score_push').value  = sP.toFixed(1);
    document.getElementById('score_pull').value  = sPl.toFixed(1);
    document.getElementById('score_core').value  = sC.toFixed(1);
    document.getElementById('score_iso').value   = sI.toFixed(1);
    function badge(id, val) {
        var el = document.getElementById(id);
        if (!el) return;
        el.textContent = id.replace('badge_','').charAt(0).toUpperCase()+id.replace('badge_','').slice(1)+': '+val.toFixed(1);
        el.style.color = val>=9?'#10b981':val>=7?'#38bdf8':val>=5?'#f59e0b':'#f87171';
    }
    badge('badge_lower',sL); badge('badge_push',sP);
    badge('badge_pull',sPl); badge('badge_core',sC); badge('badge_iso',sI);
    return [sL, sP, sPl, sC, sI];
}

function calcBWRatio() {
    var bb = g('h_berat') || 70;
    var beban = g('lower_5rm_beban');
    var ratio = bb > 0 && beban > 0 ? (beban/bb).toFixed(2) : '—';
    var el = document.getElementById('bw_ratio_display');
    if (el) el.value = ratio;
}

var radarInst = null;
function updateRadar(vals) {
    var ctx = document.getElementById('radarChart').getContext('2d');
    if (radarInst) radarInst.destroy();
    radarInst = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Lower','Push','Pull','Core','Iso'],
            datasets: [{
                label: 'Atlet', data: vals, fill: true,
                backgroundColor: 'rgba(16,185,129,0.12)',
                borderColor: '#10b981', borderWidth: 2,
                pointBackgroundColor: '#10b981', pointRadius: 4
            },{
                label: 'Elite', data: [9,9,9,9,9], fill: false,
                borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1,
                borderDash: [4,4], pointRadius: 2,
                pointBackgroundColor: 'rgba(255,255,255,0.1)'
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { r: {
                min: 0, max: 10,
                ticks: { stepSize: 2, color: 'rgba(255,255,255,0.2)', font: { size: 9 }, backdropColor: 'transparent' },
                grid: { color: 'rgba(255,255,255,0.06)' },
                pointLabels: { color: 'rgba(255,255,255,0.5)', font: { size: 10 } }
            }}
        }
    });
}
updateRadar([0,0,0,0,0]);

function liveUpdate() {
    calcBWRatio();
    var scores = autoCalcScores();
    var filled = scores.filter(function(s){ return s > 0; });
    var total = filled.length ? parseFloat((filled.reduce(function(a,b){return a+b;},0)/filled.length).toFixed(1)) : 0;
    document.getElementById('res_total').textContent = total.toFixed(1);
    var pred, col;
    if (total >= 9.0) { pred='ELITE'; col='#10b981'; }
    else if (total >= 7.5) { pred='READY'; col='#38bdf8'; }
    else if (total >= 5.5) { pred='DEVELOPING'; col='#f59e0b'; }
    else { pred='NOVICE'; col='#f87171'; }
    var predEl = document.getElementById('res_predikat');
    predEl.textContent = pred;
    document.getElementById('res_total').style.color = col;
    updateRadar(scores);
    generateNarasiL2(scores, total, pred);
}

function generateNarasiL2(scores, total, pred) {
    var panel = document.getElementById('narasi_panel');
    var box = document.getElementById('narasi_box');
    var filled = scores.filter(function(s){ return s > 0; });
    if (!filled.length) { panel.style.display='none'; return; }
    var namaEl = document.querySelector('select#select_atlet option:checked');
    var nama = namaEl ? (namaEl.getAttribute('data-nama') || namaEl.text) : 'Atlet';
    function wrn(v){ return v>=9?'#10b981':v>=7?'#38bdf8':v>=5?'#f59e0b':'#f87171'; }
    function lbl(v){ return v>=9?'sangat baik':v>=7?'baik':v>=5?'cukup':'perlu perhatian'; }
    var pilarNames = ['Lower','Push','Pull','Core','Iso'];
    var pilarData = pilarNames.map(function(n,i){ return {nama:n, val:scores[i]||0}; }).filter(function(p){return p.val>0;});
    var sorted = pilarData.slice().sort(function(a,b){return b.val-a.val;});
    var kuat = sorted.slice(0,2);
    var lemah = sorted.slice(-2).reverse();
    var layak = total >= 7.5;
    var min = Math.min.apply(null, pilarData.map(function(p){return p.val;}));
    var max = Math.max.apply(null, pilarData.map(function(p){return p.val;}));
    var prima = (max-min) <= 0.5 && min >= 8.5;
    var kPred = {
        ELITE: 'menunjukkan kapasitas kekuatan <strong style="color:#10b981">ELIT</strong> — siap program kompetisi.',
        READY: 'berada di level <strong style="color:#38bdf8">SIAP (READY)</strong> — kekuatan solid, siap naik ke L3 Power.',
        DEVELOPING: 'sedang <strong style="color:#f59e0b">BERKEMBANG</strong> — fondasi kekuatan mulai terbentuk.',
        NOVICE: 'di level <strong style="color:#f87171">PEMULA</strong> — perlu program kekuatan dasar 6-8 minggu.'
    };
    var layakStr = layak
        ? '<span style="color:#10b981;font-weight:700">&#9989; LAYAK naik ke L3 Power Assessment</span>'
        : '<span style="color:#f87171;font-weight:700">&#9940; BELUM LAYAK ke L3 — lanjutkan program L2 Strength</span>';
    var lemahHTML = prima
        ? '<div style="padding:8px 10px;background:rgba(16,185,129,0.07);border-radius:6px;border:1px solid rgba(16,185,129,0.2);"><span style="color:#10b981;font-weight:600;">&#127942; Semua pilar kekuatan dalam kondisi prima!</span></div>'
        : lemah.map(function(p){
            return '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
                +'<div style="width:6px;height:6px;border-radius:50%;background:'+wrn(p.val)+';flex-shrink:0;"></div>'
                +'<span><strong style="color:'+wrn(p.val)+'">'+p.nama+'</strong> — '+lbl(p.val)
                +' <span style="color:'+wrn(p.val)+';font-weight:700;">('+p.val.toFixed(1)+'/10)</span>'
                +(p.val<5.5?' : prioritas program korektif.':' : perlu peningkatan.')+'</span></div>';
        }).join('');
    box.innerHTML = '<div style="margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid rgba(16,185,129,0.1);">'
        +'<span style="color:#10b981;font-weight:700;font-size:12px;">&#128170; '+nama+'</span> '+(kPred[pred]||'')
        +' Total skor: <strong style="font-size:13px;color:'+wrn(total)+'">'+total.toFixed(1)+'/10</strong></div>'
        +'<div style="margin-bottom:10px;"><div style="color:#6b7280;font-size:10px;margin-bottom:5px;letter-spacing:1px;">&#9650; KEUNGGULAN</div>'
        +kuat.map(function(p){return '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><div style="width:6px;height:6px;border-radius:50%;background:#10b981;flex-shrink:0;"></div><span><strong style="color:#10b981">'+p.nama+'</strong> — '+lbl(p.val)+' <span style="color:'+wrn(p.val)+';font-weight:700;">('+p.val.toFixed(1)+'/10)</span></span></div>';}).join('')+'</div>'
        +'<div style="margin-bottom:10px;"><div style="color:#6b7280;font-size:10px;margin-bottom:5px;letter-spacing:1px;">&#9660; AREA KELEMAHAN</div>'+lemahHTML+'</div>'
        +'<div style="padding:10px 12px;border-radius:8px;background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.07);">'
        +'<div style="color:#6b7280;font-size:10px;margin-bottom:6px;letter-spacing:1px;">&#128203; KESIMPULAN</div>'
        +layakStr+'<br><span style="color:#9ca3af;font-size:10.5px;">'
        +(prima?'Pertahankan semua pilar. Atlet siap L3 Power.':layak?'Fokus perkuat <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong> selama transisi ke L3.':'Lanjutkan L2 minimal 6 minggu, prioritas <strong>'+(lemah[0]?lemah[0].nama:'-')+'</strong>.')
        +'</span></div>';
    panel.style.display = 'block';
}

function onAtletChange(sel) {
    var opt = sel.options[sel.selectedIndex];
    document.getElementById('input_atlet_id').value = sel.value;
    document.getElementById('input_nama').value = opt.getAttribute('data-nama') || opt.text.trim();
    var kat = opt.getAttribute('data-kategori') || 'Elite';
    var gen = opt.getAttribute('data-gender') || 'Putra';
    var brt = opt.getAttribute('data-berat') || '';
    var hKat = document.getElementById('h_kategori');
    var hGen = document.getElementById('h_gender');
    var hBrt = document.getElementById('h_berat');
    if (hKat) hKat.value = kat;
    if (hGen) hGen.value = gen;
    if (hBrt) hBrt.value = brt;
    liveUpdate();
}

function handlePrint() {
    window.print();
}
function toggleRubrik() {
    var rp = document.getElementById('rubrikPanel');
    rp.style.display = rp.style.display === 'none' ? 'block' : 'none';
}
function syncPrint() {}
</script>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</body>
</html>'''

if bad_ending in c:
    c = c.replace(bad_ending, SISA_HTML)
    print('OK: sisa HTML berhasil ditambahkan')
else:
    # Potong di akhir yang rusak dan tambah sisa
    idx = c.find('                            <div class="col-6">\n                                <div class="input-group input-group-sm">\n                                    }')
    if idx > 0:
        c = c[:idx] + SISA_HTML
        print('OK (alt): sisa HTML berhasil ditambahkan')
    else:
        # Potong dari baris terakhir yang valid
        last_good = c.rfind('<div class="pilar-card">')
        if last_good > 0:
            c = c[:last_good] + SISA_HTML
            print('OK (last): rebuild dari pilar-card terakhir')
        else:
            print('ERROR: tidak bisa menemukan titik potong')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('DONE - total baris:', len(c.split('\n')))
