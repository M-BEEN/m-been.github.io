"""Count archived report labels. This does NOT reproduce investment returns.

Python 3.10+, standard library only. Run beside the two JSON input files.
Optional: --source-root /path/to/blog verifies hashes AND re-extracts every row.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def extract(meta, report_id):
    return [dict(report_id=report_id, date_label=str(meta['date'])[:10],
                 asof=str(meta.get('asof', ''))[:10], card_position=pos,
                 name=card.get('name'), code=card['code'], verdict=card['verdict'], kind=card.get('kind'))
            for pos, card in enumerate(meta.get('insights', []))
            if re.fullmatch(r'\d{6}(?:\.(?:KS|KQ))?', str(card.get('code', ''))) and card.get('verdict')]


def summarize(rows, sources):
    result = {}
    for cutoff in ('2026-09-04', '2026-09-15', '2026-09-29'):
        subset = [r for r in rows if r['date_label'] <= cutoff]
        result[cutoff] = dict(reports=sum(s['date_label'] <= cutoff for s in sources),
                              rows=len(subset), counts=dict(sorted(Counter(r['verdict'] for r in subset).items())))
    result['same_or_later_asof'] = [s['report_id'] for s in sources if s['asof'] >= s['date_label']]
    result['unknown_first_available_at'] = sum(s['first_available_at'] is None for s in sources)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    rows = json.loads((here / 'verdicts.json').read_text(encoding='utf-8'))
    sources = json.loads((here / 'source-index.json').read_text(encoding='utf-8'))
    if args.source_root:
        root = args.source_root.resolve()
        rebuilt = []
        for item in sources:
            path = (root / item['archive_path']).resolve()
            path.relative_to(root)
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != item['sha256']:
                raise ValueError(f'Original bytes differ: {item["report_id"]}')
            meta, _ = json.JSONDecoder().raw_decode(raw.decode('utf-8').lstrip())
            rebuilt.extend(extract(meta, item['report_id']))
        if rows != rebuilt:
            raise ValueError('Published rows differ from source extraction')
    result = summarize(rows, sources)
    expected = json.loads((here / 'expected.json').read_text(encoding='utf-8'))
    if result != expected:
        raise ValueError('Counts differ from expected.json')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
