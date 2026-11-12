import { describe, it, expect } from 'vitest'
import fs from 'fs'
import path from 'path'
import knowledgeData from '../data/knowledge.json'
import questionsData from '../data/questions.json'
import methodsData from '../data/methods.json'

describe('交接文档验收测试套件 (Handoff Suggestions Validation)', () => {
  const records = knowledgeData.records

  describe('A. 关键词连贯性与数据三字段一致性 (Section A & A.7)', () => {
    it('应包含完整 122 张卡片', () => {
      expect(records).toHaveLength(122)
    })

    it('所有卡片正文中的关键词 {{...}} 必须与 keywords 数组严格对应', () => {
      records.forEach(r => {
        const clozeWords = (r.content.match(/\{\{([^{}]+)\}\}/g) || []).map(w => w.slice(2, -2))
        const kwWords = (r.keywords || []).map(k => k.word)
        expect(clozeWords).toEqual(kwWords)
      })
    })

    it('contentHtml 中绝对不得再出现同色紧邻的高亮切断片段', () => {
      // 检查类似 </span><span class="keyword" style="color:#xxxxxx..."> 且两者颜色相同的断片 (零间距切开同一个词)
      const sameColorAdjacentRegex = /<span class="keyword" style="color:(#[0-9a-fA-F]+);[^>]*>[^<]*<\/span><span class="keyword" style="color:\1/
      records.forEach(r => {
        const match = sameColorAdjacentRegex.exec(r.contentHtml)
        expect(match, `卡片 ${r.id} 存在同色紧邻高亮切片`).toBeNull()
      })
    })

    it('典型错误卡片关键词必须完整连贯', () => {
      const kp003 = records.find(r => r.id === 'kp-003-01')
      expect(kp003.content).toContain('{{政治法律思想}}')
      expect(kp003.content).not.toContain('{{政治法律思}}{{想}}')

      const kp005 = records.find(r => r.id === 'kp-005-01')
      expect(kp005.content).toContain('{{劳动二重性理论}}')
      expect(kp005.content).not.toContain('{{劳}}{{动}}{{二}}{{重性理论}}')

      const kp002 = records.find(r => r.id === 'kp-002-01')
      expect(kp002.content).toContain('{{科学性}}与{{革命性}}的统一')
      expect(kp002.content).toContain('（行）')

      const kp010 = records.find(r => r.id === 'kp-010-01')
      expect(kp010.content).toContain('{{价值}}寓于{{使用价值}}之中')
      expect(kp010.content).not.toContain('{{价}}{{值}}{{寓}}')

      const kp013 = records.find(r => r.id === 'kp-013-01')
      expect(kp013.content).toContain('《{{德法年鉴}}》')
      expect(kp013.content).toContain('《{{神圣家族}}》')
      expect(kp013.content).toContain('《{{德意志意识形态}}》')
      expect(kp013.content).toContain('《{{共产党宣言}}》')
      expect(kp013.content).toContain('《{{资本论}}》')
      expect(kp013.content).toContain('《{{法兰西内战}}》')
    })
  })

  describe('B. 趣味图标与符号占位符清洗 (Section B & B.8)', () => {
    it('contentHtml 中不得残留任何形如 {xxx} 的未解析占位符', () => {
      // 匹配单大括号 {xxx} 且排除 {{xxx}}
      const residualPlaceholderRegex = /(?<!\{)\{([^{}\n]+)\}(?!\})/g
      records.forEach(r => {
        const matches = r.contentHtml.match(residualPlaceholderRegex)
        expect(matches, `卡片 ${r.id} 的 contentHtml 残留占位符: ${matches}`).toBeNull()
      })
    })

    it('所有趣味小图标映射的目标图片文件必须存在于 public/symbols/', () => {
      const publicSymbolsDir = path.resolve(process.cwd(), 'public/symbols')
      expect(fs.existsSync(publicSymbolsDir)).toBe(true)

      records.forEach(r => {
        if (r.symbols && r.symbols.length > 0) {
          r.symbols.forEach(s => {
            if (s.hash) {
              const imgPng = path.join(publicSymbolsDir, `${s.hash}.png`)
              const imgJpg = path.join(publicSymbolsDir, `${s.hash}.jpeg`)
              const exists = fs.existsSync(imgPng) || fs.existsSync(imgJpg)
              expect(exists, `符号图标文件缺失: ${s.hash} in card ${r.id}`).toBe(true)
            }
          })
        }
      })
    })
  })

  describe('C. 解题方法题库数据严格校验 (Section C.1 & C.2)', () => {
    const validMethodIds = new Set(methodsData.map(m => m.id))

    it('题库应正好包含 68 道真题且 ID 唯一', () => {
      expect(questionsData).toHaveLength(68)
      const ids = new Set(questionsData.map(q => q.id))
      expect(ids.size).toBe(68)
    })

    it('每道题目必须符合标准题型架构与答案选项约束', () => {
      const solveImagesDir = path.resolve(process.cwd(), 'public/images/solve')

      questionsData.forEach(q => {
        expect(['single', 'multi']).toContain(q.type)
        expect(q.options).toBeDefined()
        expect(q.options.A).toBeTruthy()
        expect(q.options.B).toBeTruthy()
        expect(q.options.C).toBeTruthy()
        expect(q.options.D).toBeTruthy()

        // 答案有效性
        expect(q.answer.length).toBeGreaterThan(0)
        q.answer.forEach(opt => {
          expect(['A', 'B', 'C', 'D']).toContain(opt)
        })
        if (q.type === 'single') {
          expect(q.answer.length).toBe(1)
        } else if (q.type === 'multi') {
          expect(q.answer.length).toBeGreaterThanOrEqual(2)
        }

        // 手法标签有效性
        expect(q.methods.length).toBeGreaterThan(0)
        q.methods.forEach(mid => {
          expect(validMethodIds.has(mid), `题目 ${q.id} 使用了无效手法标签: ${mid}`).toBe(true)
        })

        // 图片存在性
        if (q.image) {
          const imgRel = q.image.replace(/^\/?(public\/)?images\/solve\//, '')
          const imgPath = path.join(solveImagesDir, imgRel)
          expect(fs.existsSync(imgPath), `题目 ${q.id} 图片不存在: ${imgPath}`).toBe(true)
        }
      })
    })

    it('2021.23 题官方答案与干扰项应已校正为 ABC (D为陷阱)', () => {
      const q2021_23 = questionsData.find(q => q.id === '2021.23')
      expect(q2021_23).toBeDefined()
      expect(q2021_23.answer).toEqual(['A', 'B', 'C'])
      expect(q2021_23.trapOptions).toEqual(['D'])
    })
  })

  describe('D. 数据源统一性校验 (Section D.2)', () => {
    it('data/knowledge.json 与 public/data/knowledge.json 必须 100% 同步一致', () => {
      const p1 = path.resolve(process.cwd(), 'data/knowledge.json')
      const p2 = path.resolve(process.cwd(), 'public/data/knowledge.json')
      const f1 = fs.readFileSync(p1, 'utf-8')
      const f2 = fs.readFileSync(p2, 'utf-8')
      expect(f1).toBe(f2)
    })
  })
})
