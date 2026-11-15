#!/usr/bin/env python3
"""
Generate workflows.json — static index of all workflows in this repo.
Run manually or via GitHub Actions on every push to main.
"""
import os, json, re, unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))


def is_workflow(name):
    """Accept .yaml files and extension-less files that look like YAML workflows."""
    if name.startswith('.') or name.startswith('_'):
        return False
    if name.endswith('.yaml') or name.endswith('.yml'):
        return True
    if '.' not in name:  # extension-less (e.g. outlook-triage)
        path = os.path.join(ROOT, name)
        if os.path.isfile(path):
            try:
                with open(path, encoding='utf-8', errors='ignore') as f:
                    head = f.read(256)
                return 'name:' in head or 'steps:' in head or 'yaml-language-server' in head
            except Exception:
                return False
    return False


def unquote(s):
    if s is None:
        return ''
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    return s


def parse_meta(text):
    """Minimal YAML parser for name, description, and step types."""
    name = unquote(re.search(r'^name\s*:\s*(.+)', text, re.M).group(1)) if re.search(r'^name\s*:\s*(.+)', text, re.M) else ''

    desc = ''
    dm = re.search(r'^description\s*:\s*(.*)', text, re.M)
    if dm:
        val = dm.group(1).strip()
        if val in ('>', '>-', '|', '|-', ''):
            # block scalar — collect indented lines
            after = text[dm.end():]
            parts = []
            for line in after.splitlines():
                if re.match(r'^\s+\S', line):
                    parts.append(line.strip())
                elif line.strip() == '':
                    continue
                else:
                    break
            desc = ' '.join(parts)
        else:
            desc = unquote(val)

    types = re.findall(r'^\s+type\s*:\s*(\w+)', text, re.M)
    return name, desc, types


def main():
    workflows = []
    for fname in sorted(os.listdir(ROOT)):
        if not is_workflow(fname):
            continue
        path = os.path.join(ROOT, fname)
        try:
            with open(path, encoding='utf-8', errors='ignore') as f:
                text = f.read()
            name, desc, types = parse_meta(text)
            if not name and not types:
                continue          # skip non-workflow files
            workflows.append({
                'path':  fname,
                'name':  name or fname,
                'desc':  desc,
                'types': types,
            })
        except Exception as e:
            print(f'  skip {fname}: {e}')

    out = os.path.join(ROOT, 'workflows.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(workflows, f, ensure_ascii=False, indent=2)
    print(f'workflows.json — {len(workflows)} workflow(s)')


if __name__ == '__main__':
    main()