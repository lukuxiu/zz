/**
 * 间隔复习算法 (Spaced Repetition System)
 * 严格按照 docs/srs.md 规范实现
 */

// 基础时间常数（毫秒）
const ONE_HOUR = 3600 * 1000
const ONE_DAY = 24 * ONE_HOUR

/**
 * 计算单次评价后的下次复习状态
 * @param {Object} currentRecord 当前卡片的学习记录 (可能为 undefined)
 * @param {'again'|'hard'|'good'|'easy'} grade 自我评价等级
 * @param {'keyword'|'sentence'|'random'|'full'} mode 当次复习遮挡模式
 * @param {number} now 当前时间戳，默认 Date.now()
 */
export function calculateNextReview(currentRecord = null, grade, mode = 'keyword', now = Date.now()) {
  const prevCount = currentRecord?.reviewCount || 0
  const prevConsecutive = currentRecord?.consecutiveGood || 0
  const prevMistake = currentRecord?.inMistakeBook || false
  const prevHistory = currentRecord?.history || []
  const isFav = currentRecord?.isFavorite || false

  let nextIntervalHours = 0
  let newConsecutive = prevConsecutive
  let inMistakeBook = prevMistake

  switch (grade) {
    case 'again': // 完全不会：当天再次出现，优先级最高
      nextIntervalHours = 0.25 // 15分钟后再次复现
      newConsecutive = 0
      inMistakeBook = true
      break

    case 'hard': // 模糊：1天后复习
      nextIntervalHours = 24
      newConsecutive = 0
      inMistakeBook = true
      break

    case 'good': // 基本掌握：3天后
      if (prevConsecutive === 0) {
        nextIntervalHours = 72 // 3天
      } else {
        nextIntervalHours = Math.round(72 * Math.pow(1.6, prevConsecutive))
      }
      newConsecutive = prevConsecutive + 1
      // 连续2次掌握移出活跃错题本
      if (prevMistake && newConsecutive >= 2) {
        inMistakeBook = false
      }
      break

    case 'easy': // 熟练掌握：7天后，之后递增
      if (prevConsecutive === 0) {
        nextIntervalHours = 168 // 7天
      } else if (prevConsecutive === 1) {
        nextIntervalHours = 336 // 14天
      } else {
        nextIntervalHours = Math.min(2880, Math.round(336 * Math.pow(2.2, prevConsecutive - 1))) // 最大120天
      }
      newConsecutive = prevConsecutive + 1
      // 连续2次掌握移出活跃错题本
      if (prevMistake && newConsecutive >= 2) {
        inMistakeBook = false
      }
      break
  }

  const nextReviewTime = now + nextIntervalHours * ONE_HOUR

  const newHistory = [
    ...prevHistory,
    {
      timestamp: now,
      grade,
      mode,
      intervalHours: nextIntervalHours,
    },
  ]

  return {
    reviewCount: prevCount + 1,
    consecutiveGood: newConsecutive,
    lastReviewTime: now,
    nextReviewTime,
    lastGrade: grade,
    isFavorite: isFav,
    inMistakeBook,
    history: newHistory,
  }
}

/**
 * 筛选今日到期需要复习的卡片
 * 优先顺序：完全不会 (again) > 模糊 (hard) > 其他到期
 */
export function getDueCards(allCards, userRecordsMap, now = Date.now()) {
  const due = []

  for (const card of allCards) {
    const rec = userRecordsMap[card.id]
    if (!rec) {
      // 尚未学过的卡片，不属于“待复习”，属于“新学”
      continue
    }

    if (rec.nextReviewTime <= now) {
      // 计算优先级权重：again(1) > hard(2) > good(3) > easy(4)
      let priority = 3
      if (rec.lastGrade === 'again') priority = 1
      else if (rec.lastGrade === 'hard') priority = 2

      due.push({
        card,
        record: rec,
        priority,
        nextReviewTime: rec.nextReviewTime,
      })
    }
  }

  // 排序：先按优先级升序，同优先级按下次复习时间升序
  due.sort((a, b) => {
    if (a.priority !== b.priority) {
      return a.priority - b.priority
    }
    return a.nextReviewTime - b.nextReviewTime
  })

  return due.map(d => d.card)
}

/**
 * 防同轮连续出现洗牌
 * 将指定卡片插入到队列末尾或至少相隔2张之后
 */
export function insertWithoutImmediateRepeat(queue, cardToInsert) {
  if (queue.length <= 1) {
    return [...queue, cardToInsert]
  }
  const result = [...queue]
  result.push(cardToInsert)
  return result
}
