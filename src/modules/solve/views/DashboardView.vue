<template>
  <div class="dashboard-view-container">
    <!-- 概览指标卡片 -->
    <div class="overview-grid">
      <div class="metric-card">
        <span class="metric-icon">📚</span>
        <div class="metric-info">
          <span class="metric-val">{{ overallStats.total }}</span>
          <span class="metric-label">收录真题</span>
        </div>
      </div>

      <div class="metric-card">
        <span class="metric-icon">✍️</span>
        <div class="metric-info">
          <span class="metric-val">{{ overallStats.practiced }}</span>
          <span class="metric-label">已练题目</span>
        </div>
      </div>

      <div class="metric-card">
        <span class="metric-icon">🎯</span>
        <div class="metric-info">
          <span class="metric-val accent-green">{{ overallStats.accuracy }}%</span>
          <span class="metric-label">综合正确率</span>
        </div>
      </div>

      <div class="metric-card">
        <span class="metric-icon">📕</span>
        <div class="metric-info">
          <span class="metric-val accent-red">{{ mistakeQuestions.length }}</span>
          <span class="metric-label">待复习错题</span>
        </div>
      </div>
    </div>

    <!-- 薄弱方法 Top 3 攻克卡片 -->
    <div class="weak-top-card">
      <div class="weak-header">
        <span class="weak-title">⚠️ 薄弱解题手法 Top 3（重点主攻）</span>
        <span class="weak-sub">根据您的历史作答正确率与练习量综合诊断</span>
      </div>

      <div class="weak-methods-grid">
        <div 
          v-for="(w, idx) in overallStats.weakTop3" 
          :key="w.id"
          class="weak-item"
        >
          <div class="weak-rank-chip">Top {{ idx + 1 }}</div>
          <div class="weak-name">{{ w.name }}</div>
          <div class="weak-mnemonic">{{ w.mnemonic }}</div>
          <div class="weak-stat-line">
            <span>正确率: <strong>{{ w.accuracy }}%</strong></span>
            <span>已练: {{ w.practiced }}/{{ w.total }}</span>
          </div>
          <button class="weak-action-btn" @click="$emit('start-practice', w.id)">
            🎯 立即专项攻克
          </button>
        </div>
      </div>
    </div>

    <!-- 10 类方法掌握度排行与进度柱 -->
    <div class="methods-ranking-card">
      <h3 class="card-section-title">📊 10 类解题手法掌握度统计</h3>
      <div class="methods-bars-list">
        <div 
          v-for="m in overallStats.methodRankList" 
          :key="m.id"
          class="method-bar-row"
        >
          <div class="row-info">
            <span class="method-bar-name">{{ m.name }}</span>
            <span class="method-bar-nums">{{ m.accuracy }}% ({{ m.practiced }}/{{ m.total }})</span>
          </div>
          <div class="bar-track">
            <div 
              class="bar-fill" 
              :style="{ width: `${m.accuracy}%` }"
              :class="getBarColorClass(m.accuracy)"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 方法 × 年份 二维热力矩阵图 -->
    <div class="matrix-card">
      <div class="matrix-header">
        <h3 class="card-section-title">🗺️ 方法 × 年份 真题考查分布与掌握热力图</h3>
        <div class="matrix-legend">
          <span class="legend-item"><span class="box-dot dot-none"></span> 无考题</span>
          <span class="legend-item"><span class="box-dot dot-unlearned"></span> 未练</span>
          <span class="legend-item"><span class="box-dot dot-wrong"></span> 需复习</span>
          <span class="legend-item"><span class="box-dot dot-correct"></span> 已掌握</span>
        </div>
      </div>

      <div class="matrix-scroll-wrap">
        <table class="heatmap-table">
          <thead>
            <tr>
              <th class="th-method">手法分类</th>
              <th v-for="yr in heatmapMatrix.years" :key="yr" class="th-year">
                {{ yr.toString().slice(2) }}年
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in heatmapMatrix.matrix" :key="row.methodId">
              <td class="td-method-name" @click="$emit('start-practice', row.methodId)">
                {{ row.methodName }}
              </td>
              <td 
                v-for="yr in heatmapMatrix.years" 
                :key="yr"
                class="td-cell"
                :class="`cell-${row.cells[yr].state}`"
                :title="`${yr}年 ${row.methodName}: ${row.cells[yr].count}题`"
                @click="handleCellClick(row.methodId, row.cells[yr].questions)"
              >
                {{ row.cells[yr].count > 0 ? row.cells[yr].count : '' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 危险操作区 -->
    <div class="reset-zone">
      <button class="reset-solve-btn" @click="handleResetSolve">
        ⚠️ 清空解题刷题记录
      </button>
    </div>
  </div>
</template>

<script setup>
import { useSolveState } from '../services/solveState'

const emit = defineEmits(['start-practice'])

const { 
  overallStats, 
  mistakeQuestions, 
  heatmapMatrix, 
  resetSolveData 
} = useSolveState()

function getBarColorClass(acc) {
  if (acc >= 80) return 'bar-high'
  if (acc >= 50) return 'bar-mid'
  return 'bar-low'
}

function handleCellClick(mid, questions) {
  if (questions && questions.length > 0) {
    emit('start-practice', mid)
  }
}

function handleResetSolve() {
  if (confirm('确定要清空全部解题刷题与做题记录吗？（背诵站的知识库记录不受影响）')) {
    resetSolveData()
    alert('已成功清空解题刷题记录！')
  }
}
</script>

<style scoped>
.dashboard-view-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 16px 16px 60px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.metric-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: var(--shadow-sm);
}

.metric-icon {
  font-size: 28px;
}

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-val {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.1;
}

.accent-green { color: var(--success-accent); }
.accent-red { color: var(--danger-accent); }

.metric-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* 薄弱方法卡片 */
.weak-top-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.weak-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 6px;
}

.weak-title {
  font-weight: 800;
  font-size: 16px;
  color: #a0471b;
}

.weak-sub {
  font-size: 12px;
  color: var(--text-muted);
}

.weak-methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.weak-item {
  border: 1.5px solid #ebd7b5;
  background: #fdfaf4;
  border-radius: 8px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.weak-rank-chip {
  align-self: flex-start;
  background: #c9791f;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.weak-name {
  font-weight: 800;
  font-size: 16px;
}

.weak-mnemonic {
  font-size: 12px;
  color: #7b4c10;
  background: #fff;
  padding: 6px;
  border-radius: 4px;
  border: 1px dashed #ebd7b5;
}

.weak-stat-line {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-muted);
}

.weak-action-btn {
  background: #c9791f;
  color: #fff;
  padding: 8px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 13px;
  margin-top: 4px;
}

/* 柱状进度 */
.methods-ranking-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.card-section-title {
  font-size: 16px;
  font-weight: 800;
}

.methods-bars-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.method-bar-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.row-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.method-bar-name {
  font-weight: 600;
}

.method-bar-nums {
  color: var(--text-muted);
}

.bar-track {
  height: 8px;
  background: var(--bg-warm);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--border-light);
}

.bar-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.bar-high { background: var(--success-accent); }
.bar-mid { background: var(--primary-accent); }
.bar-low { background: #c9791f; }

/* 二维矩阵热力图 */
.matrix-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.matrix-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.matrix-legend {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.box-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.dot-none { background: #f3eee6; border: 1px solid #e2dad0; }
.dot-unlearned { background: #e2e5ea; }
.dot-wrong { background: #f7c5c5; }
.dot-correct { background: #bfe5cc; }

.matrix-scroll-wrap {
  overflow-x: auto;
}

.heatmap-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.heatmap-table th, .heatmap-table td {
  border: 1px solid var(--border-light);
  padding: 8px 6px;
  text-align: center;
}

.th-method {
  text-align: left;
  padding-left: 10px;
  min-width: 130px;
}

.th-year {
  min-width: 44px;
  font-weight: 600;
  color: var(--text-muted);
}

.td-method-name {
  text-align: left;
  padding-left: 10px;
  font-weight: 600;
  cursor: pointer;
  color: var(--text-main);
}

.td-method-name:hover {
  color: var(--primary-accent);
}

.td-cell {
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.cell-none {
  background: #faf6f0;
  color: transparent;
}

.cell-unlearned {
  background: #eaecf1;
  color: #555e6d;
}

.cell-wrong {
  background: #fce8e8;
  color: #a82626;
}

.cell-correct {
  background: #eaf6ee;
  color: #1f6b3b;
}

.reset-zone {
  display: flex;
  justify-content: flex-end;
}

.reset-solve-btn {
  background: none;
  color: var(--text-muted);
  font-size: 12px;
  border: 1px dashed var(--border-card);
  padding: 6px 14px;
  border-radius: 6px;
}

.reset-solve-btn:hover {
  color: var(--danger-accent);
  border-color: var(--danger-accent);
}
</style>
