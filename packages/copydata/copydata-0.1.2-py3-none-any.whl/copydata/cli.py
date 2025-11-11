#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sys
import json
from typing import List, Tuple, Dict, Any
from pathlib import Path
from difflib import SequenceMatcher

import pandas as pd
import numpy as np


def read_df(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = p.suffix.lower()
    if suffix in {'.csv', '.txt'}:
        return pd.read_csv(p)
    if suffix in {'.xls', '.xlsx'}:
        return pd.read_excel(p)
    if suffix in {'.json'}:
        return pd.read_json(p)
    # fallback to csv
    return pd.read_csv(p)


def fmt_num(x: float) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return 'NA'
    try:
        val = float(x)
    except Exception:
        return str(x)
    if abs(val) >= 1e6:
        return f"{val/1e6:.2f}M"
    if abs(val) >= 1e3:
        return f"{val/1e3:.1f}K"
    return f"{val:.2f}"


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def detect_renames(cols_a: List[str], cols_b: List[str], threshold: float = 0.8) -> List[Tuple[str, str, float]]:
    matches: List[Tuple[str, str, float]] = []
    remaining_b = set(cols_b)
    for ca in cols_a:
        best = (None, 0.0)
        for cb in remaining_b:
            s = similar(ca.lower(), cb.lower())
            if s > best[1]:
                best = (cb, s)
        if best[0] and best[1] >= threshold and ca != best[0]:
            matches.append((ca, best[0], round(best[1], 3)))
            remaining_b.remove(best[0])
    return matches


def numeric_summary(s: pd.Series) -> Dict[str, Any]:
    s_num = pd.to_numeric(s, errors='coerce')
    non_null = s_num.dropna()
    if non_null.empty:
        return {'count': int(s.shape[0]), 'nulls': int(s.isna().sum())}
    q1 = non_null.quantile(0.25)
    q3 = non_null.quantile(0.75)
    iqr = q3 - q1 if not pd.isna(q3 - q1) else 0
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = non_null[(non_null < lower) | (non_null > upper)]
    return {
        'count': int(s.shape[0]),
        'non_null': int(non_null.shape[0]),
        'nulls': int(s.isna().sum()),
        'mean': float(non_null.mean()) if not non_null.empty else None,
        'median': float(non_null.median()) if not non_null.empty else None,
        'std': float(non_null.std()) if not non_null.empty else None,
        'min': float(non_null.min()) if not non_null.empty else None,
        'max': float(non_null.max()) if not non_null.empty else None,
        'unique': int(non_null.nunique()),
        'outlier_count': int(outliers.shape[0]),
    }


def categorical_summary(s: pd.Series, top_n: int = 5) -> Dict[str, Any]:
    vals = s.dropna().astype(str)
    if vals.empty:
        return {'count': int(s.shape[0]), 'nulls': int(s.isna().sum())}
    vc = vals.value_counts()
    top = vc.head(top_n).to_dict()
    return {
        'count': int(s.shape[0]),
        'non_null': int(vals.shape[0]),
        'nulls': int(s.isna().sum()),
        'unique': int(vc.shape[0]),
        'top': top,
    }


def compare_numeric(sa: pd.Series, sb: pd.Series) -> Dict[str, Any]:
    a = numeric_summary(sa)
    b = numeric_summary(sb)
    result: Dict[str, Any] = {'A': a, 'B': b}
    if a.get('non_null') and b.get('non_null'):
        try:
            change = None
            if a.get('mean') is not None and b.get('mean') is not None and a['mean'] != 0:
                change = (b['mean'] - a['mean']) / (abs(a['mean']) if a['mean'] != 0 else 1)
            result['mean_pct_change'] = change
            result['min_change'] = None if a.get('min') is None or b.get('min') is None else b['min'] - a['min']
            result['max_change'] = None if a.get('max') is None or b.get('max') is None else b['max'] - a['max']
        except Exception:
            result['mean_pct_change'] = None
    return result


def compare_categorical(sa: pd.Series, sb: pd.Series) -> Dict[str, Any]:
    a = categorical_summary(sa, top_n=10)
    b = categorical_summary(sb, top_n=10)
    set_a = set(sa.dropna().astype(str).unique())
    set_b = set(sb.dropna().astype(str).unique())
    added = sorted(list(set_b - set_a))
    removed = sorted(list(set_a - set_b))
    common = sorted(list(set_a & set_b))
    return {'A': a, 'B': b, 'added': added, 'removed': removed, 'common_count': len(common)}


def simple_type(s: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(s):
        return 'numeric'
    nunique = s.dropna().nunique()
    if nunique <= 20 and nunique > 1:
        return 'categorical'
    if pd.api.types.is_datetime64_any_dtype(s):
        return 'datetime'
    return 'text'


def compare_dataframes(df_a: pd.DataFrame, df_b: pd.DataFrame, rename_threshold: float = 0.82) -> Dict[str, Any]:
    report: Dict[str, Any] = {}
    cols_a = list(df_a.columns)
    cols_b = list(df_b.columns)

    report['row_count'] = {
        'A': int(df_a.shape[0]),
        'B': int(df_b.shape[0]),
        'delta': int(df_b.shape[0]) - int(df_a.shape[0])
    }

    added_cols = [c for c in cols_b if c not in cols_a]
    removed_cols = [c for c in cols_a if c not in cols_b]
    common_cols = [c for c in cols_a if c in cols_b]
    renames = detect_renames(removed_cols, added_cols, threshold=rename_threshold)
    renamed_from = [r[0] for r in renames]
    renamed_to = [r[1] for r in renames]
    added_cols = [c for c in added_cols if c not in renamed_to]
    removed_cols = [c for c in removed_cols if c not in renamed_from]

    report['structural'] = {'added': added_cols, 'removed': removed_cols, 'renamed': renames}

    total_cells_a = df_a.size
    total_cells_b = df_b.size
    nulls_a = int(df_a.isna().sum().sum())
    nulls_b = int(df_b.isna().sum().sum())
    report['nulls'] = {
        'A': nulls_a,
        'B': nulls_b,
        'pct_A': nulls_a / total_cells_a if total_cells_a else None,
        'pct_B': nulls_b / total_cells_b if total_cells_b else None
    }

    dup_a = int(df_a.duplicated().sum())
    dup_b = int(df_b.duplicated().sum())
    report['duplicates'] = {'A': dup_a, 'B': dup_b, 'delta': dup_b - dup_a}

    col_reports: Dict[str, Any] = {}
    for col in sorted(set(common_cols)):
        sa = df_a[col]
        sb = df_b[col]
        t: Dict[str, Any] = {'type_a': simple_type(sa), 'type_b': simple_type(sb)}
        if t['type_a'] == 'numeric' or t['type_b'] == 'numeric':
            t['compare'] = compare_numeric(sa, sb)
        else:
            t['compare'] = compare_categorical(sa, sb)
        col_reports[col] = t

    renamed_reports: List[Dict[str, Any]] = []
    for r in renames:
        ca, cb, score = r
        sa = df_a[ca] if ca in df_a.columns else pd.Series(dtype=object)
        sb = df_b[cb] if cb in df_b.columns else pd.Series(dtype=object)
        t = {
            'from': ca,
            'to': cb,
            'score': score,
            'type_from': simple_type(sa),
            'type_to': simple_type(sb)
        }
        if t['type_from'] == 'numeric' or t['type_to'] == 'numeric':
            t['compare'] = compare_numeric(sa, sb)
        else:
            t['compare'] = compare_categorical(sa, sb)
        renamed_reports.append(t)

    report['columns'] = col_reports
    report['renamed_columns'] = renamed_reports

    return report


def markdown_report(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append('# Data Whisperer Report')

    rc = report['row_count']
    lines.append('\n## Summary')
    lines.append(f"- Row count A: {rc['A']}, B: {rc['B']}, Δ: {rc['delta']}")
    nulls = report['nulls']
    pct_a = f"{nulls['pct_A']*100:.2f}%" if nulls['pct_A'] is not None else 'NA'
    pct_b = f"{nulls['pct_B']*100:.2f}%" if nulls['pct_B'] is not None else 'NA'
    lines.append(f"- Total nulls A: {nulls['A']} ({pct_a}) , B: {nulls['B']} ({pct_b})")
    dups = report['duplicates']
    lines.append(f"- Duplicate rows A: {dups['A']} , B: {dups['B']} , Δ: {dups['delta']}")

    lines.append('\n## Structural Changes')
    struct = report['structural']
    lines.append(f"- Added columns ({len(struct['added'])}): {', '.join(struct['added']) if struct['added'] else 'None'}")
    lines.append(f"- Removed columns ({len(struct['removed'])}): {', '.join(struct['removed']) if struct['removed'] else 'None'}")
    if struct['renamed']:
        lines.append(f"- Probable renames ({len(struct['renamed'])}):")
        for fr, to, score in struct['renamed']:
            lines.append(f"  - {fr} -> {to} (similarity {score})")
    else:
        lines.append('- Probable renames: None')

    lines.append('\n## Column Level Changes (selected)')
    col_scores: List[Tuple[float, str]] = []
    for col, info in report['columns'].items():
        cmp = info['compare']
        score_val = 0.0
        if 'mean_pct_change' in cmp:
            mc = cmp.get('mean_pct_change')
            if mc is not None:
                score_val += abs(mc)
        a_null = cmp.get('A', {}).get('nulls') if isinstance(cmp.get('A'), dict) else None
        b_null = cmp.get('B', {}).get('nulls') if isinstance(cmp.get('B'), dict) else None
        if a_null is not None and b_null is not None:
            score_val += abs(b_null - a_null) / max(1, cmp['A'].get('count', 1))
        col_scores.append((score_val, col))
    col_scores.sort(reverse=True)

    top_n = min(12, len(col_scores))
    if top_n == 0:
        lines.append('No common columns to compare.')
    for idx in range(top_n):
        _, col = col_scores[idx]
        info = report['columns'][col]
        lines.append(f"\n### {col}")
        lines.append(f"- Type A: {info['type_a']}, Type B: {info['type_b']}")
        cmp = info['compare']
        if info['type_a'] == 'numeric' or info['type_b'] == 'numeric':
            a = cmp['A']
            b = cmp['B']
            mean_a = a.get('mean')
            mean_b = b.get('mean')
            lines.append(f"- Mean: A: {fmt_num(mean_a) if mean_a is not None else 'NA'} , B: {fmt_num(mean_b) if mean_b is not None else 'NA'}")
            if cmp.get('mean_pct_change') is not None:
                lines.append(f"- Mean % change: {cmp['mean_pct_change']*100:.2f}%")
            lines.append(f"- Std A: {fmt_num(a.get('std')) if a.get('std') is not None else 'NA'} , Std B: {fmt_num(b.get('std')) if b.get('std') is not None else 'NA'}")
            lines.append(f"- Outliers A: {a.get('outlier_count', 0)} , B: {b.get('outlier_count', 0)}")
            lines.append(f"- Nulls A: {a.get('nulls', 0)} , B: {b.get('nulls', 0)}")
        else:
            a = cmp['A']
            b = cmp['B']
            lines.append(f"- Unique A: {a.get('unique', 'NA')} , B: {b.get('unique', 'NA')}")
            top_a = a.get('top') or {}
            top_b = b.get('top') or {}
            lines.append(f"- Top values A: {', '.join([f'{k}({v})' for k, v in list(top_a.items())][:3]) or 'NA'}")
            lines.append(f"- Top values B: {', '.join([f'{k}({v})' for k, v in list(top_b.items())][:3]) or 'NA'}")
            added = cmp.get('added', [])
            removed = cmp.get('removed', [])
            if added:
                lines.append(f"- New categories in B: {', '.join(added[:6])} {'(+ more)' if len(added)>6 else ''}")
            if removed:
                lines.append(f"- Categories removed in B: {', '.join(removed[:6])} {'(+ more)' if len(removed)>6 else ''}")

    if report.get('renamed_columns'):
        lines.append('\n## Renamed Column Comparisons')
        for r in report['renamed_columns']:
            lines.append(f"- {r['from']} -> {r['to']} (similarity {r['score']})")
            cmp = r['compare']
            if r['type_from'] == 'numeric' or r['type_to'] == 'numeric':
                a = cmp['A']
                b = cmp['B']
                lines.append(f"  - Mean A: {fmt_num(a.get('mean')) if a.get('mean') is not None else 'NA'} , Mean B: {fmt_num(b.get('mean')) if b.get('mean') is not None else 'NA'}")
                if cmp.get('mean_pct_change') is not None:
                    lines.append(f"  - Mean % change: {cmp['mean_pct_change']*100:.2f}%")
            else:
                a = cmp['A']
                b = cmp['B']
                lines.append(f"  - Unique A: {a.get('unique', 'NA')} , B: {b.get('unique', 'NA')}")

    lines.append('\n---')
    lines.append('Generated by Data Whisperer. Focus on meaningful numeric shifts, category churn, and schema changes.')
    return '\n'.join(lines)


def main(argv: List[str] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog='dw',
        description='Data Whisperer. Compare two tabular datasets and report what truly changed.'
    )
    parser.add_argument('a', help='Path to dataset A (older)')
    parser.add_argument('b', help='Path to dataset B (newer)')
    parser.add_argument('--output', '-o', help='Markdown output file (used when --output-save is set)', default='dw_report.md')
    parser.add_argument(
        '--output-save',
        action='store_true',
        help='If set, save markdown (and JSON if requested) to files. Otherwise print to stdout.'
    )
    parser.add_argument('--json', '-j', help='Also produce machine-readable json (printed or saved depending on --output-save)', action='store_true')
    parser.add_argument('--rename-threshold', type=float, default=0.82, help='Similarity threshold for detecting renamed columns')
    args = parser.parse_args(argv)

    df_a = read_df(args.a)
    df_b = read_df(args.b)

    report = compare_dataframes(df_a, df_b, rename_threshold=args.rename_threshold)

    md = markdown_report(report)

    if args.output_save:
        out_path = Path(args.output)
        out_path.write_text(md, encoding='utf-8')
        print(f"Wrote markdown report to {out_path}")
        if args.json:
            jpath = out_path.with_suffix('.json')
            jpath.write_text(json.dumps(report, indent=2, default=lambda o: None), encoding='utf-8')
            print(f"Wrote JSON report to {jpath}")
    else:
        print(md)
        if args.json:
            print("\n\n--- JSON OUTPUT ---\n")
            print(json.dumps(report, indent=2, default=lambda o: None))

    return 0
