#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新时代与灵修合集 V1.1 — 提取工具 v5
修复:
- README中带[]的链接文本不再破坏Markdown语法
- 正文不再出现重复的 {#anchor} 标题（同一锚点只出现一次）
- 目录条目不会被错误地转为黑体标题（跳过页码行）
"""

import os, re, struct, zlib, shutil, argparse
from collections import OrderedDict

# ── 默认路径（可通过命令行参数覆盖）──
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_EXE = os.path.join(REPO_ROOT, 'classics', '新时代与灵修合集V1.1典藏版.exe')
DEFAULT_OUT = os.path.join(REPO_ROOT, 'classics', 'xinshidai_library')

# ── helpers ──────────────────────────────────────────────────
def sanitize(s):
    """文件名安全化：[]→【】, 去掉非法字符"""
    for c in r'\/:*?"<>|':
        s = s.replace(c, '_')
    s = s.replace('[', '【').replace(']', '】')
    return s.strip()[:80]

def safe_decode(data):
    for enc in ('gb18030', 'gbk', 'gb2312'):
        try: return data.decode(enc)
        except: continue
    return data.decode('gb18030', errors='replace')

# ── index ────────────────────────────────────────────────────
def parse_index(idx_data):
    lines = idx_data.split(b'\r\n')
    raw, i = [], 0
    while i < len(lines):
        ln = lines[i].strip()
        if not ln: i += 1; continue
        try: et = int(ln)
        except ValueError: i += 1; continue
        if et in (0, 1):
            nm = safe_decode(lines[i+1]).strip() if i+1 < len(lines) else ''
            raw.append({'type': et, 'name': nm, 'path': ''})
            i += 2
        elif et == 4:
            pth = safe_decode(lines[i+1]).strip() if i+1 < len(lines) else ''
            for e in reversed(raw):
                if e['path'] == '': e['path'] = pth; break
            i += 2
        else: i += 1

    books, sec = [], ''
    for e in raw:
        if e['type'] == 0 and e['name']: sec = e['name']
        elif e['type'] == 1 and e['path']:
            books.append({'section': sec or '综合', 'name': e['name'], 'path': e['path']})
    return books

# ── zlib blocks ──────────────────────────────────────────────
def decompress_all(exe_data):
    overlay, blocks = exe_data[0x3DC00:], []
    pos = 4
    while pos < len(overlay) - 2:
        p = overlay.find(b'\x78\xda', pos)
        p2 = overlay.find(b'\x78\x9c', pos)
        if p == -1 and p2 == -1: break
        if p == -1: p = p2
        elif p2 != -1: p = min(p, p2)
        try: blocks.append(zlib.decompress(overlay[p:]))
        except: pass
        pos = p + 2
    return blocks

def classify(blocks):
    r = {'html': [], 'jpg': [], 'png': [], 'gif': [], 'bmp': [], 'other': []}
    for bi, blk in enumerate(blocks):
        if blk[:3] == b'\xff\xd8\xff':        r['jpg'].append((bi, blk))
        elif blk[:8] == b'\x89PNG\r\n\x1a\n': r['png'].append((bi, blk))
        elif blk[:6] in (b'GIF89a', b'GIF87a'): r['gif'].append((bi, blk))
        elif blk[:2] == b'BM':                 r['bmp'].append((bi, blk))
        elif b'[ebook]' in blk[:100] or b'[language]' in blk[:100] \
             or b'[Theme]' in blk[:100] or b'tree.dat' in blk[:20]:
            r['other'].append((bi, blk))
        elif b'<html' in blk[:200].lower() or b'<!doctype' in blk[:200].lower():
            txt = safe_decode(blk)
            m = re.search(r'<title>([^<]*)</title>', txt, re.I)
            title = m.group(1).strip() if m else '(no title)'
            r['html'].append((bi, title, txt))
        else:
            r['other'].append((bi, blk))
    return r

# ── HTML → MD ────────────────────────────────────────────────
def html_to_md(html_text, title, book_path, path_map):
    """HTML→MD，只输出每个标题一次，跳过页码行"""
    # ── bs4 parse ──
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_text, 'html.parser')
        for t in soup(['script', 'style', 'head', 'meta']): t.decompose()
        body = soup.find('body') or soup
    except ImportError:
        body = None

    book_dir = os.path.dirname(book_path) if book_path else ''
    raw_lines = []

    # ── extract text lines from HTML ──
    if body:
        for elem in body.descendants:
            if elem.name is None:
                t = (elem.string or '').strip()
                if t: raw_lines.append(t)
            elif elem.name == 'a' and elem.get('href'):
                href = elem['href']
                link_text = elem.get_text(strip=True)
                if not link_text: continue
                if href.startswith(('http://', 'https://')):
                    raw_lines.append(f'[{link_text}]({href})')
                else:
                    resolved = href
                    if resolved not in path_map and book_dir:
                        resolved = os.path.normpath(os.path.join(book_dir, href)).replace('\\', '/')
                    if resolved in path_map: raw_lines.append(f'[{link_text}]({path_map[resolved]})')
                    elif href in path_map:  raw_lines.append(f'[{link_text}]({path_map[href]})')
                    elif href.endswith('.htm'):
                        bn = os.path.basename(href)
                        if bn in path_map: raw_lines.append(f'[{link_text}]({path_map[bn]})')
                        else: raw_lines.append(link_text)
                    else: raw_lines.append(link_text)
            elif elem.name == 'img' and elem.get('src'):
                bn = os.path.basename(elem['src'])
                raw_lines.append(f'![{bn}](images/{bn})')
            elif elem.name in ('br', 'p', 'div', 'tr', 'li', 'table'):
                raw_lines.append('')
    else:
        text = re.sub(r'<[^>]+>', '', html_text)
        for line in text.split('\n'):
            s = line.strip()
            if s: raw_lines.append(s)

    # ── deduplicate lines ──
    lines = []
    for s in raw_lines:
        s = s.strip()
        if not s: continue
        if not lines or lines[-1] != s: lines.append(s)

    # ── heading detection ──────────────────────────
    def is_page_ref(s):
        """如 '一、向内的革命………………………………2'"""
        return bool(re.search(r'[．…\.]{3,}\s*\d+\s*$', s))

    def clean_head(s):
        """去掉尾部点号和页码"""
        s = re.sub(r'[．…\.\s\d]+$', '', s)
        return re.sub(r'[\.．]+$', '', s).strip()

    def head_body(s):
        """去掉编号前缀，返回正文标题"""
        s = re.sub(r'^[一二三四五六七八九十百千\d]+[、，．\s]+', '', s)
        s = re.sub(r'^[IVXivx]+[\.、\s]+', '', s)
        return s.strip()

    # 从 lines 中收集候选（跳过页码行）
    candidates = []
    for line in lines:
        if len(line) < 3 or len(line) > 80: continue
        if is_page_ref(line): continue
        # 第X章/节
        if re.match(r'^第[一二三四五六七八九十百千\d]+[章节卷部回]', line):
            candidates.append(line); continue
        # 一、二、三、…
        if re.match(r'^[一二三四五六七八九十]+[、，．\s]', line):
            candidates.append(line)

    # 去重
    seen_key, headings = set(), []
    for h in candidates:
        c = clean_head(h)
        k = head_body(c)[:30] or c[:30]
        if k not in seen_key and len(c) >= 3:
            seen_key.add(k)
            headings.append(c)

    # ── build MD ──
    parts = [f'# {title}', '']

    # TOC
    if len(headings) >= 3:
        parts.append('## 目录')
        parts.append('')
        for h in headings:
            anchor = re.sub(r'[^\w一-鿿]', '', h)[:30]
            parts.append(f'- [{h}](#{anchor})')
        parts.append('')
        parts.append('---')
        parts.append('')

    # ── body: 每个 heading anchor 只出现一次 ──
    anchors_used = set()
    headings_sorted = sorted(headings, key=len, reverse=True)
    # 构建 cleanup → original 映射
    heading_map = {clean_head(h): h for h in headings_sorted}

    for line in lines:
        s = line.strip()
        if not s: continue

        # 跳过页码 TOC 行
        if is_page_ref(s) and len(s) < 60: continue

        # 尝试匹配标题
        matched = False
        if 3 <= len(s) <= 80 and not is_page_ref(s):
            cs = clean_head(s)
            if cs in heading_map:
                anchor = re.sub(r'[^\w一-鿿]', '', cs)[:30]
                if anchor not in anchors_used:
                    anchors_used.add(anchor)
                    parts.append('')
                    parts.append(f'## {cs} {{#{anchor}}}')
                    parts.append('')
                    matched = True

        if not matched:
            parts.append(s)

    return '\n\n'.join(parts)

# ── tags ─────────────────────────────────────────────────────
TAG_KW = {
    '禅修': ['禅修', '禅定', '静心', '打坐', '坐禅', '默照'],
    '觉知': ['觉知', '觉察', '觉性', '观照', '内观'],
    '修行': ['修行', '修炼', '修道', '修心', '实修'],
    '开悟': ['开悟', '觉悟', '悟道', '明心见性', '证悟'],
    '佛法': ['佛法', '佛教', '菩萨', '佛陀', '禅宗', '净土宗', '密宗'],
    '道家': ['道家', '道教', '道德经', '庄子', '无为而治', '道法自然'],
    '灵性': ['灵性', '灵魂', '灵修', '高我', '本源意识'],
    '新时代': ['新时代', '新纪元', '扬升', '光之工作者', '星际种子'],
    '能量': ['能量场', '振动频率', '脉轮', '气场'],
    '通灵': ['通灵', '传讯', '灵媒', '通灵讯息'],
    '心理学': ['心理学', '潜意识', '心智模式'],
    '情绪': ['情绪管理', '情感创伤', '愤怒管理', '恐惧症', '焦虑症'],
    '关系': ['亲密关系', '婚姻关系', '家庭关系', '人际关系'],
    '成长': ['成长', '蜕变', '转化', '疗愈', '创伤疗愈'],
    '养生': ['养生', '身体健康', '中医养生', '饮食养生'],
    '辟谷': ['辟谷', '断食', '服气', '素食'],
    '哲学': ['哲学', '真理', '存在主义', '生命哲学'],
    '生死': ['死亡', '生死', '轮回转世', '前世今生', '来生'],
    '瑜伽': ['瑜伽', '奎师那', '薄伽梵歌', '巴克提瑜伽'],
    '基督教': ['耶稣基督', '圣经', '耶和华', '圣父', '圣子', '圣灵'],
    '奇迹课程': ['奇迹课程', '宽恕', '圣灵'],
    '科幻': ['外星文明', '星际旅行', '维度空间'],
    '财富': ['金钱', '财富自由', '丰盛', '吸引力法则'],
}
CAT_TAGS = {
    '与神对话': {'灵性', '新时代', '基督教'},
    '奥修文集': {'灵性', '禅修', '佛法', '哲学', '修行', '开悟'},
    '光的课程': {'灵性', '能量', '新时代'},
    '奇迹课程资料': {'奇迹课程', '灵性', '基督教'},
    '托尔特克(含唐望系列)': {'灵性', '修行'},
    '克里希纳穆提': {'哲学', '觉知', '心理学'},
    '赛斯资料': {'灵性', '通灵', '新时代'},
    '藏密': {'佛法', '修行'},
    '瑜伽资料': {'瑜伽', '灵性'},
    '医学养生类': {'养生', '健康'},
    '克里昂讯息': {'通灵', '新时代', '灵性'},
    '吸引力法则': {'灵性', '财富', '心理学'},
    '少有人走的路': {'心理学', '成长'},
    '生命花园': {'关系', '心理学', '成长'},
    '第四道': {'修行', '哲学'},
    '门罗': {'灵性', '通灵'},
    '阿米系列': {'科幻', '灵性'},
    '伊曼纽三本': {'灵性', '新时代'},
    '宇宙之光&约书亚': {'灵性', '新时代', '通灵'},
    '佩玛丘卓': {'佛法', '禅修', '心理学', '成长'},
    '肯·威尔伯': {'哲学', '心理学', '灵性', '成长'},
    '苏菲亚布朗': {'灵性', '通灵', '生死'},
    '乔斯坦贾德': {'哲学', '心理学'},
    '布莱恩·魏斯': {'灵性', '生死', '心理学'},
    '狄巴克·乔布拉': {'灵性', '养生', '新时代'},
    '钻石途径': {'灵性', '心理学', '修行'},
    '透特': {'通灵', '灵性', '新时代'},
}

def gen_tags(title, content, category):
    tags = set()
    text = (title + ' ' + content[:3000])
    for tag, kws in TAG_KW.items():
        for kw in kws:
            if kw in text: tags.add(tag); break
    for ct, xt in CAT_TAGS.items():
        if ct in category: tags.update(xt)
    return sorted(tags)[:8]

# ══════════════════════════════════════════════════════════════
# main
# ══════════════════════════════════════════════════════════════
def main(exe_path=None, out_dir=None):
    exe = exe_path or DEFAULT_EXE
    out = out_dir or DEFAULT_OUT
    print('=' * 60)
    print('新时代与灵修合集 V1.1 — 提取工具 v5')
    print('=' * 60)

    # 1. read exe
    print('[1/6] 读取 EXE...', end=' ', flush=True)
    with open(exe, 'rb') as f: exe_data = f.read()
    print(f'{len(exe_data)/1024/1024:.1f} MB')

    # 2. decompress
    print('[2/6] 解压 zlib...', end=' ', flush=True)
    blocks = decompress_all(exe_data)
    print(f'{len(blocks)} 块')

    # 3. classify
    print('[3/6] 分类...', end=' ', flush=True)
    cl = classify(blocks)
    print(f'HTML={len(cl["html"])} JPG={len(cl["jpg"])} PNG={len(cl["png"])} '
          f'GIF={len(cl["gif"])} BMP={len(cl["bmp"])}')

    # 4. index
    print('[4/6] 索引...', end=' ', flush=True)
    books = parse_index(blocks[0])
    print(f'{len(books)} 本')

    # 5. build path map
    path_map = {}
    by_path = {}
    for b in books:
        fn = sanitize(b['name'])
        cat = sanitize(b['section'] or '综合')
        rel = f'{cat}/{fn}.md'
        path_map[b['path']] = rel
        bn = os.path.basename(b['path'])
        if bn not in path_map: path_map[bn] = rel
        by_path[b['path']] = (b, fn, cat)
    print(f'  path_map: {len(path_map)} entries')

    # 6. global exact match
    print('[5/6] 匹配...', end=' ', flush=True)
    hlist = cl['html']
    used, matched = set(), []
    for b in books:
        idx = None
        for hi, (bi, ht, _) in enumerate(hlist):
            if hi in used: continue
            if ht == b['name']: idx = hi; break
        if idx is None:
            cn = re.sub(r'^[\d]+[、，．.\s]*', '', b['name']).strip()
            for hi, (bi, ht, _) in enumerate(hlist):
                if hi in used: continue
                if re.sub(r'^[\d]+[、，．.\s]*', '', ht).strip() == cn and cn:
                    idx = hi; break
        if idx is None:
            cn = re.sub(r'^\[[^\]]+\]', '', b['name']).strip()
            cn = re.sub(r'^[\d]+[、，．.\s]*', '', cn).strip()
            for hi, (bi, ht, _) in enumerate(hlist):
                if hi in used: continue
                hc = re.sub(r'^\[[^\]]+\]', '', ht).strip()
                hc = re.sub(r'^[\d]+[、，．.\s]*', '', hc).strip()
                if hc == cn and len(cn) > 3: idx = hi; break
        if idx is not None:
            used.add(idx)
            matched.append((b, hlist[idx][2], hlist[idx][0]))
        else:
            matched.append((b, '', -1))
    print(f'{sum(1 for _,t,_ in matched if t)}/{len(books)}')

    # 7. save
    print('[6/6] 保存...')
    if os.path.exists(out): shutil.rmtree(out)

    cats = OrderedDict()
    for b, ht, bi in matched:
        c = b['section'] or '综合'
        cats.setdefault(c, []).append((b, ht, bi))

    saved = 0
    for cname, items in cats.items():
        cdir = os.path.join(out, sanitize(cname))
        imgdir = os.path.join(cdir, 'images')
        os.makedirs(cdir, exist_ok=True)
        os.makedirs(imgdir, exist_ok=True)

        # ── extract images for this category ──
        c_blocks = [bi for _, _, bi in items if bi >= 0]
        if c_blocks:
            min_bi, max_bi = min(c_blocks), max(c_blocks)
            c_jpgs = [(jbi, jd) for jbi, jd in cl['jpg'] if min_bi <= jbi <= max_bi + 60]
        else:
            c_jpgs = cl['jpg']

        # For each book, get images referenced in HTML
        jpg_idx = 0
        for entry, htext, bi in items:
            if not htext: continue
            img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', htext, re.I)

            for src in img_srcs:
                bn = os.path.basename(src)
                ipath = os.path.join(imgdir, bn)
                if not os.path.exists(ipath) and jpg_idx < len(c_jpgs):
                    try:
                        with open(ipath, 'wb') as f: f.write(c_jpgs[jpg_idx][1])
                    except: pass
                    jpg_idx += 1
                # rewrite HTML src
                htext = htext.replace(f'src="{src}"', f'src="images/{bn}"')
                htext = htext.replace(f"src='{src}'", f"src='images/{bn}'")

            md = html_to_md(htext, entry['name'], entry['path'], path_map)
            tags = gen_tags(entry['name'], md, cname)

            fp = os.path.join(cdir, sanitize(entry['name']) + '.md')
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(f'---\n')
                f.write(f'title: "{entry["name"]}"\n')
                f.write(f'category: "{cname}"\n')
                f.write(f'source: "{entry["path"]}"\n')
                f.write(f'tags: {tags}\n')
                f.write(f'---\n\n')
                f.write(md)
            saved += 1

        nimg = len(os.listdir(imgdir))
        print(f'  [{cname}]: {len(items)} 本, {nimg} images')

    print(f'\n完成！共 {saved} 本')

    # ══════════════════════════════════════════════════════════
    # README
    # ══════════════════════════════════════════════════════════
    print('生成 README...', end=' ', flush=True)

    def safe_link(fn):
        """编码文件名中破坏 Markdown 链接语法的字符"""
        return fn.replace('(', '%28').replace(')', '%29')

    def fix_display(s):
        """链接文本中如有 [全][节] 等标签，去掉避免破坏 Markdown [[]] 解析"""
        # 先去掉前导的 [全][节] 等标签
        s = re.sub(r'^\[[^\]]+\]', '', s).strip()
        # 再将正文内残留的 [] 替换为「」
        return s.replace('[', '「').replace(']', '」')

    with open(os.path.join(out, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('# 新时代与灵修合集 V1.1 — 总目录\n\n')
        f.write('> 自动提取自 `新时代与灵修合集V1.1典藏版.exe`\n')
        f.write(f'> 共 {len(cats)} 个分类，{saved} 本书\n\n---\n\n')

        for cname, items in cats.items():
            cs = sanitize(cname)
            f.write(f'## {cname}\n\n')
            idx_rel = safe_link(f'{cs}/{cs}目录.md')
            f.write(f'- [📑 {cname}目录]({idx_rel})\n')
            for entry, htext, bi in items:
                if not htext: continue
                fn = sanitize(entry['name'])
                rel = safe_link(f'{cs}/{fn}.md')
                # 替换 [] 为 〖〗避免破坏 Markdown 链接语法
                display = fix_display(entry['name'])
                f.write(f'- [{display}]({rel})\n')
            f.write('\n')

    # ══════════════════════════════════════════════════════════
    # Section indexes
    # ══════════════════════════════════════════════════════════
    print('生成分类索引...', end=' ', flush=True)
    for cname, items in cats.items():
        cs = sanitize(cname)
        ipath = os.path.join(out, cs, f'{cs}目录.md')
        with open(ipath, 'w', encoding='utf-8') as f:
            f.write(f'# {cname} — 目录索引\n\n')
            f.write(f'> 共 {len(items)} 本书\n\n---\n\n')

            prev = None
            for i, (entry, htext, bi) in enumerate(items):
                if not htext: continue
                fn = sanitize(entry['name'])
                fl = safe_link(f'{fn}.md')
                # 读取该书获取标签
                bfp = os.path.join(out, cs, fn + '.md')
                ts = ''
                if os.path.exists(bfp):
                    with open(bfp, encoding='utf-8') as bf:
                        m = re.search(r'tags:\s*\[([^\]]+)\]', bf.read(500))
                        if m: ts = m.group(1)

                f.write(f'### {entry["name"]}\n\n')
                f.write(f'- 📄 [{entry["name"]}](./{fl})\n')
                if ts: f.write(f'- 🏷️ {ts}\n')

                if prev:
                    pf, pn = prev
                    pfl = safe_link(f'{pf}.md')
                    f.write(f'- ⬅️ 上一篇: [{pn}](./{pfl})\n')

                # 找下一篇
                nxt = None
                for j in range(i + 1, len(items)):
                    ne, nh, nb = items[j]
                    if nh:
                        nxt = (sanitize(ne['name']), ne['name'])
                        break
                if nxt:
                    nfl = safe_link(f'{nxt[0]}.md')
                    f.write(f'- ➡️ 下一篇: [{nxt[1]}](./{nfl})\n')

                f.write('\n')
                prev = (fn, entry['name'])

            # 快速索引
            f.write('---\n\n## 快速索引\n\n')
            for entry, htext, bi in items:
                if not htext: continue
                fn = sanitize(entry['name'])
                fl = safe_link(f'{fn}.md')
                f.write(f'- [{entry["name"]}](./{fl})\n')

    print('完成！')
    print(f'输出: {out}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='从《新时代与灵修合集 V1.1 典藏版》.exe 提取全部书目为 Markdown')
    parser.add_argument('--exe', default=DEFAULT_EXE,
                        help=f'EXE 文件路径（默认: {DEFAULT_EXE}）')
    parser.add_argument('--out', default=DEFAULT_OUT,
                        help=f'输出目录（默认: {DEFAULT_OUT}）')
    args = parser.parse_args()
    main(exe_path=args.exe, out_dir=args.out)
