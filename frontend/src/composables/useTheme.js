import { ref } from 'vue'

const isDark = ref(false)

export function useTheme() {
  const initTheme = () => {
    const saved = localStorage.getItem('tabify-theme')
    if (saved) {
      isDark.value = saved === 'dark'
    } else {
      isDark.value = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    applyTheme()
  }

  const applyTheme = () => {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('tabify-theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('tabify-theme', 'light')
    }
  }

  const toggleTheme = () => {
    isDark.value = !isDark.value
    applyTheme()
  }

  return {
    isDark,
    initTheme,
    toggleTheme,
  }
}
