import { describe, it, expect, beforeEach } from 'vitest'

if (typeof globalThis.localStorage === 'undefined') {
  let store = {}
  globalThis.localStorage = {
    getItem: (key) => store[key] || null,
    setItem: (key, val) => { store[key] = String(val) },
    removeItem: (key) => { delete store[key] },
    clear: () => { store = {} }
  }
}

import methodsData from '../data/methods.json'
import questionsData from '../data/questions.json'
import { useSolveState } from '../src/modules/solve/services/solveState'

describe('解题方法刷题模块 (Solve Module)', () => {
  describe('1. 题库数据结构与完整性', () => {
    it('应完整包含 10 类老头命题挖坑手法', () => {
      expect(methodsData).toHaveLength(10)
      const expectedIds = [
        'absolute', 'tense', 'exaggerate', 'irrelevant', 'hedge',
        'foreign', 'us_related', 'idealism', 'target', 'others'
      ]
      methodsData.forEach(m => {
        expect(expectedIds).toContain(m.id)
        expect(m.name).toBeTruthy()
        expect(m.mnemonic).toBeTruthy()
        expect(m.keywords.length).toBeGreaterThan(0)
        expect(m.questionIds.length).toBeGreaterThan(0)
      })
    })

    it('应收录全部 68 道真题且答案与字段完备', () => {
      expect(questionsData).toHaveLength(68)
      const qIds = new Set(questionsData.map(q => q.id))
      expect(qIds.size).toBe(68)

      questionsData.forEach(q => {
        expect(q.id).toMatch(/^20\d\d\.\d+$/)
        expect(q.year).toBeGreaterThanOrEqual(2010)
        expect(q.no).toBeGreaterThan(0)
        expect(['single', 'multi']).toContain(q.type)
        expect(q.options).toBeDefined()
        expect(q.options.A).toBeDefined()
        expect(q.options.B).toBeDefined()
        expect(q.options.C).toBeDefined()
        expect(q.options.D).toBeDefined()
        expect(q.answer.length).toBeGreaterThan(0)
        expect(q.methods.length).toBeGreaterThan(0)
        expect(q.tip).toBeTruthy()
      })
    })

    it('所有解题方法中的题目 ID 必须存在于题库中', () => {
      const qMap = new Set(questionsData.map(q => q.id))
      methodsData.forEach(m => {
        m.questionIds.forEach(qid => {
          expect(qMap.has(qid)).toBe(true)
        })
      })
    })
  })

  describe('2. 解题状态服务与 SRS 复习流转', () => {
    beforeEach(() => {
      localStorage.clear()
    })

    it('答对题目应计入掌握并增加复习次数', () => {
      const { recordAnswer, getRecord } = useSolveState()
      const testQ = questionsData[0] // e.g. 2010.18
      const res = recordAnswer(testQ.id, testQ.answer)

      expect(res.isCorrect).toBe(true)
      const rec = getRecord(testQ.id)
      expect(rec.reviewCount).toBe(1)
      expect(rec.consecutiveGood).toBe(1)
      expect(rec.inMistakeBook).toBe(false)
    })

    it('答错题目应强制自动加入错题本', () => {
      const { recordAnswer, getRecord, mistakeQuestions } = useSolveState()
      const testQ = questionsData[0]
      const res = recordAnswer(testQ.id, ['Z']) // 故意答错

      expect(res.isCorrect).toBe(false)
      const rec = getRecord(testQ.id)
      expect(rec.inMistakeBook).toBe(true)
      expect(rec.consecutiveGood).toBe(0)
      expect(mistakeQuestions.value.some(q => q.id === testQ.id)).toBe(true)
    })

    it('错题连续 2 次答对并自评良好后应自动移出错题本', () => {
      const { recordAnswer, getRecord } = useSolveState()
      const testQ = questionsData[0]

      // 第1次：答错 -> 进错题本
      recordAnswer(testQ.id, ['Z'])
      expect(getRecord(testQ.id).inMistakeBook).toBe(true)

      // 第2次：答对 -> consecutiveGood = 1, 仍在错题本
      recordAnswer(testQ.id, testQ.answer, null, 'good')
      expect(getRecord(testQ.id).inMistakeBook).toBe(true)
      expect(getRecord(testQ.id).consecutiveGood).toBe(1)

      // 第3次：再次答对 -> consecutiveGood = 2, 自动移出
      recordAnswer(testQ.id, testQ.answer, null, 'good')
      expect(getRecord(testQ.id).inMistakeBook).toBe(false)
      expect(getRecord(testQ.id).consecutiveGood).toBe(2)
    })

    it('盲测模式手法命中判定正常', () => {
      const { recordAnswer } = useSolveState()
      const testQ = questionsData[0]
      const trueMethod = testQ.methods[0]

      const resHit = recordAnswer(testQ.id, testQ.answer, trueMethod)
      expect(resHit.methodHit).toBe(true)

      const resMiss = recordAnswer(testQ.id, testQ.answer, 'non_existent_method')
      expect(resMiss.methodHit).toBe(false)
    })

    it('统计看板指标计算正确', () => {
      const { recordAnswer, overallStats, getMethodStats } = useSolveState()
      const testQ = questionsData[0]
      recordAnswer(testQ.id, testQ.answer)

      const stats = overallStats.value
      expect(stats.total).toBe(68)
      expect(stats.practiced).toBeGreaterThan(0)
      expect(stats.accuracy).toBeGreaterThan(0)
      expect(stats.weakTop3).toHaveLength(3)
    })
  })
})
