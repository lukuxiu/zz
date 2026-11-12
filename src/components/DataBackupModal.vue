<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">⚙️ 数据备份与系统设置</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="modal-body">
        <!-- 字号偏好 -->
        <div class="setting-group">
          <div class="setting-label">阅读字号设置</div>
          <div class="font-selector">
            <button 
              v-for="lvl in ['small', 'medium', 'large', 'xlarge']" 
              :key="lvl"
              :class="['font-btn', { active: currentFontSize === lvl }]"
              @click="$emit('change-font-size', lvl)"
            >
              {{ fontLabelMap[lvl] }}
            </button>
          </div>
        </div>

        <!-- 默认遮挡偏好 -->
        <div class="setting-group">
          <div class="setting-label">默认背诵遮挡模式</div>
          <div class="font-selector">
            <button 
              v-for="m in ['none', 'keyword', 'sentence', 'random', 'full']" 
              :key="m"
              :class="['font-btn', { active: currentDefaultMode === m }]"
              @click="$emit('change-default-mode', m)"
            >
              {{ modeLabelMap[m] }}
            </button>
          </div>
        </div>

        <hr class="divider" />

        <!-- 备份与恢复 -->
        <div class="setting-group">
          <div class="setting-label">学习记录备份与恢复 (本地存储)</div>
          <p class="setting-desc">
            ⚠️ <strong>重要提示：</strong>系统所有背诵与解题刷题进度均保存在当前浏览器本地存储中，清理浏览器缓存或在无痕模式下浏览可能导致数据丢失！强烈建议您定期点击下方按钮导出备份文件。
          </p>
          
          <div class="btn-row">
            <button class="action-btn export-btn" @click="handleExport">
              <span>📥</span> 导出备份 JSON
            </button>
            
            <label class="action-btn import-btn">
              <span>📤</span> 导入恢复备份
              <input type="file" accept=".json" style="display:none" @change="handleFileImport" />
            </label>
          </div>

          <div v-if="importMessage" :class="['import-alert', importSuccess ? 'alert-success' : 'alert-danger']">
            {{ importMessage }}
          </div>
        </div>

        <hr class="divider" />

        <!-- 危险区域 -->
        <div class="setting-group danger-zone">
          <div class="setting-label text-danger">重置学习数据</div>
          <p class="setting-desc">重置将清空所有背诵进度、错题记录与复习算法历史（只读知识库内容不受影响）。</p>
          <button class="danger-btn" @click="handleReset">清空所有学习记录</button>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-done" @click="$emit('close')">完成</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { exportBackup, validateImportData } from '../services/storage/storageInterface'
import { useUserState, getAllCards } from '../services/storage/userState'

defineProps({
  visible: { type: Boolean, default: false },
  currentFontSize: { type: String, default: 'medium' },
  currentDefaultMode: { type: String, default: 'keyword' }
})

const emit = defineEmits(['close', 'change-font-size', 'change-default-mode'])

const { state, importState, resetAllData } = useUserState()

const fontLabelMap = {
  small: '小字号',
  medium: '标准',
  large: '大字号',
  xlarge: '特大'
}

const modeLabelMap = {
  none: '显示全部 (不遮挡)',
  keyword: '关键词遮挡',
  sentence: '分句遮挡',
  random: '随机挖空',
  full: '整卡遮挡'
}

const importMessage = ref('')
const importSuccess = ref(false)

function handleExport() {
  const jsonStr = exportBackup(state)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  const dateStr = new Date().toISOString().slice(0, 10)
  a.href = url
  a.download = `zhengz_backup_${dateStr}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function handleFileImport(e) {
  const file = e.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (evt) => {
    try {
      const parsed = JSON.parse(evt.target.result)
      const allCards = getAllCards()
      const validIds = new Set(allCards.map(c => c.id))

      const check = validateImportData(parsed, validIds)
      if (!check.valid) {
        importSuccess.value = false
        importMessage.value = `❌ 导入失败: ${check.error}`
        return
      }

      const conf = confirm(`检测到有效备份记录 ${check.matchedRecords} 条。\n导入将覆盖当前的本地学习记录，是否继续？`)
      if (!conf) return

      importState(parsed)
      importSuccess.value = true
      importMessage.value = `✅ 成功恢复 ${check.matchedRecords} 条学习记录！`
    } catch (err) {
      importSuccess.value = false
      importMessage.value = `❌ 解析文件失败: ${err.message}`
    }
  }
  reader.readAsText(file, 'utf-8')
}

function handleReset() {
  const conf = confirm('⚠️ 确定要清空全部背诵记录与错题本吗？此操作无法撤销！')
  if (conf) {
    resetAllData()
    alert('已成功清空本地学习记录！')
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(30, 27, 24, 0.7);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-dialog {
  background: #ffffff;
  border-radius: var(--radius-lg);
  max-width: 520px;
  width: 100%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: var(--bg-beige);
  border-bottom: 1px solid var(--border-light);
}

.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
}

.close-btn {
  background: transparent;
  font-size: 18px;
  color: var(--text-muted);
}

.modal-body {
  padding: 18px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
}

.setting-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.font-selector {
  display: flex;
  gap: 8px;
}

.font-btn {
  flex: 1;
  padding: 8px 4px;
  border: 1px solid var(--border-card);
  background: #fff;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-regular);
}

.font-btn.active {
  background: var(--primary-accent-bg);
  border-color: var(--primary-accent);
  color: var(--primary-accent);
  font-weight: 700;
}

.divider {
  border: none;
  border-top: 1px dashed var(--border-light);
  margin: 4px 0;
}

.btn-row {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--border-card);
  background: #fff;
  color: var(--text-main);
}

.action-btn:hover {
  background: var(--bg-beige-light);
}

.import-alert {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  margin-top: 8px;
}

.alert-success {
  background: var(--success-accent-bg);
  color: var(--success-accent);
}

.alert-danger {
  background: var(--danger-accent-bg);
  color: var(--danger-accent);
}

.danger-zone {
  background: #fdf6f6;
  padding: 12px;
  border-radius: var(--radius-md);
  border: 1px solid #fae1e1;
}

.text-danger {
  color: var(--danger-accent);
}

.danger-btn {
  background: #fff;
  border: 1px solid var(--danger-accent);
  color: var(--danger-accent);
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  align-self: flex-start;
  margin-top: 4px;
}

.danger-btn:hover {
  background: var(--danger-accent);
  color: white;
}

.modal-footer {
  padding: 10px 18px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  background: #fafaf8;
}

.btn-done {
  background: var(--primary-accent);
  color: white;
  padding: 6px 18px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
}
</style>
