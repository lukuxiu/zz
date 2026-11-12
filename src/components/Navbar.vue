<template>
  <nav class="nav-container">
    <div class="nav-brand" @click="$emit('navigate', 'browse')">
      <span class="brand-badge">2027</span>
      <span class="brand-title">一页纸考研政治</span>
    </div>

    <div class="nav-links">
      <button 
        :class="['nav-btn', { active: currentTab === 'browse' }]"
        @click="$emit('navigate', 'browse')"
      >
        <span class="icon">📖</span>
        <span class="label">知识点浏览背诵</span>
      </button>

      <button 
        :class="['nav-btn', { active: currentTab === 'solve' }]"
        @click="$emit('navigate', 'solve')"
      >
        <span class="icon">✍️</span>
        <span class="label">真题模拟题刷题</span>
      </button>
    </div>

    <div class="nav-actions">
      <button class="icon-btn" title="数据备份与设置" @click="$emit('open-settings')">
        ⚙️
      </button>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  currentTab: { type: String, default: 'browse' },
  dueCount: { type: Number, default: 0 },
  mistakeCount: { type: Number, default: 0 }
})

defineEmits(['navigate', 'open-settings'])
</script>

<style scoped>
.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid var(--border-card);
  padding: 8px 20px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  height: 60px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.brand-badge {
  background: var(--primary-accent);
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.brand-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-regular);
  font-size: 14px;
  font-weight: 500;
  position: relative;
}

.nav-btn:hover {
  background: var(--bg-beige-light);
}

.nav-btn.active {
  background: var(--bg-beige);
  color: var(--text-main);
  font-weight: 700;
}

.badge-count {
  background: var(--primary-accent);
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}

.badge-count.mistake {
  background: var(--danger-accent);
}

.icon-btn {
  background: var(--bg-beige-light);
  border: 1px solid var(--border-light);
  font-size: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: var(--bg-beige);
}

@media (max-width: 768px) {
  .nav-container {
    padding: 6px 10px;
    height: 52px;
    gap: 6px;
  }
  .brand-title {
    display: none;
  }
  .brand-badge {
    font-size: 11px;
    padding: 3px 6px;
    border-radius: 6px;
  }
  .nav-links {
    flex: 1;
    justify-content: center;
    background: var(--bg-beige-light);
    padding: 3px;
    border-radius: 10px;
    border: 1px solid var(--border-light);
    gap: 4px;
    max-width: 310px;
  }
  .nav-btn {
    flex: 1;
    justify-content: center;
    padding: 6px 8px;
    flex-direction: row;
    gap: 4px;
    border-radius: 7px;
    white-space: nowrap;
  }
  .nav-btn.active {
    background: #ffffff;
    color: var(--primary-accent);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }
  .nav-btn .icon {
    font-size: 14px;
    line-height: 1;
  }
  .nav-btn .label {
    font-size: 12.5px;
    font-weight: 700;
  }
  .icon-btn {
    width: 32px;
    height: 32px;
    font-size: 14px;
    flex-shrink: 0;
  }
}
</style>
