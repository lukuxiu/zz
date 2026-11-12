<template>
  <div class="methods-view-container">
    <!-- 顶部引言卡片 -->
    <div class="methods-intro-card">
      <div class="intro-badge">澄潇宇 · 政治选择题一页纸</div>
      <h2 class="intro-title">🎯 老头命题手法（挖坑点）与解题思维模式</h2>
      <p class="intro-desc">
        有了正确的解题思维，才能显著提高选择题正确率。命题老师挖坑常有固定手法，掌握 10 类核心手法、4 大解题思维模式、马恩经典真理名言与 18 大墓碑词，考场秒杀排除干扰项！
      </p>

      <div class="intro-stats-row">
        <div class="stat-item">
          <span class="stat-num">{{ overallStats.total }}</span>
          <span class="stat-label">收录真题总数</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ overallStats.practiced }}</span>
          <span class="stat-label">已练习题目</span>
        </div>
        <div class="stat-item">
          <span class="stat-num accent">{{ overallStats.accuracy }}%</span>
          <span class="stat-label">综合正确率</span>
        </div>
      </div>

      <!-- 快速导航选项卡 -->
      <div class="section-tabs">
        <button 
          :class="['section-tab-btn', { active: activeSection === 'methods' }]" 
          @click="activeSection = 'methods'"
        >
          🎯 10 类命题挖坑手法 ({{ allMethods.length }})
        </button>
        <button 
          :class="['section-tab-btn', { active: activeSection === 'mindset' }]" 
          @click="activeSection = 'mindset'"
        >
          ⚡ 四大解题思维模式 (必背心法)
        </button>
        <button 
          :class="['section-tab-btn', { active: activeSection === 'quotes' }]" 
          @click="activeSection = 'quotes'"
        >
          📖 马恩列真题名言避坑 ({{ classicMarxQuotes.length }})
        </button>
        <button 
          :class="['section-tab-btn', { active: activeSection === 'tombstones' }]" 
          @click="activeSection = 'tombstones'"
        >
          ⚰️ 18 大高频墓碑词雷达
        </button>
      </div>
    </div>

    <!-- 1. 四大解题思维模式 (黄金方法论) -->
    <div v-show="activeSection === 'mindset' || activeSection === 'all'" class="mindset-principles-box">
      <div class="mindset-header">
        <span class="mindset-badge">实战破题核心 · 系统总结</span>
        <h3 class="mindset-title">⚡ 政治选择题四大解题思维模式</h3>
        <p class="mindset-subtitle">有了正确的解题思维，才能显著提高选择题正确率。牢记四大黄金准则：</p>
      </div>

      <div class="mindset-grid">
        <div 
          v-for="item in mindsetPrinciples" 
          :key="item.id"
          class="mindset-item"
        >
          <div class="mindset-item-top">
            <span class="mindset-icon">{{ item.num }}</span>
            <div class="mindset-item-head">
              <span class="mindset-tag">{{ item.tag }}</span>
              <h4 class="mindset-item-title">{{ item.title }}</h4>
            </div>
          </div>
          <p class="mindset-item-desc">{{ item.summary }}</p>
          <ul class="mindset-details-list">
            <li v-for="(d, dIdx) in item.details" :key="dIdx" class="mindset-detail-li">
              {{ d }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 2. 马恩列经典真理名言避坑表 -->
    <div v-show="activeSection === 'quotes' || activeSection === 'all'" class="quotes-section-box">
      <div class="quotes-header">
        <span class="quotes-badge">手法 9 进阶 · 经典作家名言</span>
        <h3 class="quotes-title">📖 马恩列原话真题避坑表</h3>
        <p class="quotes-sub">
          命题人常引用马恩列斯原话作为选项，由于语言陌生且抽象，考生极易因“读不懂”而盲目当作错项排除。以下均为真题考查过的经典原话，表述完全正确：
        </p>
      </div>

      <div class="quotes-grid">
        <div v-for="(q, qIdx) in classicMarxQuotes" :key="qIdx" class="quote-card">
          <div class="quote-text">“{{ q.quote }}”</div>
          <div class="quote-meta">
            <span class="quote-author">—— {{ q.author }}</span>
            <span class="quote-context">📌 {{ q.context }}</span>
          </div>
          <div class="quote-trap-alert">
            <span class="alert-label">⚠️ 易错点分析：</span>
            <span class="alert-text">{{ q.trapAlert }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. 18 大高频墓碑词敏锐雷达 -->
    <div v-show="activeSection === 'tombstones' || activeSection === 'all'" class="tombstones-section-box">
      <div class="tombstones-header">
        <span class="tombstones-badge">手法 10 核心 · 敏感词雷达</span>
        <h3 class="tombstones-title">⚰️ 18 大高频墓碑词全景速查</h3>
        <p class="tombstones-sub">
          命题人极喜欢在特定词语上面做文章。单列为专项雷达，科学刺激大脑、建立高警惕度，遇到这些词立刻启动怀疑反思：
        </p>
      </div>

      <div class="tombstones-grid">
        <div v-for="(tb, tbIdx) in tombstoneWords" :key="tbIdx" class="tombstone-pill-card">
          <div class="tb-top">
            <span class="tb-word">{{ tb.word }}</span>
            <span class="tb-type">{{ tb.trapType }}</span>
          </div>
          <p class="tb-desc">{{ tb.desc }}</p>
        </div>
      </div>
    </div>

    <!-- 4. 10 类方法卡片网格 -->
    <div v-show="activeSection === 'methods' || activeSection === 'all'" class="methods-section-wrap">
      <div class="methods-section-header">
        <h3 class="section-title">🎯 10 类老头命题挖坑手法全景剖析</h3>
        <p class="section-subtitle">点击【专项刷题】立即进入真题演练，在实战中淬炼识坑直觉！</p>
      </div>

      <div class="methods-grid">
        <div 
          v-for="(method, index) in allMethods" 
          :key="method.id"
          class="method-card"
        >
          <div class="method-card-header">
            <div class="method-idx-badge">手法 {{ index + 1 }}</div>
            <h3 class="method-name">{{ method.name }}</h3>
            <span class="method-count">{{ method.questionIds.length }} 题</span>
          </div>

          <!-- 记忆口诀栏 -->
          <div class="mnemonic-banner">
            <span class="mnemonic-icon">🗣️ 口诀：</span>
            <span class="mnemonic-text">{{ method.mnemonic }}</span>
          </div>

          <!-- 识别关键词 (高亮标签) -->
          <div class="keywords-wrap">
            <div class="keywords-label">核心识别标志词：</div>
            <div class="keywords-list">
              <span 
                v-for="kw in method.keywords" 
                :key="kw"
                class="keyword-pill"
              >
                {{ kw }}
              </span>
            </div>
          </div>

          <!-- 手法考点特征简述 -->
          <p class="method-desc">{{ method.description }}</p>

          <!-- 深入挖坑套路剖析 -->
          <div v-if="method.trapsBreakdown && method.trapsBreakdown.length" class="traps-breakdown-box">
            <div class="traps-label">⚠️ 命题挖坑拆解：</div>
            <ul class="traps-list">
              <li v-for="(t, tIdx) in method.trapsBreakdown" :key="tIdx">{{ t }}</li>
            </ul>
          </div>

          <!-- 特例与考场防坑要诀 -->
          <div v-if="method.specialNotes" class="special-notes-box">
            <span class="notes-icon">📌 防坑技巧：</span>
            <span class="notes-text">{{ method.specialNotes }}</span>
          </div>

          <!-- 正确率与进度条 -->
          <div class="method-stats-bar">
            <div class="stats-label-row">
              <span>掌握进度: {{ getStats(method.id).practiced }} / {{ method.questionIds.length }}</span>
              <span class="accuracy-text">正确率: {{ getStats(method.id).accuracy }}%</span>
            </div>
            <div class="progress-track">
              <div 
                class="progress-fill" 
                :style="{ width: `${getStats(method.id).accuracy}%` }"
              ></div>
            </div>
          </div>

          <!-- 卡片底部动作栏 -->
          <div class="method-card-footer">
            <button 
              class="start-practice-btn"
              @click="$emit('start-practice', method.id)"
            >
              <span>🎯 专项刷题 ({{ method.questionIds.length }}题)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSolveState } from '../services/solveState'

defineEmits(['start-practice'])

const activeSection = ref('methods') // methods | mindset | quotes | tombstones | all

const { 
  allMethods, 
  getMethodStats, 
  overallStats, 
  mindsetPrinciples, 
  classicMarxQuotes, 
  tombstoneWords 
} = useSolveState()

function getStats(methodId) {
  return getMethodStats(methodId)
}
</script>

<style scoped>
.methods-view-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px 16px 40px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.methods-intro-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.intro-badge {
  align-self: flex-start;
  background: #fbf1e4;
  color: #ab5712;
  font-weight: 700;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.intro-title {
  font-size: 22px;
  color: var(--text-main);
  font-weight: 800;
  line-height: 1.3;
}

.intro-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
}

.intro-stats-row {
  display: flex;
  gap: 24px;
  margin-top: 4px;
  padding-top: 14px;
  border-top: 1px dashed var(--border-light);
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-main);
}

.stat-num.accent {
  color: var(--primary-accent);
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

/* 选项卡按钮组 */
.section-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.section-tab-btn {
  background: var(--bg-cream);
  border: 1px solid var(--border-card);
  color: var(--text-main);
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.section-tab-btn:hover {
  background: #ffffff;
  border-color: var(--primary-accent);
}

.section-tab-btn.active {
  background: var(--primary-accent);
  color: #ffffff;
  border-color: var(--primary-accent);
  box-shadow: 0 2px 6px rgba(171, 87, 18, 0.25);
}

/* 1. 四大思维模式 */
.mindset-principles-box {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mindset-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mindset-badge {
  display: inline-block;
  align-self: flex-start;
  background: #fef3c7;
  color: #92400e;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.mindset-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-main);
  margin: 4px 0 0;
}

.mindset-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.mindset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}

.mindset-item {
  background: #faf6f0;
  border: 1px solid #ebd7b5;
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mindset-item-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mindset-icon {
  font-size: 20px;
}

.mindset-item-head {
  display: flex;
  flex-direction: column;
}

.mindset-tag {
  font-size: 11px;
  font-weight: 700;
  color: #ab5712;
}

.mindset-item-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.mindset-item-desc {
  font-size: 13px;
  color: #555555;
  line-height: 1.5;
  margin: 0;
  font-weight: 600;
}

.mindset-details-list {
  margin: 4px 0 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mindset-detail-li {
  font-size: 12px;
  color: #666666;
  line-height: 1.5;
}

/* 2. 马恩名言专区 */
.quotes-section-box {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quotes-badge {
  align-self: flex-start;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.quotes-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-main);
  margin: 4px 0 0;
}

.quotes-sub {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
}

.quotes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}

.quote-card {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-left: 4px solid #0284c7;
  border-radius: 6px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quote-text {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.5;
}

.quote-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
}

.quote-trap-alert {
  background: #fffbeb;
  border: 1px dashed #f59e0b;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
}

.alert-label {
  font-weight: 700;
  color: #b45309;
}

.alert-text {
  color: #78350f;
}

/* 3. 墓碑词雷达 */
.tombstones-section-box {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tombstones-badge {
  align-self: flex-start;
  background: #fee2e2;
  color: #991b1b;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.tombstones-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-main);
  margin: 4px 0 0;
}

.tombstones-sub {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
}

.tombstones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.tombstone-pill-card {
  background: #fdf2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tb-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tb-word {
  font-size: 14px;
  font-weight: 800;
  color: #991b1b;
}

.tb-type {
  font-size: 11px;
  background: #fee2e2;
  color: #b91c1c;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.tb-desc {
  font-size: 12px;
  color: #7f1d1d;
  line-height: 1.4;
  margin: 0;
}

/* 4. 10 类方法卡片 */
.methods-section-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.methods-section-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-main);
  margin: 0;
}

.section-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}

.method-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.method-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.method-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.method-idx-badge {
  background: var(--bg-cream);
  color: var(--primary-accent);
  font-weight: 700;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
}

.method-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.method-count {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 600;
}

.mnemonic-banner {
  background: #fdf5ec;
  border-left: 3px solid var(--primary-accent);
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.mnemonic-icon {
  font-weight: 700;
  font-size: 12px;
  color: var(--primary-accent);
  flex-shrink: 0;
}

.mnemonic-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.4;
}

.keywords-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.keywords-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 600;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.keyword-pill {
  background: #fff8f0;
  color: #ab5712;
  border: 1px solid #ebd7b5;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}

.method-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
}

.traps-breakdown-box {
  background: #fbfbfb;
  border: 1px dashed var(--border-light);
  border-radius: 6px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.traps-label {
  font-size: 12px;
  font-weight: 700;
  color: #b91c1c;
}

.traps-list {
  margin: 0;
  padding-left: 16px;
  font-size: 12px;
  color: #555555;
  line-height: 1.5;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.special-notes-box {
  background: #fefce8;
  border: 1px solid #fef08a;
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.5;
  color: #854d0e;
}

.notes-icon {
  font-weight: 700;
}

.method-stats-bar {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
}

.stats-label-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-muted);
}

.accuracy-text {
  font-weight: 700;
  color: var(--primary-accent);
}

.progress-track {
  width: 100%;
  height: 6px;
  background: var(--bg-cream);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-accent);
  transition: width 0.3s;
}

.start-practice-btn {
  width: 100%;
  background: var(--primary-accent);
  color: #ffffff;
  border: none;
  padding: 10px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: opacity 0.2s;
}

.start-practice-btn:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .methods-view-container {
    padding: 12px 10px 30px;
    gap: 14px;
  }
  .methods-intro-card {
    padding: 14px;
    gap: 10px;
  }
  .intro-title {
    font-size: 17px;
  }
  .intro-desc {
    font-size: 12.5px;
  }
  .intro-stats-row {
    gap: 16px;
    padding-top: 10px;
  }
  .stat-num {
    font-size: 18px;
  }
  .section-tabs {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px;
  }
  .section-tab-btn {
    padding: 7px 6px;
    font-size: 11.5px;
    text-align: center;
    justify-content: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .method-card {
    padding: 14px;
    gap: 10px;
  }
  .methods-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .mindset-grid {
    grid-template-columns: 1fr;
  }
  .quotes-grid {
    grid-template-columns: 1fr;
  }
  .tombstones-grid {
    grid-template-columns: 1fr;
  }
}
</style>
