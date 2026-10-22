#!/usr/bin/env python3
"""Build offline EPUB 3 and a static reading site from shared XHTML sources."""
from pathlib import Path
import html
import shutil
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
TITLE = 'HotKey 源码实战：从热点探测到集群治理'
NS = {'h': 'http://www.w3.org/1999/xhtml'}
CSS = '''body{font-family:system-ui,"PingFang SC","Noto Sans CJK SC",sans-serif;line-height:1.9;color:#243445;background:#faf8f3;margin:0}main{max-width:48rem;margin:auto;padding:2rem 1.3rem 6rem}h1,h2{line-height:1.4;color:#132f42}h1{font-size:2rem;margin:2rem 0}h2{margin-top:2.5rem;font-size:1.3rem}p{text-align:justify}a{color:#146a78;text-underline-offset:.2em}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:1rem;background:#eaece8;border-radius:.4rem;font-size:.9rem;line-height:1.65}nav{display:flex;flex-wrap:wrap;gap:1rem;margin:2rem 0}li{margin:.7rem 0}.eyebrow{letter-spacing:.15em;color:#586c76}.cover{padding:3rem 0;border-bottom:3px solid #146a78}.meta{color:#586c76;font-size:.9rem}button,input{font:inherit}input{width:100%;box-sizing:border-box;padding:.6rem;border:1px solid #9aacab;border-radius:.3rem}footer{margin-top:3rem;border-top:1px solid #bbc7c5;padding-top:1rem}@media(prefers-color-scheme:dark){body{background:#14232c;color:#d4dfdf}h1,h2{color:#e0eeee}a{color:#86c9ce}pre{background:#233742}.meta,.eyebrow{color:#acc2c8}}'''

def page(title, body, epub=False):
    extra = ' xmlns:epub="http://www.idpf.org/2007/ops"' if epub else ''
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
        f'<html xmlns="http://www.w3.org/1999/xhtml"{extra} lang="zh-CN" xml:lang="zh-CN"><head>'
        f'<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>'
        f'<title>{html.escape(title)}</title><link rel="stylesheet" href="style.css"/></head><body><main>{body}</main></body></html>')

def build():
    OUT.mkdir(exist_ok=True)
    chapters = []
    for path in sorted((ROOT / 'book/chapters').glob('*.xhtml')):
        section = ET.fromstring(path.read_text())
        title = section.find('h:h1', NS).text
        # Preserve the authored XHTML without namespace-prefix rewriting.
        body = path.read_text().strip()
        chapters.append((path.stem, title, body))
    assert len(chapters) == 12
    toc = '<ol>' + ''.join(f'<li><a href="{i}.html">{html.escape(t)}</a></li>' for i,t,_ in chapters) + '</ol>'
    intro = (f'<div class="cover"><p class="eyebrow">SOURCE CODE / ENGINEERING</p><h1>{TITLE}</h1>'
        '<p>以一次请求为线索，读懂 Java 热点探测系统的设计、边界与实践。</p>'
        '<p class="meta">12 章 · 中文原创讲解 · 源码基线 f1c8181</p>'
        '<nav><a href="01.html">开始阅读 →</a><a href="hotkey-sourcebook.epub" download="download">下载 EPUB</a>'
        '<a href="https://github.com/Aias00/hotkey-book">GitHub 源码</a></nav></div>')
    OUT.joinpath('index.html').write_text(page(TITLE, intro + '<h2>目录</h2>'+toc))
    OUT.joinpath('style.css').write_text(CSS)
    for n,(i,t,b) in enumerate(chapters):
        links = '<a href="index.html">目录</a>'
        if n: links += f'<a href="{chapters[n-1][0]}.html">← 上一章</a>'
        if n+1<len(chapters): links += f'<a href="{chapters[n+1][0]}.html">下一章 →</a>'
        OUT.joinpath(i+'.html').write_text(page(t, '<nav>'+links+'</nav>'+b+'<footer><nav>'+links+'</nav></footer>'))
    with zipfile.ZipFile(OUT/'hotkey-sourcebook.epub','w') as z:
        z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
        def put(name, data): z.writestr(name,data,compress_type=zipfile.ZIP_DEFLATED)
        put('META-INF/container.xml','''<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>''')
        manifest = '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="style.css" media-type="text/css"/>'
        spine = ''
        for i,t,b in chapters:
            put('OEBPS/'+i+'.xhtml',page(t,b,True))
            manifest += f'<item id="c{i}" href="{i}.xhtml" media-type="application/xhtml+xml"/>'
            spine += f'<itemref idref="c{i}"/>'
        nav = '<nav epub:type="toc" id="toc"><h1>'+TITLE+'</h1><ol>'+''.join(f'<li><a href="{i}.xhtml">{html.escape(t)}</a></li>' for i,t,_ in chapters)+'</ol></nav>'
        put('OEBPS/nav.xhtml',page(TITLE,nav,True))
        put('OEBPS/style.css',CSS)
        put('OEBPS/package.opf',f'''<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:uuid:9f8482f6-079e-4ce4-8355-9212760f97d3</dc:identifier><dc:title>{TITLE}</dc:title><dc:language>zh-CN</dc:language><dc:creator>Aias00 · 源码研读与 AI 辅助编写</dc:creator><dc:rights>Apache-2.0; HotKey 原项目权利归原作者所有</dc:rights><meta property="dcterms:modified">2026-10-22T00:00:00Z</meta></metadata><manifest>{manifest}</manifest><spine>{spine}</spine></package>''')
    print(f'Built {len(chapters)} chapters; {sum(len(b) for _,_,b in chapters)} source characters')

if __name__ == '__main__': build()
