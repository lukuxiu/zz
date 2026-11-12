/**
 * 本地持久化与数据备份接口
 * 负责与 localStorage 交互，并提供防御性校验与导入导出保护
 */

const STORAGE_KEY = 'zhengz_recite_user_data_v1'
const CURRENT_VERSION = 1

/**
 * 默认空状态
 */
export function getDefaultUserState() {
  return {
    version: CURRENT_VERSION,
    records: {},       // cardId -> LearningRecord
    settings: {
      fontSizeLevel: 'medium', // small, medium, large, xlarge
      defaultClozeMode: 'keyword', // keyword, sentence, random, full
    },
    updatedAt: Date.now(),
  }
}

/**
 * 从 localStorage 读取用户数据
 */
export function loadUserState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return getDefaultUserState()
    }
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object' || !parsed.records) {
      console.warn('LocalStorage data corrupted, using default state')
      return getDefaultUserState()
    }
    return {
      version: parsed.version || CURRENT_VERSION,
      records: parsed.records || {},
      settings: {
        fontSizeLevel: parsed.settings?.fontSizeLevel || 'medium',
        defaultClozeMode: parsed.settings?.defaultClozeMode || 'keyword',
      },
      updatedAt: parsed.updatedAt || Date.now(),
    }
  } catch (err) {
    console.error('Failed to load user state from localStorage:', err)
    return getDefaultUserState()
  }
}

/**
 * 保存用户数据到 localStorage
 */
export function saveUserState(state) {
  try {
    const toSave = {
      version: CURRENT_VERSION,
      records: state.records || {},
      settings: state.settings || { fontSizeLevel: 'medium', defaultClozeMode: 'keyword' },
      updatedAt: Date.now(),
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
    return true
  } catch (err) {
    console.error('Failed to save user state to localStorage:', err)
    return false
  }
}

/**
 * 校验导入的数据格式与知识点有效性
 * @param {any} data 待导入的JSON对象
 * @param {Set<string>|Array<string>} validCardIds 系统中现有的全部知识点ID列表
 */
export function validateImportData(data, validCardIds) {
  if (!data || typeof data !== 'object') {
    return { valid: false, error: '导入数据必须是合法的 JSON 对象' }
  }

  if (typeof data.version !== 'number') {
    return { valid: false, error: '数据缺少版本号 (version)' }
  }

  if (!data.records || typeof data.records !== 'object') {
    return { valid: false, error: '数据缺少 records 学习记录对象' }
  }

  const validIdSet = validCardIds instanceof Set ? validCardIds : new Set(validCardIds)
  const incomingIds = Object.keys(data.records)
  
  // 检查是否包含至少部分有效的ID
  let matchCount = 0
  for (const id of incomingIds) {
    if (validIdSet.has(id)) {
      matchCount++
    }
  }

  if (incomingIds.length > 0 && matchCount === 0) {
    return { valid: false, error: '数据中的知识点ID与当前系统知识库完全不匹配' }
  }

  return {
    valid: true,
    totalRecords: incomingIds.length,
    matchedRecords: matchCount,
    updatedAt: data.updatedAt || null,
  }
}

/**
 * 导出备份 JSON 字符串 (包含背诵模块与解题刷题模块完整数据)
 */
export function exportBackup(state) {
  let solveRecords = {}
  let solveSettings = null
  if (typeof localStorage !== 'undefined') {
    try {
      const sr = localStorage.getItem('solve_records_v1')
      if (sr) solveRecords = JSON.parse(sr)
      const ss = localStorage.getItem('solve_settings_v1')
      if (ss) solveSettings = JSON.parse(ss)
    } catch (e) {
      console.warn('Failed to read solve storage during export:', e)
    }
  }

  const exportPayload = {
    version: CURRENT_VERSION,
    appName: '2027考研政治一页纸智能背诵',
    exportedAt: new Date().toISOString(),
    records: state.records,
    settings: state.settings,
    solveRecords,
    solveSettings,
    updatedAt: Date.now(),
  }
  return JSON.stringify(exportPayload, null, 2)
}
