# -*- coding: utf-8 -*-
"""
生成考研政治一页纸智能背诵与刷题精简纯净版 (zhengz_recite_app_lite.html)
特点：
1. 彻底剔除所有 PDF 原图及思维导图切图资源，生成极致轻量级网页（约 1 MB）
2. 隐藏所有与原图相关的按键（如“查看 PDF 原文高清裁切图”、“原图思维导图”、“原图对照弹窗”等）
3. 完美保留所有文本核心功能：122 张背诵卡片、Cloze 遮挡复诵、SRS 记忆曲线、10 类解题手法、四大思维心法、名言库、18 墓碑词雷达
4. 保留所有手机端防边缘误退、防浏览器底栏遮挡等交互优化
"""

import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

# 读取数据
with open("data/knowledge.json", "r", encoding="utf-8") as f:
    kb_data = json.load(f)
records_json_str = json.dumps(kb_data["records"], ensure_ascii=False)
import base64
import glob

print("Embedding symbols into standalone HTML...")
image_b64_map = {}
for p in glob.glob("public/symbols/*.*"):
    rel = os.path.relpath(p, "public").replace(os.sep, "/")
    ext = "jpeg" if p.lower().endswith((".jpg", ".jpeg")) else "png"
    with open(p, "rb") as img_f:
        image_b64_map[rel] = f"data:image/{ext};base64," + base64.b64encode(img_f.read()).decode("ascii")
images_json_str = json.dumps(image_b64_map, ensure_ascii=False)


with open("data/methods.json", "r", encoding="utf-8") as f:
    methods_json_str = json.dumps(json.load(f), ensure_ascii=False)

with open("data/questions.json", "r", encoding="utf-8") as f:
    questions_json_str = json.dumps(json.load(f), ensure_ascii=False)

with open("data/mindsets.json", "r", encoding="utf-8") as f:
    mindsets_json_str = json.dumps(json.load(f), ensure_ascii=False)

vue_js_path = "node_modules/vue/dist/vue.global.prod.js"
if os.path.exists(vue_js_path):
    with open(vue_js_path, "r", encoding="utf-8") as f:
        vue_script_content = f.read()
    vue_tag = f"<script>{vue_script_content}</script>"
    print("Embedded local Vue 3 prod runtime (100% offline ready).")
else:
    vue_tag = '<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>'

html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=5.0, user-scalable=yes, viewport-fit=cover">
  <title>2027考研政治一页纸 · 智能背诵与真题解题刷题全功能发布版</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📖</text></svg>">
  __VUE_TAG__
  <style>
    :root {
      --bg-warm: #fbf9f5;
      --bg-card: #ffffff;
      --bg-beige: #f5efe6;
      --bg-beige-light: #faf6f0;
      --border-card: #e5ded2;
      --border-light: #ebe4d8;
      
      --text-main: #1f1d1a;
      --text-regular: #3d3934;
      --text-muted: #736d64;
      --text-light: #948d82;

      --primary-accent: #2e6297;
      --primary-accent-bg: #eef4fb;
      --success-accent: #2e7d4a;
      --success-accent-bg: #edf7f0;
      --warning-accent: #b46b1d;
      --warning-accent-bg: #fdf5ea;
      --danger-accent: #b53838;
      --danger-accent-bg: #fdf1f1;

      --shadow-sm: 0 1px 3px rgba(31, 29, 26, 0.05);
      --shadow-md: 0 4px 14px rgba(31, 29, 26, 0.07);
      --shadow-lg: 0 10px 25px rgba(31, 29, 26, 0.1);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 16px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    html, body {
      overscroll-behavior-x: none; /* 彻底阻止手机左右滑动手势触发浏览器历史后退/前进退出 */
    }
    body {
      background-color: var(--bg-warm);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      line-height: 1.6;
      font-size: 16px;
      overflow-x: hidden;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }

    button { font-family: inherit; cursor: pointer; border: none; outline: none; user-select: none; transition: all 0.15s ease; touch-action: manipulation; }
    button:active { transform: scale(0.97); }

    .cloze-hidden {
      background-color: #dfd8cb !important;
      color: transparent !important;
      border-radius: 4px;
      padding: 1px 6px;
      margin: 0 2px;
      cursor: pointer;
      user-select: none;
      display: inline-block;
      min-width: 2.2em;
      transition: all 0.2s;
      box-shadow: inset 0 1px 2px rgba(0,0,0,0.08);
    }
    .cloze-hidden:hover { background-color: #d2cabb !important; }
    .cloze-revealed {
      background-color: rgba(223, 216, 203, 0.3);
      border-radius: 4px;
      padding: 1px 5px;
      margin: 0 2px;
      cursor: pointer;
      border-bottom: 2px dashed #b8ad9b;
      transition: all 0.2s;
    }
    .muted-text { color: #888075 !important; font-weight: normal !important; opacity: 0.88; }

    .font-small { font-size: 14px; }
    .font-medium { font-size: 16px; }
    .font-large { font-size: 18px; }
    .font-xlarge { font-size: 20px; }

    /* 顶部统一导航栏 */
    .nav-container {
      display: flex; align-items: center; justify-content: space-between;
      background: #ffffff; border-bottom: 1px solid var(--border-card);
      padding: 8px 20px; position: sticky; top: 0; z-index: 100;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03); height: 60px;
    }
    .nav-brand { display: flex; align-items: center; gap: 8px; cursor: pointer; user-select: none; }
    .brand-badge { background: var(--primary-accent); color: white; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
    .brand-title { font-size: 16px; font-weight: 700; color: var(--text-main); }
    .nav-links { display: flex; align-items: center; gap: 6px; }
    .nav-btn {
      display: flex; align-items: center; gap: 6px; padding: 7px 14px;
      border-radius: var(--radius-md); background: transparent; color: var(--text-regular);
      font-size: 14px; font-weight: 500; position: relative;
    }
    .nav-btn:hover { background: var(--bg-beige-light); }
    .nav-btn.active { background: var(--bg-beige); color: var(--text-main); font-weight: 700; }
    .badge-count {
      background: var(--primary-accent); color: white; font-size: 10px; font-weight: 700;
      padding: 1px 5px; border-radius: 10px; min-width: 16px; text-align: center;
    }
    .badge-count.mistake { background: var(--danger-accent); }
    .icon-btn {
      background: var(--bg-beige-light); border: 1px solid var(--border-light);
      font-size: 16px; width: 36px; height: 36px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
    }

    .page-container { max-width: 900px; margin: 0 auto; padding: 16px 16px calc(80px + env(safe-area-inset-bottom, 20px)) 16px; display: flex; flex-direction: column; gap: 16px; }

    /* 卡片通用样式 */
    .card-container {
      background: var(--bg-card); border: 1px solid var(--border-card);
      border-radius: var(--radius-lg); box-shadow: var(--shadow-sm);
      overflow: hidden; display: flex; flex-direction: column;
    }
    .card-header {
      background: var(--bg-beige); border-bottom: 1px solid var(--border-light);
      padding: 10px 18px; display: flex; justify-content: space-between; align-items: center;
    }
    .header-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .source-id-tag {
      background: #ffffff; border: 1px solid var(--border-card); color: var(--text-main);
      font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 4px;
    }
    .hierarchy-tag { font-size: 12px; color: var(--text-muted); font-weight: 500; }
    .fav-btn {
      background: #ffffff; border: 1px solid var(--border-card);
      padding: 4px 10px; border-radius: 20px; font-size: 12px; color: var(--text-muted);
    }
    .fav-btn.active { color: #d97706; border-color: #f59e0b; background: #fffbeb; font-weight: 700; }
    .card-title-bar {
      padding: 16px 20px 8px 20px; display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px;
    }
    .kp-title { font-size: 1.35em; font-weight: 700; color: var(--text-main); }
    .page-hint { font-size: 0.85em; color: var(--text-light); }

    .full-cover {
      padding: 70px 20px; background: #f7f1e7; text-align: center; cursor: pointer;
      border-top: 1px dashed var(--border-light); border-bottom: 1px dashed var(--border-light);
    }
    .card-body { padding: 14px 20px 20px 20px; display: flex; flex-direction: column; gap: 16px; }
    .cloze-toolbar {
      display: flex; justify-content: space-between; align-items: center;
      padding: 6px 12px; background: var(--bg-beige-light); border-radius: var(--radius-sm); font-size: 12px;
    }
    .tool-link { background: none; color: var(--primary-accent); font-size: 12px; font-weight: 600; padding: 2px 6px; }
    .content-text { line-height: 2.0; font-size: 1.05em; word-break: break-word; }
    .keyword-highlight {
      font-weight: 700 !important; display: inline; padding: 1px 3px; border-radius: 4px;
      background: rgba(46, 98, 151, 0.08); border-bottom: 1.5px solid var(--kw-color, currentColor);
      box-decoration-break: clone; -webkit-box-decoration-break: clone;
    }
    .distinctions-box {
      background: #faf6f0; border-radius: var(--radius-md); border-left: 3px solid var(--warning-accent);
      padding: 10px 14px; display: flex; flex-direction: column; gap: 8px;
    }
    .dist-title { font-size: 13px; font-weight: 700; color: var(--warning-accent); }
    .dist-item { font-size: 0.9em; display: flex; align-items: flex-start; gap: 6px; }
    .dist-badge {
      font-size: 10px; font-weight: 700; padding: 1px 5px; border-radius: 3px; flex-shrink: 0; margin-top: 2px;
    }
    .dist-badge.correct { background: var(--success-accent-bg); color: var(--success-accent); border: 1px solid #cce8d5; }
    .dist-badge.wrong { background: var(--danger-accent-bg); color: var(--danger-accent); border: 1px solid #f8c8c8; }
    .dist-badge.unclear { background: var(--warning-accent-bg); color: var(--warning-accent); border: 1px solid #f6dfbe; }

    .mnemonics-box {
      background: #edf7f0; border-radius: var(--radius-md); border-left: 3px solid var(--success-accent);
      padding: 10px 14px; display: flex; flex-direction: column; gap: 6px;
    }
    .mnemonic-item { font-size: 0.95em; color: #1e5631; font-weight: 600; display: flex; align-items: flex-start; gap: 6px; }
    .symbol-sticker {
      display: inline-block; vertical-align: middle; line-height: 1; margin: 0 2px;
      cursor: pointer; position: relative; user-select: none; -webkit-user-select: none;
    }
    .symbol-sticker-img {
      height: 1.35em; width: auto; max-width: 2.2em; vertical-align: -0.22em;
      display: inline-block; object-fit: contain;
      transition: transform 0.18s cubic-bezier(0.34, 1.56, 0.64, 1);
      filter: drop-shadow(0 1px 1.5px rgba(0, 0, 0, 0.10));
    }
    .symbol-sticker:hover .symbol-sticker-img,
    .symbol-sticker:active .symbol-sticker-img {
      transform: scale(1.25) translateY(-1.5px);
      filter: drop-shadow(0 3px 4px rgba(0, 0, 0, 0.18));
    }
    .symbol-fallback {
      font-size: 0.85em; color: #92400e; background: #fef3c7; padding: 1px 4px; border-radius: 4px;
    }
    
    /* 考点对应真题与模拟题区域 (借鉴 Markji 一页纸逻辑) */
    .related-questions-section {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-left: 4px solid #3b82f6;
      border-radius: var(--radius-md, 8px);
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 14px;
    }
    .related-badge {
      color: #1e40af;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 12px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.9em;
    }
    .related-count-pill {
      font-size: 0.85em;
      background: #dbeafe;
      color: #1d4ed8;
      padding: 1px 8px;
      border-radius: 12px;
      font-weight: 700;
    }
    .related-groups-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .question-source-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .source-group-header {
      display: flex;
      align-items: center;
    }
    .source-tag, .q-source-tag {
      font-size: 0.8em;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
    }
    .true-tag, .tag-true {
      background: #fee2e2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }
    .mock-tag, .tag-mock {
      background: #e0f2fe;
      color: #075985;
      border: 1px solid #bae6fd;
    }
    .question-pill-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .q-pill-btn {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      color: #334155;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.85em;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .q-pill-btn:hover {
      border-color: #3b82f6;
      color: #1d4ed8;
      background: #f0f7ff;
      transform: translateY(-1px);
    }
    .q-pill-btn.answered-right {
      border-color: #86efac;
      background: #f0fdf4;
      color: #166534;
    }
    .q-pill-btn.answered-wrong {
      border-color: #fca5a5;
      background: #fef2f2;
      color: #991b1b;
    }
    .q-status-badge {
      font-size: 0.85em;
      font-weight: 800;
    }
    .q-status-badge.right { color: #16a34a; }
    .q-status-badge.wrong { color: #dc2626; }

    /* 题目练习弹窗样式 (Markji 答题逻辑) */
    .q-modal-backdrop {
      position: fixed; inset: 0; background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(4px); z-index: 1000;
      display: flex; justify-content: center; align-items: center;
      padding: 16px; animation: fadeIn 0.18s ease-out;
    }
    .q-modal-container {
      background: #ffffff; width: 100%; max-width: 680px; max-height: 90vh;
      border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
      display: flex; flex-direction: column; overflow: hidden; border: 1px solid #e2e8f0;
    }
    .q-modal-header {
      padding: 14px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
      display: flex; justify-content: space-between; align-items: center;
    }
    .q-header-badges { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .q-label-tag { font-size: 0.85em; font-weight: 700; color: #334155; background: #f1f5f9; padding: 2px 8px; border-radius: 6px; }
    .q-kind-tag { font-size: 0.8em; color: #64748b; }
    .q-close-btn { background: none; border: none; font-size: 1.2em; color: #94a3b8; cursor: pointer; padding: 4px 8px; border-radius: 6px; }
    .q-close-btn:hover { background: #e2e8f0; color: #1e293b; }
    .q-modal-body { padding: 20px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 16px; -webkit-overflow-scrolling: touch; }
    .q-stem-text { font-size: 1.05em; line-height: 1.65; color: #1e293b; font-weight: 600; }
    .q-num-prefix { color: var(--primary-accent, #98521c); margin-right: 4px; }
    .q-options-list { display: flex; flex-direction: column; gap: 10px; }
    .q-option-item {
      display: flex; align-items: center; gap: 12px; padding: 12px 14px;
      border: 1.5px solid #e2e8f0; border-radius: 10px; background: #ffffff;
      cursor: pointer; transition: all 0.15s ease; user-select: none;
    }
    .q-option-item:hover:not(.correct):not(.wrong) { border-color: #cbd5e1; background: #f8fafc; }
    .q-option-item.selected:not(.correct):not(.wrong) {
      border-color: var(--primary-accent, #98521c); background: #fdf8f4;
    }
    .q-option-item.selected .q-opt-letter-box {
      background: var(--primary-accent, #98521c); color: #ffffff; border-color: var(--primary-accent, #98521c);
    }
    .q-opt-letter-box {
      width: 28px; height: 28px; border-radius: 50%; border: 1.5px solid #cbd5e1;
      display: flex; align-items: center; justify-content: center;
      font-size: 0.88em; font-weight: 700; color: #475569; flex-shrink: 0;
    }
    .q-opt-content { flex: 1; font-size: 0.95em; color: #334155; line-height: 1.5; }
    .q-option-item.correct { border-color: #22c55e; background: #f0fdf4; }
    .q-option-item.correct .q-opt-letter-box { background: #22c55e; border-color: #22c55e; color: #ffffff; }
    .q-option-item.wrong { border-color: #ef4444; background: #fef2f2; }
    .q-option-item.wrong .q-opt-letter-box { background: #ef4444; border-color: #ef4444; color: #ffffff; }
    .q-opt-feedback-icon { font-size: 0.8em; font-weight: 700; }
    .icon-right { color: #16a34a; }
    .icon-wrong { color: #dc2626; }
    .q-action-bar { margin-top: 4px; }
    .q-submit-btn {
      width: 100%; padding: 12px; background: var(--primary-accent, #98521c);
      color: #ffffff; border: none; border-radius: 10px; font-size: 1em; font-weight: 700; cursor: pointer;
    }
    .q-submit-btn:disabled { background: #cbd5e1; cursor: not-allowed; opacity: 0.7; }
    .q-submitted-actions { display: flex; flex-direction: column; gap: 10px; }
    .q-result-banner {
      padding: 12px 16px; border-radius: 10px; display: flex; align-items: center; gap: 8px; font-size: 0.95em; font-weight: 700;
    }
    .result-right { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .result-wrong { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
    .q-retry-btn {
      align-self: flex-end; background: #f1f5f9; border: 1px solid #cbd5e1;
      color: #475569; padding: 6px 14px; border-radius: 6px; font-size: 0.85em; font-weight: 600; cursor: pointer;
    }
    .q-explanation-card {
      background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid var(--primary-accent, #98521c);
      border-radius: 8px; padding: 14px 16px; font-size: 0.9em; line-height: 1.65; color: #334155;
    }
    .q-exp-title { font-weight: 700; color: #1e293b; margin-bottom: 6px; }
    .q-exp-content { white-space: pre-wrap; }
    .q-linked-kp-box {
      padding: 8px 12px; background: #fffbeb; border: 1px solid #fef3c7; border-radius: 8px; font-size: 0.85em; color: #92400e;
    }
    .q-linked-name { font-weight: 700; }
    .q-modal-footer {
      padding: 12px 20px; background: #f8fafc; border-top: 1px solid #e2e8f0;
      display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
    }
    .q-footer-nav { display: flex; align-items: center; gap: 10px; }
    .q-nav-step-btn {
      background: #ffffff; border: 1px solid #cbd5e1; color: #334155;
      padding: 6px 12px; border-radius: 6px; font-size: 0.85em; font-weight: 600; cursor: pointer;
    }
    .q-nav-step-btn:disabled { opacity: 0.4; cursor: not-allowed; }
    .q-footer-counter { font-size: 0.85em; color: #64748b; font-weight: 600; }
    .q-footer-done-btn {
      background: #ffffff; border: 1.5px solid var(--primary-accent, #98521c);
      color: var(--primary-accent, #98521c); padding: 6px 16px; border-radius: 6px;
      font-size: 0.88em; font-weight: 700; cursor: pointer;
    }
    .q-footer-done-btn:hover { background: var(--primary-accent, #98521c); color: #ffffff; }

    /* 置顶考点脉络高清原图 (如考点037史纲脉络) */
    .card-inline-image-box {
      width: 100%;
      margin: 4px 0 16px 0;
      background: #ffffff;
      border: 1px solid var(--border-card);
      border-radius: 8px;
      padding: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      box-shadow: 0 1px 4px rgba(0,0,0,0.04);
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      box-sizing: border-box;
    }
    .card-inline-img {
      width: 100%;
      max-width: 100%;
      height: auto;
      border-radius: 6px;
      display: block;
      cursor: pointer;
      object-fit: contain;
      transition: width 0.2s ease, max-width 0.2s ease;
    }
    .card-inline-img.zoomed {
      width: 180%;
      max-width: none;
    }
    .inline-img-tip {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 6px;
      text-align: center;
      user-select: none;
    }

    .card-footer {
      border-top: 1px solid var(--border-light); padding: 10px 20px; background: #faf8f5;
      display: flex; justify-content: space-between; align-items: center; font-size: 0.85em; flex-wrap: wrap; gap: 8px;
    }

    /* SRS 评价区域 */
    .eval-box {
      background: var(--bg-card); border: 1px solid var(--border-card);
      border-radius: var(--radius-lg); padding: 16px; display: flex; flex-direction: column; gap: 12px;
    }
    .eval-title { font-size: 14px; font-weight: 700; color: var(--text-muted); text-align: center; }
    .eval-buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
    .eval-btn { padding: 12px 6px; border-radius: var(--radius-md); display: flex; flex-direction: column; align-items: center; gap: 4px; border: 1px solid transparent; }
    .btn-again { background: #fee2e2; color: #991b1b; border-color: #fca5a5; }
    .btn-hard { background: #ffedd5; color: #9a3412; border-color: #fed7aa; }
    .btn-good { background: #dbeafe; color: #1e40af; border-color: #bfdbfe; }
    .btn-easy { background: #dcfce7; color: #166534; border-color: #bbf7d0; }
    .btn-key { font-size: 10px; font-weight: 700; opacity: 0.6; }
    .btn-main { font-size: 14px; font-weight: 700; }
    .btn-sub { font-size: 11px; opacity: 0.85; }

    /* 解决初始加载 FOUC 闪烁与弹窗误显 */
    [v-cloak] { display: none !important; }
    template { display: none !important; }

    /* 弹窗通用 */
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(31, 29, 26, 0.7); backdrop-filter: blur(4px);
      z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 16px;
    }
    .modal-dialog { background: #ffffff; border-radius: var(--radius-lg); width: 100%; max-width: 760px; max-height: 90vh; overflow-y: auto; box-shadow: var(--shadow-lg); }
    .modal-header { padding: 14px 20px; border-bottom: 1px solid var(--border-light); display: flex; justify-content: space-between; align-items: center; }

    /* 首页仪表盘 */
    .welcome-card { background: var(--bg-card); border: 1px solid var(--border-card); border-radius: var(--radius-lg); padding: 20px; display: flex; flex-direction: column; gap: 16px; }
    .welcome-header { display: flex; justify-content: space-between; align-items: center; }
    .welcome-title { font-size: 20px; font-weight: 800; color: var(--text-main); }
    .progress-ring { width: 64px; height: 64px; border-radius: 50%; background: conic-gradient(var(--primary-accent) calc(v-bind(progressPercent) * 1%), #ebe4d8 0); display: flex; align-items: center; justify-content: center; position: relative; }
    .progress-ring::before { content: ""; position: absolute; width: 48px; height: 48px; border-radius: 50%; background: #ffffff; }
    .ring-val { position: relative; z-index: 2; font-size: 14px; font-weight: 800; color: var(--text-main); }

    .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
    .stat-box { background: var(--bg-warm); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 12px; text-align: center; cursor: pointer; }
    .stat-box:hover { border-color: var(--border-card); }
    .stat-box.box-due { border-color: #fbcfe8; background: #fdf2f8; }
    .stat-box.box-due .stat-num { color: #be185d; }
    .stat-box.box-mistake { border-color: #fecaca; background: #fef2f2; }
    .stat-box.box-mistake .stat-num { color: #b91c1c; }
    .stat-box.box-mastered { border-color: #bbf7d0; background: #f0fdf4; }
    .stat-box.box-mastered .stat-num { color: #15803d; }
    .stat-num { font-size: 22px; font-weight: 800; color: var(--text-main); }

    .action-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
    .action-card { background: #ffffff; border: 1.5px solid var(--border-card); border-radius: var(--radius-lg); padding: 16px; display: flex; align-items: center; gap: 14px; cursor: pointer; }
    .action-card.card-primary { border-color: var(--primary-accent); background: #f4f8fd; }
    .action-card.card-secondary { border-color: var(--warning-accent); background: #fdfaf5; }
    .card-icon { font-size: 28px; }

    /* 知识库浏览多栏/抽屉布局 */
    .browse-layout { display: flex; height: calc(100vh - 60px); overflow: hidden; position: relative; }
    .browse-sidebar { width: 300px; border-right: 1px solid var(--border-card); background: #ffffff; display: flex; flex-direction: column; flex-shrink: 0; z-index: 10; transition: transform 0.25s ease; }
    .sidebar-header { display: none; padding: 14px 16px; background: var(--bg-beige); border-bottom: 1px solid var(--border-light); justify-content: space-between; align-items: center; }
    .sidebar-title { font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    .count-pill { font-size: 11px; background: #fff; padding: 2px 6px; border-radius: 10px; border: 1px solid var(--border-card); }
    .drawer-close-btn { background: none; font-size: 18px; color: var(--text-muted); }
    .search-box { padding: 12px; border-bottom: 1px solid var(--border-light); background: var(--bg-beige-light); position: relative; }
    .search-input { width: 100%; padding: 8px 12px; border: 1px solid var(--border-card); border-radius: var(--radius-sm); font-size: 13px; background: #fff; }
    .subject-tabs { display: flex; padding: 6px 10px; gap: 4px; background: #fafaf8; border-bottom: 1px solid var(--border-light); overflow-x: auto; }
    .sub-tab { flex: 1; padding: 6px 8px; border-radius: var(--radius-sm); background: transparent; font-size: 12px; color: var(--text-muted); white-space: nowrap; text-align: center; }
    .sub-tab.active { background: var(--bg-beige); color: #78350f; font-weight: 700; }
    .card-nav-list { flex: 1; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 4px; }
    .nav-card-item { padding: 10px 12px; border-radius: var(--radius-sm); border: 1px solid transparent; cursor: pointer; transition: all 0.15s; }
    .nav-card-item:hover { background: var(--bg-beige-light); }
    .nav-card-item.active { background: #f4efe6; border-color: #dfd4c4; }

    .browse-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: var(--bg-warm); position: relative; }
    .browse-controls {
      padding: 10px 20px; background: #ffffff; border-bottom: 1px solid var(--border-light);
      display: flex; justify-content: space-between; align-items: center; gap: 8px; z-index: 5;
    }
    .controls-left { display: flex; align-items: center; gap: 10px; }
    .controls-right { display: flex; align-items: center; gap: 8px; }
    .desktop-arrows { display: flex; align-items: center; gap: 10px; }
    .ctrl-btn {
      padding: 6px 12px; border-radius: var(--radius-sm); background: var(--bg-beige-light);
      border: 1px solid var(--border-card); font-size: 13px; font-weight: 600; color: var(--text-regular);
      display: flex; align-items: center; gap: 6px;
    }
    .ctrl-btn:disabled { opacity: 0.35; cursor: not-allowed; }
    .drawer-trigger-btn { display: none; }
    .index-display { font-size: 13px; font-weight: 700; color: var(--text-muted); }

    .cloze-mode-stepper, .font-stepper {
      display: flex; background: var(--bg-beige-light); border: 1px solid var(--border-light);
      border-radius: var(--radius-sm); padding: 2px;
    }
    .mode-step-btn, .font-btn {
      padding: 4px 8px; background: transparent; font-size: 11px; font-weight: 600;
      color: var(--text-muted); border-radius: 4px; white-space: nowrap;
    }
    .mode-step-btn.active {
      background: var(--primary-accent); color: #ffffff; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .font-btn.active {
      background: #ffffff; color: var(--primary-accent); box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }

    .card-display-area {
      flex: 1; overflow-y: auto; padding: 20px; max-width: 860px; width: 100%; margin: 0 auto;
      scroll-behavior: smooth; -webkit-overflow-scrolling: touch;
    }
    .swipe-hint { display: none; text-align: center; font-size: 11px; color: var(--text-muted); margin-bottom: 8px; letter-spacing: 0.5px; }

    /* 移动端吸底操作条：紧凑且防止被浏览器底栏遮挡 */
    .mobile-bottom-bar {
      display: none; position: sticky; bottom: 0; left: 0; right: 0;
      background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(12px);
      border-top: 1px solid var(--border-card);
      padding: 8px 12px calc(12px + env(safe-area-inset-bottom, 10px));
      justify-content: space-between; align-items: center; gap: 8px; z-index: 50; box-shadow: 0 -4px 16px rgba(0,0,0,0.06);
    }
    .mobile-nav-btn {
      flex: 1; max-width: 115px; padding: 8px 10px; background: #ffffff; border: 1px solid var(--border-card);
      border-radius: 8px; font-size: 13px; font-weight: 600; display: flex; align-items: center; justify-content: center;
    }
    .mobile-nav-btn:disabled { opacity: 0.35; }
    .mobile-index-chip { padding: 6px 14px; background: var(--bg-beige); border-radius: 20px; font-size: 12px; font-weight: 700; color: #78350f; cursor: pointer; }
    .drawer-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.45); backdrop-filter: blur(2px); z-index: 999; }

    @keyframes fadeIn {
      from { opacity: 0; transform: scale(0.98); }
      to { opacity: 1; transform: scale(1); }
    }
    @keyframes slideUpSheet {
      from { transform: translateY(100%); }
      to { transform: translateY(0); }
    }

    /* ================= 手机端响应式深度优化 (<= 768px) ================= */
    @media (max-width: 768px) {
      body { font-size: 15px; }
      .nav-container { padding: 6px 10px; height: 52px; gap: 6px; }
      .brand-title { display: none; }
      .brand-badge { font-size: 11px; padding: 3px 6px; border-radius: 6px; }
      .nav-links {
        flex: 1; justify-content: center; background: var(--bg-beige-light);
        padding: 3px; border-radius: 10px; border: 1px solid var(--border-light);
        gap: 4px; max-width: 310px;
      }
      .nav-btn {
        flex: 1; justify-content: center; padding: 6px 8px;
        flex-direction: row; gap: 4px; border-radius: 7px; white-space: nowrap;
      }
      .nav-btn.active {
        background: #ffffff; color: var(--primary-accent);
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      }
      .nav-btn .icon { font-size: 14px; line-height: 1; }
      .nav-btn .label { font-size: 12.5px; font-weight: 700; }
      .icon-btn { width: 32px; height: 32px; font-size: 14px; flex-shrink: 0; }

      .page-container { padding: 12px 10px calc(60px + env(safe-area-inset-bottom, 16px)) 10px; gap: 12px; }

      .browse-layout { height: calc(100vh - 52px); height: calc(100dvh - 52px); }
      .browse-sidebar {
        position: fixed; top: 0; left: 0; bottom: 0; width: 84%; max-width: 320px; height: 100vh; height: 100dvh;
        z-index: 1000; transform: translateX(-100%);
      }
      .browse-sidebar.drawer-open { transform: translateX(0); box-shadow: 4px 0 25px rgba(0,0,0,0.25); }
      .sidebar-header { display: flex; }
      .drawer-trigger-btn { display: flex; padding: 5px 9px; font-size: 12px; }
      .desktop-arrows { display: none !important; }
      .browse-controls { padding: 6px 10px; gap: 6px; flex-wrap: wrap; }
      .controls-right { gap: 6px; }
      .mode-step-btn, .font-btn { padding: 4px 6px; font-size: 11px; }
      .card-display-area { 
        padding: 8px 8px calc(86px + env(safe-area-inset-bottom, 16px)) 8px; 
        touch-action: pan-y pinch-zoom;
      }
      .swipe-hint { display: block; font-size: 10.5px; margin-bottom: 6px; }
      .mobile-bottom-bar { display: flex !important; }

      .card-container { border-radius: 12px; }
      .card-header { padding: 8px 12px; gap: 6px; }
      .source-id-tag { font-size: 11px; padding: 2px 7px; }
      .hierarchy-tag { font-size: 11px; }
      .fav-btn { padding: 3px 8px; font-size: 11px; }
      .card-title-bar { padding: 10px 12px 4px 12px; flex-direction: row; align-items: center; justify-content: space-between; gap: 6px; }
      .kp-title { font-size: 1.18em; line-height: 1.32; }
      .page-hint { font-size: 0.75em; }
      .card-body { padding: 10px 12px 14px 12px; gap: 12px; }
      .content-text { line-height: 1.88; letter-spacing: 0.2px; font-size: 1em; }
      .distinctions-box, .mnemonics-box, .related-questions-section { padding: 10px 12px; gap: 8px; }
      .q-pill-btn { padding: 5px 10px; min-height: 31px; font-size: 12.5px; }
      .card-footer { padding: 8px 12px; }

      /* 题目练习弹窗手机端底部抽屉式 (Bottom Sheet) */
      .q-modal-backdrop { align-items: flex-end; padding: 0; }
      .q-modal-container {
        max-width: 100%; max-height: 88vh; max-height: 88dvh;
        border-radius: 18px 18px 0 0; border-bottom: none;
        animation: slideUpSheet 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      }
      .q-modal-header { padding: 12px 14px; }
      .q-header-badges { gap: 6px; }
      .q-source-tag, .q-label-tag, .q-kind-tag { font-size: 12px; }
      .q-modal-body { padding: 14px; gap: 12px; }
      .q-stem-text { font-size: 0.98em; line-height: 1.6; }
      .q-options-list { gap: 8px; }
      .q-option-item { padding: 10px 12px; gap: 10px; }
      .q-opt-letter-box { width: 26px; height: 26px; font-size: 0.82em; }
      .q-opt-content { font-size: 0.92em; line-height: 1.45; }
      .q-submit-btn { padding: 11px; font-size: 0.95em; }
      .q-explanation-card { padding: 12px; font-size: 0.88em; }
      .q-modal-footer {
        padding: 10px 14px calc(12px + env(safe-area-inset-bottom, 10px));
        gap: 8px; flex-wrap: nowrap;
      }
      .q-footer-nav { gap: 6px; }
      .q-nav-step-btn, .q-footer-done-btn { padding: 6px 10px; font-size: 12px; white-space: nowrap; }
      .q-footer-counter { font-size: 12px; white-space: nowrap; }

      /* 刷题页手机端优化 */
      .solve-sub-nav {
        top: 52px; margin: -12px -10px 2px -10px; padding: 8px 10px;
        scrollbar-width: none; -webkit-overflow-scrolling: touch;
      }
      .solve-sub-nav::-webkit-scrollbar { display: none; }
      .sub-pill { padding: 5px 11px; font-size: 12px; }
      .welcome-card { padding: 14px; gap: 10px; }
      .methods-grid-std, .mindset-grid-std, .tombstones-grid-std { grid-template-columns: 1fr !important; gap: 12px; }
      .mindset-nav-tabs { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
      .mindset-nav-tabs .sub-pill { text-align: center; justify-content: center; padding: 7px 6px; font-size: 11.5px; overflow: hidden; text-overflow: ellipsis; }
      .mindset-strip-bar { flex-direction: column; align-items: flex-start; gap: 6px; padding: 8px 10px; }
      .mindset-strip-btn { align-self: flex-end; flex-shrink: 0; white-space: nowrap; }

      .stat-grid { grid-template-columns: repeat(2, 1fr); }
      .action-grid { grid-template-columns: 1fr; }
      .eval-buttons { grid-template-columns: repeat(2, 1fr); }
    }

    /* 解题模块样式 */
    .solve-sub-nav { display: flex; gap: 8px; overflow-x: auto; padding: 10px 16px; background: #fff; border-bottom: 1px solid var(--border-card); position: sticky; top: 60px; z-index: 90; }
    .sub-pill { padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; color: var(--text-muted); background: var(--bg-warm); border: 1px solid var(--border-light); white-space: nowrap; cursor: pointer; }
    .sub-pill.active { background: var(--primary-accent-bg); color: var(--primary-accent); border-color: var(--primary-accent); }
    .methods-grid-std { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; margin-top: 14px; }
    .method-card-std { background: #fff; border: 1px solid var(--border-card); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
    .mnemonic-box { background: #fbf7ee; border: 1px solid #ebd7b5; border-left: 3px solid #c9791f; padding: 6px 10px; border-radius: 4px; font-size: 13px; color: #7b4c10; font-weight: 600; }
    .kw-pill { background: #fdeee0; color: #b34a17; font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; border: 1px solid #f9d8c0; }
    .opt-std-item { display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px; border-radius: 8px; border: 1.5px solid var(--border-light); background: #fff; cursor: pointer; margin-bottom: 8px; }
    .opt-std-item.selected { border-color: var(--primary-accent); background: var(--primary-accent-bg); }
    .opt-std-item.correct-rev { border-color: var(--success-accent) !important; background: var(--success-accent-bg) !important; }
    .opt-std-item.wrong-rev { border-color: var(--danger-accent) !important; background: var(--danger-accent-bg) !important; }
    .opt-bubble-std { min-width: 26px; height: 26px; border-radius: 50%; background: var(--bg-warm); border: 1px solid var(--border-card); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; flex-shrink: 0; }
    .opt-std-item.selected .opt-bubble-std { background: var(--primary-accent); color: #fff; }
    .opt-std-item.correct-rev .opt-bubble-std { background: var(--success-accent); color: #fff; }
    .opt-std-item.wrong-rev .opt-bubble-std { background: var(--danger-accent); color: #fff; }
    .hit-tag-std { background: #fbf5ea; color: #9b5a14; border: 1px solid #ebd4b0; padding: 2px 7px; border-radius: 4px; font-size: 12px; font-weight: 600; display: inline-block; }
    .tip-box-std { background: #fdfaf4; border: 1px solid #eedec7; border-left: 4px solid #b46b1d; border-radius: 6px; padding: 12px; font-size: 13px; color: #3b3327; line-height: 1.6; }
    .heatmap-table-std { width: 100%; border-collapse: collapse; font-size: 12px; }
    .heatmap-table-std th, .heatmap-table-std td { border: 1px solid var(--border-light); padding: 6px 4px; text-align: center; }

    /* 解题思维与命题挖坑增强样式 */
    .mindset-nav-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
    .mindset-grid-std { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 14px; margin-top: 14px; }
    .mindset-card-std { background: #fff; border: 1px solid var(--border-card); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
    .mindset-item-top { display: flex; align-items: flex-start; gap: 10px; }
    .mindset-num-icon { font-size: 20px; line-height: 1; }
    .mindset-badge-tag { background: #eef2ff; color: #4338ca; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 4px; display: inline-block; margin-bottom: 4px; }
    .mindset-item-title { font-size: 15px; font-weight: 700; color: var(--text-main); }
    .mindset-item-summary { font-size: 13px; font-weight: 600; color: #1e3a8a; background: #f0fdf4; border-left: 3px solid #16a34a; padding: 6px 10px; border-radius: 4px; line-height: 1.5; }
    .mindset-details-list { font-size: 12px; color: var(--text-regular); padding-left: 18px; line-height: 1.6; display: flex; flex-direction: column; gap: 4px; }

    .quote-card-std { background: #fff; border: 1px solid var(--border-card); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; gap: 8px; }
    .quote-text-std { font-size: 14px; font-weight: 700; color: var(--text-main); line-height: 1.6; font-style: italic; }
    .quote-meta-std { font-size: 12px; color: var(--text-muted); display: flex; gap: 8px; }
    .quote-alert-std { font-size: 12px; background: #fff7ed; border-left: 3px solid #ea580c; padding: 6px 10px; border-radius: 4px; color: #9a3412; line-height: 1.5; }

    .tombstones-grid-std { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; margin-top: 14px; }
    .tombstone-card-std { background: #fff; border: 1px solid var(--border-card); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; gap: 6px; }

    .mindset-strip-bar { background: #f0f4ff; border: 1px solid #c7d2fe; border-radius: 8px; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none; }
    .mindset-strip-left { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #1e3a8a; }
    .mindset-strip-btn { font-size: 12px; font-weight: 600; color: #4338ca; background: #e0e7ff; padding: 4px 8px; border-radius: 4px; }

    .trap-insight-box { background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #d97706; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 6px; font-size: 13px; }
    .deep-traps-box { background: #fef2f2; border: 1px solid #fecaca; border-left: 4px solid #ef4444; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 6px; font-size: 13px; }
    .guidance-box { background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 8px; font-size: 13px; }
  </style>
</head>
<body>
  <div id="app" v-cloak>
    <!-- 统一导航 -->
    <nav class="nav-container">
      <div class="nav-brand" @click="currentTab = 'browse'">
        <span class="brand-badge">2027</span>
        <span class="brand-title">一页纸背诵</span>
      </div>

      <div class="nav-links">
        <button :class="['nav-btn', { active: currentTab === 'browse' }]" @click="currentTab = 'browse'">
          <span class="icon">📖</span>
          <span class="label">知识点浏览背诵</span>
        </button>
        <button :class="['nav-btn', { active: currentTab === 'solve' }]" @click="currentTab = 'solve'">
          <span class="icon">✍️</span>
          <span class="label">真题模拟题刷题</span>
        </button>
      </div>

      <button class="icon-btn" title="数据备份与设置" @click="showSettingsModal = true">⚙️</button>
    </nav>

    <!-- 首页 -->
    <div v-if="currentTab === 'home'" class="page-container">
      <div class="welcome-card">
        <div class="welcome-header">
          <div>
            <h1 class="welcome-title">考研政治一页纸 · 智能背诵</h1>
            <p style="color:var(--text-muted); font-size:13px; margin-top:4px;">澄潇宇原书 100 个核心考点 · 122 张卡片逐条回溯 (轻量版)</p>
          </div>
          <div class="progress-ring">
            <span class="ring-val">{{ progressPercent }}%</span>
            <span style="font-size:10px; color:var(--text-muted);">总体掌握</span>
          </div>
        </div>

        <div class="stat-grid">
          <div class="stat-box box-due" @click="currentTab = 'recite'">
            <div class="stat-num">{{ dueCards.length }}</div>
            <div style="font-size:12px; color:var(--text-muted);">今日待背</div>
          </div>
          <div class="stat-box" @click="currentTab = 'browse'">
            <div class="stat-num">{{ learnedCount }}</div>
            <div style="font-size:12px; color:var(--text-muted);">已学考点</div>
          </div>
          <div class="stat-box box-mastered">
            <div class="stat-num">{{ masteredCount }}</div>
            <div style="font-size:12px; color:var(--text-muted);">熟练掌握</div>
          </div>
          <div class="stat-box box-mistake" @click="currentTab = 'mistakes'">
            <div class="stat-num">{{ mistakeCards.length }}</div>
            <div style="font-size:12px; color:var(--text-muted);">薄弱错题</div>
          </div>
        </div>

        <div class="action-grid">
          <div class="action-card card-primary" @click="currentTab = 'recite'">
            <div class="card-icon">🧠</div>
            <div>
              <div style="font-weight:700; font-size:16px;">开始今日复习</div>
              <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">艾宾浩斯智能排期 · 挖空记忆</div>
            </div>
          </div>
          <div class="action-card card-secondary" @click="currentTab = 'quiz'">
            <div class="card-icon">🎲</div>
            <div>
              <div style="font-weight:700; font-size:16px;">快速随机抽查</div>
              <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">不限范围 · 10 题速测防生疏</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识库浏览 -->
    <div v-else-if="currentTab === 'browse'" class="browse-layout">
      <!-- 移动端抽屉遮罩 -->
      <div v-if="isDrawerOpen" class="drawer-backdrop" @click="isDrawerOpen = false"></div>

      <!-- 左侧目录 / 移动端滑动抽屉 -->
      <aside :class="['browse-sidebar', { 'drawer-open': isDrawerOpen }]">
        <div class="sidebar-header">
          <div class="sidebar-title">
            <span>📚 考点目录</span>
            <span class="count-pill">{{ filteredCards.length }} 条</span>
          </div>
          <button class="drawer-close-btn" @click="isDrawerOpen = false">✕</button>
        </div>

        <div class="search-box">
          <input v-model="searchQuery" class="search-input" placeholder="搜索编号、标题或原文...">
        </div>
        <div class="subject-tabs">
          <button v-for="sub in ['全部', '马原', '政经', '史纲', '其他']" :key="sub"
            :class="['sub-tab', { active: selectedSubject === sub }]" @click="selectedSubject = sub">
            {{ sub }}
          </button>
        </div>
        <div class="card-nav-list">
          <div v-for="c in filteredCards" :key="c.id"
            :class="['nav-card-item', { active: currentBrowseCard?.id === c.id }]"
            @click="selectBrowseCard(c)">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="source-id-tag">考点 {{ c.sourceId }}</span>
              <span v-if="isFavorite(c.id)" style="color:#d97706;">★</span>
            </div>
            <div style="font-size:13px; font-weight:600; margin:3px 0;">{{ c.title }}</div>
            <div style="font-size:11px; color:var(--text-muted);">{{ c.subject }} · {{ c.section }} | P{{ c.sourcePage[0] }}</div>
          </div>
        </div>
      </aside>

      <!-- 右侧主浏览区 -->
      <main class="browse-main">
        <div class="browse-controls">
          <div class="controls-left">
            <button class="ctrl-btn drawer-trigger-btn" @click="isDrawerOpen = true">
              <span>📋</span>
              <span>目录 ({{ currentBrowseIndex + 1 }}/{{ filteredCards.length }}) ▾</span>
            </button>
            <div class="desktop-arrows">
              <button class="ctrl-btn" :disabled="currentBrowseIndex <= 0" @click="prevBrowseCard">◀ 上一条</button>
              <span class="index-display">{{ currentBrowseIndex + 1 }} / {{ filteredCards.length }}</span>
              <button class="ctrl-btn" :disabled="currentBrowseIndex >= filteredCards.length - 1" @click="nextBrowseCard">下一条 ▶</button>
            </div>
          </div>
          <div class="controls-right">
            <div class="cloze-mode-stepper" title="切换背诵遮挡模式">
              <button v-for="m in [{key:'none',label:'原文'},{key:'keyword',label:'挖词'},{key:'random',label:'随机'},{key:'full',label:'全遮'}]" :key="m.key"
                :class="['mode-step-btn', { active: browseClozeMode === m.key }]"
                @click="browseClozeMode = m.key">{{ m.label }}</button>
            </div>
            <div class="font-stepper" title="切换显示字号">
              <button :class="['font-btn', { active: userSettings.fontSizeLevel === 'small' }]" @click="setFontSize('small')">小</button>
              <button :class="['font-btn', { active: userSettings.fontSizeLevel === 'medium' }]" @click="setFontSize('medium')">中</button>
              <button :class="['font-btn', { active: userSettings.fontSizeLevel === 'large' }]" @click="setFontSize('large')">大</button>
            </div>
          </div>
        </div>

        <div ref="browseCardAreaRef" class="card-display-area"
          @touchstart="handleTouchStart" @touchend="handleTouchEnd">
          <div class="swipe-hint">👈 左右滑动可无缝切换考点 👉</div>
          <card-viewer-component 
            v-if="currentBrowseCard"
            :card="currentBrowseCard" 
            :mode="browseClozeMode" 
            :font-size="userSettings.fontSizeLevel"
            :is-favorite="isFavorite(currentBrowseCard.id)"
            @toggle-fav="toggleFavorite(currentBrowseCard.id)">
          </card-viewer-component>
        </div>

        <!-- 移动端底栏翻页 -->
        <div class="mobile-bottom-bar">
          <button class="mobile-nav-btn" :disabled="currentBrowseIndex <= 0" @click="prevBrowseCard">
            ◀ 上一卡
          </button>
          <div class="mobile-index-chip" @click="isDrawerOpen = true">
            <span>{{ currentBrowseIndex + 1 }} / {{ filteredCards.length }} ▾</span>
          </div>
          <button class="mobile-nav-btn" :disabled="currentBrowseIndex >= filteredCards.length - 1" @click="nextBrowseCard">
            下一卡 ▶
          </button>
        </div>
      </main>
    </div>

    <!-- 智能背诵模式 -->
    <div v-else-if="currentTab === 'recite'" class="page-container">
      <div v-if="reciteFinished || reciteQueue.length === 0" class="welcome-card" style="text-align:center; padding:40px 20px;">
        <div style="font-size:40px;">🎉</div>
        <h2 style="font-size:20px; font-weight:800; margin-top:10px;">今日任务已全部搞定！</h2>
        <p style="color:var(--text-muted); font-size:14px; margin-top:6px;">保持记忆节律，考研政治稳过线！</p>
        <div style="display:flex; justify-content:center; gap:10px; margin-top:20px;">
          <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:700;" @click="loadMoreRecite">再学 10 张新卡</button>
          <button class="ctrl-btn" @click="currentTab = 'browse'">返回首页</button>
        </div>
      </div>

      <div v-else style="display:flex; flex-direction:column; gap:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:13px; font-weight:bold; color:var(--text-muted);">
            正在复习：第 {{ reciteIndex + 1 }} / {{ reciteQueue.length }} 张
          </span>
          <div style="display:flex; gap:6px;">
            <button v-for="m in ['keyword', 'random', 'full']" :key="m"
              :class="['sub-pill', { active: currentClozeMode === m }]"
              @click="currentClozeMode = m">
              {{ m === 'keyword' ? '挖词' : m === 'random' ? '随机' : '全遮' }}
            </button>
          </div>
        </div>

        <card-viewer-component 
          v-if="currentReciteCard"
          :card="currentReciteCard" 
          :mode="currentClozeMode" 
          :font-size="userSettings.fontSizeLevel"
          :is-favorite="isFavorite(currentReciteCard.id)"
          @toggle-fav="toggleFavorite(currentReciteCard.id)">
        </card-viewer-component>

        <div class="eval-box">
          <div class="eval-title">自评掌握度 · 自动计算下次复习周期</div>
          <div class="eval-buttons">
            <button class="eval-btn btn-again" @click="handleEvaluate('again')">
              <span class="btn-main">完全生疏</span>
              <span class="btn-sub">今日重新背</span>
            </button>
            <button class="eval-btn btn-hard" @click="handleEvaluate('hard')">
              <span class="btn-main">有些模糊</span>
              <span class="btn-sub">明天复习</span>
            </button>
            <button class="eval-btn btn-good" @click="handleEvaluate('good')">
              <span class="btn-main">基本掌握</span>
              <span class="btn-sub">3 天后</span>
            </button>
            <button class="eval-btn btn-easy" @click="handleEvaluate('easy')">
              <span class="btn-main">熟练秒杀</span>
              <span class="btn-sub">7 天后</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 随机抽查 -->
    <div v-else-if="currentTab === 'quiz'" class="page-container">
      <div v-if="!isQuizRunning" class="welcome-card">
        <h2 style="font-size:18px;">🎲 随机考点速测抽查</h2>
        <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">从知识库中随机抽取 10 张卡片，在全遮挡状态下测试主动回忆能力！</p>
        <div style="display:flex; gap:8px; margin-top:14px;">
          <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold; padding:10px 20px;" @click="startQuiz('all')">
            全库随机抽查 10 张
          </button>
          <button class="ctrl-btn" style="background:var(--warning-accent-bg); color:var(--warning-accent); font-weight:bold; padding:10px 20px;" @click="startQuiz('mistakes')">
            只抽查薄弱错题
          </button>
        </div>
      </div>

      <div v-else style="display:flex; flex-direction:column; gap:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:13px; font-weight:bold;">抽测进度：{{ quizIndex + 1 }} / {{ quizPool.length }}</span>
          <button class="ctrl-btn" style="font-size:12px;" @click="isQuizRunning = false">结束抽查</button>
        </div>

        <card-viewer-component 
          v-if="currentQuizCard"
          :card="currentQuizCard" 
          :mode="quizRevealed ? 'none' : 'full'" 
          :font-size="userSettings.fontSizeLevel"
          :is-favorite="isFavorite(currentQuizCard.id)"
          @toggle-fav="toggleFavorite(currentQuizCard.id)">
        </card-viewer-component>

        <div v-if="!quizRevealed" style="display:flex; justify-content:center;">
          <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold; padding:12px 30px;" @click="quizRevealed = true">
            揭晓卡片核对回忆 👁️
          </button>
        </div>

        <div v-else class="eval-box">
          <div class="eval-title" style="margin-bottom:8px;">自评本次回忆程度：</div>
          <div class="eval-buttons">
            <button class="eval-btn btn-again" @click="handleQuizEval('again')"><span class="btn-main">生疏</span></button>
            <button class="eval-btn btn-hard" @click="handleQuizEval('hard')"><span class="btn-main">模糊</span></button>
            <button class="eval-btn btn-good" @click="handleQuizEval('good')"><span class="btn-main">掌握</span></button>
            <button class="eval-btn btn-easy" @click="handleQuizEval('easy')"><span class="btn-main">熟练</span></button>
          </div>
        </div>
      </div>
    </div>

    <!-- 错题本 -->
    <div v-else-if="currentTab === 'mistakes'" class="page-container">
      <div class="welcome-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h2 style="font-size:18px;">📕 背诵薄弱卡片库</h2>
            <p style="font-size:13px; color:var(--text-muted); margin-top:2px;">标记为生疏或错误的卡片集合 · 连续 2 次答对自动移出</p>
          </div>
          <span style="font-size:22px; font-weight:800; color:var(--danger-accent);">{{ mistakeCards.length }} 张</span>
        </div>
      </div>

      <div v-if="mistakeCards.length === 0" style="background:#fff; padding:40px; border-radius:12px; text-align:center; color:var(--text-muted); border:1px dashed var(--border-card);">
        🌟 太棒了！当前没有任何背诵错题！
      </div>

      <div v-else style="display:flex; flex-direction:column; gap:10px;">
        <div v-for="c in mistakeCards" :key="c.id" style="background:#fff; border:1px solid var(--border-card); border-radius:10px; padding:14px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="display:flex; gap:6px; align-items:center; margin-bottom:4px;">
              <span class="source-id-tag">考点 {{ c.sourceId }}</span>
              <span style="font-size:12px; color:var(--text-muted);">{{ c.subject }} · {{ c.section }}</span>
            </div>
            <div style="font-size:14px; font-weight:600;">{{ c.title }}</div>
          </div>
          <div style="display:flex; gap:8px;">
            <button class="ctrl-btn" style="background:var(--primary-accent-bg); color:var(--primary-accent);" @click="startReciteSingle(c.id)">突击</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 解题方法刷题模块 -->
    <div v-else-if="currentTab === 'solve'" class="page-container">
      <!-- 刷题二级导航 -->
      <div class="solve-sub-nav">
        <button :class="['sub-pill', { active: solveSubTab === 'methods' }]" @click="solveSubTab = 'methods'">🎯 方法库</button>
        <button :class="['sub-pill', { active: solveSubTab === 'practice' }]" @click="solveSubTab = 'practice'">📝 分类刷题</button>
        <button :class="['sub-pill', { active: solveSubTab === 'blind' }]" @click="solveSubTab = 'blind'">👁️ 盲测识坑</button>
        <button :class="['sub-pill', { active: solveSubTab === 'mock' }]" @click="solveSubTab = 'mock'">⏱️ 限时模考</button>
        <button :class="['sub-pill', { active: solveSubTab === 'dashboard' }]" @click="solveSubTab = 'dashboard'">📊 统计看板</button>
        <button :class="['sub-pill', { active: solveSubTab === 'mistakes' }]" @click="solveSubTab = 'mistakes'">
          📕 错题本 <span v-if="solveMistakeCount > 0">({{ solveMistakeCount }})</span>
        </button>
      </div>

      <!-- 1. 方法库与思维模式 -->
      <div v-if="solveSubTab === 'methods'">
        <div class="welcome-card" style="margin-top:12px;">
          <h2 style="font-size:18px;">🎯 老头命题手法（挖坑点）与四大解题思维模式</h2>
          <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">澄潇宇 · 政治选择题一页纸：掌握 10 类命题套路、4 大黄金解题思维模式、马恩真题名言与 18 大墓碑词</p>
          
          <div class="mindset-nav-tabs">
            <button :class="['sub-pill', { active: methodsActiveTab === 'methods' }]" @click="methodsActiveTab = 'methods'">
              🎯 10 类命题挖坑手法 ({{ ALL_METHODS.length }})
            </button>
            <button :class="['sub-pill', { active: methodsActiveTab === 'mindset' }]" @click="methodsActiveTab = 'mindset'">
              ⚡ 四大解题思维模式 (必背心法)
            </button>
            <button :class="['sub-pill', { active: methodsActiveTab === 'quotes' }]" @click="methodsActiveTab = 'quotes'">
              📖 马恩列真题名言避坑 ({{ classicMarxQuotes.length }})
            </button>
            <button :class="['sub-pill', { active: methodsActiveTab === 'tombstones' }]" @click="methodsActiveTab = 'tombstones'">
              ⚰️ 18 大高频墓碑词雷达
            </button>
          </div>
        </div>

        <!-- 子选项卡 1：10 类命题手法 -->
        <div v-if="methodsActiveTab === 'methods'" class="methods-grid-std">
          <div v-for="m in ALL_METHODS" :key="m.id" class="method-card-std">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:16px; font-weight:bold; color:var(--text-main);">{{ m.name }}</span>
              <span style="font-size:12px; color:var(--text-muted);">{{ m.questionIds.length }} 题</span>
            </div>
            <div class="mnemonic-box">💡 口诀：{{ m.mnemonic }}</div>
            <div style="display:flex; flex-wrap:wrap; gap:4px;">
              <span v-for="kw in m.keywords" :key="kw" class="kw-pill">{{ kw }}</span>
            </div>
            <div style="font-size:12px; color:var(--text-muted);">{{ m.description }}</div>
            
            <!-- 详细挖坑套路 -->
            <div v-if="m.trapsBreakdown && m.trapsBreakdown.length" style="background:#fef7f7; border-left:3px solid #ef4444; padding:8px 10px; border-radius:4px; font-size:12px;">
              <div style="font-weight:bold; color:#b91c1c; margin-bottom:4px;">⚠️ 设坑套路剖析：</div>
              <ul style="padding-left:16px; color:#4b5563; line-height:1.5; margin:0;">
                <li v-for="(t, tIdx) in m.trapsBreakdown" :key="tIdx">{{ t }}</li>
              </ul>
            </div>

            <!-- 特别注意 -->
            <div v-if="m.specialNotes" style="background:#fffbeb; border-left:3px solid #f59e0b; padding:6px 10px; border-radius:4px; font-size:12px; color:#92400e;">
              📌 <strong>防坑要诀：</strong>{{ m.specialNotes }}
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:auto; padding-top:8px; border-top:1px dashed var(--border-light);">
              <span style="font-size:12px; color:var(--text-muted);">掌握度: {{ getMethodStatStd(m.id).accuracy }}% ({{ getMethodStatStd(m.id).practiced }}/{{ m.questionIds.length }})</span>
              <button class="ctrl-btn" style="background:var(--primary-accent-bg); color:var(--primary-accent); font-weight:600; padding:6px 14px;" @click="startPracticeMethod(m.id)">
                开始刷题 →
              </button>
            </div>
          </div>
        </div>

        <!-- 子选项卡 2：四大解题思维模式 -->
        <div v-else-if="methodsActiveTab === 'mindset'" class="mindset-grid-std">
          <div v-for="item in mindsetPrinciples" :key="item.id" class="mindset-card-std">
            <div class="mindset-item-top">
              <span class="mindset-num-icon">{{ item.num }}</span>
              <div>
                <span class="mindset-badge-tag">{{ item.tag }}</span>
                <h4 class="mindset-item-title">{{ item.title }}</h4>
              </div>
            </div>
            <div class="mindset-item-summary">{{ item.summary }}</div>
            <ul class="mindset-details-list">
              <li v-for="(d, dIdx) in item.details" :key="dIdx">{{ d }}</li>
            </ul>
          </div>
        </div>

        <!-- 子选项卡 3：马恩列原话避坑表 -->
        <div v-else-if="methodsActiveTab === 'quotes'" style="margin-top:14px; display:flex; flex-direction:column; gap:12px;">
          <div style="background:#fff; border:1px solid var(--border-card); border-radius:10px; padding:14px; font-size:13px; color:var(--text-muted);">
            📌 命题人常引用马恩列斯原话作为选项，考生极易因“读不懂”而当成错项盲目排除。以下均为真题考查过的经典原话，表述完全正确：
          </div>
          <div class="methods-grid-std" style="margin-top:0;">
            <div v-for="(q, qIdx) in classicMarxQuotes" :key="qIdx" class="quote-card-std">
              <div class="quote-text-std">“{{ q.quote }}”</div>
              <div class="quote-meta-std">
                <span>—— {{ q.author }}</span>
                <span>📌 {{ q.context }}</span>
              </div>
              <div class="quote-alert-std">
                <strong>⚠️ 易错点分析：</strong>{{ q.trapAlert }}
              </div>
            </div>
          </div>
        </div>

        <!-- 子选项卡 4：18 大高频墓碑词雷达 -->
        <div v-else-if="methodsActiveTab === 'tombstones'" style="margin-top:14px;">
          <div style="background:#fff; border:1px solid var(--border-card); border-radius:10px; padding:14px; font-size:13px; color:var(--text-muted);">
            ⚰️ 命题人极喜欢在特定敏感词上做文章。单列为专项雷达，遇到这些词立刻启动怀疑反思：
          </div>
          <div class="tombstones-grid-std">
            <div v-for="(t, tIdx) in tombstoneWords" :key="tIdx" class="tombstone-card-std">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:bold; font-size:15px; color:#b91c1c;">⚰️ {{ t.word }}</span>
                <span class="kw-pill" style="background:#fee2e2; color:#991b1b; border-color:#fca5a5;">{{ t.category }}</span>
              </div>
              <div style="font-size:12px; color:var(--danger-accent); margin-top:4px;">
                <strong>设坑机制：</strong>{{ t.trap }}
              </div>
              <div style="font-size:12px; color:var(--success-accent); background:#f0fdf4; padding:4px 8px; border-radius:4px; margin-top:2px;">
                <strong>正确表述：</strong>{{ t.correctUsage }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 分类刷题 -->
      <div v-else-if="solveSubTab === 'practice'" style="margin-top:12px; display:flex; flex-direction:column; gap:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; background:#fff; padding:10px 16px; border-radius:10px; border:1px solid var(--border-card); flex-wrap:wrap; gap:8px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:13px; font-weight:bold;">筛选分类：</span>
            <select v-model="selectedPracticeMethod" @change="currentPracticeIndex = 0; solveUserAnswers = []; isSolveSubmitted = false;" style="padding:6px 10px; border-radius:6px; border:1px solid var(--border-card); background:#fff; font-size:13px;">
              <option value="all">全部题目 ({{ ALL_QUESTIONS.length }})</option>
              <option v-for="m in ALL_METHODS" :key="m.id" :value="m.id">{{ m.name }} ({{ m.questionIds.length }})</option>
            </select>
          </div>
          <span style="font-size:13px; font-weight:bold; color:var(--text-muted);" v-if="currentPracticeQ">
            第 {{ currentPracticeIndex + 1 }} / {{ filteredSolveQuestions.length }} 题
          </span>
        </div>

        <div v-if="currentPracticeQ" style="background:#fff; border:1px solid var(--border-card); border-radius:12px; padding:20px; display:flex; flex-direction:column; gap:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; gap:6px; align-items:center;">
              <span class="source-id-tag">{{ currentPracticeQ.year }}年第{{ currentPracticeQ.no }}题</span>
              <span :class="['type-badge', currentPracticeQ.type === 'single' ? 'single-badge' : 'multi-badge']">
                {{ currentPracticeQ.type === 'single' ? '单选题' : '多选题' }}
              </span>
            </div>
            <div style="display:flex; gap:8px;">
              <button class="ctrl-btn" :style="isSolveMistake(currentPracticeQ.id) ? 'background:#fde8e8; color:#c53030;' : ''" @click="toggleSolveMistake(currentPracticeQ.id)">
                {{ isSolveMistake(currentPracticeQ.id) ? '★ 已入错题' : '☆ 收藏错题' }}
              </button>
            </div>
          </div>

          <div style="font-size:15px; font-weight:600; line-height:1.7; color:var(--text-main);">
            {{ currentPracticeQ.stem }}
          </div>

          <!-- 💡 破题思维模式锦囊快捷条 -->
          <div class="mindset-strip-bar" @click="showMindsetBanner = !showMindsetBanner">
            <div class="mindset-strip-left">
              <span>⚡</span>
              <span>
                <strong>{{ currentPracticeQ.type === 'single' ? '单选题思维心法' : '多选题思维心法' }}：</strong>
                {{ currentPracticeQ.type === 'single' ? '三项解题法 · 圈定题干核心提问，找意思相近或相同词选项' : '核心用排除法 · 明显错才排 · 其余疑罪从无全选 · 马哲题不全选' }}
              </span>
            </div>
            <button class="mindset-strip-btn">
              {{ showMindsetBanner ? '收起 ▴' : '速查四大心法 ▾' }}
            </button>
          </div>

          <!-- 展开的思维心法微型卡 -->
          <div v-if="showMindsetBanner" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px; display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:10px;">
            <div v-for="item in mindsetPrinciples" :key="item.id" style="font-size:12px;">
              <div style="font-weight:bold; color:#1e293b;">{{ item.num }} {{ item.title }}</div>
              <div style="color:#64748b; margin-top:2px;">{{ item.summary }}</div>
            </div>
          </div>

          <!-- 选项列表 -->
          <div style="display:flex; flex-direction:column; gap:6px;">
            <div v-for="(txt, key) in currentPracticeQ.options" :key="key"
              :class="['opt-std-item', 
                { 
                  'selected': solveUserAnswers.includes(key),
                  'correct-rev': isSolveSubmitted && currentPracticeQ.answer.includes(key),
                  'wrong-rev': isSolveSubmitted && solveUserAnswers.includes(key) && !currentPracticeQ.answer.includes(key)
                }]"
              @click="toggleSolveOption(key)">
              <div class="opt-bubble-std">{{ key }}</div>
              <div style="font-size:14px; line-height:1.6; color:var(--text-main); flex:1;">{{ txt }}</div>
            </div>
          </div>

          <!-- 操作与提交 -->
          <div v-if="!isSolveSubmitted" style="display:flex; justify-content:flex-end;">
            <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold; padding:10px 24px;"
              :disabled="solveUserAnswers.length === 0" @click="submitSolvePractice">
              提交答案
            </button>
          </div>

          <!-- 结果与解析 -->
          <div v-else style="background:var(--bg-warm); border-radius:10px; padding:16px; display:flex; flex-direction:column; gap:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="font-weight:bold; font-size:15px;" :style="{ color: isSolveCorrect ? 'var(--success-accent)' : 'var(--danger-accent)' }">
                {{ isSolveCorrect ? '🎉 回答正确！' : '❌ 回答错误' }}
                <span style="color:var(--text-main); margin-left:8px; font-size:14px;">正确答案：{{ currentPracticeQ.answer.join('') }}</span>
              </div>
              <div style="display:flex; gap:6px; flex-wrap:wrap;">
                <span v-for="m in currentPracticeQ.methods" :key="m" class="hit-tag-std">
                  🎯 命中手法：{{ getMethodName(m) }}
                </span>
              </div>
            </div>

            <!-- 1. 考场识坑点睛与排雷分析 -->
            <div v-if="currentPracticeQ.trapReason || (currentPracticeQ.trapOptions && currentPracticeQ.trapOptions.length)" class="trap-insight-box">
              <div style="font-weight:bold; color:#b45309; display:flex; align-items:center; gap:4px;">
                <span>⚡</span>
                <span>考场识坑点睛与排雷分析</span>
              </div>
              <div v-if="currentPracticeQ.trapOptions && currentPracticeQ.trapOptions.length" style="display:flex; gap:6px; align-items:center;">
                <span style="color:#78350f; font-weight:600;">⚠️ 命题干扰项：</span>
                <span v-for="tOpt in currentPracticeQ.trapOptions" :key="tOpt" class="kw-pill" style="background:#fee2e2; color:#991b1b; border-color:#fca5a5;">选项 {{ tOpt }}</span>
              </div>
              <div v-if="currentPracticeQ.identKeywords && currentPracticeQ.identKeywords.length" style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                <span style="color:#78350f; font-weight:600;">🎯 破题识别关键词：</span>
                <span v-for="kw in currentPracticeQ.identKeywords" :key="kw" class="kw-pill">{{ kw }}</span>
              </div>
              <div v-if="currentPracticeQ.trapReason" style="color:#92400e; line-height:1.6;">
                <strong>破题要诀：</strong>{{ currentPracticeQ.trapReason }}
              </div>
            </div>

            <!-- 2. 一页纸原版破题批注 -->
            <div class="tip-box-std">
              <div style="font-weight:bold; margin-bottom:4px; color:#874900;">澄潇宇「一页纸」原版破题批注：</div>
              <div style="white-space:pre-line; line-height:1.6;">{{ currentPracticeQ.tip || '暂无详细提示' }}</div>
            </div>

            <!-- 3. 老头命题套路深度剖析 -->
            <div v-if="getMethodObj(currentPracticeQ.methods[0])" class="deep-traps-box">
              <div style="font-weight:bold; color:#b91c1c; display:flex; align-items:center; gap:4px;">
                <span>🎯</span>
                <span>老头命题挖坑套路剖析 · {{ getMethodObj(currentPracticeQ.methods[0]).name }}</span>
              </div>
              <div style="color:#7f1d1d;">
                🗣️ <strong>口诀：</strong>{{ getMethodObj(currentPracticeQ.methods[0]).mnemonic }}
              </div>
              <div v-if="getMethodObj(currentPracticeQ.methods[0]).trapsBreakdown && getMethodObj(currentPracticeQ.methods[0]).trapsBreakdown.length">
                <div style="font-weight:600; color:#991b1b; margin-bottom:2px;">⚠️ 常见挖坑设伏机制：</div>
                <ul style="padding-left:16px; color:#374151; line-height:1.5; margin:0;">
                  <li v-for="(t, idx) in getMethodObj(currentPracticeQ.methods[0]).trapsBreakdown" :key="idx">{{ t }}</li>
                </ul>
              </div>
              <div v-if="getMethodObj(currentPracticeQ.methods[0]).specialNotes" style="color:#92400e; margin-top:2px;">
                📌 <strong>防坑要诀：</strong>{{ getMethodObj(currentPracticeQ.methods[0]).specialNotes }}
              </div>
            </div>

            <!-- 4. 解题思维模式落地指导 -->
            <div class="guidance-box">
              <div style="font-weight:bold; color:#15803d; display:flex; align-items:center; gap:4px;">
                <span>⚡</span>
                <span>解题思维模式落地复盘</span>
              </div>
              <div style="color:#166534; line-height:1.6;">
                <strong>{{ currentPracticeQ.type === 'single' ? '单选题思维心法：' : '多选题思维心法：' }}</strong>
                {{ currentPracticeQ.type === 'single' 
                  ? '【三项解题法 & 排除法】对于时政与生疏单选题，先抓题干核心关键词与设问角度，优先排除具有绝对极端词或与材料不合的选项，寻找与材料意思最契合的选项。' 
                  : '【多选疑罪从无】核心采用排除法，明显错才算错（抓到违背常识规律、绝对极端、时态颠倒、答非所问证据），拿不准的坚持疑罪从无全选上！若为马原题（尤其是马哲），切忌盲目全选。' }}
              </div>
              <div style="display:flex; gap:8px; margin-top:4px; flex-wrap:wrap;">
                <button class="ctrl-btn" style="background:#e0f2fe; color:#0369a1; padding:4px 10px; font-size:12px;" @click="showMarxModal = true">📖 查看马恩列名言避坑表</button>
                <button class="ctrl-btn" style="background:#fee2e2; color:#991b1b; padding:4px 10px; font-size:12px;" @click="showTombstoneModal = true">⚰️ 查看18大墓碑词雷达</button>
              </div>
            </div>

            <div style="text-align:center;">
              <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;">SRS 掌握度自评：</div>
              <div class="eval-buttons" style="max-width:500px; margin:0 auto;">
                <button class="eval-btn btn-again" @click="gradeSolveSRS('again', true)"><span class="btn-main">生疏 (重做)</span></button>
                <button class="eval-btn btn-hard" @click="gradeSolveSRS('hard', true)"><span class="btn-main">模糊 (重做)</span></button>
                <button class="eval-btn btn-good" @click="gradeSolveSRS('good', true)"><span class="btn-main">掌握 (下一题)</span></button>
                <button class="eval-btn btn-easy" @click="gradeSolveSRS('easy', true)"><span class="btn-main">熟练 (下一题)</span></button>
              </div>
            </div>
          </div>

          <!-- 上下题切换 -->
          <div style="display:flex; justify-content:space-between; margin-top:8px;">
            <button class="ctrl-btn" :disabled="currentPracticeIndex === 0" @click="currentPracticeIndex--; solveUserAnswers = []; isSolveSubmitted = false;">
              ← 上一题
            </button>
            <button class="ctrl-btn" :disabled="currentPracticeIndex >= filteredSolveQuestions.length - 1" @click="currentPracticeIndex++; solveUserAnswers = []; isSolveSubmitted = false;">
              下一题 →
            </button>
          </div>
        </div>
      </div>

      <!-- 3. 盲测识坑 -->
      <div v-else-if="solveSubTab === 'blind'" style="margin-top:12px; display:flex; flex-direction:column; gap:14px;">
        <div class="welcome-card">
          <h2 style="font-size:18px;">👁️ 盲测识坑模式</h2>
          <p style="font-size:13px; color:var(--text-muted); margin-top:2px;">不预设分类，先做题再判断出题人用了什么「套路」，锻炼真题考场识坑眼力！</p>
        </div>

        <div v-if="currentBlindQ" style="background:#fff; border:1px solid var(--border-card); border-radius:12px; padding:20px; display:flex; flex-direction:column; gap:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="source-id-tag">{{ currentBlindQ.year }}年第{{ currentBlindQ.no }}题</span>
            <span :class="['type-badge', currentBlindQ.type === 'single' ? 'single-badge' : 'multi-badge']">
              {{ currentBlindQ.type === 'single' ? '单选题' : '多选题' }}
            </span>
          </div>

          <div style="font-size:15px; font-weight:600; line-height:1.7;">{{ currentBlindQ.stem }}</div>

          <!-- 选项 -->
          <div style="display:flex; flex-direction:column; gap:6px;">
            <div v-for="(txt, key) in currentBlindQ.options" :key="key"
              :class="['opt-std-item', { selected: blindUserAnswers.includes(key) }]"
              @click="toggleBlindOption(key)">
              <div class="opt-bubble-std">{{ key }}</div>
              <div style="font-size:14px; flex:1;">{{ txt }}</div>
            </div>
          </div>

          <!-- 猜手法阶段 -->
          <div v-if="!isBlindSubmitted" style="background:var(--bg-warm); padding:14px; border-radius:8px; border:1px dashed var(--border-card);">
            <div style="font-size:13px; font-weight:bold; margin-bottom:8px;">🎯 猜猜出题人用了什么挖坑手法？</div>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
              <button v-for="m in ALL_METHODS" :key="m.id"
                :class="['sub-pill', { active: chosenBlindMethod === m.id }]"
                @click="chosenBlindMethod = m.id">
                {{ m.name }}
              </button>
            </div>
            <div style="display:flex; justify-content:flex-end; margin-top:12px;">
              <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold; padding:8px 20px;"
                :disabled="blindUserAnswers.length === 0 || !chosenBlindMethod"
                @click="submitBlind">
                提交作答并揭晓手法
              </button>
            </div>
          </div>

          <!-- 揭晓结果 -->
          <div v-else style="background:var(--bg-warm); padding:16px; border-radius:10px; display:flex; flex-direction:column; gap:10px;">
            <div style="font-weight:bold; font-size:15px;">
              正确答案：{{ currentBlindQ.answer.join('') }} · 命中方法：
              <span v-for="m in currentBlindQ.methods" :key="m" class="hit-tag-std">{{ getMethodName(m) }}</span>
            </div>
            <div :style="{ color: isBlindMethodHit ? 'var(--success-accent)' : 'var(--danger-accent)', fontWeight:'bold' }">
              {{ isBlindMethodHit ? '🎉 识坑成功！你准确看穿了出题老师的套路！' : '❌ 辨识偏差：该题出题人主要运用的是【' + currentBlindQ.methods.map(getMethodName).join(' / ') + '】' }}
            </div>
            <div class="tip-box-std">{{ currentBlindQ.tip }}</div>
            <div style="display:flex; justify-content:flex-end; margin-top:6px;">
              <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff;" @click="nextBlindQuestion">下一题 →</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. 限时模考 -->
      <div v-else-if="solveSubTab === 'mock'" style="margin-top:12px;">
        <div v-if="!isMockRunning" class="welcome-card">
          <h2 style="font-size:18px;">⏱️ 考场全真限时模考</h2>
          <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">全真模拟考场环境，倒计时抽题连刷，训练临场快速破题与排除硬伤能力！</p>
          <div style="display:flex; gap:10px; margin-top:14px;">
            <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold; padding:10px 20px;" @click="startMockExam(10, 15)">
              抽做 10 题 (限时 15 分钟)
            </button>
            <button class="ctrl-btn" style="background:var(--bg-beige); font-weight:bold; padding:10px 20px;" @click="startMockExam(20, 30)">
              抽做 20 题 (限时 30 分钟)
            </button>
          </div>
        </div>

        <div v-else style="display:flex; flex-direction:column; gap:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center; background:#fff; padding:10px 16px; border-radius:10px; border:1px solid var(--border-card);">
            <span style="font-weight:bold; font-size:14px;">模考进度：{{ mockQIndex + 1 }} / {{ mockPool.length }}</span>
            <span style="font-size:16px; font-weight:800; color:var(--danger-accent);">⏱️ 剩余时间：{{ Math.floor(mockSeconds / 60) }}:{{ (mockSeconds % 60).toString().padStart(2, '0') }}</span>
            <button class="ctrl-btn" style="background:#fee2e2; color:#991b1b; font-size:12px;" @click="finishMockExam">交卷</button>
          </div>

          <div v-if="currentMockQ" style="background:#fff; border:1px solid var(--border-card); border-radius:12px; padding:20px; display:flex; flex-direction:column; gap:14px;">
            <div style="display:flex; gap:6px; align-items:center;">
              <span class="source-id-tag">{{ currentMockQ.year }}年第{{ currentMockQ.no }}题</span>
              <span :class="['type-badge', currentMockQ.type === 'single' ? 'single-badge' : 'multi-badge']">
                {{ currentMockQ.type === 'single' ? '单选题' : '多选题' }}
              </span>
            </div>
            <div style="font-size:15px; font-weight:600;">{{ currentMockQ.stem }}</div>
            <div style="display:flex; flex-direction:column; gap:6px;">
              <div v-for="(txt, key) in currentMockQ.options" :key="key"
                :class="['opt-std-item', { selected: (mockAnswers[currentMockQ.id] || []).includes(key) }]"
                @click="toggleMockOpt(key)">
                <div class="opt-bubble-std">{{ key }}</div>
                <div style="font-size:14px; flex:1;">{{ txt }}</div>
              </div>
            </div>

            <div style="display:flex; justify-content:space-between; margin-top:10px;">
              <button class="ctrl-btn" :disabled="mockQIndex <= 0" @click="mockQIndex--">← 上一题</button>
              <button class="ctrl-btn" v-if="mockQIndex < mockPool.length - 1" @click="mockQIndex++">下一题 →</button>
              <button class="ctrl-btn" v-else style="background:var(--success-accent); color:#fff; font-weight:bold;" @click="finishMockExam">交卷并查看分数</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. 统计看板 -->
      <div v-else-if="solveSubTab === 'dashboard'" style="margin-top:12px; display:flex; flex-direction:column; gap:14px;">
        <div class="stat-grid">
          <div class="stat-box">
            <div class="stat-num">{{ ALL_QUESTIONS.length }}</div>
            <div style="font-size:12px; color:var(--text-muted);">收录真题总数</div>
          </div>
          <div class="stat-box">
            <div class="stat-num">{{ solvePracticedCount }}</div>
            <div style="font-size:12px; color:var(--text-muted);">已练题数</div>
          </div>
          <div class="stat-box box-mastered">
            <div class="stat-num">{{ solveAccuracy }}%</div>
            <div style="font-size:12px; color:var(--text-muted);">综合正确率</div>
          </div>
          <div class="stat-box box-mistake">
            <div class="stat-num">{{ solveMistakeCount }}</div>
            <div style="font-size:12px; color:var(--text-muted);">错题待巩固</div>
          </div>
        </div>

        <!-- 10类手法正确率 -->
        <div style="background:#fff; border:1px solid var(--border-card); border-radius:10px; padding:16px;">
          <h3 style="font-size:15px; margin-bottom:12px;">📊 10 类方法掌握度</h3>
          <div style="display:flex; flex-direction:column; gap:10px;">
            <div v-for="m in ALL_METHODS" :key="m.id">
              <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;">
                <span style="font-weight:600;">{{ m.name }}</span>
                <span style="color:var(--text-muted);">{{ getMethodStatStd(m.id).accuracy }}% ({{ getMethodStatStd(m.id).practiced }}/{{ m.questionIds.length }})</span>
              </div>
              <div style="height:6px; background:#f0f0f0; border-radius:3px; overflow:hidden;">
                <div :style="{ width: getMethodStatStd(m.id).accuracy + '%', background: 'var(--primary-accent)', height: '100%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 6. 错题本 -->
      <div v-else-if="solveSubTab === 'mistakes'" style="margin-top:12px; display:flex; flex-direction:column; gap:12px;">
        <div class="welcome-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h2 style="font-size:18px;">📕 解题薄弱错题本</h2>
              <p style="font-size:13px; color:var(--text-muted); margin-top:2px;">按解题方法归类的做错真题 · 连续 2 次答对掌握自动移出</p>
            </div>
            <span style="font-size:22px; font-weight:800; color:var(--danger-accent);">{{ solveMistakeQuestions.length }} 题</span>
          </div>
        </div>

        <div v-if="solveMistakeQuestions.length === 0" style="background:#fff; padding:40px; border-radius:12px; text-align:center; color:var(--text-muted); border:1px dashed var(--border-card);">
          🌟 当前解题题库没有任何错题！继续保持！
        </div>

        <div v-else style="display:flex; flex-direction:column; gap:10px;">
          <div v-for="q in solveMistakeQuestions" :key="q.id" style="background:#fff; border:1px solid var(--border-card); border-radius:10px; padding:14px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="display:flex; gap:6px; align-items:center; margin-bottom:4px;">
                <span class="source-id-tag">{{ q.year }}年第{{ q.no }}题</span>
                <span class="hit-tag-std" v-for="m in q.methods" :key="m">{{ getMethodName(m) }}</span>
              </div>
              <div style="font-size:13px; color:var(--text-main); max-width:600px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                {{ q.stem }}
              </div>
            </div>
            <div style="display:flex; gap:8px;">
              <button class="ctrl-btn" style="background:var(--primary-accent-bg); color:var(--primary-accent);" @click="startPracticeMethod(q.methods[0])">重做</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 设置与备份弹窗 -->
    <template v-if="showSettingsModal">
      <div class="modal-overlay" @click.self="showSettingsModal = false">
        <div class="modal-dialog" style="max-width:500px;">
          <div class="modal-header">
            <div style="font-weight:bold;">⚙️ 系统设置与数据备份</div>
            <button style="background:none; font-size:18px;" @click="showSettingsModal = false">✕</button>
          </div>
          <div style="padding:20px; display:flex; flex-direction:column; gap:16px;">
            <div>
              <div style="font-size:13px; font-weight:bold; margin-bottom:6px;">默认阅读字号：</div>
              <div style="display:flex; gap:8px;">
                <button v-for="lvl in ['small', 'medium', 'large', 'xlarge']" :key="lvl"
                  :class="['sub-tab', { active: userSettings.fontSizeLevel === lvl }]"
                  @click="setFontSize(lvl)" style="flex:1; padding:8px; border:1px solid var(--border-card);">
                  {{ lvl }}
                </button>
              </div>
            </div>
            <hr style="border:none; border-top:1px dashed var(--border-light);">
            <div>
              <div style="font-size:13px; font-weight:bold; margin-bottom:6px;">数据备份与导出：</div>
              <button class="ctrl-btn" style="width:100%; padding:10px; font-weight:bold;" @click="exportDataBackup">
                📥 导出本地备份 JSON
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 马恩列真题名言避坑弹窗 -->
    <template v-if="showMarxModal">
      <div class="modal-overlay" @click.self="showMarxModal = false">
        <div class="modal-dialog" style="max-width:700px; max-height:85vh; display:flex; flex-direction:column;">
          <div class="modal-header">
            <div style="font-weight:bold; font-size:15px;">📖 马恩列真题原话避坑表</div>
            <button style="background:none; font-size:18px;" @click="showMarxModal = false">✕</button>
          </div>
          <div style="padding:16px; overflow-y:auto; display:flex; flex-direction:column; gap:12px;">
            <div v-for="(q, idx) in classicMarxQuotes" :key="idx" class="quote-card-std">
              <div style="font-weight:600; color:var(--text-main); font-size:14px; margin-bottom:6px;">“{{ q.quote }}”</div>
              <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;">—— {{ q.author }} · {{ q.context }}</div>
              <div style="font-size:12px; background:#fff7ed; border-left:3px solid #ea580c; padding:6px 10px; border-radius:4px; color:#9a3412;">
                <strong>⚠️ 避坑提醒：</strong>{{ q.trapAlert }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 18大高频墓碑词速查弹窗 -->
    <template v-if="showTombstoneModal">
      <div class="modal-overlay" @click.self="showTombstoneModal = false">
        <div class="modal-dialog" style="max-width:760px; max-height:85vh; display:flex; flex-direction:column;">
          <div class="modal-header">
            <div style="font-weight:bold; font-size:15px;">⚰️ 18 大高频墓碑词敏感雷达</div>
            <button style="background:none; font-size:18px;" @click="showTombstoneModal = false">✕</button>
          </div>
          <div style="padding:16px; overflow-y:auto; display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:10px;">
            <div v-for="(t, idx) in tombstoneWords" :key="idx" class="tombstone-card-std">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <span style="font-weight:bold; font-size:15px; color:#b91c1c;">⚰️ {{ t.word }}</span>
                <span class="kw-pill" style="background:#fee2e2; color:#991b1b; border-color:#fca5a5;">{{ t.category }}</span>
              </div>
              <div style="font-size:12px; color:var(--danger-accent); margin-bottom:4px;"><strong>设坑机制：</strong>{{ t.trap }}</div>
              <div style="font-size:12px; color:var(--success-accent); background:#f0fdf4; padding:4px 8px; border-radius:4px;"><strong>正确表述：</strong>{{ t.correctUsage }}</div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>

  <script>
    const { createApp, ref, computed, watch, onMounted } = Vue;

    
    const ALL_EMBEDDED_IMAGES = __ALL_IMAGES_JSON__;
    function resolveImageUrl(imgRelPath) {
      if (!imgRelPath) return '';
      const cleanKey = imgRelPath.replace(/^[\\/]+/, '').replace(/^public[\\/]+/, '');
      if (ALL_EMBEDDED_IMAGES && ALL_EMBEDDED_IMAGES[cleanKey]) {
        return ALL_EMBEDDED_IMAGES[cleanKey];
      }
      return cleanKey;
    }

    // 39种原书趣味小图精确MD5哈希与描述映射表
    const SYMBOL_MAP = {
      '直升机': { hash: '0516485bd1dce29f34fa082d19c8a898', desc: '牢二枢纽直升机' },
      '鸡': { hash: '5a9490a12d44beb9e7746e1a94426828', desc: '偷鸡心虚虚空鸡' },
      '俄国国旗': { hash: 'e380284efa1fbd56310cd5f8f4fcfe1d', desc: '十月革命俄国国旗' },
      '人像': { hash: '168dcc0bc57d714b82bfe6874f43e862', desc: '历史人物图标' },
      '帽子人物': { hash: '40aaf32abfc71ea9500e34c32d8d20e5', desc: '国际寡妇助记' },
      '生子': { hash: '6cb1e12616262e72dadbc1257ec66830', desc: '生孩子助记' },
      '机器多了': { hash: '940abc17f526e6beac695add820827ae', desc: '技术构成机器多' },
      '工人少了': { hash: 'fdf97e4e7d1a6bea4fd877d0e40d31c7', desc: '有机构成工人少' },
      '威海技师': { hash: '7057fa3e3ce5ecba32cac43eb4565e73', desc: '威海技师洋务' },
      '工农革命旗': { hash: '5f2f87becb22c2ab56431d205ab73ab3', desc: '秋收起义旗帜' },
      '民主政权标': { hash: '87dd47b6f4ca93850f0130dc659c77a0', desc: '赞成抗日民主' },
      '著作:书标': { hash: '99386d902eb6272b3c82bc3a6e1e022f', desc: '毛泽东著作标志' },
      '著作:飞标': { hash: '12d6fc3c71073f73b549fd983c0c7f88', desc: '论联合政府标志' },
      '著作:章标': { hash: 'cd54f7c7ed776f063a883f04b9aa270a', desc: '毛泽东著作奖章' },
      '高质量发展标': { hash: '5b175efae41e61ff41f9a7e91b6e8ccb', desc: '高质量发展' },
      '全面依法治国标': { hash: '34df7d1a3b49696a8c06d78d0079121c', desc: '全面依法治国' },
      '变动标': { hash: 'b7e1a94be66a6858d0f7db1457cc7ce0', desc: '构成变动' },
      '发展标': { hash: 'e4fa63d9756f3f7ae302ec676fabf054', desc: '继续发展' }
    };

    function getSymbolInfo(name, cardSymbols) {
      if (SYMBOL_MAP[name]) return SYMBOL_MAP[name];
      if (cardSymbols) {
        const found = cardSymbols.find(s => s.char === '{' + name + '}' || s.char === name);
        if (found) return found;
      }
      return null;
    }

    const ALL_CARDS = __ALL_CARDS_JSON__;

    const CardViewerComponent = {
      props: ['card', 'mode', 'fontSize', 'isFavorite'],
      emits: ['toggle-fav'],
      setup(props) {
        const fullRevealed = ref(false);
        const revealedSet = ref(new Set());
        const isImgZoomed = ref(false);

        watch(() => props.card?.id, () => {
          isImgZoomed.value = false;
        });

        const cleanDistinctions = computed(() => {
          if (!props.card || !props.card.distinctions) return [];
          return props.card.distinctions.map(d => ({
            ...d,
            statement: d.statement ? d.statement.replace(/\\{\\{([^}]+)\\}\\}/g, '$1').trim() : ''
          })).filter(d => d.statement.length > 0);
        });

        const cleanMnemonics = computed(() => {
          if (!props.card || !props.card.mnemonics) return [];
          return props.card.mnemonics.map(m => ({
            ...m,
            text: m.text ? m.text.replace(/\\{\\{([^}]+)\\}\\}/g, '$1').trim() : ''
          })).filter(m => m.text.length > 0);
        });

        function parseMnemonicParts(text) {
          if (!text) return [];
          const parts = [];
          const regex = /\\{([^}]+)\\}/g;
          let lastIdx = 0;
          let match;
          while ((match = regex.exec(text)) !== null) {
            if (match.index > lastIdx) {
              parts.push({ type: 'text', text: text.substring(lastIdx, match.index) });
            }
            const symName = match[1];
            const symInfo = getSymbolInfo(symName, props.card.symbols);
            parts.push({ 
              type: 'symbol', 
              text: symName,
              hash: symInfo ? symInfo.hash : null,
              desc: symInfo ? symInfo.desc : symName
            });
            lastIdx = regex.lastIndex;
          }
          if (lastIdx < text.length) {
            parts.push({ type: 'text', text: text.substring(lastIdx) });
          }
          return parts;
        }

        function addPlainTextSegments(text, segments, nextId) {
          const lines = text.split('\\n');
          lines.forEach((line, lIdx) => {
            if (lIdx > 0) {
              segments.push({ type: 'newline' });
            }
            if (line) {
              const symRegex = /\\{([^{}\\n]+)\\}/g;
              let lastSymIdx = 0;
              let symMatch;
              while ((symMatch = symRegex.exec(line)) !== null) {
                if (symMatch.index > lastSymIdx) {
                  const piece = line.substring(lastSymIdx, symMatch.index);
                  if (piece) {
                    const segId = nextId();
                    const shouldCloze = props.mode === 'sentence' && piece.trim().length > 1;
                    segments.push({
                      id: segId,
                      type: 'plain',
                      text: piece,
                      shouldCloze: shouldCloze,
                      revealed: revealedSet.value.has(segId)
                    });
                  }
                }
                const symName = symMatch[1];
                const symInfo = getSymbolInfo(symName, props.card.symbols);
                if (symInfo) {
                  segments.push({
                    id: nextId(),
                    type: 'symbol',
                    name: symName,
                    hash: symInfo.hash,
                    desc: symInfo.desc,
                    shouldCloze: false
                  });
                } else {
                  segments.push({
                    id: nextId(),
                    type: 'plain',
                    text: symMatch[0],
                    shouldCloze: false,
                    revealed: true
                  });
                }
                lastSymIdx = symRegex.lastIndex;
              }
              if (lastSymIdx < line.length) {
                const tailPiece = line.substring(lastSymIdx);
                if (tailPiece) {
                  const segId = nextId();
                  const shouldCloze = props.mode === 'sentence' && tailPiece.trim().length > 1;
                  segments.push({
                    id: segId,
                    type: 'plain',
                    text: tailPiece,
                    shouldCloze: shouldCloze,
                    revealed: revealedSet.value.has(segId)
                  });
                }
              }
            }
          });
        }

        const parsedSegments = computed(() => {
          if (!props.card || !props.card.content) return [];
          const content = props.card.content;
          const segments = [];
          const regex = /\\{\\{([^}]+)\\}\\}/g;
          let lastIndex = 0;
          let match;
          let idx = 0;

          const colorMap = new Map();
          if (props.card.keywords) {
            props.card.keywords.forEach(k => colorMap.set(k.word, k.color));
          }

          while ((match = regex.exec(content)) !== null) {
            if (match.index > lastIndex) {
              const txt = content.substring(lastIndex, match.index);
              addPlainTextSegments(txt, segments, () => 'p-' + (idx++));
            }
            const kw = match[1];
            const segId = 'kw-' + (idx++);
            const shouldCloze = props.mode === 'keyword' || (props.mode === 'random' && idx % 2 === 0);
            segments.push({
              id: segId,
              type: 'keyword',
              text: kw,
              color: colorMap.get(kw) || '#2e6297',
              shouldCloze: shouldCloze,
              revealed: revealedSet.value.has(segId)
            });
            lastIndex = regex.lastIndex;
          }

          if (lastIndex < content.length) {
            addPlainTextSegments(content.substring(lastIndex), segments, () => 'p-' + (idx++));
          }
          return segments;
        });

        function toggleSeg(seg) {
          if (!seg.shouldCloze) return;
          if (revealedSet.value.has(seg.id)) {
            revealedSet.value.delete(seg.id);
          } else {
            revealedSet.value.add(seg.id);
          }
        }

        function revealAll() {
          parsedSegments.value.forEach(s => { if (s.shouldCloze) revealedSet.value.add(s.id); });
          fullRevealed.value = true;
        }

        function hideAll() {
          revealedSet.value.clear();
          fullRevealed.value = false;
        }

        
        const activeQuestion = ref(null);
        const selectedOptions = ref(new Set());
        const hasSubmitted = ref(false);
        const isCorrect = ref(false);
        const questionRecords = ref({});

        function loadQuestionRecords() {
          try {
            questionRecords.value = JSON.parse(localStorage.getItem('zhengz_question_records') || '{}');
          } catch (e) {
            questionRecords.value = {};
          }
        }
        loadQuestionRecords();

        const groupedQuestions = computed(() => {
          const groups = { '真题': [], '模拟题': [] };
          if (!props.card || !props.card.relatedQuestions) return groups;
          props.card.relatedQuestions.forEach(q => {
            if (q.sourceType === '真题') {
              groups['真题'].push(q);
            } else {
              groups['模拟题'].push(q);
            }
          });
          return groups;
        });

        const activeQuestionIndex = computed(() => {
          if (!activeQuestion.value || !props.card || !props.card.relatedQuestions) return 0;
          return props.card.relatedQuestions.findIndex(q => q.id === activeQuestion.value.id);
        });

        const isMultiChoice = computed(() => {
          if (!activeQuestion.value) return false;
          return (activeQuestion.value.kind && activeQuestion.value.kind.includes('多项')) || activeQuestion.value.type === 'multi';
        });

        const normalizedCorrectAnswer = computed(() => {
          if (!activeQuestion.value || !activeQuestion.value.answer) return '';
          if (Array.isArray(activeQuestion.value.answer)) {
            return activeQuestion.value.answer.join('');
          }
          return String(activeQuestion.value.answer).toUpperCase();
        });

        const formattedOptions = computed(() => {
          if (!activeQuestion.value || !activeQuestion.value.options) return [];
          if (Array.isArray(activeQuestion.value.options)) {
            return activeQuestion.value.options;
          }
          return Object.keys(activeQuestion.value.options).sort().map(letter => ({
            letter,
            text: activeQuestion.value.options[letter]
          }));
        });

        function openQuestion(q) {
          activeQuestion.value = q;
          hasSubmitted.value = false;
          selectedOptions.value = new Set();
          const rec = questionRecords.value[q.id];
          if (rec) {
            hasSubmitted.value = true;
            isCorrect.value = rec.status === 'right';
            if (rec.selected && Array.isArray(rec.selected)) {
              selectedOptions.value = new Set(rec.selected);
            }
          }
        }

        function handleOptionClick(letter) {
          if (hasSubmitted.value) return;
          if (isMultiChoice.value) {
            if (selectedOptions.value.has(letter)) {
              selectedOptions.value.delete(letter);
            } else {
              selectedOptions.value.add(letter);
            }
            selectedOptions.value = new Set(selectedOptions.value);
          } else {
            selectedOptions.value = new Set([letter]);
          }
        }

        function isOptionCorrect(letter) {
          return normalizedCorrectAnswer.value.includes(letter);
        }

        function submitAnswer() {
          if (selectedOptions.value.size === 0) return;
          const userAns = Array.from(selectedOptions.value).sort().join('');
          const correctAns = normalizedCorrectAnswer.value.split('').sort().join('');
          const correct = userAns === correctAns;

          hasSubmitted.value = true;
          isCorrect.value = correct;

          try {
            const recs = JSON.parse(localStorage.getItem('zhengz_question_records') || '{}');
            recs[activeQuestion.value.id] = {
              status: correct ? 'right' : 'wrong',
              selected: Array.from(selectedOptions.value),
              answeredAt: Date.now()
            };
            localStorage.setItem('zhengz_question_records', JSON.stringify(recs));
            questionRecords.value = recs;
          } catch (e) {}
        }

        function resetQuestion() {
          hasSubmitted.value = false;
          selectedOptions.value = new Set();
        }

        function prevQuestion() {
          const qs = props.card?.relatedQuestions || [];
          const idx = activeQuestionIndex.value;
          if (idx > 0) openQuestion(qs[idx - 1]);
        }

        function nextQuestion() {
          const qs = props.card?.relatedQuestions || [];
          const idx = activeQuestionIndex.value;
          if (idx < qs.length - 1) openQuestion(qs[idx + 1]);
        }

        function getQuestionStatus(qid) {
          return questionRecords.value[qid]?.status || null;
        }

        function getQuestionStatusClass(qid) {
          const s = getQuestionStatus(qid);
          if (s === 'right') return 'answered-right';
          if (s === 'wrong') return 'answered-wrong';
          return '';
        }

        return { fullRevealed, revealedSet, isImgZoomed, parsedSegments, cleanDistinctions, cleanMnemonics, parseMnemonicParts, resolveImageUrl, toggleSeg, revealAll, hideAll, activeQuestion, selectedOptions, hasSubmitted, isCorrect, questionRecords, groupedQuestions, activeQuestionIndex, isMultiChoice, normalizedCorrectAnswer, formattedOptions, openQuestion, handleOptionClick, isOptionCorrect, submitAnswer, resetQuestion, prevQuestion, nextQuestion, getQuestionStatus, getQuestionStatusClass };
      },
      template: `
        <div :class="['card-container', 'font-' + fontSize]">
          <div class="card-header">
            <div class="header-left">
              <span class="source-id-tag">考点 {{ card.sourceId }}</span>
              <span class="hierarchy-tag">{{ card.subject }} · {{ card.section }}</span>
            </div>
            <button :class="['fav-btn', { active: isFavorite }]" @click="$emit('toggle-fav')">
              {{ isFavorite ? '★ 已收藏' : '☆ 收藏' }}
            </button>
          </div>

          <div class="card-title-bar">
            <h2 class="kp-title">{{ card.title }}</h2>
            <span class="page-hint">📖 原书 P{{ card.bookPage[0] }} · PDF P{{ card.sourcePage[0] }}</span>
          </div>

          <div v-if="mode === 'full' && !fullRevealed" class="full-cover" @click="fullRevealed = true">
            <div style="font-size:26px;">🙈</div>
            <div style="font-weight:600; color:#7c6853; margin-top:6px;">整卡已遮挡 · 点击揭晓正文</div>
          </div>

          <div v-else class="card-body">
            <div v-if="mode !== 'none'" class="cloze-toolbar">
              <span style="color:var(--primary-accent); font-weight:bold;">{{ mode }} 遮挡模式</span>
              <div style="display:flex; gap:6px;">
                <button class="tool-link" @click="revealAll">全部显示</button>
                <button class="tool-link" @click="hideAll">重新遮挡</button>
              </div>
            </div>


            <!-- 考点脉络原图 (如考点037史纲整体脉络图) -->
            <div v-if="card.inlineImage" class="card-inline-image-box">
              <img 
                :src="card.inlineImage" 
                alt="考点原始脉络图" 
                :class="['card-inline-img', { zoomed: isImgZoomed }]"
                @click="isImgZoomed = !isImgZoomed"
                title="点击切换放大/缩小脉络图"
              />
              <div class="inline-img-tip">📊 考点037 史纲整体脉络原始高清大图（点击切换放大 / 左右滑动浏览）</div>
            </div>

            <div class="content-text">
              <template v-for="seg in parsedSegments" :key="seg.id">
                <br v-if="seg.type === 'newline'" />
                <span v-else-if="seg.type === 'keyword'"
                  :class="[seg.shouldCloze ? (revealedSet.has(seg.id) ? 'cloze-revealed' : 'cloze-hidden') : 'keyword-highlight']"
                  :style="(!seg.shouldCloze || revealedSet.has(seg.id)) ? { color: seg.color, '--kw-color': seg.color } : {}"
                  @click="toggleSeg(seg)">
                  {{ seg.text }}
                </span>
                <span v-else-if="seg.type === 'symbol'" class="symbol-sticker" :title="seg.desc || seg.name" @click.stop>
                  <img v-if="seg.hash" :src="resolveImageUrl('symbols/' + seg.hash + '.png')" :alt="seg.desc || seg.name" class="symbol-sticker-img" />
                  <span v-else class="symbol-fallback">[{{ seg.name }}]</span>
                </span>
                <span v-else
                  :class="[seg.shouldCloze ? (revealedSet.has(seg.id) ? 'cloze-revealed' : 'cloze-hidden') : '']"
                  @click="toggleSeg(seg)">{{ seg.text }}</span>
              </template>
            </div>

            <div v-if="cleanDistinctions.length > 0" class="distinctions-box">
              <div class="dist-title">⚡ 命题陷阱 & 概念辨析：</div>
              <div v-for="(d, dIdx) in cleanDistinctions" :key="dIdx" class="dist-item">
                <span :class="['dist-badge', d.verdict === 'correct' ? 'correct' : d.verdict === 'wrong' ? 'wrong' : 'unclear']">
                  {{ d.verdict === 'correct' ? '正确表述' : d.verdict === 'wrong' ? '错误干扰' : '易混辨析' }}
                </span>
                <span style="flex:1;">{{ d.statement }}</span>
              </div>
            </div>

            <div v-if="cleanMnemonics.length > 0" class="mnemonics-box">
              <div v-for="(m, mIdx) in cleanMnemonics" :key="mIdx" class="mnemonic-item">
                <span style="font-size:1.1em;">🎯</span>
                <div>
                  <template v-for="(part, pIdx) in parseMnemonicParts(m.text)" :key="pIdx">
                    <span v-if="part.type === 'symbol'" class="symbol-sticker" :title="part.desc || part.text" @click.stop>
                      <img v-if="part.hash" :src="resolveImageUrl('symbols/' + part.hash + '.png')" :alt="part.desc || part.text" class="symbol-sticker-img" />
                      <span v-else class="symbol-fallback">[{{ part.text }}]</span>
                    </span>
                    <span v-else>{{ part.text }}</span>
                  </template>
                </div>
              </div>
            </div>

            <!-- 原书考点对应真题与模拟题 (学习 Markji 一页纸逻辑) -->
            <div v-if="card.relatedQuestions && card.relatedQuestions.length > 0" class="related-questions-section">
              <div class="section-badge related-badge">
                <span>🎯 原书考点对应真题与模拟题</span>
                <span class="related-count-pill">{{ card.relatedQuestions.length }} 题</span>
              </div>

              <div class="related-groups-list">
                <!-- 历年真题组 -->
                <div v-if="groupedQuestions['真题']?.length" class="question-source-group group-true">
                  <div class="source-group-header">
                    <span class="source-tag true-tag">🔴 历年真题 ({{ groupedQuestions['真题'].length }})</span>
                  </div>
                  <div class="question-pill-grid">
                    <button
                      v-for="q in groupedQuestions['真题']"
                      :key="q.id"
                      :class="['q-pill-btn', getQuestionStatusClass(q.id)]"
                      @click.stop="openQuestion(q)"
                      :title="'【真题】' + q.label + ' · ' + q.kind + ' (点击做题)'"
                    >
                      <span class="q-pill-label">{{ q.label }}</span>
                      <span v-if="getQuestionStatus(q.id) === 'right'" class="q-status-badge right">✓</span>
                      <span v-else-if="getQuestionStatus(q.id) === 'wrong'" class="q-status-badge wrong">✗</span>
                    </button>
                  </div>
                </div>

                <!-- 名师模拟题组 -->
                <div v-if="groupedQuestions['模拟题']?.length" class="question-source-group group-mock">
                  <div class="source-group-header">
                    <span class="source-tag mock-tag">🔵 名师模拟题 ({{ groupedQuestions['模拟题'].length }})</span>
                  </div>
                  <div class="question-pill-grid">
                    <button
                      v-for="q in groupedQuestions['模拟题']"
                      :key="q.id"
                      :class="['q-pill-btn', getQuestionStatusClass(q.id)]"
                      @click.stop="openQuestion(q)"
                      :title="'【模拟题】' + q.label + ' · ' + q.kind + ' (点击做题)'"
                    >
                      <span class="q-pill-label">{{ q.label }}</span>
                      <span v-if="getQuestionStatus(q.id) === 'right'" class="q-status-badge right">✓</span>
                      <span v-else-if="getQuestionStatus(q.id) === 'wrong'" class="q-status-badge wrong">✗</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="card-footer">
            <span style="font-family:monospace; color:var(--text-muted);">考点 ID: {{ card.id }}</span>
          </div>

          <!-- 题目练习弹窗 (学习 Markji 答题抽屉/弹窗逻辑) -->
          <div v-if="activeQuestion" class="q-modal-backdrop" @click.self="activeQuestion = null">
            <div class="q-modal-container" role="dialog" aria-modal="true">
              <div class="q-modal-header">
                <div class="q-header-badges">
                  <span :class="['q-source-tag', activeQuestion.sourceType === '真题' ? 'tag-true' : 'tag-mock']">
                    {{ activeQuestion.sourceType === '真题' ? '🔴 历年真题' : '🔵 名师模拟题' }}
                  </span>
                  <span class="q-label-tag">{{ activeQuestion.label }}</span>
                  <span class="q-kind-tag">{{ activeQuestion.kind }}</span>
                </div>
                <button class="q-close-btn" @click="activeQuestion = null" aria-label="关闭">✕</button>
              </div>

              <div class="q-modal-body">
                <div class="q-stem-text">
                  <span class="q-num-prefix" v-if="card.relatedQuestions?.length > 1">({{ activeQuestionIndex + 1 }}/{{ card.relatedQuestions.length }})</span>
                  {{ activeQuestion.stem }}
                </div>

                <div class="q-options-list">
                  <div
                    v-for="opt in formattedOptions"
                    :key="opt.letter"
                    :class="[
                      'q-option-item',
                      {
                        selected: selectedOptions.has(opt.letter),
                        correct: hasSubmitted && isOptionCorrect(opt.letter),
                        wrong: hasSubmitted && selectedOptions.has(opt.letter) && !isOptionCorrect(opt.letter)
                      }
                    ]"
                    @click="handleOptionClick(opt.letter)"
                  >
                    <div class="q-opt-letter-box">
                      <span class="q-letter">{{ opt.letter }}</span>
                    </div>
                    <div class="q-opt-content">{{ opt.text }}</div>
                    <div v-if="hasSubmitted" class="q-opt-feedback-icon">
                      <span v-if="isOptionCorrect(opt.letter)" class="icon-right">✓ 正确</span>
                      <span v-else-if="selectedOptions.has(opt.letter)" class="icon-wrong">✗ 你的选择</span>
                    </div>
                  </div>
                </div>

                <div class="q-action-bar">
                  <button 
                    v-if="!hasSubmitted"
                    class="q-submit-btn" 
                    :disabled="selectedOptions.size === 0"
                    @click="submitAnswer"
                  >
                    确认提交答案
                  </button>
                  <div v-else class="q-submitted-actions">
                    <div :class="['q-result-banner', isCorrect ? 'result-right' : 'result-wrong']">
                      <span class="result-icon">{{ isCorrect ? '🎉' : '⚠️' }}</span>
                      <span class="result-text">
                        {{ isCorrect ? '回答正确！' : ('回答错误，正确答案是：' + normalizedCorrectAnswer) }}
                      </span>
                    </div>
                    <button class="q-retry-btn" @click="resetQuestion">重做本题</button>
                  </div>
                </div>

                <div v-if="hasSubmitted && activeQuestion.explanation" class="q-explanation-card">
                  <div class="q-exp-title">📖 答案与详细解析</div>
                  <div class="q-exp-content">{{ activeQuestion.explanation }}</div>
                </div>

                <div v-if="card" class="q-linked-kp-box">
                  <span class="q-linked-tip">📌 对应考点：</span>
                  <span class="q-linked-name">考点 {{ card.sourceId || card.id }} · {{ card.title }}</span>
                </div>
              </div>

              <div class="q-modal-footer">
                <div class="q-footer-nav">
                  <button 
                    class="q-nav-step-btn" 
                    :disabled="activeQuestionIndex <= 0"
                    @click="prevQuestion"
                  >
                    ← 上一题
                  </button>
                  <span class="q-footer-counter" v-if="card.relatedQuestions?.length > 1">
                    {{ activeQuestionIndex + 1 }} / {{ card.relatedQuestions.length }}
                  </span>
                  <button 
                    class="q-nav-step-btn" 
                    :disabled="activeQuestionIndex >= (card.relatedQuestions?.length || 1) - 1"
                    @click="nextQuestion"
                  >
                    下一题 →
                  </button>
                </div>
                <button class="q-footer-done-btn" @click="activeQuestion = null">完成 / 返回考点</button>
              </div>
            </div>
          </div>
        </div>
      `
    };

    createApp({
      components: { 'card-viewer-component': CardViewerComponent },
      setup() {
        const VALID_TABS = ['browse', 'solve'];

        function parseHash() {
          try {
            const rawHash = window.location.hash.replace(/^#\/?/, '');
            if (!rawHash) return null;
            const [tabPart, queryPart] = rawHash.split('?');
            const tab = VALID_TABS.includes(tabPart) ? tabPart : null;
            let cardId = '';
            if (queryPart) {
              const params = new URLSearchParams(queryPart);
              cardId = params.get('card') || '';
            }
            return { tab, cardId };
          } catch(e) {
            return null;
          }
        }

        function getInitialState() {
          const fromHash = parseHash();
          if (fromHash && fromHash.tab) {
            return {
              tab: fromHash.tab,
              cardId: fromHash.cardId || (typeof localStorage !== 'undefined' ? localStorage.getItem('zhengz_last_browse_card') || '' : '')
            };
          }
          let savedTab = 'browse';
          let savedCardId = '';
          try {
            savedTab = localStorage.getItem('zhengz_active_tab') || 'browse';
            if (!VALID_TABS.includes(savedTab)) savedTab = 'browse';
            savedCardId = localStorage.getItem('zhengz_last_browse_card') || '';
          } catch(e) {}
          return { tab: savedTab, cardId: savedCardId };
        }

        const initial = getInitialState();
        const currentTab = ref(initial.tab);
        const browseClozeMode = ref('none');
        const showSettingsModal = ref(false);
        const isDrawerOpen = ref(false);
        const browseCardAreaRef = ref(null);

        const userRecords = ref({});
        const userSettings = ref({ fontSizeLevel: 'medium', defaultClozeMode: 'keyword' });

        function loadStorage() {
          try {
            const recStr = localStorage.getItem('zhengz_records_v1');
            if (recStr) userRecords.value = JSON.parse(recStr);
            const setStr = localStorage.getItem('zhengz_settings_v1');
            if (setStr) userSettings.value = { ...userSettings.value, ...JSON.parse(setStr) };
          } catch(e) {}
        }

        function saveStorage() {
          try {
            localStorage.setItem('zhengz_records_v1', JSON.stringify(userRecords.value));
            localStorage.setItem('zhengz_settings_v1', JSON.stringify(userSettings.value));
          } catch(e) {}
        }

        function updateUrlAndStorage(tab, cardId = null) {
          try {
            localStorage.setItem('zhengz_active_tab', tab);
            let hash = `#/${tab}`;
            if (tab === 'browse') {
              const cId = cardId || currentBrowseCard.value?.id;
              if (cId) {
                hash += `?card=${cId}`;
                localStorage.setItem('zhengz_last_browse_card', cId);
              }
            }
            if (window.location.hash !== hash) {
              window.history.replaceState(null, '', hash);
            }
          } catch(e) {}
        }

        function handleHashChange() {
          const state = parseHash();
          if (state && state.tab && state.tab !== currentTab.value) {
            currentTab.value = state.tab;
          }
        }

        watch(currentTab, (newTab) => {
          updateUrlAndStorage(newTab);
        });

        const initialCard = (initial.cardId && ALL_CARDS.find(c => c.id === initial.cardId)) || ALL_CARDS[0] || null;
        const currentBrowseCard = ref(initialCard);

        watch(currentBrowseCard, (newCard) => {
          if (newCard && currentTab.value === 'browse') {
            try {
              if (typeof localStorage !== 'undefined') {
                updateUrlAndStorage('browse', newCard.id);
              }
            } catch(e) {}
          }
        });

        const currentClozeMode = ref('keyword');
        const reciteQueue = ref([]);
        const reciteIndex = ref(0);
        const reciteFinished = ref(false);

        const isQuizRunning = ref(false);
        const quizScope = ref('all');
        const quizPool = ref([]);
        const quizIndex = ref(0);
        const quizRevealed = ref(false);

        const ALL_METHODS = __ALL_METHODS_JSON__;
        const ALL_QUESTIONS = __ALL_QUESTIONS_JSON__;
        const ALL_MINDSETS = __ALL_MINDSETS_JSON__;
        const mindsetPrinciples = ALL_MINDSETS.mindsetPrinciples || [];
        const classicMarxQuotes = ALL_MINDSETS.classicMarxQuotes || [];
        const tombstoneWords = ALL_MINDSETS.tombstoneWords || [];

        const solveSubTab = ref('methods');
        const methodsActiveTab = ref('methods');
        const showMindsetBanner = ref(false);
        const showMarxModal = ref(false);
        const showTombstoneModal = ref(false);

        function getMethodObj(mid) {
          return ALL_METHODS.find(x => x.id === mid) || null;
        }

        const selectedPracticeMethod = ref('all');
        const currentPracticeIndex = ref(0);
        const solveUserAnswers = ref([]);
        const isSolveSubmitted = ref(false);

        const solveRecords = ref({});
        function loadSolveStorage() {
          try {
            const raw = localStorage.getItem('solve_records_v1');
            if (raw) solveRecords.value = JSON.parse(raw);
          } catch(e) {}
        }
        function saveSolveStorage() {
          try {
            localStorage.setItem('solve_records_v1', JSON.stringify(solveRecords.value));
          } catch(e) {}
        }

        const filteredSolveQuestions = computed(() => {
          if (selectedPracticeMethod.value === 'all') return ALL_QUESTIONS;
          return ALL_QUESTIONS.filter(q => q.methods.includes(selectedPracticeMethod.value));
        });

        const currentPracticeQ = computed(() => filteredSolveQuestions.value[currentPracticeIndex.value] || null);

        function toggleSolveOption(opt) {
          if (isSolveSubmitted.value) return;
          if (currentPracticeQ.value.type === 'single') {
            solveUserAnswers.value = [opt];
          } else {
            const idx = solveUserAnswers.value.indexOf(opt);
            if (idx >= 0) solveUserAnswers.value.splice(idx, 1);
            else { solveUserAnswers.value.push(opt); solveUserAnswers.value.sort(); }
          }
        }

        const isSolveCorrect = computed(() => {
          if (!currentPracticeQ.value) return false;
          return [...currentPracticeQ.value.answer].sort().join('') === [...solveUserAnswers.value].sort().join('');
        });

        function submitSolvePractice() {
          if (solveUserAnswers.value.length === 0) return;
          isSolveSubmitted.value = true;
          gradeSolveSRS(isSolveCorrect.value ? 'good' : 'again', false);
        }

        function gradeSolveSRS(grade, advance = true) {
          if (!currentPracticeQ.value) return;
          const qid = currentPracticeQ.value.id;
          const prev = solveRecords.value[qid] || { reviewCount:0, consecutiveGood:0, inMistakeBook:false, history:[] };
          let newConsecutive = prev.consecutiveGood;
          let inMistake = prev.inMistakeBook;

          if (grade === 'again' || grade === 'hard') {
            newConsecutive = 0;
            inMistake = true;
          } else {
            newConsecutive++;
            if (newConsecutive >= 2) inMistake = false;
          }

          solveRecords.value[qid] = {
            ...prev,
            reviewCount: prev.reviewCount + 1,
            consecutiveGood: newConsecutive,
            inMistakeBook: inMistake,
            lastGrade: grade,
            history: [...prev.history, { time: Date.now(), isCorrect: isSolveCorrect.value, userSelected: solveUserAnswers.value }]
          };
          saveSolveStorage();

          if (advance && currentPracticeIndex.value < filteredSolveQuestions.value.length - 1) {
            currentPracticeIndex.value++;
            solveUserAnswers.value = [];
            isSolveSubmitted.value = false;
          }
        }

        function startPracticeMethod(mid) {
          selectedPracticeMethod.value = mid;
          currentPracticeIndex.value = 0;
          solveUserAnswers.value = [];
          isSolveSubmitted.value = false;
          solveSubTab.value = 'practice';
        }

        function getMethodName(mid) {
          const m = ALL_METHODS.find(x => x.id === mid);
          return m ? m.name : mid;
        }

        function isSolveMistake(qid) {
          return !!solveRecords.value[qid]?.inMistakeBook;
        }

        function toggleSolveMistake(qid) {
          const prev = solveRecords.value[qid] || { reviewCount:0, consecutiveGood:0, inMistakeBook:false, history:[] };
          solveRecords.value[qid] = { ...prev, inMistakeBook: !prev.inMistakeBook };
          saveSolveStorage();
        }

        // 盲测模式
        const currentBlindIndex = ref(0);
        const blindUserAnswers = ref([]);
        const chosenBlindMethod = ref('');
        const isBlindSubmitted = ref(false);

        const currentBlindQ = computed(() => ALL_QUESTIONS[currentBlindIndex.value] || null);
        function toggleBlindOption(opt) {
          if (isBlindSubmitted.value) return;
          if (currentBlindQ.value.type === 'single') blindUserAnswers.value = [opt];
          else {
            const idx = blindUserAnswers.value.indexOf(opt);
            if (idx >= 0) blindUserAnswers.value.splice(idx, 1);
            else { blindUserAnswers.value.push(opt); blindUserAnswers.value.sort(); }
          }
        }
        const isBlindMethodHit = computed(() => currentBlindQ.value && currentBlindQ.value.methods.includes(chosenBlindMethod.value));
        function submitBlind() {
          isBlindSubmitted.value = true;
        }
        function nextBlindQuestion() {
          if (currentBlindIndex.value < ALL_QUESTIONS.length - 1) {
            currentBlindIndex.value++;
            blindUserAnswers.value = [];
            chosenBlindMethod.value = '';
            isBlindSubmitted.value = false;
          }
        }

        // 限时模考
        const isMockRunning = ref(false);
        const mockSeconds = ref(900);
        const mockPool = ref([]);
        const mockQIndex = ref(0);
        const mockAnswers = ref({});
        let mockTimer = null;

        const currentMockQ = computed(() => mockPool.value[mockQIndex.value] || null);

        function startMockExam(count = 10, minutes = 15) {
          const shuffled = [...ALL_QUESTIONS].sort(() => Math.random() - 0.5);
          mockPool.value = shuffled.slice(0, count);
          mockQIndex.value = 0;
          mockAnswers.value = {};
          mockSeconds.value = minutes * 60;
          isMockRunning.value = true;

          if (mockTimer) clearInterval(mockTimer);
          mockTimer = setInterval(() => {
            if (mockSeconds.value > 0) {
              mockSeconds.value--;
            } else {
              finishMockExam();
            }
          }, 1000);
        }

        function toggleMockOpt(key) {
          if (!currentMockQ.value) return;
          const qid = currentMockQ.value.id;
          const curr = mockAnswers.value[qid] ? [...mockAnswers.value[qid]] : [];
          if (currentMockQ.value.type === 'single') {
            mockAnswers.value[qid] = [key];
          } else {
            const idx = curr.indexOf(key);
            if (idx >= 0) curr.splice(idx, 1);
            else { curr.push(key); curr.sort(); }
            mockAnswers.value[qid] = curr;
          }
        }

        function finishMockExam() {
          if (mockTimer) clearInterval(mockTimer);
          let score = 0;
          mockPool.value.forEach(q => {
            const userAns = mockAnswers.value[q.id] || [];
            const isCor = [...userAns].sort().join('') === [...q.answer].sort().join('');
            if (isCor) score++;
          });
          alert(`模考结束！得分：${score} / ${mockPool.value.length} (正确率 ${Math.round((score/mockPool.value.length)*100)}%)`);
          isMockRunning.value = false;
        }

        // 错题统计
        const solveMistakeQuestions = computed(() => {
          return ALL_QUESTIONS.filter(q => solveRecords.value[q.id]?.inMistakeBook);
        });
        const solveMistakeCount = computed(() => solveMistakeQuestions.value.length);
        const solvePracticedCount = computed(() => {
          return Object.values(solveRecords.value).filter(r => r.history && r.history.length > 0).length;
        });
        const solveAccuracy = computed(() => {
          let totalReviews = 0;
          let totalCorrect = 0;
          Object.values(solveRecords.value).forEach(r => {
            if (r.history) {
              r.history.forEach(h => {
                totalReviews++;
                if (h.isCorrect) totalCorrect++;
              });
            }
          });
          return totalReviews > 0 ? Math.round((totalCorrect / totalReviews) * 100) : 0;
        });

        function getMethodStatStd(mid) {
          const m = ALL_METHODS.find(x => x.id === mid);
          if (!m) return { practiced:0, accuracy:0 };
          let p = 0, c = 0;
          m.questionIds.forEach(qid => {
            const r = solveRecords.value[qid];
            if (r && r.history.length > 0) {
              p++;
              if (r.history[r.history.length - 1].isCorrect) c++;
            }
          });
          return { practiced: p, accuracy: p > 0 ? Math.round((c / p) * 100) : 0 };
        }

        onMounted(() => {
          showSettingsModal.value = false;
          showMarxModal.value = false;
          showTombstoneModal.value = false;
          loadStorage();
          loadSolveStorage();
          if (initial.cardId) {
            const target = ALL_CARDS.find(c => c.id === initial.cardId);
            if (target) currentBrowseCard.value = target;
          }
          if (!currentBrowseCard.value && ALL_CARDS.length > 0) {
            currentBrowseCard.value = ALL_CARDS[0];
          }
          initReciteQueue();
          updateUrlAndStorage(currentTab.value, currentBrowseCard.value?.id);
          window.addEventListener('hashchange', handleHashChange);
        });

        const isFavorite = (id) => !!userRecords.value[id]?.isFavorite;
        function toggleFavorite(id) {
          if (!userRecords.value[id]) {
            userRecords.value[id] = { reviewCount:0, consecutiveGood:0, inMistakeBook:false, isFavorite:false };
          }
          userRecords.value[id].isFavorite = !userRecords.value[id].isFavorite;
          saveStorage();
        }

        const dueCards = computed(() => {
          const now = Date.now();
          return ALL_CARDS.filter(c => {
            const r = userRecords.value[c.id];
            return r && r.nextReviewTime <= now;
          });
        });

        const mistakeCards = computed(() => {
          return ALL_CARDS.filter(c => userRecords.value[c.id]?.inMistakeBook);
        });

        const learnedCount = computed(() => {
          return Object.values(userRecords.value).filter(r => r.reviewCount > 0).length;
        });

        const masteredCount = computed(() => {
          return Object.values(userRecords.value).filter(r => r.consecutiveGood >= 2 && !r.inMistakeBook).length;
        });

        const progressPercent = computed(() => {
          return Math.round((masteredCount.value / ALL_CARDS.length) * 100);
        });

        const searchQuery = ref('');
        const selectedSubject = ref('全部');

        const filteredCards = computed(() => {
          const q = searchQuery.value.trim().toLowerCase();
          const sub = selectedSubject.value;
          return ALL_CARDS.filter(c => {
            if (sub !== '全部' && c.subject !== sub) return false;
            if (q) {
              const match = c.id.toLowerCase().includes(q) || c.sourceId.includes(q) || c.title.toLowerCase().includes(q) || c.content.toLowerCase().includes(q);
              if (!match) return false;
            }
            return true;
          });
        });

        const currentBrowseIndex = computed(() => {
          if (!currentBrowseCard.value) return 0;
          return filteredCards.value.findIndex(c => c.id === currentBrowseCard.value.id);
        });

        function scrollBrowseTop() {
          if (browseCardAreaRef.value) {
            browseCardAreaRef.value.scrollTop = 0;
          }
        }

        function selectBrowseCard(card) {
          currentBrowseCard.value = card;
          isDrawerOpen.value = false;
          scrollBrowseTop();
        }

        function prevBrowseCard() {
          const idx = currentBrowseIndex.value;
          if (idx > 0) {
            currentBrowseCard.value = filteredCards.value[idx - 1];
            scrollBrowseTop();
          }
        }

        function nextBrowseCard() {
          const idx = currentBrowseIndex.value;
          if (idx < filteredCards.value.length - 1) {
            currentBrowseCard.value = filteredCards.value[idx + 1];
            scrollBrowseTop();
          }
        }

        function setFontSize(lvl) {
          userSettings.value.fontSizeLevel = lvl;
          saveStorage();
        }

        // 手机手势切卡：防边缘退出手势 + 优化阈值与角度判定
        let touchX = 0;
        let touchY = 0;
        let touchStartTime = 0;
        let isEdgeTouch = false;

        function handleTouchStart(e) {
          if (e.changedTouches && e.changedTouches.length > 0) {
            const t = e.changedTouches[0];
            touchX = t.clientX;
            touchY = t.clientY;
            touchStartTime = Date.now();
            const screenW = window.innerWidth || document.documentElement.clientWidth;
            isEdgeTouch = (touchX < 40 || touchX > screenW - 40);
          }
        }

        function handleTouchEnd(e) {
          if (!e.changedTouches || e.changedTouches.length === 0) return;
          if (isEdgeTouch) return;

          const t = e.changedTouches[0];
          const dx = t.clientX - touchX;
          const dy = t.clientY - touchY;
          const dt = Date.now() - touchStartTime;

          if (Math.abs(dx) >= 70 && Math.abs(dx) > Math.abs(dy) * 2.0 && dt < 600) {
            if (dx < 0) {
              nextBrowseCard();
            } else {
              prevBrowseCard();
            }
          }
        }

        function initReciteQueue() {
          const due = dueCards.value;
          if (due.length > 0) {
            reciteQueue.value = [...due];
          } else {
            const unstudied = ALL_CARDS.filter(c => !userRecords.value[c.id]);
            reciteQueue.value = unstudied.slice(0, 10);
          }
          reciteIndex.value = 0;
          reciteFinished.value = false;
        }

        const currentReciteCard = computed(() => reciteQueue.value[reciteIndex.value] || null);

        function handleEvaluate(grade) {
          if (!currentReciteCard.value) return;
          const cardId = currentReciteCard.value.id;
          const prev = userRecords.value[cardId] || { reviewCount: 0, consecutiveGood: 0, inMistakeBook: false };

          let nextIntervalDays = 1;
          let newConsecutive = prev.consecutiveGood;
          let inMistake = prev.inMistakeBook;

          if (grade === 'again') {
            nextIntervalDays = 0.5;
            newConsecutive = 0;
            inMistake = true;
          } else if (grade === 'hard') {
            nextIntervalDays = 1;
            newConsecutive = 0;
            inMistake = true;
          } else if (grade === 'good') {
            newConsecutive++;
            nextIntervalDays = newConsecutive === 1 ? 2 : newConsecutive === 2 ? 4 : 7;
            if (newConsecutive >= 2) inMistake = false;
          } else if (grade === 'easy') {
            newConsecutive += 2;
            nextIntervalDays = 7;
            inMistake = false;
          }

          userRecords.value[cardId] = {
            ...prev,
            reviewCount: prev.reviewCount + 1,
            consecutiveGood: newConsecutive,
            inMistakeBook: inMistake,
            lastReviewed: Date.now(),
            nextReviewTime: Date.now() + nextIntervalDays * 24 * 60 * 60 * 1000
          };
          saveStorage();

          if (reciteIndex.value < reciteQueue.value.length - 1) {
            reciteIndex.value++;
          } else {
            reciteFinished.value = true;
          }
        }

        function loadMoreRecite() {
          const unstudied = ALL_CARDS.filter(c => !userRecords.value[c.id]);
          if (unstudied.length > 0) {
            reciteQueue.value = unstudied.slice(0, 10);
            reciteIndex.value = 0;
            reciteFinished.value = false;
          } else {
            alert('全库卡片已全部开始学习！');
          }
        }

        function startReciteSingle(cardId) {
          const target = ALL_CARDS.find(c => c.id === cardId);
          if (target) {
            reciteQueue.value = [target];
            reciteIndex.value = 0;
            reciteFinished.value = false;
            currentTab.value = 'recite';
          }
        }

        function startQuiz(scope) {
          quizScope.value = scope;
          let pool = [];
          if (scope === 'mistakes') {
            pool = mistakeCards.value.length > 0 ? [...mistakeCards.value] : [...ALL_CARDS];
          } else {
            pool = [...ALL_CARDS];
          }
          pool.sort(() => Math.random() - 0.5);
          quizPool.value = pool.slice(0, 10);
          quizIndex.value = 0;
          quizRevealed.value = false;
          isQuizRunning.value = true;
        }

        const currentQuizCard = computed(() => quizPool.value[quizIndex.value] || null);

        function handleQuizEval(grade) {
          handleEvaluate(grade);
          if (quizIndex.value < quizPool.value.length - 1) {
            quizIndex.value++;
            quizRevealed.value = false;
          } else {
            alert('本轮 10 题抽查完成！继续加油！');
            isQuizRunning.value = false;
          }
        }

        function exportDataBackup() {
          const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({
            version: 1,
            records: userRecords.value,
            settings: userSettings.value,
            updatedAt: Date.now()
          }));
          const dlAnchorElem = document.createElement('a');
          dlAnchorElem.setAttribute("href", dataStr);
          dlAnchorElem.setAttribute("download", `zhengz_backup_${new Date().toISOString().slice(0,10)}.json`);
          dlAnchorElem.click();
        }

        return {
          currentTab, browseClozeMode, ALL_CARDS, dueCards, mistakeCards, learnedCount, masteredCount, progressPercent,
          searchQuery, selectedSubject, filteredCards, currentBrowseCard, currentBrowseIndex,
          isDrawerOpen, browseCardAreaRef, selectBrowseCard, prevBrowseCard, nextBrowseCard, setFontSize,
          handleTouchStart, handleTouchEnd,
          currentClozeMode, reciteQueue, reciteIndex, reciteFinished, currentReciteCard, handleEvaluate, loadMoreRecite, startReciteSingle,
          isQuizRunning, quizScope, quizPool, quizIndex, quizRevealed, currentQuizCard, startQuiz, handleQuizEval,
          showSettingsModal, userSettings, exportDataBackup,
          isFavorite, toggleFavorite,
          ALL_METHODS, ALL_QUESTIONS, solveSubTab, selectedPracticeMethod, currentPracticeIndex,
          filteredSolveQuestions, currentPracticeQ, solveUserAnswers, isSolveSubmitted, isSolveCorrect,
          toggleSolveOption, submitSolvePractice, gradeSolveSRS, startPracticeMethod, getMethodName,
          isSolveMistake, toggleSolveMistake,
          currentBlindIndex, blindUserAnswers, chosenBlindMethod, isBlindSubmitted, currentBlindQ,
          toggleBlindOption, isBlindMethodHit, submitBlind, nextBlindQuestion,
          isMockRunning, mockSeconds, mockPool, mockQIndex, currentMockQ, mockAnswers,
          startMockExam, toggleMockOpt, finishMockExam,
          solveMistakeQuestions, solveMistakeCount, solvePracticedCount, solveAccuracy, getMethodStatStd,
          ALL_MINDSETS, mindsetPrinciples, classicMarxQuotes, tombstoneWords,
          methodsActiveTab, showMindsetBanner, showMarxModal, showTombstoneModal, getMethodObj
        };
      }
    }).mount('#app');
  </script>
</body>
</html>
"""

final_html = html_template.replace("__VUE_TAG__", vue_tag)\
    .replace("__ALL_CARDS_JSON__", records_json_str)\
    .replace("__ALL_METHODS_JSON__", methods_json_str)\
    .replace("__ALL_QUESTIONS_JSON__", questions_json_str)\
    .replace("__ALL_MINDSETS_JSON__", mindsets_json_str)\
    .replace("__ALL_IMAGES_JSON__", images_json_str)

output_files = [
    "2027考研政治一页纸智能背诵与解题刷题全功能发布版.html",
    "2027考研政治一页纸智能背诵与刷题精简纯净版.html",
    "zhengz_recite_app.html",
    "zhengz_recite_app_lite.html",
    "index.html"
]
for out_p in output_files:
    with open(out_p, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"  Wrote: {out_p} ({len(final_html.encode('utf-8'))} bytes)")

print(f"Generated standalone HTML successfully:")
for out_p in output_files:
    print(f"  {out_p}: {len(final_html.encode('utf-8'))} bytes ({len(final_html.encode('utf-8')) / (1024*1024):.2f} MB)")
