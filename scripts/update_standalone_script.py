# -*- coding: utf-8 -*-
import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

# Read original generate_standalone_html.py
with open('scripts/generate_standalone_html.py', 'r', encoding='utf-8') as f:
    orig = f.read()

# 1. Update data loading at the top
top_insert = """
methods_path = "data/methods.json"
questions_path = "data/questions.json"

with open(methods_path, "r", encoding="utf-8") as f:
    methods_json_str = json.dumps(json.load(f), ensure_ascii=False)

with open(questions_path, "r", encoding="utf-8") as f:
    questions_json_str = json.dumps(json.load(f), ensure_ascii=False)
"""

orig = orig.replace(
    'records_json_str = json.dumps(kb_data["records"], ensure_ascii=False)',
    'records_json_str = json.dumps(kb_data["records"], ensure_ascii=False)' + top_insert
)

# 2. Add solve CSS styles before </style>
solve_css = """
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
"""

orig = orig.replace('  </style>\n</head>', solve_css + '  </style>\n</head>')

# 3. Add solve nav button in nav-links
solve_nav_btn = """        <button :class="['nav-btn', { active: currentTab === 'solve' }]" @click="currentTab = 'solve'">
          <span class="icon">🎯</span>
          <span class="label">解题刷题</span>
        </button>
"""
orig = orig.replace('      </div>\n\n      <button class="icon-btn"', solve_nav_btn + '      </div>\n\n      <button class="icon-btn"')

# 4. Add solve UI view in template right before <!-- PDF 原文图片弹窗 -->
solve_view_template = """
    <!-- 解题方法刷题模块 -->
    <div v-else-if="currentTab === 'solve'" style="min-height:calc(100vh - 60px);">
      <!-- 模块二级导航 -->
      <div class="solve-sub-nav">
        <button :class="['sub-pill', { active: solveSubTab === 'methods' }]" @click="solveSubTab = 'methods'">📚 方法库</button>
        <button :class="['sub-pill', { active: solveSubTab === 'practice' }]" @click="solveSubTab = 'practice'">✍️ 分类刷题</button>
        <button :class="['sub-pill', { active: solveSubTab === 'blind' }]" @click="solveSubTab = 'blind'">🎯 盲测识坑</button>
        <button :class="['sub-pill', { active: solveSubTab === 'mock' }]" @click="solveSubTab = 'mock'">⏱️ 限时模考</button>
        <button :class="['sub-pill', { active: solveSubTab === 'dashboard' }]" @click="solveSubTab = 'dashboard'">📊 统计看板</button>
        <button :class="['sub-pill', { active: solveSubTab === 'mistakes' }]" @click="solveSubTab = 'mistakes'">
          📕 错题本 <span v-if="solveMistakeCount > 0" style="background:var(--danger-accent); color:#fff; padding:1px 5px; border-radius:8px; font-size:11px;">{{ solveMistakeCount }}</span>
        </button>
      </div>

      <!-- 子视图 1: 方法库 -->
      <div v-if="solveSubTab === 'methods'" class="page-container">
        <div class="welcome-card">
          <div style="font-size:12px; background:#fbf1e4; color:#ab5712; padding:2px 8px; border-radius:4px; font-weight:700; width:fit-content;">澄潇宇 · 政治选择题一页纸</div>
          <h2 style="font-size:18px; font-weight:800; margin-top:6px;">🎯 10 类老头命题挖坑手法库</h2>
          <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">命题老师挖坑常有固定手法。掌握 10 类核心手法与标志词，在考场上能迅速识破陷阱、秒杀排除错误选项！</p>
        </div>

        <div class="methods-grid-std">
          <div v-for="(m, idx) in ALL_METHODS" :key="m.id" class="method-card-std">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:11px; background:var(--bg-warm); padding:2px 6px; border-radius:4px; font-weight:700; color:var(--text-muted);">手法 {{ idx + 1 }}</span>
              <strong style="font-size:16px;">{{ m.name }}</strong>
              <span style="font-size:12px; color:var(--primary-accent); font-weight:700; background:var(--primary-accent-bg); padding:2px 6px; border-radius:10px;">{{ m.questionIds.length }} 题</span>
            </div>
            <div class="mnemonic-box">🗣️ 口诀：{{ m.mnemonic }}</div>
            <div style="display:flex; flex-wrap:wrap; gap:4px;">
              <span v-for="kw in m.keywords" :key="kw" class="kw-pill">{{ kw }}</span>
            </div>
            <p style="font-size:12px; color:var(--text-muted); line-height:1.5;">{{ m.description }}</p>
            <button class="ctrl-btn" style="margin-top:auto; background:var(--primary-accent); color:#fff; padding:8px; font-weight:700;" @click="startPracticeMethod(m.id)">
              🎯 专项刷题 ({{ m.questionIds.length }}题)
            </button>
          </div>
        </div>
      </div>

      <!-- 子视图 2: 分类刷题 -->
      <div v-else-if="solveSubTab === 'practice'" class="page-container" style="max-width:850px;">
        <div style="display:flex; justify-content:space-between; align-items:center; background:#fff; padding:10px 14px; border-radius:8px; border:1px solid var(--border-card);">
          <div style="display:flex; align-items:center; gap:6px;">
            <span style="font-size:13px; font-weight:700;">分类:</span>
            <select v-model="selectedPracticeMethod" style="padding:4px 8px; border-radius:4px; border:1px solid var(--border-card);">
              <option value="all">🌟 全部 68 道真题</option>
              <option v-for="m in ALL_METHODS" :key="m.id" :value="m.id">{{ m.name }} ({{ m.questionIds.length }}题)</option>
            </select>
          </div>
          <span style="font-size:13px; font-weight:700; color:var(--primary-accent);">{{ currentPracticeIndex + 1 }} / {{ filteredSolveQuestions.length }}</span>
          <div style="display:flex; gap:6px;">
            <button class="ctrl-btn" :disabled="currentPracticeIndex <= 0" @click="currentPracticeIndex--">◀</button>
            <button class="ctrl-btn" :disabled="currentPracticeIndex >= filteredSolveQuestions.length - 1" @click="currentPracticeIndex++">▶</button>
          </div>
        </div>

        <div v-if="currentPracticeQ" style="background:#fff; border:1px solid var(--border-card); border-radius:10px; padding:18px; display:flex; flex-direction:column; gap:14px; margin-top:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px dashed var(--border-light); padding-bottom:8px;">
            <div style="display:flex; gap:6px; align-items:center;">
              <span style="font-weight:700; font-size:13px; background:var(--bg-beige); padding:2px 6px; border-radius:4px;">{{ currentPracticeQ.year }}年 第{{ currentPracticeQ.no }}题</span>
              <span :style="{ fontSize:'12px', padding:'2px 6px', borderRadius:'4px', fontWeight:'bold', background: currentPracticeQ.type === 'single' ? '#e9f3ff':'#fdf0ec', color: currentPracticeQ.type === 'single' ? '#1a62c4':'#c04928' }">
                {{ currentPracticeQ.type === 'single' ? '单选题' : '多选题' }}
              </span>
            </div>
            <button class="ctrl-btn" style="padding:3px 8px; font-size:12px;" @click="toggleSolveMistake(currentPracticeQ.id)">
              {{ isSolveMistake(currentPracticeQ.id) ? '📕 移出错题本' : '📖 加入错题本' }}
            </button>
          </div>

          <div style="font-size:15px; font-weight:600; line-height:1.7;">{{ currentPracticeQ.stem || '题干请对照下方真题大图：' }}</div>
          <div v-if="currentPracticeQ.image" style="background:var(--bg-warm); padding:6px 10px; border-radius:4px; font-size:12px; color:var(--text-muted); cursor:pointer;" @click="openSolveImageModal(currentPracticeQ)">
            🖼️ <span>点击查看原版思维导图真迹剪切图 (高清) 👁️</span>
          </div>

          <!-- 选项 -->
          <div>
            <div v-for="opt in ['A','B','C','D']" :key="opt"
              :class="['opt-std-item', { 
                selected: solveUserAnswers.includes(opt),
                'correct-rev': isSolveSubmitted && currentPracticeQ.answer.includes(opt),
                'wrong-rev': isSolveSubmitted && solveUserAnswers.includes(opt) && !currentPracticeQ.answer.includes(opt)
              }]"
              @click="toggleSolveOption(opt)"
            >
              <div class="opt-bubble-std">
                <span v-if="isSolveSubmitted && currentPracticeQ.answer.includes(opt)">✓</span>
                <span v-else-if="isSolveSubmitted && solveUserAnswers.includes(opt) && !currentPracticeQ.answer.includes(opt)">✕</span>
                <span v-else>{{ opt }}</span>
              </div>
              <div style="font-size:14px; line-height:1.5;">{{ currentPracticeQ.options[opt] || `(选项 ${opt} 见原题图)` }}</div>
            </div>
          </div>

          <!-- 提交作答 -->
          <div v-if="!isSolveSubmitted" style="text-align:right;">
            <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold; padding:8px 24px;" :disabled="solveUserAnswers.length === 0" @click="submitSolvePractice">
              确认提交
            </button>
          </div>

          <!-- 揭晓解析与自评 -->
          <div v-else style="display:flex; flex-direction:column; gap:12px; border-top:1px solid var(--border-light); padding-top:12px;">
            <div :style="{ padding:'10px 14px', borderRadius:'6px', background: isSolveCorrect ? 'var(--success-accent-bg)' : 'var(--danger-accent-bg)', border: '1px solid ' + (isSolveCorrect ? '#bee0ca' : '#f6caca') }">
              <strong>{{ isSolveCorrect ? '🎉 回答正确！' : '❌ 作答有误！' }}</strong>
              <span style="margin-left:8px;">正确答案：<strong style="color:var(--primary-accent); font-size:16px;">{{ currentPracticeQ.answer.join('') }}</strong></span>
            </div>

            <div style="display:flex; align-items:center; gap:6px;">
              <span style="font-size:12px; font-weight:700; color:var(--text-muted);">命中手法:</span>
              <span v-for="mid in currentPracticeQ.methods" :key="mid" class="hit-tag-std">🏷️ {{ getMethodName(mid) }}</span>
            </div>

            <div class="tip-box-std">
              <strong style="color:#8c5210;">💡 澄潇宇「一页纸」原版破题批注：</strong>
              <div style="margin-top:4px; white-space:pre-wrap;">{{ currentPracticeQ.tip }}</div>
            </div>

            <!-- SRS 自评 -->
            <div style="background:var(--bg-warm); padding:10px; border-radius:6px; display:flex; flex-direction:column; gap:6px;">
              <div style="font-size:12px; font-weight:700; color:var(--text-muted);">四档掌握度自评（纳入遗忘曲线）：</div>
              <div class="eval-buttons" style="display:grid; grid-template-columns:repeat(4,1fr); gap:6px;">
                <button class="eval-btn btn-again" @click="gradeSolveSRS('again')"><span class="btn-main">不会</span><span class="btn-sub">当天</span></button>
                <button class="eval-btn btn-hard" @click="gradeSolveSRS('hard')"><span class="btn-main">模糊</span><span class="btn-sub">1天</span></button>
                <button class="eval-btn btn-good" @click="gradeSolveSRS('good')"><span class="btn-main">掌握</span><span class="btn-sub">3天</span></button>
                <button class="eval-btn btn-easy" @click="gradeSolveSRS('easy')"><span class="btn-main">熟练</span><span class="btn-sub">7天</span></button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 子视图 3: 盲测识坑 -->
      <div v-else-if="solveSubTab === 'blind'" class="page-container" style="max-width:850px;">
        <div class="welcome-card">
          <div style="font-size:12px; background:#eef4fb; color:var(--primary-accent); padding:2px 8px; border-radius:4px; font-weight:700; width:fit-content;">🎯 高阶实战训练</div>
          <h2 style="font-size:18px; font-weight:800; margin-top:6px;">盲测模式 · 识别命题老头挖坑手法</h2>
          <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">题目分类已隐去。先做题，提交答案后判定命题手法。只有在无提示下识破挖坑逻辑，考场才能临危不乱！</p>
        </div>

        <div v-if="currentBlindQ" style="background:#fff; border:1px solid var(--border-card); border-radius:10px; padding:18px; display:flex; flex-direction:column; gap:14px; margin-top:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:13px;">第 {{ currentBlindIndex + 1 }} 题 / 共 {{ ALL_QUESTIONS.length }} 题</span>
            <button class="ctrl-btn" @click="nextBlindQuestion">下一题 ➔</button>
          </div>

          <div style="font-size:15px; font-weight:600; line-height:1.7;">{{ currentBlindQ.stem || '题干见原题图：' }}</div>
          <div v-if="currentBlindQ.image" style="background:var(--bg-warm); padding:6px 10px; border-radius:4px; font-size:12px; color:var(--text-muted); cursor:pointer;" @click="openSolveImageModal(currentBlindQ)">
            🖼️ <span>点击查看原版思维导图剪切图 (高清) 👁️</span>
          </div>

          <!-- 选项 -->
          <div>
            <div v-for="opt in ['A','B','C','D']" :key="opt"
              :class="['opt-std-item', { 
                selected: blindUserAnswers.includes(opt),
                'correct-rev': isBlindSubmitted && currentBlindQ.answer.includes(opt),
                'wrong-rev': isBlindSubmitted && blindUserAnswers.includes(opt) && !currentBlindQ.answer.includes(opt)
              }]"
              @click="toggleBlindOption(opt)"
            >
              <div class="opt-bubble-std">{{ opt }}</div>
              <div style="font-size:14px;">{{ currentBlindQ.options[opt] || `(选项 ${opt})` }}</div>
            </div>
          </div>

          <!-- 盲测手法判定 -->
          <div v-if="!isBlindSubmitted">
            <div style="font-size:13px; font-weight:700; margin-bottom:6px; color:var(--primary-accent);">你认为此题命题人使用了哪种手法/挖坑点？</div>
            <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(120px, 1fr)); gap:6px; margin-bottom:12px;">
              <button v-for="m in ALL_METHODS" :key="m.id"
                :class="['sub-pill', { active: chosenBlindMethod === m.id }]"
                @click="chosenBlindMethod = m.id" style="padding:6px 4px; text-align:center;">
                {{ m.name }}
              </button>
            </div>
            <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold; padding:8px 24px; width:100%;" :disabled="blindUserAnswers.length === 0 || !chosenBlindMethod" @click="submitBlind">
              双重揭晓（答案 + 手法）
            </button>
          </div>

          <div v-else style="display:flex; flex-direction:column; gap:10px; border-top:1px solid var(--border-light); padding-top:12px;">
            <div style="padding:10px; border-radius:6px; background:var(--bg-warm); border:1px solid var(--border-card);">
              <div>答案：<strong>{{ currentBlindQ.answer.join('') }}</strong> (作答: {{ blindUserAnswers.join('') }})</div>
              <div>手法判定：<strong :style="{ color: isBlindMethodHit ? 'var(--success-accent)' : 'var(--danger-accent)' }">{{ isBlindMethodHit ? '✅ 识破挖坑！' : '⚠️ 未命中' }}</strong> (真实手法: {{ currentBlindQ.methods.map(getMethodName).join(', ') }})</div>
            </div>
            <div class="tip-box-std">{{ currentBlindQ.tip }}</div>
            <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold;" @click="nextBlindQuestion">下一题 ➔</button>
          </div>
        </div>
      </div>

      <!-- 子视图 4: 限时模考 -->
      <div v-else-if="solveSubTab === 'mock'" class="page-container" style="max-width:850px;">
        <div v-if="!isMockRunning" class="welcome-card">
          <div style="font-size:12px; background:#fdf5ea; color:#b46b1d; padding:2px 8px; border-radius:4px; font-weight:700; width:fit-content;">⏱️ 限时实战模考</div>
          <h2 style="font-size:18px; font-weight:800; margin-top:6px;">全真真题限时模拟</h2>
          <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">真实考场时间压力训练。按标准计时，交卷后自动生成分析报告并归集错题。</p>
          <div style="margin:14px 0; display:flex; gap:10px;">
            <button class="sub-pill active" style="padding:8px 16px;">🎲 随机 16 题限时模考 (25分钟)</button>
          </div>
          <button class="ctrl-btn" style="background:var(--primary-accent); color:#fff; font-weight:bold; padding:10px;" @click="startMockExam">
            🚀 开始限时模考
          </button>
        </div>

        <div v-else style="display:flex; flex-direction:column; gap:14px;">
          <div style="display:flex; justify-content:space-between; align-items:center; background:#fff; padding:10px 14px; border-radius:8px; border:1px solid var(--border-card);">
            <span style="font-weight:700; color:var(--danger-accent);">⏱️ 倒计时: {{ Math.floor(mockSeconds / 60) }}:{{ (mockSeconds % 60).toString().padStart(2, '0') }}</span>
            <span style="font-size:13px;">第 {{ mockQIndex + 1 }} / {{ mockPool.length }} 题</span>
            <button class="ctrl-btn" style="background:var(--danger-accent); color:#fff;" @click="finishMockExam">提前交卷</button>
          </div>

          <div v-if="currentMockQ" style="background:#fff; border:1px solid var(--border-card); border-radius:10px; padding:18px; display:flex; flex-direction:column; gap:12px;">
            <div style="font-weight:700; font-size:14px;">{{ currentMockQ.year }}.{{ currentMockQ.no }} ({{ currentMockQ.type === 'single' ? '单选' : '多选' }})</div>
            <div style="font-size:15px; line-height:1.6;">{{ currentMockQ.stem || '题干见图：' }}</div>
            <div v-for="opt in ['A','B','C','D']" :key="opt"
              :class="['opt-std-item', { selected: (mockAnswers[currentMockQ.id] || []).includes(opt) }]"
              @click="toggleMockOpt(currentMockQ.id, currentMockQ.type, opt)"
            >
              <div class="opt-bubble-std">{{ opt }}</div>
              <div>{{ currentMockQ.options[opt] }}</div>
            </div>

            <div style="display:flex; justify-content:space-between; margin-top:8px;">
              <button class="ctrl-btn" :disabled="mockQIndex <= 0" @click="mockQIndex--">上一题</button>
              <button class="ctrl-btn" :disabled="mockQIndex >= mockPool.length - 1" @click="mockQIndex++">下一题</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 子视图 5: 统计看板 -->
      <div v-else-if="solveSubTab === 'dashboard'" class="page-container">
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:12px;">
          <div class="welcome-card" style="padding:14px; text-align:center;">
            <div style="font-size:24px; font-weight:800;">{{ ALL_QUESTIONS.length }}</div>
            <div style="font-size:12px; color:var(--text-muted);">收录真题</div>
          </div>
          <div class="welcome-card" style="padding:14px; text-align:center;">
            <div style="font-size:24px; font-weight:800; color:var(--primary-accent);">{{ solvePracticedCount }}</div>
            <div style="font-size:12px; color:var(--text-muted);">已练习</div>
          </div>
          <div class="welcome-card" style="padding:14px; text-align:center;">
            <div style="font-size:24px; font-weight:800; color:var(--success-accent);">{{ solveAccuracy }}%</div>
            <div style="font-size:12px; color:var(--text-muted);">综合正确率</div>
          </div>
          <div class="welcome-card" style="padding:14px; text-align:center;">
            <div style="font-size:24px; font-weight:800; color:var(--danger-accent);">{{ solveMistakeCount }}</div>
            <div style="font-size:12px; color:var(--text-muted);">待攻克错题</div>
          </div>
        </div>

        <!-- 10 类方法进度条 -->
        <div class="welcome-card" style="margin-top:14px;">
          <h3 style="font-size:15px; font-weight:800; margin-bottom:12px;">📊 10 类解题手法练习正确率</h3>
          <div v-for="m in ALL_METHODS" :key="m.id" style="margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
              <span>{{ m.name }}</span>
              <span>{{ getMethodStatStd(m.id).accuracy }}% ({{ getMethodStatStd(m.id).practiced }}/{{ m.questionIds.length }})</span>
            </div>
            <div style="height:6px; background:var(--bg-warm); border-radius:3px; overflow:hidden;">
              <div :style="{ width: getMethodStatStd(m.id).accuracy + '%', height:'100%', background:'var(--primary-accent)' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 子视图 6: 解题错题本 -->
      <div v-else-if="solveSubTab === 'mistakes'" class="page-container" style="max-width:850px;">
        <div class="welcome-card">
          <div style="font-size:12px; background:#fdf1f1; color:var(--danger-accent); padding:2px 8px; border-radius:4px; font-weight:700; width:fit-content;">📕 靶向攻坚</div>
          <h2 style="font-size:18px; font-weight:800; margin-top:6px;">解题方法错题本 ({{ solveMistakeQuestions.length }}题)</h2>
          <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">连续 2 次答对并自评良好即可从活跃错题本中自动移出。</p>
        </div>

        <div v-if="solveMistakeQuestions.length > 0" style="display:flex; flex-direction:column; gap:14px; margin-top:14px;">
          <div v-for="q in solveMistakeQuestions" :key="q.id" style="background:#fff; border:1px solid var(--border-card); border-radius:8px; padding:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <span style="font-weight:700; font-size:13px;">{{ q.year }}.{{ q.no }} ({{ q.type === 'single' ? '单选' : '多选' }})</span>
              <button class="ctrl-btn" style="padding:2px 6px; font-size:11px;" @click="toggleSolveMistake(q.id)">移出错题本 ✕</button>
            </div>
            <div style="font-size:14px; margin-bottom:8px;">{{ q.stem || '(图文题)' }}</div>
            <div style="font-size:13px; color:var(--text-muted); margin-bottom:4px;">正确答案：<strong style="color:var(--success-accent);">{{ q.answer.join('') }}</strong></div>
            <div class="tip-box-std">{{ q.tip }}</div>
          </div>
        </div>
        <div v-else class="welcome-card" style="text-align:center; padding:40px; margin-top:14px;">
          🎉 太棒了！当前没有任何解题错题！
        </div>
      </div>
    </div>
"""

orig = orig.replace('    <!-- PDF 原文图片弹窗 -->', solve_view_template + '\n    <!-- PDF 原文图片弹窗 -->')

# 5. Add script variables and logic in setup()
script_insert = """
        const ALL_METHODS = __ALL_METHODS_JSON__;
        const ALL_QUESTIONS = __ALL_QUESTIONS_JSON__;

        const solveSubTab = ref('methods');
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
        const mockSeconds = ref(25 * 60);
        const mockPool = ref([]);
        const mockQIndex = ref(0);
        const mockAnswers = ref({});
        let mockTimer = null;

        function startMockExam() {
          const singles = ALL_QUESTIONS.filter(q => q.type === 'single').sort(() => Math.random() - 0.5).slice(0, 8);
          const multis = ALL_QUESTIONS.filter(q => q.type === 'multi').sort(() => Math.random() - 0.5).slice(0, 8);
          mockPool.value = [...singles, ...multis];
          mockQIndex.value = 0;
          mockAnswers.value = {};
          mockSeconds.value = 25 * 60;
          isMockRunning.value = true;
          if (mockTimer) clearInterval(mockTimer);
          mockTimer = setInterval(() => {
            if (mockSeconds.value > 0) mockSeconds.value--;
            else finishMockExam();
          }, 1000);
        }
        const currentMockQ = computed(() => mockPool.value[mockQIndex.value] || null);
        function toggleMockOpt(qid, type, opt) {
          const cur = mockAnswers.value[qid] ? [...mockAnswers.value[qid]] : [];
          if (type === 'single') mockAnswers.value[qid] = [opt];
          else {
            const idx = cur.indexOf(opt);
            if (idx >= 0) cur.splice(idx, 1);
            else { cur.push(opt); cur.sort(); }
            mockAnswers.value[qid] = cur;
          }
        }
        function finishMockExam() {
          if (mockTimer) clearInterval(mockTimer);
          isMockRunning.value = false;
          alert('模考交卷完成！已录入刷题记录。');
        }

        // 看板统计
        const solveMistakeQuestions = computed(() => ALL_QUESTIONS.filter(q => solveRecords.value[q.id]?.inMistakeBook));
        const solveMistakeCount = computed(() => solveMistakeQuestions.value.length);
        const solvePracticedCount = computed(() => Object.values(solveRecords.value).filter(r => r.reviewCount > 0).length);
        const solveAccuracy = computed(() => {
          let c = 0, t = 0;
          ALL_QUESTIONS.forEach(q => {
            const r = solveRecords.value[q.id];
            if (r && r.history.length > 0) {
              t++;
              if (r.history[r.history.length - 1].isCorrect) c++;
            }
          });
          return t > 0 ? Math.round((c / t) * 100) : 0;
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

        function openSolveImageModal(q) {
          openImageModal({
            id: q.id,
            sourceId: q.id,
            title: `${q.year}年第${q.no}题 · 一页纸思维导图真题真迹`,
            sourceImages: [q.image]
          });
        }
"""

orig = orig.replace(
    '        onMounted(() => {\n          loadStorage();',
    script_insert + '\n        onMounted(() => {\n          loadStorage();\n          loadSolveStorage();'
)

# 6. Add return bindings
orig = orig.replace(
    '          isFavorite, toggleFavorite\n        };',
    """          isFavorite, toggleFavorite,
          ALL_METHODS, ALL_QUESTIONS, solveSubTab, selectedPracticeMethod, currentPracticeIndex,
          filteredSolveQuestions, currentPracticeQ, solveUserAnswers, isSolveSubmitted, isSolveCorrect,
          toggleSolveOption, submitSolvePractice, gradeSolveSRS, startPracticeMethod, getMethodName,
          isSolveMistake, toggleSolveMistake, openSolveImageModal,
          currentBlindIndex, blindUserAnswers, chosenBlindMethod, isBlindSubmitted, currentBlindQ,
          toggleBlindOption, isBlindMethodHit, submitBlind, nextBlindQuestion,
          isMockRunning, mockSeconds, mockPool, mockQIndex, currentMockQ, mockAnswers,
          startMockExam, toggleMockOpt, finishMockExam,
          solveMistakeQuestions, solveMistakeCount, solvePracticedCount, solveAccuracy, getMethodStatStd
        };"""
)

# 7. Final string replacement of template json markers
orig = orig.replace(
    'final_html = html_template.replace("__VUE_TAG__", vue_tag).replace("__ALL_CARDS_JSON__", records_json_str)',
    'final_html = html_template.replace("__VUE_TAG__", vue_tag).replace("__ALL_CARDS_JSON__", records_json_str).replace("__ALL_METHODS_JSON__", methods_json_str).replace("__ALL_QUESTIONS_JSON__", questions_json_str)'
)

with open('scripts/generate_standalone_html.py', 'w', encoding='utf-8') as f:
    f.write(orig)

print("Updated scripts/generate_standalone_html.py successfully!")
