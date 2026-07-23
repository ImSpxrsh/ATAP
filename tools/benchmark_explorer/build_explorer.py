"""
build_explorer.py — issue #49: generate the offline interactive benchmark explorer.

The interactive object IS the finding: *most candidate axes do not survive scrutiny.* This
computes, for each candidate axis, its effect size against each BH3-mimetic, a permutation
"sham null band", the spread across specifications (drug x metric), and the inter-axis
correlation matrix — then writes a SINGLE self-contained `index.html` (data embedded inline,
no network, no external libs) that runs offline at a poster.

It presents NO individual-level susceptibility prediction and makes NO clinical claim — it is a
methods explorer over aggregate axis behaviour.

Axes: composite, BCL2_alone, BCL2_minus_MCL1, MCL1_over_BCL2L1, monocytic_signature,
executioner_loss_score. Drugs: venetoclax, navitoclax (GDSC2), S63845 (PRISM 24Q2, if present).

Run: PYTHONPATH=src python tools/benchmark_explorer/build_explorer.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from atap import data, features, scoring  # noqa: E402

CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
SEED = CFG.get("seed", 20260710)
MONO = CFG["monocytic_markers"]
GDSC = ROOT / "data" / "raw" / "gdsc" / "GDSC2_fitted_dose_response.xlsx"
PRISM = ROOT / "data" / "raw" / "prism" / "Repurposing_Public_24Q2_Extended_Primary_Data_Matrix.csv"
FULL_EXPR = ROOT / "data" / "raw" / "depmap" / "OmicsExpressionProteinCodingGenesTPMLogp1.csv"
OUT_HTML = Path(__file__).resolve().parent / "index.html"


def _monocytic(model_ids):
    header = pd.read_csv(FULL_EXPR, nrows=0).columns
    idc = header[0]
    keep = {idc: idc}
    for c in header[1:]:
        if c.split(" (")[0] in MONO:
            keep[c] = c.split(" (")[0]
    df = pd.read_csv(FULL_EXPR, usecols=list(keep)).rename(columns=keep).set_index(idc)
    df = df.reindex(model_ids)
    z = (df - df.mean()) / df.std(ddof=0)
    return z.mean(axis=1)


def _null_band(x, y, n=1000):
    rng = np.random.default_rng(SEED)
    yv = np.asarray(y, float).copy()
    rs = []
    for _ in range(n):
        rng.shuffle(yv)
        rs.append(spearmanr(x, yv).statistic)
    return float(np.nanpercentile(rs, 2.5)), float(np.nanpercentile(rs, 97.5))


def _prism_s63845(idx):
    if not PRISM.exists():
        return None
    ix = pd.read_csv(PRISM, usecols=[0]); ix.columns = ["cid"]
    row = ix.index[ix.cid.str.contains("K91876515")]
    if len(row) == 0:
        return None
    r = int(row[0])
    mat = pd.read_csv(PRISM, skiprows=lambda i: i != 0 and (i - 1) != r).set_index("Unnamed: 0")
    return mat.T.iloc[:, 0].reindex(idx)


def main() -> None:
    co = data.load_depmap(heme_only=True)
    z = features.zscore_expression(co.expr)
    el = features.executioner_loss_score(co.expr, co.mutations)["executioner_loss_score"]
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    comp = scoring.SusceptibilityModel().score(blocks)["venetoclax_score"]

    axes = pd.DataFrame(index=co.expr.index)
    axes["composite"] = comp.values
    axes["BCL2_alone"] = z["BCL2"].values
    axes["BCL2_minus_MCL1"] = (z["BCL2"] - z["MCL1"]).values
    axes["MCL1_over_BCL2L1"] = (z["MCL1"] - z["BCL2L1"]).values
    axes["monocytic_signature"] = _monocytic(list(co.expr.index)).values
    axes["executioner_loss_score"] = el.values

    model = pd.read_csv(ROOT / "data" / "raw" / "depmap" / "Model.csv").set_index("ModelID")
    smid = model["SangerModelID"].reindex(co.expr.index)

    gdsc = pd.read_excel(GDSC)
    responses = {}
    for drug in ("Venetoclax", "Navitoclax"):
        d = gdsc[gdsc["DRUG_NAME"].astype(str).str.contains(drug, case=False, na=False)]
        for metric in ("LN_IC50", "AUC"):
            r = d.groupby("SANGER_MODEL_ID")[metric].median().reindex(smid.values)
            r.index = co.expr.index
            responses[f"{drug} {metric}"] = r
    s63 = _prism_s63845(co.expr.index)
    if s63 is not None:
        responses["S63845 viability"] = s63

    # per axis x spec: rho + null band
    axis_names = list(axes.columns)
    specs = list(responses.keys())
    effect = {a: {} for a in axis_names}
    for a in axis_names:
        for s in specs:
            sub = pd.concat([axes[a], responses[s].rename("r")], axis=1).dropna()
            if len(sub) < 20:
                continue
            rho = float(spearmanr(sub[a], sub["r"]).statistic)
            lo, hi = _null_band(sub[a].values, sub["r"].values)
            effect[a][s] = dict(rho=round(rho, 3), n=int(len(sub)),
                                null_lo=round(lo, 3), null_hi=round(hi, 3),
                                survives=bool(abs(rho) > max(abs(lo), abs(hi))))

    # inter-axis correlation (Spearman) on shared lines
    corr = axes.corr(method="spearman").round(2)
    payload = dict(
        axes=axis_names, specs=specs, effect=effect,
        corr={a: {b: float(corr.loc[a, b]) for b in axis_names} for a in axis_names},
        meta=dict(seed=SEED, cohort="DepMap heme x GDSC2 (+PRISM S63845)",
                  note="Aggregate axis behaviour only. No individual prediction. No clinical claim."),
    )
    OUT_HTML.write_text(_html(payload))
    print(f"Wrote {OUT_HTML} ({OUT_HTML.stat().st_size/1024:.0f} KB, self-contained).")
    # quick console summary of the finding
    print("\nAxis survival vs sham null (how many specs each axis clears):")
    for a in axis_names:
        surv = sum(v["survives"] for v in effect[a].values())
        print(f"  {a:24s} survives {surv}/{len(effect[a])} specs")


def _html(payload: dict) -> str:
    data_json = json.dumps(payload)
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ATAP benchmark explorer</title>
<style>
  :root{--bg:#faf9f7;--fg:#1a1a1a;--mut:#666;--card:#fff;--line:#e2e0dc;
        --blue:#0072B2;--orange:#D55E00;--grey:#999;--band:#d9d9d9;}
  @media (prefers-color-scheme:dark){:root{--bg:#16171a;--fg:#eee;--mut:#aaa;--card:#1f2125;--line:#33363c;--band:#3a3d43;}}
  *{box-sizing:border-box}body{margin:0;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}
  .wrap{max-width:920px;margin:0 auto;padding:20px}
  h1{font-size:20px;margin:0 0 2px}.sub{color:var(--mut);font-size:13px;margin-bottom:16px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin-bottom:16px}
  select{font-size:15px;padding:6px 10px;border-radius:7px;border:1px solid var(--line);background:var(--card);color:var(--fg)}
  .row{display:flex;align-items:center;gap:8px;margin:9px 0}
  .lab{width:150px;font-size:12px;color:var(--mut);text-align:right;flex:none}
  .track{position:relative;flex:1;height:26px;background:linear-gradient(90deg,transparent,transparent);border-left:1px solid var(--line);border-right:1px solid var(--line)}
  .mid{position:absolute;left:50%;top:0;bottom:0;border-left:1px dashed var(--line)}
  .band{position:absolute;top:4px;bottom:4px;background:var(--band);border-radius:3px;opacity:.7}
  .bar{position:absolute;top:7px;height:12px;border-radius:3px}
  .val{position:absolute;top:3px;font-size:11px;color:var(--fg)}
  .verdict{font-size:12px;margin-left:6px}.win{color:var(--blue);font-weight:600}.fail{color:var(--orange)}
  table{border-collapse:collapse;font-size:12px}td,th{border:1px solid var(--line);padding:4px 7px;text-align:center}
  th{color:var(--mut);font-weight:600}.diag{color:var(--mut)}
  .key{font-size:12px;color:var(--mut);margin-top:8px}
  .big{font-size:14px;margin:0 0 4px}code{background:var(--band);padding:1px 5px;border-radius:4px;font-size:12px}
</style></head><body><div class="wrap">
<h1>ATAP benchmark explorer</h1>
<div class="sub" id="meta"></div>

<div class="card">
  <p class="big"><b>The finding:</b> pick an axis and see how it does against real BH3-mimetic response.
  Most candidate axes sit inside the grey <b>sham null band</b> on most specs — they don't survive scrutiny.</p>
  <div class="row"><b>Axis:</b>&nbsp;<select id="sel"></select></div>
  <div id="bars"></div>
  <div class="key">Bar = Spearman &rho; (blue = clears the sham null band, orange = inside it).
  Grey band = 95% permutation null. Center line = &rho;=0. Range shown: &minus;1 &hellip; +1.</div>
</div>

<div class="card">
  <p class="big"><b>Inter-axis correlation</b> (Spearman) — how redundant the axes are with each other.</p>
  <div style="overflow-x:auto"><table id="corr"></table></div>
</div>

<div class="card">
  <p class="big"><b>Survival scoreboard</b> — specs each axis clears the sham null on.</p>
  <div id="score"></div>
  <div class="key">This scoreboard is the point: a real axis clears the null on most specs; a
  weak or redundant axis clears few. No individual-level prediction is made anywhere in this tool.</div>
</div>

<script>
const D = __DATA__;
document.getElementById('meta').textContent = D.meta.cohort + " — " + D.meta.note + " (seed " + D.meta.seed + ")";
const sel = document.getElementById('sel');
D.axes.forEach(a=>{const o=document.createElement('option');o.value=a;o.textContent=a;sel.appendChild(o);});
function pct(v){return ((v+1)/2*100).toFixed(1)+'%';}          // map [-1,1] -> [0,100]%
function width(v){return (Math.abs(v)/2*100).toFixed(1)+'%';}
function drawBars(a){
  const host=document.getElementById('bars');host.innerHTML='';
  D.specs.forEach(s=>{
    const e=D.effect[a][s]; if(!e) return;
    const row=document.createElement('div');row.className='row';
    const lab=document.createElement('div');lab.className='lab';lab.textContent=s+' (n='+e.n+')';
    const tr=document.createElement('div');tr.className='track';
    const mid=document.createElement('div');mid.className='mid';tr.appendChild(mid);
    const band=document.createElement('div');band.className='band';
    band.style.left=pct(e.null_lo);band.style.width=(Math.abs(e.null_hi-e.null_lo)/2*100)+'%';tr.appendChild(band);
    const bar=document.createElement('div');bar.className='bar';
    bar.style.background=e.survives?'var(--blue)':'var(--orange)';
    if(e.rho>=0){bar.style.left='50%';bar.style.width=width(e.rho);}
    else{bar.style.left=pct(e.rho);bar.style.width=width(e.rho);}
    tr.appendChild(bar);
    const val=document.createElement('div');val.className='val';val.textContent=(e.rho>0?'+':'')+e.rho;
    val.style.left=e.rho>=0?'calc(50% + '+width(e.rho)+' + 4px)':'calc('+pct(e.rho)+' - 34px)';
    tr.appendChild(val);
    const vd=document.createElement('span');vd.className='verdict '+(e.survives?'win':'fail');
    vd.textContent=e.survives?'clears null':'in null';
    row.appendChild(lab);row.appendChild(tr);row.appendChild(vd);host.appendChild(row);
  });
}
sel.addEventListener('change',()=>drawBars(sel.value));
drawBars(D.axes[0]);
// correlation matrix
const ct=document.getElementById('corr');let h='<tr><th></th>';
D.axes.forEach(a=>h+='<th>'+a.replace(/_/g,' ')+'</th>');h+='</tr>';
D.axes.forEach(a=>{h+='<tr><th style="text-align:right">'+a.replace(/_/g,' ')+'</th>';
  D.axes.forEach(b=>{const v=D.corr[a][b];const abs=Math.abs(v);
    const bg=a===b?'transparent':'rgba(0,114,178,'+(abs*0.5)+')';
    h+='<td class="'+(a===b?'diag':'')+'" style="background:'+bg+'">'+(a===b?'—':v.toFixed(2))+'</td>';});
  h+='</tr>';});
ct.innerHTML=h;
// scoreboard
const sc=document.getElementById('score');let sh='';
D.axes.forEach(a=>{const specs=Object.values(D.effect[a]);const surv=specs.filter(e=>e.survives).length;
  const frac=specs.length?surv/specs.length:0;
  sh+='<div class="row"><div class="lab">'+a.replace(/_/g,' ')+'</div>'+
      '<div class="track" style="border:none;background:var(--band);border-radius:5px">'+
      '<div class="bar" style="left:0;top:3px;height:20px;border-radius:5px;background:'+
      (frac>=0.5?'var(--blue)':'var(--orange)')+';width:'+(frac*100)+'%"></div></div>'+
      '<span class="verdict">'+surv+'/'+specs.length+'</span></div>';});
sc.innerHTML=sh;
</script>
</div></body></html>""".replace("__DATA__", data_json)


if __name__ == "__main__":
    main()
