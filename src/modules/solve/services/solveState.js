import { ref, computed } from 'vue'
import methodsData from '../../../../data/methods.json'
import questionsData from '../../../../data/questions.json'
import mindsetsData from '../../../../data/mindsets.json'
import { calculateNextReview, getDueCards } from '../../../services/srs/srsAlgorithm'

const STORAGE_KEY_RECORDS = 'solve_records_v1'
const STORAGE_KEY_SETTINGS = 'solve_settings_v1'

// 响应式状态
const records = ref({})
const settings = ref({
  fontSizeLevel: 'medium',
  mockDurationMin: 25
})

// 初始化与持久化
function loadSolveStorage() {
  try {
    if (typeof localStorage === 'undefined') return
    const rawRecords = localStorage.getItem(STORAGE_KEY_RECORDS)
    if (rawRecords) {
      records.value = JSON.parse(rawRecords)
    }
    const rawSettings = localStorage.getItem(STORAGE_KEY_SETTINGS)
    if (rawSettings) {
      settings.value = { ...settings.value, ...JSON.parse(rawSettings) }
    }
  } catch (e) {
    console.error('Failed to load solve storage:', e)
  }
}

function saveSolveStorage() {
  try {
    if (typeof localStorage === 'undefined') return
    localStorage.setItem(STORAGE_KEY_RECORDS, JSON.stringify(records.value))
    localStorage.setItem(STORAGE_KEY_SETTINGS, JSON.stringify(settings.value))
  } catch (e) {
    console.error('Failed to save solve storage:', e)
  }
}

// 首次加载
loadSolveStorage()

export function useSolveState() {
  const allMethods = methodsData
  const allQuestions = questionsData
  const questionsMap = new Map(allQuestions.map(q => [q.id, q]))
  const methodsMap = new Map(allMethods.map(m => [m.id, m]))

  // 获取单题学习记录
  const getRecord = (qid) => {
    return records.value[qid] || {
      reviewCount: 0,
      consecutiveGood: 0,
      nextReviewTime: 0,
      lastReviewTime: 0,
      lastGrade: null,
      inMistakeBook: false,
      isFavorite: false,
      history: []
    }
  }

  // 记录用户作答
  const recordAnswer = (qid, userSelected = [], chosenMethod = null, selfGrade = null) => {
    const q = questionsMap.get(qid)
    if (!q) return

    const now = Date.now()
    const currentRec = getRecord(qid)

    // 判断选项是否完全正确
    const correctAns = [...q.answer].sort().join('')
    const userAns = [...userSelected].sort().join('')
    const isCorrect = correctAns === userAns

    // 判断盲测手法选择是否命中
    const methodHit = chosenMethod ? q.methods.includes(chosenMethod) : null

    // 如果未传入手动评分，根据对错自动默认初始等级：正确 -> good, 错误 -> again
    const grade = selfGrade || (isCorrect ? 'good' : 'again')

    // 复用现有 SRS 算法
    const srsResult = calculateNextReview(currentRec, grade, 'solve', now)

    // 如果用户答错，强制保证进入错题本
    if (!isCorrect) {
      srsResult.inMistakeBook = true
    }

    // 追加作答详情到历史记录
    const latestHistory = srsResult.history[srsResult.history.length - 1]
    if (latestHistory) {
      latestHistory.userSelected = userSelected
      latestHistory.isCorrect = isCorrect
      latestHistory.chosenMethod = chosenMethod
      latestHistory.methodHit = methodHit
    }

    records.value[qid] = {
      ...srsResult,
      isFavorite: currentRec.isFavorite
    }

    saveSolveStorage()
    return { isCorrect, methodHit, srsResult }
  }

  // 收藏切换
  const toggleFavorite = (qid) => {
    const cur = getRecord(qid)
    records.value[qid] = {
      ...cur,
      isFavorite: !cur.isFavorite
    }
    saveSolveStorage()
  }

  // 手动加入/移出错题本
  const toggleMistake = (qid) => {
    const cur = getRecord(qid)
    records.value[qid] = {
      ...cur,
      inMistakeBook: !cur.inMistakeBook
    }
    saveSolveStorage()
  }

  // 重置解题数据
  const resetSolveData = () => {
    records.value = {}
    saveSolveStorage()
  }

  // 计算属性：错题列表
  const mistakeQuestions = computed(() => {
    return allQuestions.filter(q => records.value[q.id]?.inMistakeBook)
  })

  // 计算属性：SRS 今日到期题目列表
  const dueQuestions = computed(() => {
    const now = Date.now()
    return allQuestions.filter(q => {
      const r = records.value[q.id]
      return r && r.nextReviewTime > 0 && r.nextReviewTime <= now
    })
  })

  // 计算属性：收藏列表
  const favoriteQuestions = computed(() => {
    return allQuestions.filter(q => records.value[q.id]?.isFavorite)
  })

  // 各方法统计指标
  const getMethodStats = (methodId) => {
    const method = methodsMap.get(methodId)
    if (!method) return { total: 0, practiced: 0, correctCount: 0, accuracy: 0 }

    const qids = method.questionIds
    let practiced = 0
    let correctCount = 0

    qids.forEach(qid => {
      const rec = records.value[qid]
      if (rec && rec.history && rec.history.length > 0) {
        practiced++
        // 最新一次作答是否正确
        const lastAns = rec.history[rec.history.length - 1]
        if (lastAns?.isCorrect) {
          correctCount++
        }
      }
    })

    const accuracy = practiced > 0 ? Math.round((correctCount / practiced) * 100) : 0
    return {
      total: qids.length,
      practiced,
      correctCount,
      accuracy
    }
  }

  // 计算属性：薄弱手法列表 (练习过的题目且正确率 < 70%)
  const weakMethods = computed(() => {
    return allMethods
      .map(m => {
        const stats = getMethodStats(m.id)
        return {
          ...m,
          ...stats,
          isWeak: stats.practiced >= 1 && stats.accuracy < 70
        }
      })
      .filter(m => m.isWeak)
  })

  // 薄弱手法题目队列
  const weakMethodQuestions = computed(() => {
    const weakIds = new Set(weakMethods.value.map(m => m.id))
    if (weakIds.size === 0) return []
    return allQuestions.filter(q => q.methods.some(m => weakIds.has(m)))
  })

  // 全局总体统计指标
  const overallStats = computed(() => {
    const total = allQuestions.length
    let practiced = 0
    let correctCount = 0

    allQuestions.forEach(q => {
      const rec = records.value[q.id]
      if (rec && rec.history && rec.history.length > 0) {
        practiced++
        const lastAns = rec.history[rec.history.length - 1]
        if (lastAns?.isCorrect) {
          correctCount++
        }
      }
    })

    const accuracy = practiced > 0 ? Math.round((correctCount / practiced) * 100) : 0
    const progressPercent = Math.round((practiced / total) * 100)

    // 计算各方法正确率以提取薄弱方法 Top3
    const methodRankList = allMethods.map(m => {
      const st = getMethodStats(m.id)
      return {
        id: m.id,
        name: m.name,
        mnemonic: m.mnemonic,
        practiced: st.practiced,
        accuracy: st.accuracy,
        total: st.total,
        // 排序分值：已刷过但正确率低的优先排在薄弱前列
        weakScore: st.practiced > 0 ? (100 - st.accuracy) : 50
      }
    })

    // 薄弱 Top3（至少刷过题且正确率最低，或未刷过的）
    const weakTop3 = [...methodRankList]
      .sort((a, b) => b.weakScore - a.weakScore)
      .slice(0, 3)

    return {
      total,
      practiced,
      correctCount,
      accuracy,
      progressPercent,
      weakTop3,
      methodRankList
    }
  })

  // 二维矩阵：方法 × 年份 (2010 ~ 2024)
  const heatmapMatrix = computed(() => {
    const years = [2010, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    const matrix = []

    allMethods.forEach(m => {
      const row = {
        methodId: m.id,
        methodName: m.name,
        cells: {}
      }
      years.forEach(yr => {
        const matching = allQuestions.filter(q => q.year === yr && q.methods.includes(m.id))
        const count = matching.length
        let state = 'none' // none | mastered | wrong | practiced
        if (count > 0) {
          const recs = matching.map(q => records.value[q.id])
          const hasRecord = recs.some(r => r && r.history && r.history.length > 0)
          if (!hasRecord) {
            state = 'unlearned'
          } else {
            const allCorrect = matching.every(q => {
              const r = records.value[q.id]
              const last = r?.history?.[r.history.length - 1]
              return last?.isCorrect
            })
            state = allCorrect ? 'correct' : 'wrong'
          }
        }
        row.cells[yr] = { count, state, questions: matching }
      })
      matrix.push(row)
    })

    return { years, matrix }
  })

  const mindsetPrinciples = mindsetsData.mindsetPrinciples || []
  const classicMarxQuotes = mindsetsData.classicMarxQuotes || []
  const tombstoneWords = mindsetsData.tombstoneWords || []

  return {
    records,
    settings,
    allMethods,
    allQuestions,
    questionsMap,
    methodsMap,
    mindsetPrinciples,
    classicMarxQuotes,
    tombstoneWords,
    getRecord,
    recordAnswer,
    toggleFavorite,
    toggleMistake,
    resetSolveData,
    mistakeQuestions,
    dueQuestions,
    favoriteQuestions,
    getMethodStats,
    overallStats,
    weakMethods,
    weakMethodQuestions,
    heatmapMatrix
  }
}
