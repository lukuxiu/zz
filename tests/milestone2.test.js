import { describe, it, expect, beforeEach } from 'vitest'
import { 
  calculateNextReview, 
  getDueCards, 
  insertWithoutImmediateRepeat 
} from '../src/services/srs/srsAlgorithm.js'
import { 
  getDefaultUserState, 
  validateImportData, 
  exportBackup 
} from '../src/services/storage/storageInterface.js'

describe('里程碑2核心测试套件', () => {
  // 1. Storage 读写与默认状态
  it('Storage 初始化测试: 应返回合规的默认状态', () => {
    const defaultState = getDefaultUserState()
    expect(defaultState.version).toBe(1)
    expect(defaultState.records).toEqual({})
    expect(defaultState.settings.fontSizeLevel).toBe('medium')
    expect(defaultState.settings.defaultClozeMode).toBe('keyword')
  })

  // 2. 间隔复习算法 (SRS) 测试
  describe('SRS 间隔复习算法测试', () => {
    it('评价为“完全不会 (again)”：应设置为高优先级，短间隔复现并标记入错题本', () => {
      const now = 1700000000000
      const res = calculateNextReview(null, 'again', 'keyword', now)
      expect(res.reviewCount).toBe(1)
      expect(res.consecutiveGood).toBe(0)
      expect(res.inMistakeBook).toBe(true)
      expect(res.lastGrade).toBe('again')
      // 间隔约15分钟
      expect(res.nextReviewTime).toBe(now + 0.25 * 3600 * 1000)
    })

    it('评价为“模糊 (hard)”：应设置1天后复习并标记入错题本', () => {
      const now = 1700000000000
      const res = calculateNextReview(null, 'hard', 'keyword', now)
      expect(res.reviewCount).toBe(1)
      expect(res.consecutiveGood).toBe(0)
      expect(res.inMistakeBook).toBe(true)
      expect(res.nextReviewTime).toBe(now + 24 * 3600 * 1000)
    })

    it('连续评价为“基本掌握 (good)”：间隔应逐步递增', () => {
      const now = 1700000000000
      // 第一次基本掌握
      const r1 = calculateNextReview(null, 'good', 'keyword', now)
      expect(r1.consecutiveGood).toBe(1)
      expect(r1.nextReviewTime).toBe(now + 72 * 3600 * 1000) // 3天

      // 第二次基本掌握
      const r2 = calculateNextReview(r1, 'good', 'keyword', now)
      expect(r2.consecutiveGood).toBe(2)
      expect(r2.nextReviewTime).toBeGreaterThan(now + 72 * 3600 * 1000)
    })

    it('连续评价为“熟练掌握 (easy)”：长期间隔倍增', () => {
      const now = 1700000000000
      const r1 = calculateNextReview(null, 'easy', 'keyword', now)
      expect(r1.consecutiveGood).toBe(1)
      expect(r1.nextReviewTime).toBe(now + 168 * 3600 * 1000) // 7天

      const r2 = calculateNextReview(r1, 'easy', 'keyword', now)
      expect(r2.consecutiveGood).toBe(2)
      expect(r2.nextReviewTime).toBe(now + 336 * 3600 * 1000) // 14天
    })
  })

  // 3. 错题本状态流转测试
  describe('错题本流转机制测试', () => {
    it('初次不会入错题本，连续两次基本掌握后应自动移出活跃错题本，但保留历史记录', () => {
      const now = 1700000000000
      // 1. 第一次完全不会 -> 入错题本
      const r1 = calculateNextReview(null, 'again', 'keyword', now)
      expect(r1.inMistakeBook).toBe(true)

      // 2. 第二次好转 -> 1次掌握，仍保留在错题本
      const r2 = calculateNextReview(r1, 'good', 'keyword', now + 1000)
      expect(r2.consecutiveGood).toBe(1)
      expect(r2.inMistakeBook).toBe(true)

      // 3. 第三次好转 -> 连续2次掌握，移出错题本
      const r3 = calculateNextReview(r2, 'good', 'keyword', now + 2000)
      expect(r3.consecutiveGood).toBe(2)
      expect(r3.inMistakeBook).toBe(false)
      // 历史记录不应被抹除
      expect(r3.history.length).toBe(3)
      expect(r3.history[0].grade).toBe('again')
    })
  })

  // 4. 到期卡片筛选与优先级调度
  describe('到期复习与优先级调度', () => {
    it('完全不会的到期卡片应拥有最高调度优先级', () => {
      const now = 1700000000000
      const mockCards = [
        { id: 'kp-001-01', title: '卡片1' },
        { id: 'kp-002-01', title: '卡片2' },
        { id: 'kp-003-01', title: '卡片3' },
      ]

      const recordsMap = {
        'kp-001-01': {
          nextReviewTime: now - 1000,
          lastGrade: 'good',
        },
        'kp-002-01': {
          nextReviewTime: now - 2000,
          lastGrade: 'again', // 优先级最高
        },
        'kp-003-01': {
          nextReviewTime: now + 50000, // 未到期
          lastGrade: 'easy',
        },
      }

      const due = getDueCards(mockCards, recordsMap, now)
      expect(due.length).toBe(2)
      expect(due[0].id).toBe('kp-002-01') // again 优先排第一
      expect(due[1].id).toBe('kp-001-01')
    })

    it('同轮防连续复现机制: 不会立即紧随出现', () => {
      const q = [{ id: 'a' }, { id: 'b' }, { id: 'c' }]
      const updated = insertWithoutImmediateRepeat(q, { id: 'a' })
      expect(updated[updated.length - 1].id).toBe('a')
    })
  })

  // 5. JSON 导入与覆盖保护测试
  describe('JSON 导入、导出与防御性校验测试', () => {
    const validCardIds = new Set(['kp-001-01', 'kp-002-01', 'kp-003-01'])

    it('合法 JSON 导入应能成功识别与匹配记录', () => {
      const validPayload = {
        version: 1,
        records: {
          'kp-001-01': { reviewCount: 2, consecutiveGood: 1 },
          'kp-002-01': { reviewCount: 1, consecutiveGood: 0 },
        },
      }
      const res = validateImportData(validPayload, validCardIds)
      expect(res.valid).toBe(true)
      expect(res.matchedRecords).toBe(2)
    })

    it('非法或损坏的 JSON 导入应被坚决拒绝，不破坏现有数据', () => {
      expect(validateImportData(null, validCardIds).valid).toBe(false)
      expect(validateImportData('invalid string', validCardIds).valid).toBe(false)
      expect(validateImportData({ version: 1 }, validCardIds).valid).toBe(false)
      
      // 知识点 ID 全不匹配
      const alienData = {
        version: 1,
        records: { 'alien-id-999': { reviewCount: 1 } },
      }
      expect(validateImportData(alienData, validCardIds).valid).toBe(false)
    })

    it('导出备份测试: 生成的字符串应包含完整结构与有效 JSON', () => {
      const state = {
        version: 1,
        records: { 'kp-001-01': { reviewCount: 5 } },
        settings: { fontSizeLevel: 'large' },
      }
      const exported = exportBackup(state)
      const parsed = JSON.parse(exported)
      expect(parsed.version).toBe(1)
      expect(parsed.appName).toBe('2027考研政治一页纸智能背诵')
      expect(parsed.records['kp-001-01'].reviewCount).toBe(5)
    })
  })
})
