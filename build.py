#!/usr/bin/env python3
"""一人一码 · 批量生成脚本

读 members.json（人员名单）→ 为每位人员生成：
  1. 独立信息页   people/<id>.html   （扫码只看到本人信息）
  2. 专属二维码   qr/<id>.png        （指向对应信息页）
  3. 管理总览页   index.html         （社区管理用，含全部二维码，不含隐私）

用法:  python3 build.py
改完 members.json 后重跑，再 git push 即可。
依赖: pip install qrcode pillow
"""
import json, os
from gen_qr import make_qr

BASE = "https://yolo23530.github.io/care-qr/"

def build_overview(members):
    cards = ""
    for m in members:
        url = BASE + "people/" + m["id"] + ".html"
        cards += f'''
        <div class="mcard">
          <img class="mqr" src="qr/{m['id']}.png" alt="{m['name']}的二维码">
          <div class="minfo">
            <div class="mno">NO.{m.get('no','')}</div>
            <div class="mname">{m['name']}</div>
            <div class="mmeta">{m.get('gender','')} · {m.get('age','')}岁 · {m.get('addr','')}</div>
            <a class="mlink" href="{url}" target="_blank">打开信息页</a>
          </div>
        </div>'''
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>关怀码管理总览 · 内部使用</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;background:#f5f1ea;color:#2b2118;}}
  .wrap{{max-width:900px;margin:0 auto;padding:24px 16px 48px;}}
  h1{{font-size:22px;color:#c9361a;margin-bottom:4px;}}
  .desc{{font-size:13px;color:#8a6b4c;margin-bottom:20px;}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;}}
  .mcard{{background:#fff;border-radius:14px;border:1px solid rgba(80,45,20,.08);padding:16px;display:flex;gap:14px;align-items:center;box-shadow:0 2px 8px rgba(80,45,20,.05);}}
  .mqr{{width:110px;height:110px;flex:none;}}
  .minfo .mno{{font-size:12px;color:#b06b3f;letter-spacing:1px;}}
  .minfo .mname{{font-size:18px;font-weight:700;margin:2px 0;}}
  .minfo .mmeta{{font-size:12.5px;color:#8a6b4c;}}
  .mlink{{display:inline-block;margin-top:8px;font-size:12.5px;color:#e8532f;text-decoration:none;border:1px solid #f0b69e;border-radius:999px;padding:3px 12px;}}
  .notefoot{{margin-top:24px;font-size:12px;color:#a99c8b;line-height:1.8;}}
</style>
</head>
<body>
<div class="wrap">
  <h1>社区关怀码 · 管理总览</h1>
  <div class="desc">共 {len(members)} 位特殊人员 · 本页仅社区内部管理使用，请勿对外转发</div>
  <div class="grid">{cards}</div>
  <div class="notefoot">
    说明：本总览页不含病史、住址等隐私信息；每个人的完整信息在各自的专属页面中，需家属验证码解锁。<br>
    打印：点击上方二维码图片另存，或用脚本生成的 qr/ 目录下 PNG（建议 5cm 以上）打印塑封。
  </div>
</div>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"总览页 index.html 已生成（{len(members)} 人）")

def main():
    members = json.load(open("members.json", encoding="utf-8"))
    tpl = open("template.html", encoding="utf-8").read()
    if "__DATA_JSON__" not in tpl:
        raise SystemExit("template.html 缺少 __DATA_JSON__ 占位符")
    os.makedirs("people", exist_ok=True)
    os.makedirs("qr", exist_ok=True)
    ids = {m["id"] for m in members}
    # 清理已删除人员的旧页面与旧二维码
    for d, ext in (("people", ".html"), ("qr", ".png")):
        for fn in os.listdir(d):
            if fn.endswith(ext) and fn[: -len(ext)] not in ids:
                os.remove(os.path.join(d, fn))
                print(f"  清理旧文件 {d}/{fn}")
    for m in members:
        if "id" not in m:
            raise SystemExit(f"成员缺少 id: {m.get('name','?')}")
        # 页面生成在 people/ 子目录，照片路径需换算为 ../assets/xxx
        m2 = dict(m)
        if m2.get("photo") and m2["photo"].startswith("assets/"):
            m2["photo"] = "../" + m2["photo"]
        # 注入数据（转义 </ 防止破坏脚本标签）
        data = json.dumps(m2, ensure_ascii=False).replace("</", "<\\/")
        page = tpl.replace("__DATA_JSON__", data)
        path = f"people/{m['id']}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        url = BASE + path
        make_qr(url, f"qr/{m['id']}.png")
        print(f"  [{m.get('no','?')}] {m['name']} -> {url}")
    build_overview(members)

if __name__ == "__main__":
    main()
