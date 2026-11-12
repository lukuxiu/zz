import { reactive, computed } from 'vue'
import { loadUserState, saveUserState, getDefaultUserState } from './storageInterface'
import { calculateNextReview, getDueCards } from '../srs/srsAlgorithm'

const state = reactive(loadUserState())

// 知识库全局缓存 (只读)
let allKnowledgeCards = []
const cardIdMap = new Map()

export function setKnowledgeCards(cards) {
  allKnowledgeCards = cards
  cardIdMap.clear()
  cards.forEach(c => cardIdMap.set(c.id, c))
}

export function getAllCards() {
  return allKnowledgeCards
}

export function getCardById(id) {
  return cardIdMap.get(id)
}

// 自动持久化辅助
function persist() {
  saveUserState(state)
}

export const useUserState = () => {
  // 记录一次评价
  function recordReview(cardId, grade, mode = 'keyword') {
    const cur = state.records[cardId]
    const updated = calculateNextReview(cur, grade, mode)
    state.records[cardId] = updated
    state.updatedAt = Date.now()
    persist()
  }

  // 切换收藏
  function toggleFavorite(cardId) {
    if (!state.records[cardId]) {
      state.records[cardId] = {
        reviewCount: 0,
        consecutiveGood: 0,
        lastReviewTime: 0,
        nextReviewTime: 0,
        lastGrade: null,
        isFavorite: true,
        inMistakeBook: false,
        history: [],
      }
    } else {
      state.records[cardId].isFavorite = !state.records[cardId].isFavorite
    }
    state.updatedAt = Date.now()
    persist()
  }

  // 手动移出错题本
  function removeFromMistakes(cardId) {
    if (state.records[cardId]) {
      state.records[cardId].inMistakeBook = false
      state.updatedAt = Date.now()
      persist()
    }
  }

  // 更新设置（字号等）
  function updateSettings(patch) {
    state.settings = { ...state.settings, ...patch }
    persist()
  }

  // 恢复导入
  function importState(validatedData) {
    state.records = { ...validatedData.records }
    if (validatedData.settings) {
      state.settings = { ...state.settings, ...validatedData.settings }
    }
    state.updatedAt = Date.now()
    persist()

    // 若包含解题刷题模块的数据，一并恢复
    if (validatedData.solveRecords && typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem('solve_records_v1', JSON.stringify(validatedData.solveRecords))
        if (validatedData.solveSettings) {
          localStorage.setItem('solve_settings_v1', JSON.stringify(validatedData.solveSettings))
        }
      } catch (e) {
        console.warn('Failed to restore solve records from backup:', e)
      }
    }
  }

  // 清空数据
  function resetAllData() {
    const fresh = getDefaultUserState()
    state.records = fresh.records
    state.settings = fresh.settings
    state.updatedAt = fresh.updatedAt
    persist()
  }

  // === 统计指标 ===
  const totalCardsCount = computed(() => allKnowledgeCards.length)

  // 待复习卡片
  const dueCards = computed(() => {
    return getDueCards(allKnowledgeCards, state.records)
  })

  // 今日新学数量
  const learnedCardsCount = computed(() => {
    return Object.values(state.records).filter(r => r.reviewCount > 0).length
  })

  // 错题数量 (活跃错题)
  const mistakeCards = computed(() => {
    return allKnowledgeCards.filter(c => state.records[c.id]?.inMistakeBook)
  })

  // 熟练掌握数量 (连续掌握 >= 2 且不在错题本中)
  const masteredCardsCount = computed(() => {
    return Object.values(state.records).filter(r => r.consecutiveGood >= 2 && !r.inMistakeBook).length
  })

  // 收藏卡片列表
  const favoriteCards = computed(() => {
    return allKnowledgeCards.filter(c => state.records[c.id]?.isFavorite)
  })

  return {
    state,
    recordReview,
    toggleFavorite,
    removeFromMistakes,
    updateSettings,
    importState,
    resetAllData,
    totalCardsCount,
    dueCards,
    learnedCardsCount,
    mistakeCards,
    masteredCardsCount,
    favoriteCards,
  }
}
