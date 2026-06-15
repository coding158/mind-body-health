#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新时代与灵修合集 V1.1 - 自动提取脚本 v4（备用方案）
通过 Win32 API 操作阅读器树形目录，提取全部书目为 Markdown

⚠️ 安全告知 · Security Notice：
本脚本通过跨进程内存读写（ReadProcessMemory / WriteProcessMemory）与目标 EXE
的 TreeView 控件交互。这是操作 GUI 程序的必要技术手段，但可能被杀毒软件标记为
可疑行为（"进程注入"特征）。本脚本是备用方案——首选方案 extract_all_books.py
使用 zlib 静态解压，不涉及任何进程操作，不会被误报。

本脚本仅读取目标进程的 TreeView 节点文本，不修改、不注入代码、不联网。

如需提取：建议优先使用 extract_all_books.py。本脚本仅在 zlib 方式无法正常工作时
作为替代方案使用。

依赖（pip install）：pywin32  beautifulsoup4
"""

import os, re, sys, time, ctypes, ctypes.wintypes, struct
from pathlib import Path

# ── 依赖检查 ─────────────────────────────────────────────────
try:
    import win32gui, win32api, win32con, win32process
except ImportError:
    print('请先安装：pip install pywin32')
    sys.exit(1)

# ── 配置 ─────────────────────────────────────────────────────
TEMP_DIR    = os.path.expandvars('%TEMP%')
OUTPUT_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xinshidai_library')
WAIT_SEC    = 20
STEP_SEC    = 1.0

# ── TreeView Win32 常量 ──────────────────────────────────────
TVM_GETNEXTITEM = 0x110A
TVM_GETITEMW    = 0x111B
TVM_EXPAND      = 0x1102
TVM_SELECTITEM  = 0x110B
TVGN_ROOT       = 0
TVGN_NEXT       = 1
TVGN_CHILD      = 4
TVGN_CARET      = 9
TVE_EXPAND      = 2
TVIF_TEXT       = 0x1
TVIF_CHILDREN   = 0x40
PROCESS_VM_OPERATION = 0x0008  # VirtualAllocEx / VirtualFreeEx
PROCESS_VM_READ     = 0x0010  # ReadProcessMemory
PROCESS_VM_WRITE    = 0x0020  # WriteProcessMemory
PROCESS_ACCESS      = PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE
MEM_COMMIT          = 0x1000
MEM_RELEASE         = 0x8000
PAGE_READWRITE      = 0x04


# ── 跨进程读取树节点文本（适配 32/64 位） ───────────────────
class RemoteMemory:
    """在目标进程（32位）中分配内存，用于 SendMessage IPC"""
    def __init__(self, pid, size=4096):
        self.size = size
        self.hproc = ctypes.windll.kernel32.OpenProcess(PROCESS_ACCESS, False, pid)
        self.addr  = ctypes.windll.kernel32.VirtualAllocEx(
            self.hproc, None, size, MEM_COMMIT, PAGE_READWRITE)
        if not self.addr:
            raise OSError('VirtualAllocEx 失败')

    def write(self, data: bytes):
        n = ctypes.c_ulong()
        ctypes.windll.kernel32.WriteProcessMemory(
            self.hproc, self.addr, data, len(data), ctypes.byref(n))

    def read(self, offset, size) -> bytes:
        buf = ctypes.create_string_buffer(size)
        n   = ctypes.c_ulong()
        ctypes.windll.kernel32.ReadProcessMemory(
            self.hproc, self.addr + offset, buf, size, ctypes.byref(n))
        return buf.raw

    def close(self):
        ctypes.windll.kernel32.VirtualFreeEx(self.hproc, self.addr, 0, MEM_RELEASE)
        ctypes.windll.kernel32.CloseHandle(self.hproc)


def get_treeview_item_text(tree_hwnd, hitem, rmem: RemoteMemory) -> str:
    """读取 32 位进程中树节点的文字"""
    TEXT_OFFSET = 64   # TVITEMW 结构之后放文本缓冲区
    text_remote = rmem.addr + TEXT_OFFSET

    # 构造 TVITEMW（32位对齐，共 10x4=40 字节）
    # mask, hItem, state, stateMask, pszText(ptr32), cchTextMax,
    # iImage, iSelectedImage, cChildren, lParam
    tvitem = struct.pack('<IIIIIiiii',
        TVIF_TEXT,
        hitem & 0xFFFFFFFF,
        0, 0,
        text_remote & 0xFFFFFFFF,
        255,
        0, 0, 0)
    # lParam 省略（总共 36 字节，结构末尾补齐到 TEXT_OFFSET）
    padded = tvitem + b'\x00' * (TEXT_OFFSET - len(tvitem))
    rmem.write(padded)

    win32api.SendMessage(tree_hwnd, TVM_GETITEMW, 0, rmem.addr)

    raw = rmem.read(TEXT_OFFSET, 512)
    try:
        text = raw.decode('utf-16-le', errors='replace')
        return text.split('\x00')[0]
    except Exception:
        return ''


def tree_next(hwnd, hitem, rel):
    return win32api.SendMessage(hwnd, TVM_GETNEXTITEM, rel, hitem)


def walk_tree(tree_hwnd, rmem):
    """
    遍历树形控件所有节点，返回列表：
    每项 = (hitem, text, parent_text, is_leaf)
    """
    results = []

    def recurse(hitem, parent_text, depth):
        while hitem:
            text = get_treeview_item_text(tree_hwnd, hitem, rmem)

            # 展开节点
            win32api.SendMessage(tree_hwnd, TVM_EXPAND, TVE_EXPAND, hitem)
            time.sleep(0.05)

            child = tree_next(tree_hwnd, hitem, TVGN_CHILD)
            if child:
                # 有子节点 -> 分类
                results.append((hitem, text, parent_text, False))
                recurse(child, text, depth + 1)
            else:
                # 叶节点 -> 书目
                results.append((hitem, text, parent_text, True))

            hitem = tree_next(tree_hwnd, hitem, TVGN_NEXT)

    root = tree_next(tree_hwnd, 0, TVGN_ROOT)
    recurse(root, '', 0)
    return results


# ── 临时文件监控 ─────────────────────────────────────────────
def snap_temp():
    r = {}
    for f in Path(TEMP_DIR).glob('*.htm'):
        try: r[str(f)] = f.stat().st_size
        except: pass
    return r


def wait_new_htm(before, timeout=WAIT_SEC):
    end = time.time() + timeout
    while time.time() < end:
        cur = snap_temp()
        new = {k: v for k, v in cur.items() if k not in before and v > 400}
        if new:
            time.sleep(0.5)
            return max(new, key=lambda k: cur[k])
        time.sleep(0.35)
    return None


# ── HTML -> Markdown ─────────────────────────────────────────
def htm_to_md(path, title):
    try:
        from bs4 import BeautifulSoup
        html = open(path, encoding='gbk', errors='replace').read()
        soup = BeautifulSoup(html, 'html.parser')
        for t in soup(['script', 'style', 'head', 'meta']): t.decompose()
        text = (soup.find('body') or soup).get_text('\n', strip=True)
    except ImportError:
        text = re.sub(r'<[^>]+>', '', open(path, encoding='gbk', errors='replace').read())
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    dedup = []
    for l in lines:
        if not dedup or dedup[-1] != l:
            dedup.append(l)
    return '# ' + title + '\n\n' + '\n\n'.join(dedup)


def sanitize(s):
    for c in r'\/:*?"<>|': s = s.replace(c, '_')
    return s.strip()[:80]


# ── 主程序 ───────────────────────────────────────────────────
def main():
    import warnings; warnings.filterwarnings('ignore')

    print('=' * 60)
    print('新时代与灵修合集 V1.1 — 自动提取工具 v4')
    print('=' * 60)

    # 找阅读器主窗口 — 取最大的可见窗口
    reader_windows = []
    def cb(hwnd, _):
        t = win32gui.GetWindowText(hwnd)
        if '新时代' in t and '典藏版' in t:
            r = win32gui.GetWindowRect(hwnd)
            area = (r[2]-r[0]) * (r[3]-r[1])
            if area > 10000:  # 忽略最小化/隐藏的窗口
                reader_windows.append((hwnd, area))
        return True
    win32gui.EnumWindows(cb, None)

    if not reader_windows:
        print('[X] 找不到阅读器窗口，请先打开 .exe')
        return
    reader_hwnd = max(reader_windows, key=lambda x: x[1])[0]
    print(f'[OK] 找到窗口: {win32gui.GetWindowText(reader_hwnd)}')

    # 找主树形控件：用 EnumChildWindows 递归查找所有 TTreeView
    def find_all_by_class(root, target_class):
        found = []
        def enum_recursive(hwnd):
            def enum_cb(child, _):
                try:
                    if win32gui.GetClassName(child) == target_class:
                        found.append(child)
                except Exception:
                    pass
                # 继续枚举这个 child 的子窗口
                enum_recursive(child)
                return True
            win32gui.EnumChildWindows(hwnd, enum_cb, None)
        enum_recursive(root)
        return found

    all_trees = find_all_by_class(reader_hwnd, 'TTreeView')
    print(f'  找到 {len(all_trees)} 个 TTreeView')
    for h in all_trees:
        r = win32gui.GetWindowRect(h)
        print(f'    HWND={h}  size={r[2]-r[0]}x{r[3]-r[1]}  rect={r}')

    if not all_trees:
        print('[X] 找不到 TTreeView 控件')
        return

    # 取面积最大的（即主导航树）
    tree_hwnd = max(all_trees,
                    key=lambda h: (win32gui.GetWindowRect(h)[2]-win32gui.GetWindowRect(h)[0]) *
                                  (win32gui.GetWindowRect(h)[3]-win32gui.GetWindowRect(h)[1]))
    print(f'[OK] 找到树形控件 HWND={tree_hwnd}')

    # 获取进程 ID，创建远程内存
    _, pid = win32process.GetWindowThreadProcessId(tree_hwnd)
    print(f'  进程 PID={pid} (32位应用)')

    try:
        rmem = RemoteMemory(pid)
    except OSError as e:
        print(f'[X] 无法分配进程内存: {e}')
        print('  提示: 尝试以管理员身份运行 PowerShell 后再执行脚本')
        return

    # 遍历所有节点
    print('正在遍历目录树 (请稍候)...')
    try:
        items = walk_tree(tree_hwnd, rmem)
    except Exception as e:
        print(f'[X] 遍历失败: {e}')
        rmem.close()
        return

    leaf_items = [(h, text, cat) for h, text, cat, is_leaf in items if is_leaf and text.strip()]
    print(f'[OK] 找到 {len(leaf_items)} 个书目')

    os.makedirs(OUTPUT_BASE, exist_ok=True)
    success, failed = 0, []

    for i, (hitem, title, category) in enumerate(leaf_items):
        category = category or '综合'
        cat_dir  = os.path.join(OUTPUT_BASE, sanitize(category))
        os.makedirs(cat_dir, exist_ok=True)
        md_path  = os.path.join(cat_dir, sanitize(title) + '.md')

        if os.path.exists(md_path) and os.path.getsize(md_path) > 200:
            print(f'[{i+1:3d}/{len(leaf_items)}] SKIP (已存在): {title}')
            success += 1
            continue

        print(f'[{i+1:3d}/{len(leaf_items)}] {category} / {title} ... ', end='', flush=True)

        before = snap_temp()
        win32api.SendMessage(tree_hwnd, TVM_SELECTITEM, TVGN_CARET, hitem)

        new_htm = wait_new_htm(before)

        if new_htm and os.path.getsize(new_htm) > 300:
            try:
                md = htm_to_md(new_htm, title)
                open(md_path, 'w', encoding='utf-8').write(md)
                kb = os.path.getsize(md_path) // 1024
                print(f'OK ({kb} KB)')
                success += 1
            except Exception as e:
                print(f'ERR: {e}')
                failed.append(title)
        else:
            print('TIMEOUT/EMPTY')
            failed.append(title)

        time.sleep(STEP_SEC)

    rmem.close()

    print()
    print('=' * 60)
    print(f'完成! 成功 {success} / {len(leaf_items)}')
    if failed:
        print(f'失败 {len(failed)} 本:')
        for f in failed[:15]: print(f'  - {f}')
    print(f'输出: {OUTPUT_BASE}')
    print('=' * 60)


if __name__ == '__main__':
    main()
