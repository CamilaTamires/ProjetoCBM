import { ref, computed } from 'vue'
import type { CustomUser } from '@/types/api' // Importe o tipo CustomUser

const token = ref<string | null>(localStorage.getItem('authToken'))
// Ref para guardar os dados do usuário
const user = ref<CustomUser | null>(JSON.parse(localStorage.getItem('authUser') || 'null'))

const isAuthenticated = computed(() => !!token.value)

function setToken(newToken: string) {
  token.value = newToken
  localStorage.setItem('authToken', newToken)
}

export function clearToken() {
  token.value = null
  localStorage.removeItem('authToken')
  // Limpa o usuário também
  user.value = null
  localStorage.removeItem('authUser')
}

// Função para definir o usuário
function setUser(userData: CustomUser) {
  user.value = userData
  localStorage.setItem('authUser', JSON.stringify(userData))
}

export function useAuth() {
  return {
    token,
    user, 
    isAuthenticated,
    setToken,
    clearToken,
    setUser, 
  }
}
