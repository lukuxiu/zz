<template>
  <div v-if="card" :class="['card-container', `font-${fontSize}`]">
    <!-- 顶部米色标题栏 -->
    <div class="card-header">
      <div class="header-left">
        <span class="source-id-tag">知识点 {{ card.sourceId }}</span>
        <span class="hierarchy-tag">{{ card.subject }} · {{ card.section }}</span>
      </div>
      <div class="header-right">
        <button 
          :class="['fav-btn', { active: isFavorite }]" 
          :title="isFavorite ? '取消收藏' : '收藏知识点'"
          @click="$emit('toggle-fav', card.id)"
        >
          {{ isFavorite ? '★ 已收藏' : '☆ 收藏' }}
        </button>
      </div>
    </div>

    <!-- 知识点标题 -->
    <div class="card-title-bar">
      <h2 class="kp-title">{{ card.title }}</h2>
      <span class="page-hint">📖 原书 P{{ card.bookPage[0] }} · PDF P{{ card.sourcePage[0] }}</span>
    </div>

    <!-- 整卡遮挡覆盖层 -->
    <div v-if="mode === 'full' && !fullCardRevealed" class="full-cover" @click="fullCardRevealed = true">
      <div class="full-cover-content">
        <span class="cover-icon">🙈</span>
        <span class="cover-text">整卡已遮挡 · 点击揭晓正文</span>
      </div>
    </div>

    <!-- 卡片正文内容区 -->
    <div v-else class="card-body">
      <!-- 遮挡模式操作提示 -->
      <div v-if="mode !== 'none'" class="cloze-toolbar">
        <span class="mode-badge">
          {{ modeNameMap[mode] }}
        </span>
        <div class="toolbar-actions">
          <button class="tool-btn" @click="revealAll">全部显示</button>
          <button class="tool-btn" @click="hideAll">全部遮挡</button>
        </div>
      </div>

      <!-- 置顶考点脉络原图 -->
      <div v-if="card.inlineImage" class="card-inline-image-box">
        <img 
          :src="card.inlineImage" 
          alt="考点原始脉络图" 
          :class="['card-inline-img', { zoomed: isImgZoomed }]"
          @click="handleImgClick"
          title="点击查看放大原图"
        />
        <div class="inline-img-tip">📊 原始知识脉络高清大图（点击可切换缩放 / 弹出原图）</div>
      </div>

      <!-- 渲染正文文本 -->
      <div class="content-text">
        <template v-for="(seg, idx) in parsedSegments" :key="idx">
          <!-- 换行 -->
          <br v-if="seg.type === 'newline'" />
          
          <!-- 关键词挖空/高亮片段 -->
          <span 
            v-else-if="seg.type === 'keyword'"
            :class="[
              seg.isMuted ? 'muted-text' : '',
              seg.shouldCloze ? (seg.revealed ? 'cloze-revealed' : 'cloze-hidden') : 'keyword-highlight'
            ]"
            :style="(!seg.shouldCloze || seg.revealed) && !seg.isMuted ? { color: seg.color, '--kw-color': seg.color } : {}"
            @click="toggleSeg(seg)"
            :title="seg.shouldCloze ? '点击切换显隐' : '原书核心考点'"
          >
            {{ seg.text }}
          </span>

          <!-- 趣味助记小图贴纸 (还原PDF风味，保留线索，不挖空) -->
          <span 
            v-else-if="seg.type === 'symbol'"
            class="symbol-sticker"
            :title="seg.desc || seg.name"
            @click.stop
          >
            <img 
              v-if="seg.hash" 
              :src="'/symbols/' + seg.hash + '.png'" 
              :alt="seg.desc || seg.name" 
              class="symbol-sticker-img" 
            />
            <span v-else class="symbol-fallback">[{{ seg.name }}]</span>
          </span>

          <!-- 普通文字片段 -->
          <span 
            v-else
            :class="[
              seg.isMuted ? 'muted-text' : '',
              seg.shouldCloze ? (seg.revealed ? 'cloze-revealed' : 'cloze-hidden') : ''
            ]"
            @click="toggleSeg(seg)"
          >
            {{ seg.text }}
          </span>
        </template>
      </div>

      <!-- 原书辨析 (Distinctions) -->
      <div v-if="cleanDistinctions.length > 0" class="distinction-section">
        <div class="section-badge">⚖️ 原书辨析与真伪判断</div>
        <div 
          v-for="(d, dIdx) in cleanDistinctions" 
          :key="dIdx"
          :class="['dist-item', `verdict-${d.verdict || 'warn'}`]"
        >
          <div class="dist-header-tag">
            <span class="verdict-icon">{{ d.verdict === 'correct' ? '✅' : (d.verdict === 'wrong' ? '❌' : '⚠️') }}</span>
            <span class="verdict-label">{{ d.verdict === 'correct' ? '正确表述' : (d.verdict === 'wrong' ? '易错/混淆' : '辨析提醒') }}</span>
          </div>
          <div class="dist-stmt">{{ d.statement }}</div>
        </div>
      </div>

      <!-- 原书口诀助记 (Mnemonics) -->
      <div v-if="cleanMnemonics.length > 0" class="mnemonic-section">
        <div class="section-badge">💡 原书速记口诀</div>
        <div v-for="(m, mIdx) in cleanMnemonics" :key="mIdx" class="mne-item">
          <span class="mne-icon">🎯</span>
          <div class="mne-text">
            <template v-for="(part, pIdx) in parseMnemonicParts(m.text)" :key="pIdx">
              <span 
                v-if="part.type === 'symbol'" 
                class="symbol-sticker" 
                :title="part.desc || part.text"
                @click.stop
              >
                <img 
                  v-if="part.hash" 
                  :src="'/symbols/' + part.hash + '.png'" 
                  :alt="part.desc || part.text" 
                  class="symbol-sticker-img" 
                />
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
                :title="`【真题】${q.label} · ${q.kind} (点击做题)`"
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
                :title="`【模拟题】${q.label} · ${q.kind} (点击做题)`"
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

    <!-- 卡片底部信息与原图入口 -->
    <div class="card-footer">
      <div class="footer-left">
        <span class="card-uid">考点 ID: {{ card.id }}</span>
      </div>
      <div class="footer-right">
        <button class="source-img-btn" @click="$emit('view-image', card)">
          <span>🖼️</span> 查看 PDF 原文高清裁切图
        </button>
      </div>
    </div>

    <!-- 题目练习弹窗 -->
    <QuestionPracticeModal
      v-if="activeQuestion"
      :question="activeQuestion"
      :card="card"
      :current-index="activeQuestionIndex"
      :total-count="card.relatedQuestions?.length || 0"
      @close="activeQuestion = null"
      @prev="prevQuestion"
      @next="nextQuestion"
      @record-answer="handleAnswerRecorded"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import QuestionPracticeModal from './QuestionPracticeModal.vue'

const props = defineProps({
  card: { type: Object, required: true },
  mode: { type: String, default: 'none' }, // none, keyword, sentence, random, full
  fontSize: { type: String, default: 'medium' },
  isFavorite: { type: Boolean, default: false }
})

const emit = defineEmits(['toggle-fav', 'view-image'])

const fullCardRevealed = ref(false)
const revealedMap = ref(new Map())
const isImgZoomed = ref(false)

const activeQuestion = ref(null)
const questionRecords = ref({})

function loadQuestionRecords() {
  try {
    questionRecords.value = JSON.parse(localStorage.getItem('zhengz_question_records') || '{}')
  } catch (e) {
    questionRecords.value = {}
  }
}
loadQuestionRecords()

const groupedQuestions = computed(() => {
  const groups = { '真题': [], '模拟题': [] }
  if (!props.card?.relatedQuestions) return groups
  props.card.relatedQuestions.forEach(q => {
    if (q.sourceType === '真题') {
      groups['真题'].push(q)
    } else {
      groups['模拟题'].push(q)
    }
  })
  return groups
})

const activeQuestionIndex = computed(() => {
  if (!activeQuestion.value || !props.card?.relatedQuestions) return 0
  return props.card.relatedQuestions.findIndex(q => q.id === activeQuestion.value.id)
})

function openQuestion(q) {
  activeQuestion.value = q
}

function prevQuestion() {
  const qs = props.card?.relatedQuestions || []
  const idx = activeQuestionIndex.value
  if (idx > 0) {
    activeQuestion.value = qs[idx - 1]
  }
}

function nextQuestion() {
  const qs = props.card?.relatedQuestions || []
  const idx = activeQuestionIndex.value
  if (idx < qs.length - 1) {
    activeQuestion.value = qs[idx + 1]
  }
}

function getQuestionStatus(qid) {
  return questionRecords.value[qid]?.status || null
}

function getQuestionStatusClass(qid) {
  const s = getQuestionStatus(qid)
  if (s === 'right') return 'answered-right'
  if (s === 'wrong') return 'answered-wrong'
  return ''
}

function handleAnswerRecorded() {
  loadQuestionRecords()
}

function handleImgClick() {
  isImgZoomed.value = !isImgZoomed.value
  emit('view-image', props.card)
}

const modeNameMap = {
  keyword: '关键词遮挡 (点击单个揭晓)',
  sentence: '分句遮挡',
  random: '随机挖空',
  full: '整卡遮挡'
}

watch(() => [props.card?.id, props.mode], () => {
  fullCardRevealed.value = false
  revealedMap.value = new Map()
  isImgZoomed.value = false
}, { immediate: true })

function toggleSeg(seg) {
  if (!seg.shouldCloze) return
  const cur = revealedMap.value.get(seg.id)
  revealedMap.value.set(seg.id, !cur)
}

function revealAll() {
  if (props.mode === 'full') {
    fullCardRevealed.value = true
    return
  }
  parsedSegments.value.forEach(s => {
    if (s.shouldCloze) {
      revealedMap.value.set(s.id, true)
    }
  })
}

function hideAll() {
  if (props.mode === 'full') {
    fullCardRevealed.value = false
    return
  }
  parsedSegments.value.forEach(s => {
    if (s.shouldCloze) {
      revealedMap.value.set(s.id, false)
    }
  })
}

// 防御性清洗辨析列表，去除可能残存的大括号
const cleanDistinctions = computed(() => {
  if (!props.card || !props.card.distinctions) return []
  return props.card.distinctions.map(d => ({
    ...d,
    statement: d.statement ? d.statement.replace(/\{\{([^}]+)\}\}/g, '$1').trim() : ''
  })).filter(d => d.statement.length > 0)
})

// 防御性清洗口诀列表，去除可能残存的大括号
const cleanMnemonics = computed(() => {
  if (!props.card || !props.card.mnemonics) return []
  return props.card.mnemonics.map(m => ({
    ...m,
    text: m.text ? m.text.replace(/\{\{([^}]+)\}\}/g, '$1').trim() : ''
  })).filter(m => m.text.length > 0)
})

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
}

function getSymbolInfo(name) {
  if (SYMBOL_MAP[name]) return SYMBOL_MAP[name]
  if (props.card?.symbols) {
    const found = props.card.symbols.find(s => s.char === `{${name}}` || s.char === name)
    if (found) return found
  }
  return null
}

// 解析口诀中的特殊图示符号占位符 (例如 {俄国国旗}{直升机})
function parseMnemonicParts(text) {
  if (!text) return []
  const parts = []
  const regex = /\{([^}]+)\}/g
  let lastIdx = 0
  let match
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIdx) {
      parts.push({ type: 'text', text: text.substring(lastIdx, match.index) })
    }
    const symName = match[1]
    const symInfo = getSymbolInfo(symName)
    parts.push({ 
      type: 'symbol', 
      text: symName,
      hash: symInfo?.hash || null,
      desc: symInfo?.desc || symName
    })
    lastIdx = regex.lastIndex
  }
  if (lastIdx < text.length) {
    parts.push({ type: 'text', text: text.substring(lastIdx) })
  }
  return parts
}

const parsedSegments = computed(() => {
  if (!props.card || !props.card.content) return []

  const content = props.card.content
  const segments = []
  
  const regex = /\{\{([^}]+)\}\}/g
  let lastIndex = 0
  let match
  let segIdCounter = 0

  const kwColorMap = new Map()
  if (props.card.keywords) {
    props.card.keywords.forEach(k => kwColorMap.set(k.word, k.color))
  }

  while ((match = regex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      const plainText = content.substring(lastIndex, match.index)
      addPlainTextSegments(plainText, segments, () => `seg-${segIdCounter++}`)
    }

    const kwText = match[1]
    const segId = `kw-${segIdCounter++}`
    const color = kwColorMap.get(kwText) || '#2e6297'
    
    let shouldCloze = false
    if (props.mode === 'keyword') {
      shouldCloze = true
    } else if (props.mode === 'random') {
      shouldCloze = (segIdCounter % 2 === 0)
    }

    const isRev = revealedMap.value.has(segId) ? revealedMap.value.get(segId) : false

    segments.push({
      id: segId,
      type: 'keyword',
      text: kwText,
      color,
      isMuted: false,
      shouldCloze,
      revealed: isRev,
    })

    lastIndex = regex.lastIndex
  }

  if (lastIndex < content.length) {
    const tailText = content.substring(lastIndex)
    addPlainTextSegments(tailText, segments, () => `seg-${segIdCounter++}`)
  }

  return segments
})

function addPlainTextSegments(text, segments, nextId) {
  const lines = text.split('\n')
  lines.forEach((line, lIdx) => {
    if (lIdx > 0) {
      segments.push({ type: 'newline' })
    }
    if (line) {
      // 识别行内的趣味小图占位符 (例如 {俄国国旗}{直升机})
      const symRegex = /\{([^{}\n]+)\}/g
      let lastSymIdx = 0
      let symMatch
      while ((symMatch = symRegex.exec(line)) !== null) {
        if (symMatch.index > lastSymIdx) {
          const piece = line.substring(lastSymIdx, symMatch.index)
          if (piece) {
            const segId = nextId()
            const shouldCloze = props.mode === 'sentence' && piece.trim().length > 1
            const isRev = revealedMap.value.has(segId) ? revealedMap.value.get(segId) : false
            segments.push({
              id: segId,
              type: 'plain',
              text: piece,
              isMuted: false,
              shouldCloze,
              revealed: isRev,
            })
          }
        }
        const symName = symMatch[1]
        const symInfo = getSymbolInfo(symName)
        if (symInfo) {
          // 趣味助记图作为线索保留，不参与挖空遮盖
          segments.push({
            id: nextId(),
            type: 'symbol',
            name: symName,
            hash: symInfo.hash,
            desc: symInfo.desc,
            shouldCloze: false,
            isMuted: false,
          })
        } else {
          const segId = nextId()
          segments.push({
            id: segId,
            type: 'plain',
            text: symMatch[0],
            isMuted: false,
            shouldCloze: false,
            revealed: true,
          })
        }
        lastSymIdx = symRegex.lastIndex
      }
      if (lastSymIdx < line.length) {
        const tailPiece = line.substring(lastSymIdx)
        if (tailPiece) {
          const segId = nextId()
          const shouldCloze = props.mode === 'sentence' && tailPiece.trim().length > 1
          const isRev = revealedMap.value.has(segId) ? revealedMap.value.get(segId) : false
          segments.push({
            id: segId,
            type: 'plain',
            text: tailPiece,
            isMuted: false,
            shouldCloze,
            revealed: isRev,
          })
        }
      }
    }
  })
}
</script>

<style scoped>
.card-container {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
}

.card-header {
  background: var(--bg-beige);
  border-bottom: 1px solid var(--border-light);
  padding: 10px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.source-id-tag {
  font-weight: 700;
  color: #78350f;
  font-size: 0.85em;
  background: #fef3c7;
  border: 1px solid #fde68a;
  padding: 2px 10px;
  border-radius: 6px;
  letter-spacing: 0.3px;
}

.hierarchy-tag {
  color: var(--text-muted);
  font-size: 0.85em;
  font-weight: 500;
}

.fav-btn {
  background: #ffffff;
  border: 1px solid var(--border-light);
  color: var(--text-muted);
  font-size: 0.85em;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.fav-btn.active {
  color: #b45309;
  font-weight: 700;
  background: #fef3c7;
  border-color: #fde68a;
}

.card-title-bar {
  padding: 16px 20px 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}

.kp-title {
  font-size: 1.35em;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: 0.3px;
  line-height: 1.35;
}

.page-hint {
  font-size: 0.82em;
  color: var(--text-muted);
  background: var(--bg-beige-light);
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.full-cover {
  padding: 70px 20px;
  background: #f7f1e7;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-top: 1px dashed var(--border-light);
  border-bottom: 1px dashed var(--border-light);
}

.full-cover:hover {
  background: #f0e8db;
}

.full-cover-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.cover-icon {
  font-size: 2.5em;
}

.cover-text {
  font-size: 1em;
  color: #7c6853;
  font-weight: 600;
}

.card-body {
  padding: 14px 20px 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cloze-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-beige-light);
  border: 1px solid var(--border-light);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: 0.85em;
}

.mode-badge {
  color: var(--primary-accent);
  font-weight: 700;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.tool-btn {
  background: #fff;
  border: 1px solid var(--border-light);
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 0.85em;
  font-weight: 500;
  color: var(--text-regular);
}

.tool-btn:hover {
  background: var(--bg-beige);
}

.content-text {
  line-height: 1.95;
  color: var(--text-main);
  white-space: pre-wrap;
  word-break: break-word;
  letter-spacing: 0.35px;
}

/* 核心关键词高亮增强（清晰醒目） */
.keyword-highlight {
  font-weight: 700 !important;
  display: inline;
  padding: 1px 3px;
  border-radius: 4px;
  background: rgba(46, 98, 151, 0.08);
  border-bottom: 1.5px solid var(--kw-color, currentColor);
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}

.distinction-section {
  border-top: 1px dashed var(--border-light);
  padding-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-badge {
  font-size: 0.82em;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.dist-item {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 0.92em;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dist-header-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82em;
  font-weight: 700;
}

.dist-stmt {
  line-height: 1.6;
  font-weight: 500;
}

.verdict-correct {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-left: 4px solid #16a34a;
  color: #14532d;
}
.verdict-correct .dist-header-tag {
  color: #15803d;
}

.verdict-wrong {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-left: 4px solid #dc2626;
  color: #7f1d1d;
}
.verdict-wrong .dist-header-tag {
  color: #b91c1c;
}

.verdict-warn {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-left: 4px solid #d97706;
  color: #78350f;
}
.verdict-warn .dist-header-tag {
  color: #b45309;
}

.mnemonic-section {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-left: 4px solid #d97706;
  border-radius: var(--radius-md);
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mne-item {
  font-size: 0.95em;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #78350f;
  font-weight: 600;
  line-height: 1.6;
}

.mne-icon {
  font-size: 1.1em;
  line-height: 1.4;
}

.symbol-sticker {
  display: inline-block;
  vertical-align: middle;
  line-height: 1;
  margin: 0 2px;
  cursor: pointer;
  position: relative;
  user-select: none;
  -webkit-user-select: none;
}

.symbol-sticker-img {
  height: 1.35em;
  width: auto;
  max-width: 2.2em;
  vertical-align: -0.22em;
  display: inline-block;
  object-fit: contain;
  transition: transform 0.18s cubic-bezier(0.34, 1.56, 0.64, 1);
  filter: drop-shadow(0 1px 1.5px rgba(0, 0, 0, 0.10));
}

.symbol-sticker:hover .symbol-sticker-img,
.symbol-sticker:active .symbol-sticker-img {
  transform: scale(1.25) translateY(-1.5px);
  filter: drop-shadow(0 3px 4px rgba(0, 0, 0, 0.18));
}

.symbol-fallback {
  font-size: 0.85em;
  color: #92400e;
  background: #fef3c7;
  padding: 1px 4px;
  border-radius: 4px;
}

.card-footer {
  border-top: 1px solid var(--border-light);
  padding: 10px 20px;
  background: #faf8f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85em;
  flex-wrap: wrap;
  gap: 8px;
}

.card-uid {
  color: var(--text-muted);
  font-family: monospace;
  font-size: 0.9em;
}

.source-img-btn {
  background: #ffffff;
  border: 1px solid var(--border-card);
  color: var(--primary-accent);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.source-img-btn:hover {
  background: var(--bg-beige-light);
}

/* 置顶图片展示样式 */
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

/* 手机端专用优化 */
@media (max-width: 768px) {
  .card-container {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
  .card-header {
    padding: 8px 12px;
    gap: 6px;
  }
  .source-id-tag {
    font-size: 0.8em;
    padding: 2px 7px;
  }
  .hierarchy-tag {
    font-size: 0.78em;
  }
  .fav-btn {
    padding: 4px 9px;
    font-size: 0.78em;
  }
  .card-title-bar {
    padding: 10px 12px 4px 12px;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
  }
  .kp-title {
    font-size: 1.18em;
    line-height: 1.32;
  }
  .page-hint {
    font-size: 0.75em;
    padding: 2px 6px;
  }
  .card-body {
    padding: 10px 12px 14px 12px;
    gap: 12px;
  }
  .cloze-toolbar {
    padding: 6px 10px;
    font-size: 0.8em;
  }
  .content-text {
    line-height: 1.88;
    letter-spacing: 0.2px;
  }
  .dist-item {
    padding: 8px 10px;
    font-size: 0.88em;
  }
  .mnemonic-section {
    padding: 10px 12px;
  }
  .related-questions-section {
    padding: 10px 12px;
    gap: 10px;
  }
  .q-pill-btn {
    padding: 5px 10px;
    min-height: 31px;
    font-size: 0.84em;
  }
  .card-footer {
    padding: 8px 12px;
  }
  .source-img-btn {
    width: 100%;
    justify-content: center;
    padding: 8px 12px;
  }
}

/* 考点对应真题与模拟题区域 (借鉴 Markji 一页纸逻辑) */
.related-questions-section {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #3b82f6;
  border-radius: var(--radius-md);
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 4px;
}

.related-badge {
  color: #1e40af;
  background: #eff6ff;
  border-color: #bfdbfe;
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.source-tag {
  font-size: 0.8em;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.true-tag {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.mock-tag {
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

.q-status-badge.right {
  color: #16a34a;
}

.q-status-badge.wrong {
  color: #dc2626;
}
</style>
