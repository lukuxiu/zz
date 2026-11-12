<template>
  <div v-if="question" class="question-card-container">
    <!-- 头部信息栏 -->
    <div class="card-top-bar">
      <div class="badge-group">
        <span class="badge-year">{{ question.year }}年 第{{ question.no }}题</span>
        <span :class="['badge-type', question.type]">
          {{ question.type === 'single' ? '单选题' : '多选题 (全选/多选)' }}
        </span>
        <span v-if="question.needsReview" class="badge-review" title="原题文字层部分来自截图，点击下方可查看真题切图">
          🔍 真题图文对照
        </span>
      </div>

      <div class="action-icons">
        <button 
          :class="['icon-action-btn', { active: isFavorite }]" 
          title="收藏本题"
          @click="$emit('toggle-fav', question.id)"
        >
          {{ isFavorite ? '⭐' : '☆' }}
        </button>

        <button 
          :class="['icon-action-btn', { active: inMistakeBook }]" 
          title="加入/移出错题本"
          @click="$emit('toggle-mistake', question.id)"
        >
          {{ inMistakeBook ? '📕' : '📖' }}
        </button>
      </div>
    </div>

    <!-- 题干展示区 -->
    <div class="stem-area">
      <p v-if="question.stem" class="stem-text">{{ question.stem }}</p>
      <div v-else class="stem-fallback-alert">
        <span>📸 本题原书为手写思维导图标注剪贴图，请结合下方真迹原图作答：</span>
        <button class="view-raw-img-btn" @click="showImageModal = true">
          🖼️ 点击放大查看原真题切图
        </button>
      </div>
    </div>

    <!-- 原图内嵌简易预览条 -->
    <div v-if="question.image" class="image-preview-strip">
      <button class="preview-strip-btn" @click="showImageModal = true">
        <span>🖼️ 查看原版思维导图真题真迹 (300 DPI 高清)</span>
        <span class="preview-arrow">👁️ 放大</span>
      </button>
    </div>

    <!-- 💡 破题思维模式锦囊快捷条 (做题前点睛提示) -->
    <div class="mindset-strip" @click="showMindsetBanner = !showMindsetBanner">
      <div class="mindset-strip-left">
        <span class="mindset-strip-icon">⚡</span>
        <span class="mindset-strip-text">
          <strong>{{ question.type === 'single' ? '单选题思维心法' : '多选题思维心法' }}：</strong>
          {{ question.type === 'single' ? '三项解题法 · 圈定题干核心提问，找意思相近或相同词选项' : '核心用排除法 · 明显错才排 · 其余疑罪从无全选 · 马哲题不全选' }}
        </span>
      </div>
      <button class="mindset-strip-btn">
        {{ showMindsetBanner ? '收起 ▴' : '速查四准则 ▾' }}
      </button>
    </div>

    <!-- 展开的思维四准则微型面板 -->
    <div v-if="showMindsetBanner" class="mindset-accordion-panel">
      <div class="acc-head">
        <span class="acc-badge">⚡ 政治选择题四大解题思维模式</span>
        <span class="acc-hint">有了正确的解题思维，才能显著提高选择题正确率：</span>
      </div>
      <div class="acc-grid">
        <div v-for="item in mindsetPrinciples" :key="item.id" class="acc-item">
          <div class="acc-item-title">{{ item.num }} {{ item.title }}</div>
          <div class="acc-item-desc">{{ item.summary }}</div>
        </div>
      </div>
    </div>

    <!-- 选项交互列表 -->
    <div class="options-list">
      <div 
        v-for="optKey in ['A', 'B', 'C', 'D']" 
        :key="optKey"
        :class="[
          'option-item', 
          { 
            selected: selectedOptions.includes(optKey),
            'correct-revealed': isSubmitted && question.answer.includes(optKey),
            'wrong-selected': isSubmitted && selectedOptions.includes(optKey) && !question.answer.includes(optKey),
            disabled: isSubmitted
          }
        ]"
        @click="handleSelectOption(optKey)"
      >
        <div class="option-key-bubble">
          <span v-if="isSubmitted && question.answer.includes(optKey)">✓</span>
          <span v-else-if="isSubmitted && selectedOptions.includes(optKey) && !question.answer.includes(optKey)">✕</span>
          <span v-else>{{ optKey }}</span>
        </div>
        <div class="option-content">
          {{ question.options[optKey] || `(选项 ${optKey} 内容见原真题切图)` }}
        </div>
      </div>
    </div>

    <!-- 提交 / 盲测手法交互区 -->
    <div v-if="!isSubmitted" class="submit-action-bar">
      <div class="selection-indicator">
        已选：<strong>{{ selectedOptions.length > 0 ? selectedOptions.join(' ') : '未选择' }}</strong>
      </div>
      <button 
        class="submit-btn" 
        :disabled="selectedOptions.length === 0"
        @click="handleSubmitAnswer"
      >
        确认提交作答
      </button>
    </div>

    <!-- 盲测模式：选择命题手法阶段 -->
    <div v-else-if="blindMode && !blindRevealed" class="blind-guess-box">
      <div class="blind-title">🎯 进阶盲测 · 命题人在此题使用了哪种手法/挖坑点？</div>
      <p class="blind-sub">训练考场识坑嗅觉，判断正确答案背后的命题逻辑：</p>
      
      <div class="method-chips-grid">
        <button 
          v-for="m in allMethods" 
          :key="m.id"
          :class="['method-guess-chip', { active: chosenMethod === m.id }]"
          @click="chosenMethod = m.id"
        >
          {{ m.name }}
        </button>
      </div>

      <button 
        class="reveal-blind-btn" 
        :disabled="!chosenMethod"
        @click="handleBlindConfirm"
      >
        揭晓手法与完整解析 👁️
      </button>
    </div>

    <!-- 作答揭晓与深度解析面板 -->
    <div v-else class="analysis-panel">
      <!-- 对错反馈横幅 -->
      <div :class="['result-banner', isAnswerCorrect ? 'banner-correct' : 'banner-wrong']">
        <div class="banner-icon">{{ isAnswerCorrect ? '🎉' : '❌' }}</div>
        <div class="banner-info">
          <div class="banner-headline">
            {{ isAnswerCorrect ? '回答正确！' : '回答有误！' }}
            <span class="ref-answer">正确答案：<strong>{{ question.answer.join('') }}</strong></span>
          </div>
          <div class="banner-sub">
            您的作答：{{ selectedOptions.join('') || '未作答' }}
            <span v-if="blindMode">
              · 手法判断：{{ isMethodHit ? '✅ 识破挖坑！' : '⚠️ 未命中' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 盲测误判时的手法归因卡片 -->
      <div v-if="blindMode && !isMethodHit" class="blind-misjudge-banner">
        <span class="misjudge-icon">⚠️</span>
        <div class="misjudge-body">
          <div class="misjudge-title">盲测手法识别误判归因</div>
          <div class="misjudge-text">
            您判定的手法为「{{ getMethodName(chosenMethod) }}」，实际题设核心挖坑手法为「{{ question.methods.map(getMethodName).join('、') }}」。请结合下方<strong>破题识别关键词</strong>与<strong>干扰项排雷分析</strong>建立条件反射！
          </div>
        </div>
      </div>

      <!-- 命中的解题手法标签 -->
      <div class="hit-methods-row">
        <span class="hit-label">命中命题手法：</span>
        <div class="hit-tags">
          <span 
            v-for="mid in question.methods" 
            :key="mid"
            class="hit-method-tag"
            @click="$emit('view-method', mid)"
          >
            🏷️ {{ getMethodName(mid) }}
          </span>
        </div>
      </div>

      <!-- 1. 考场识坑点睛与排雷分析 -->
      <div v-if="question.trapReason || (question.trapOptions && question.trapOptions.length)" class="trap-insight-box">
        <div class="trap-insight-header">
          <span class="trap-icon">⚡</span>
          <span class="trap-title">考场识坑点睛与排雷分析</span>
        </div>
        <div class="trap-insight-content">
          <div v-if="question.trapOptions && question.trapOptions.length" class="trap-row">
            <span class="trap-label">⚠️ 命题干扰项：</span>
            <span class="trap-badges">
              <span v-for="tOpt in question.trapOptions" :key="tOpt" class="trap-badge-pill">选项 {{ tOpt }}</span>
            </span>
          </div>
          <div v-if="question.identKeywords && question.identKeywords.length" class="trap-row">
            <span class="trap-label">🎯 破题识别关键词：</span>
            <span class="kw-badges">
              <span v-for="kw in question.identKeywords" :key="kw" class="ident-kw-pill">{{ kw }}</span>
            </span>
          </div>
          <div v-if="question.trapReason" class="trap-reason-text">
            <strong>破题要诀：</strong>{{ question.trapReason }}
          </div>
        </div>
      </div>

      <!-- 2. 一页纸名师破题批注 -->
      <div class="tip-box">
        <div class="tip-header">
          <span class="tip-icon">💡</span>
          <span class="tip-title">澄潇宇「一页纸」原版破题批注：</span>
        </div>
        <div class="tip-body">
          <p v-for="(line, idx) in splitTip(question.tip)" :key="idx" class="tip-line">
            {{ line }}
          </p>
        </div>
      </div>

      <!-- 3. 老头命题手法深入剖析 (挖坑套路 + 防坑技巧) -->
      <div v-if="primaryMethodObj" class="method-deep-box">
        <div class="method-deep-header">
          <span class="deep-icon">🎯</span>
          <span class="deep-title">老头命题挖坑套路剖析 · {{ primaryMethodObj.name }}</span>
        </div>
        <div class="method-deep-body">
          <div class="deep-mnemonic">🗣️ <strong>口诀：</strong>{{ primaryMethodObj.mnemonic }}</div>
          <div v-if="primaryMethodObj.trapsBreakdown && primaryMethodObj.trapsBreakdown.length" class="deep-traps">
            <div class="deep-traps-label">⚠️ 常见挖坑设伏机制：</div>
            <ul class="deep-traps-list">
              <li v-for="(t, idx) in primaryMethodObj.trapsBreakdown" :key="idx">{{ t }}</li>
            </ul>
          </div>
          <div v-if="primaryMethodObj.specialNotes" class="deep-notes">
            📌 <strong>防坑要诀：</strong>{{ primaryMethodObj.specialNotes }}
          </div>
        </div>
      </div>

      <!-- 4. 解题思维模式落地指导 -->
      <div class="mindset-guidance-box">
        <div class="guidance-header">
          <span class="guidance-icon">⚡</span>
          <span class="guidance-title">解题思维模式落地复盘</span>
        </div>
        <div class="guidance-body">
          <div class="guidance-text">
            <strong>{{ question.type === 'single' ? '单选题思维心法：' : '多选题思维心法：' }}</strong>
            {{ question.type === 'single' 
              ? '【三项解题法 & 排除法】对于时政与生疏单选题，先抓题干核心关键词与设问角度，优先排除具有绝对极端词或与材料不合的选项，寻找与材料意思最契合的选项。' 
              : '【多选疑罪从无】核心采用排除法，明显错才算错（抓到违背常识规律、绝对极端、时态颠倒、答非所问证据），拿不准的坚持疑罪从无全选上！若为马原题（尤其是马哲），切忌盲目全选。' }}
          </div>
          <div class="guidance-tools">
            <button class="tool-btn" @click="showMarxModal = true">📖 查看马恩列名言避坑表</button>
            <button class="tool-btn" @click="showTombstoneModal = true">⚰️ 查看18大墓碑词雷达</button>
          </div>
        </div>
      </div>

      <!-- 四档 SRS 自我评价面板 -->
      <div class="srs-eval-wrapper">
        <div class="srs-eval-title">本次掌握自评（纳入遗忘曲线间隔复习）：</div>
        <div class="srs-eval-btns">
          <button class="eval-btn btn-again" @click="handleEvaluate('again')">
            <span class="eval-main">完全不会</span>
            <span class="eval-sub">当天复现</span>
          </button>
          <button class="eval-btn btn-hard" @click="handleEvaluate('hard')">
            <span class="eval-main">模糊</span>
            <span class="eval-sub">1天后</span>
          </button>
          <button class="eval-btn btn-good" @click="handleEvaluate('good')">
            <span class="eval-main">基本掌握</span>
            <span class="eval-sub">3天后</span>
          </button>
          <button class="eval-btn btn-easy" @click="handleEvaluate('easy')">
            <span class="eval-main">熟练秒杀</span>
            <span class="eval-sub">7天后</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 原版切图弹窗 -->
    <div v-if="showImageModal" class="image-modal-overlay" @click.self="showImageModal = false">
      <div class="image-modal-dialog">
        <div class="image-modal-header">
          <div class="image-modal-title">
            🖼️ [{{ question.id }}] 澄潇宇《一页纸》原版思维导图真迹
          </div>
          <button class="close-img-btn" @click="showImageModal = false">✕</button>
        </div>
        <div class="image-modal-body">
          <img :src="question.image" :alt="question.id" class="modal-raw-img" />
        </div>
      </div>
    </div>

    <!-- 马恩列真题名言弹窗 -->
    <div v-if="showMarxModal" class="image-modal-overlay" @click.self="showMarxModal = false">
      <div class="image-modal-dialog mini-dialog">
        <div class="image-modal-header">
          <div class="image-modal-title">📖 马恩列经典真理名言真题避坑表</div>
          <button class="close-img-btn" @click="showMarxModal = false">✕</button>
        </div>
        <div class="modal-content-scroll">
          <div v-for="(q, idx) in classicMarxQuotes" :key="idx" class="modal-quote-item">
            <div class="m-q-text">“{{ q.quote }}”</div>
            <div class="m-q-meta">—— {{ q.author }} · {{ q.context }}</div>
            <div class="m-q-alert">⚠️ {{ q.trapAlert }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 18 大墓碑词弹窗 -->
    <div v-if="showTombstoneModal" class="image-modal-overlay" @click.self="showTombstoneModal = false">
      <div class="image-modal-dialog mini-dialog">
        <div class="image-modal-header">
          <div class="image-modal-title">⚰️ 18 大高频墓碑词敏锐雷达</div>
          <button class="close-img-btn" @click="showTombstoneModal = false">✕</button>
        </div>
        <div class="modal-content-scroll">
          <div class="modal-tb-grid">
            <div v-for="(tb, idx) in tombstoneWords" :key="idx" class="modal-tb-card">
              <div class="m-tb-top">
                <span class="m-tb-w">{{ tb.word }}</span>
                <span class="m-tb-t">{{ tb.trapType }}</span>
              </div>
              <div class="m-tb-d">{{ tb.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useSolveState } from '../services/solveState'

const props = defineProps({
  question: { type: Object, required: true },
  record: { type: Object, default: () => ({}) },
  allMethods: { type: Array, default: () => [] },
  blindMode: { type: Boolean, default: false }
})

const emit = defineEmits([
  'answer-submitted', 
  'evaluate', 
  'toggle-fav', 
  'toggle-mistake',
  'view-method'
])

const { mindsetPrinciples, classicMarxQuotes, tombstoneWords } = useSolveState()

const selectedOptions = ref([])
const isSubmitted = ref(false)
const chosenMethod = ref(null)
const blindRevealed = ref(false)
const showImageModal = ref(false)
const showMindsetBanner = ref(false)
const showMarxModal = ref(false)
const showTombstoneModal = ref(false)

// 监听题目切换，重置作答状态
watch(() => props.question.id, () => {
  selectedOptions.value = []
  isSubmitted.value = false
  chosenMethod.value = null
  blindRevealed.value = false
}, { immediate: true })

const isFavorite = computed(() => !!props.record?.isFavorite)
const inMistakeBook = computed(() => !!props.record?.inMistakeBook)

const primaryMethodObj = computed(() => {
  if (!props.question?.methods?.length) return null
  const firstId = props.question.methods[0]
  return props.allMethods?.find(m => m.id === firstId) || null
})

function handleSelectOption(optKey) {
  if (isSubmitted.value) return

  if (props.question.type === 'single') {
    selectedOptions.value = [optKey]
  } else {
    const idx = selectedOptions.value.indexOf(optKey)
    if (idx >= 0) {
      selectedOptions.value.splice(idx, 1)
    } else {
      selectedOptions.value.push(optKey)
      selectedOptions.value.sort()
    }
  }
}

const isAnswerCorrect = computed(() => {
  const correct = [...props.question.answer].sort().join('')
  const user = [...selectedOptions.value].sort().join('')
  return correct === user
})

const isMethodHit = computed(() => {
  return chosenMethod.value && props.question.methods.includes(chosenMethod.value)
})

function handleSubmitAnswer() {
  if (selectedOptions.value.length === 0) return
  isSubmitted.value = true

  if (!props.blindMode) {
    emit('answer-submitted', {
      qid: props.question.id,
      userSelected: selectedOptions.value,
      chosenMethod: null
    })
  }
}

function handleBlindConfirm() {
  blindRevealed.value = true
  emit('answer-submitted', {
    qid: props.question.id,
    userSelected: selectedOptions.value,
    chosenMethod: chosenMethod.value
  })
}

function handleEvaluate(grade) {
  emit('evaluate', {
    qid: props.question.id,
    grade,
    userSelected: selectedOptions.value,
    chosenMethod: chosenMethod.value
  })
}

function getMethodName(mid) {
  const m = props.allMethods.find(x => x.id === mid)
  return m ? m.name : mid
}

function splitTip(tip) {
  if (!tip) return ['(暂无批注)']
  return tip.split('\n').map(s => s.trim()).filter(Boolean)
}
</script>

<style scoped>
.question-card-container {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed var(--border-light);
  padding-bottom: 12px;
}

.badge-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.badge-year {
  background: var(--bg-beige);
  color: var(--text-main);
  font-weight: 700;
  font-size: 13px;
  padding: 3px 8px;
  border-radius: 4px;
}

.badge-type {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.badge-type.single {
  background: #e9f3ff;
  color: #1a62c4;
}

.badge-type.multi {
  background: #fdf0ec;
  color: #c04928;
}

.badge-review {
  background: var(--warning-accent-bg);
  color: var(--warning-accent);
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #ebd7b5;
}

.action-icons {
  display: flex;
  gap: 8px;
}

.icon-action-btn {
  background: var(--bg-warm);
  border: 1px solid var(--border-light);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.icon-action-btn.active {
  background: var(--warning-accent-bg);
  border-color: var(--warning-accent);
}

.stem-area {
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-main);
  font-weight: 500;
}

.stem-fallback-alert {
  background: #fbf7ee;
  border: 1px solid #fae2b2;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: #8c5d15;
}

.view-raw-img-btn {
  align-self: flex-start;
  background: #fff;
  border: 1px solid #e8bc72;
  color: #8c5d15;
  padding: 6px 14px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
}

.image-preview-strip {
  margin-top: -6px;
}

.preview-strip-btn {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-warm);
  border: 1px dashed var(--border-card);
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

.preview-arrow {
  color: var(--primary-accent);
  font-weight: 600;
}

/* 💡 思维模式速查条 */
.mindset-strip {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 6px;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background 0.15s;
}

.mindset-strip:hover {
  background: #fef3c7;
}

.mindset-strip-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #92400e;
}

.mindset-strip-icon {
  font-size: 15px;
}

.mindset-strip-btn {
  background: none;
  border: none;
  font-size: 12px;
  font-weight: 700;
  color: #b45309;
  cursor: pointer;
  flex-shrink: 0;
}

.mindset-accordion-panel {
  background: #faf6f0;
  border: 1px solid #ebd7b5;
  border-radius: 8px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.acc-head {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.acc-badge {
  font-size: 12px;
  font-weight: 800;
  color: #ab5712;
}

.acc-hint {
  font-size: 11px;
  color: #8c5d15;
}

.acc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.acc-item {
  background: #fff;
  border: 1px solid #f0e2cc;
  border-radius: 6px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.acc-item-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-main);
}

.acc-item-desc {
  font-size: 11px;
  color: #666;
  line-height: 1.4;
}

/* 选项列表 */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1.5px solid var(--border-light);
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.15s ease;
}

.option-item:hover:not(.disabled) {
  border-color: var(--primary-accent);
  background: var(--primary-accent-bg);
}

.option-item.selected {
  border-color: var(--primary-accent);
  background: var(--primary-accent-bg);
}

.option-item.correct-revealed {
  border-color: var(--success-accent) !important;
  background: var(--success-accent-bg) !important;
}

.option-item.wrong-selected {
  border-color: var(--danger-accent) !important;
  background: var(--danger-accent-bg) !important;
}

.option-key-bubble {
  min-width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-warm);
  border: 1px solid var(--border-card);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  color: var(--text-regular);
  flex-shrink: 0;
}

.option-item.selected .option-key-bubble {
  background: var(--primary-accent);
  color: #fff;
  border-color: var(--primary-accent);
}

.option-item.correct-revealed .option-key-bubble {
  background: var(--success-accent);
  color: #fff;
  border-color: var(--success-accent);
}

.option-item.wrong-selected .option-key-bubble {
  background: var(--danger-accent);
  color: #fff;
  border-color: var(--danger-accent);
}

.option-content {
  font-size: 15px;
  line-height: 1.5;
  color: var(--text-main);
  padding-top: 2px;
}

/* 提交条 */
.submit-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
}

.selection-indicator {
  font-size: 14px;
  color: var(--text-muted);
}

.submit-btn {
  background: var(--primary-accent);
  color: #ffffff;
  font-weight: 700;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 15px;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 盲测选手法面板 */
.blind-guess-box {
  background: #f7f9fd;
  border: 1.5px dashed var(--primary-accent);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.blind-title {
  font-weight: 700;
  font-size: 15px;
  color: var(--primary-accent);
}

.blind-sub {
  font-size: 13px;
  color: var(--text-muted);
}

.method-chips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 8px;
}

.method-guess-chip {
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  border: 1px solid var(--border-card);
  color: var(--text-regular);
  font-weight: 500;
  text-align: center;
}

.method-guess-chip.active {
  background: var(--primary-accent);
  color: #fff;
  border-color: var(--primary-accent);
  font-weight: 700;
}

.reveal-blind-btn {
  align-self: center;
  background: var(--primary-accent);
  color: #fff;
  padding: 10px 30px;
  border-radius: 20px;
  font-weight: 700;
  margin-top: 6px;
}

/* 解析与自评面板 */
.analysis-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-top: 8px;
  border-top: 1px solid var(--border-light);
}

.result-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
}

.blind-misjudge-banner {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-left: 4px solid #f97316;
  border-radius: 6px;
  padding: 10px 14px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-top: 4px;
}
.blind-misjudge-banner .misjudge-icon {
  font-size: 1.25em;
  line-height: 1.2;
}
.blind-misjudge-banner .misjudge-title {
  font-weight: 700;
  font-size: 13px;
  color: #c2410c;
  margin-bottom: 3px;
}
.blind-misjudge-banner .misjudge-text {
  font-size: 12.5px;
  color: #9a3412;
  line-height: 1.5;
}

.banner-correct {
  background: var(--success-accent-bg);
  border: 1px solid #bee0ca;
  color: #1e5c36;
}

.banner-wrong {
  background: var(--danger-accent-bg);
  border: 1px solid #f6caca;
  color: #922424;
}

.banner-icon {
  font-size: 24px;
}

.banner-headline {
  font-size: 16px;
  font-weight: 700;
}

.ref-answer {
  margin-left: 12px;
  color: var(--text-main);
  font-weight: normal;
}

.ref-answer strong {
  font-size: 18px;
  color: var(--primary-accent);
}

.banner-sub {
  font-size: 13px;
  margin-top: 2px;
  opacity: 0.85;
}

.hit-methods-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hit-label {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 600;
}

.hit-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.hit-method-tag {
  background: #fbf5ea;
  color: #9b5a14;
  border: 1px solid #ebd4b0;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

/* 考场识坑点睛框 */
.trap-insight-box {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-left: 4px solid #3b82f6;
  border-radius: 6px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.trap-insight-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  font-size: 13px;
  color: #1e40af;
}

.trap-insight-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
}

.trap-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.trap-label {
  font-weight: 600;
  color: #475569;
}

.trap-badge-pill {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fecaca;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 11px;
}

.ident-kw-pill {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 11px;
}

.trap-reason-text {
  color: #0f172a;
  line-height: 1.5;
  background: #ffffff;
  padding: 6px 10px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.tip-box {
  background: #fdfaf4;
  border: 1px solid #eedec7;
  border-left: 4px solid var(--warning-accent);
  border-radius: 6px;
  padding: 14px;
}

.tip-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-weight: 700;
  font-size: 14px;
  color: #8c5210;
}

.tip-body {
  font-size: 14px;
  line-height: 1.7;
  color: #3b3327;
}

.tip-line {
  margin-bottom: 4px;
}

/* 🎯 老头命题手法深入剖析 */
.method-deep-box {
  background: #fff8f8;
  border: 1px solid #fed7d7;
  border-left: 4px solid #e53e3e;
  border-radius: 6px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.method-deep-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 800;
  font-size: 14px;
  color: #9b2c2c;
}

.method-deep-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: #4a5568;
}

.deep-mnemonic {
  background: #fff;
  border: 1px dashed #feb2b2;
  padding: 6px 10px;
  border-radius: 4px;
  color: #c53030;
  font-weight: 600;
}

.deep-traps {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.deep-traps-label {
  font-weight: 700;
  color: #9b2c2c;
}

.deep-traps-list {
  margin: 0;
  padding-left: 18px;
  line-height: 1.5;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.deep-notes {
  background: #fefcbf;
  border: 1px solid #faf089;
  padding: 6px 10px;
  border-radius: 4px;
  color: #744210;
  line-height: 1.5;
}

/* ⚡ 解题思维落地指导 */
.mindset-guidance-box {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-left: 4px solid #16a34a;
  border-radius: 6px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.guidance-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 800;
  font-size: 14px;
  color: #15803d;
}

.guidance-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  color: #166534;
  line-height: 1.5;
}

.guidance-tools {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.tool-btn {
  background: #ffffff;
  border: 1px solid #86efac;
  color: #15803d;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.tool-btn:hover {
  background: #dcfce7;
}

.srs-eval-wrapper {
  background: var(--bg-warm);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 14px;
}

.srs-eval-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.srs-eval-btns {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.eval-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 4px;
  border-radius: 6px;
  border: 1px solid var(--border-card);
  background: #fff;
}

.eval-main {
  font-weight: 700;
  font-size: 14px;
}

.eval-sub {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.btn-again { color: #a32222; border-color: #f1baba; }
.btn-again:hover { background: #fdf1f1; }
.btn-hard { color: #b46b1d; border-color: #ebd7b5; }
.btn-hard:hover { background: #fdf5ea; }
.btn-good { color: #2e6297; border-color: #bad2ed; }
.btn-good:hover { background: #eef4fb; }
.btn-easy { color: #2e7d4a; border-color: #bce3cb; }
.btn-easy:hover { background: #edf7f0; }

/* 模态弹窗 */
.image-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.image-modal-dialog {
  background: #fff;
  border-radius: 12px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.image-modal-dialog.mini-dialog {
  max-width: 600px;
}

.image-modal-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-light);
  font-weight: 700;
}

.close-img-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.image-modal-body {
  padding: 16px;
  overflow-y: auto;
  text-align: center;
  background: #333;
}

.modal-raw-img {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}

.modal-content-scroll {
  padding: 16px;
  overflow-y: auto;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-quote-item {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-left: 4px solid #0284c7;
  padding: 10px 12px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.m-q-text {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.m-q-meta {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
}

.m-q-alert {
  background: #fffbeb;
  border: 1px dashed #f59e0b;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #92400e;
}

.modal-tb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 8px;
}

.modal-tb-card {
  background: #fdf2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.m-tb-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.m-tb-w {
  font-weight: 800;
  color: #991b1b;
  font-size: 13px;
}

.m-tb-t {
  font-size: 11px;
  background: #fee2e2;
  color: #b91c1c;
  padding: 1px 4px;
  border-radius: 3px;
}

.m-tb-d {
  font-size: 11px;
  color: #7f1d1d;
  line-height: 1.4;
}

@media (max-width: 600px) {
  .question-card-container {
    padding: 14px;
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
  .srs-eval-btns {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
