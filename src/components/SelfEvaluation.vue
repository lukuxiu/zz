<template>
  <div class="eval-container">
    <div class="eval-title">完成背诵 · 请选择掌握程度</div>
    <div class="eval-buttons">
      <button class="eval-btn btn-again" @click="$emit('evaluate', 'again')">
        <span class="btn-key">1</span>
        <span class="btn-main">完全不会</span>
        <span class="btn-sub">当天再次出现</span>
      </button>

      <button class="eval-btn btn-hard" @click="$emit('evaluate', 'hard')">
        <span class="btn-key">2</span>
        <span class="btn-main">模糊</span>
        <span class="btn-sub">1天后复习</span>
      </button>

      <button class="eval-btn btn-good" @click="$emit('evaluate', 'good')">
        <span class="btn-key">3</span>
        <span class="btn-main">基本掌握</span>
        <span class="btn-sub">3天后复习</span>
      </button>

      <button class="eval-btn btn-easy" @click="$emit('evaluate', 'easy')">
        <span class="btn-key">4</span>
        <span class="btn-main">熟练掌握</span>
        <span class="btn-sub">7天后 / 延长期</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['evaluate'])
</script>

<style scoped>
.eval-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 14px;
  box-shadow: var(--shadow-sm);
}

.eval-title {
  font-size: 0.9em;
  font-weight: 700;
  color: var(--text-muted);
  text-align: center;
}

.eval-buttons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.eval-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 6px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  position: relative;
  transition: all 0.15s ease;
}

.btn-key {
  position: absolute;
  top: 4px;
  left: 6px;
  font-size: 10px;
  opacity: 0.6;
  font-weight: 700;
}

.btn-main {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 3px;
}

.btn-sub {
  font-size: 11px;
  opacity: 0.85;
}

/* 四档色彩规范 */
.btn-again {
  background: #faeeee;
  color: #b84c4c;
  border-color: #f1d3d3;
}
.btn-again:hover {
  background: #f7dede;
}

.btn-hard {
  background: #fdf5eb;
  color: #c07828;
  border-color: #f7e4ce;
}
.btn-hard:hover {
  background: #faecd9;
}

.btn-good {
  background: #eef4fb;
  color: #3b6aa0;
  border-color: #d6e4f5;
}
.btn-good:hover {
  background: #e1edfa;
}

.btn-easy {
  background: #edf6f0;
  color: #48825d;
  border-color: #d4ebd9;
}
.btn-easy:hover {
  background: #dfefe4;
}

@media (max-width: 640px) {
  .eval-buttons {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  .eval-btn {
    padding: 10px 4px;
  }
}
</style>
