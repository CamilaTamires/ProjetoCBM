<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import type { Ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import api from '../services/api'
import type { Equipment } from '../types/api'

// --- Estado do Componente ---
const equipments: Ref<Equipment[]> = ref([])
const loading: Ref<boolean> = ref(true)
const error: Ref<string | null> = ref(null)
const searchQuery: Ref<string> = ref('')
const router = useRouter()
const { user, clearToken } = useAuth()

// --- Estado de Ordenação ---
// '' = sem ordenação, 'name', 'code', 'category', 'environment'
const sortColumn = ref('')
// 1 = Crescente (A-Z), -1 = Decrescente (Z-A)
const sortDirection = ref(1)

// --- Funções ---
async function fetchEquipments() {
  try {
    const response = await api.getEquipments()
    equipments.value = response.data
  } catch (err) {
    console.error('Erro ao buscar os equipamentos:', err)
    error.value = 'Falha ao carregar os equipamentos. Verifique se o backend está rodando.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchEquipments)

// --- Função de Ordenação (Click no Botão) ---
function handleSort(column: string) {
  if (sortColumn.value === column) {
    // Se clicou na mesma coluna, inverte a direção
    sortDirection.value = sortDirection.value * -1
  } else {
    // Se clicou em nova coluna, define ela e reseta para Crescente
    sortColumn.value = column
    sortDirection.value = 1
  }
}

// --- Computed: Filtra E Ordena ---
const filteredEquipments = computed<Equipment[]>(() => {
  // 1. Primeiro Filtra pela Busca
  let result = equipments.value

  if (searchQuery.value) {
    const lowerCaseQuery = searchQuery.value.toLowerCase()
    result = result.filter(
      (equip) =>
        equip.name.toLowerCase().includes(lowerCaseQuery) ||
        equip.code.toLowerCase().includes(lowerCaseQuery) ||
        equip.environment_FK?.name.toLowerCase().includes(lowerCaseQuery) ||
        equip.category_FK?.name.toLowerCase().includes(lowerCaseQuery)
    )
  }

  // 2. Depois Ordena (Se houver coluna selecionada)
  if (sortColumn.value) {
    result = [...result].sort((a, b) => {
      let valA = ''
      let valB = ''

      // Define qual valor comparar baseado na coluna
      switch (sortColumn.value) {
        case 'name':
          valA = a.name?.toLowerCase() || ''
          valB = b.name?.toLowerCase() || ''
          break
        case 'code':
          valA = a.code?.toLowerCase() || ''
          valB = b.code?.toLowerCase() || ''
          break
        case 'category':
          valA = a.category_FK?.name?.toLowerCase() || ''
          valB = b.category_FK?.name?.toLowerCase() || ''
          break
        case 'environment':
          valA = a.environment_FK?.name?.toLowerCase() || ''
          valB = b.environment_FK?.name?.toLowerCase() || ''
          break
      }

      if (valA < valB) return -1 * sortDirection.value
      if (valA > valB) return 1 * sortDirection.value
      return 0
    })
  }

  return result
})

async function handleLogout() {
  if (window.confirm('Tem certeza que deseja sair?')) {
    try {
      await api.logout()
    } catch (e) {
    } finally {
      clearToken()
      router.push({ name: 'login' })
    }
  }
}
</script>

<template>
  <div class="app-container">
    <header class="header">
      <div class="header-left">
        <div class="brand-logo">MANGE_TECH</div>
        <nav class="nav-links">
          <router-link to="/" class="nav-item">Dashboard</router-link>
          <router-link to="/equipments" class="nav-item active">Ativos</router-link>
          <router-link to="/reports" class="nav-item">Relatórios</router-link>
        </nav>
      </div>

      <div class="header-right">
        <div class="user-menu">
          <button class="icon-btn disabled" title="Em breve">
            <i class="fas fa-bell"></i>
          </button>
          <div class="user-info" v-if="user">
            <span class="user-name">{{ user.name }}</span>
            <img src="@/assets/user.png" alt="Avatar" class="user-avatar" />
          </div>
          <button @click="handleLogout" class="logout-btn" title="Sair">
            <i class="fas fa-sign-out-alt"></i>
          </button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="content-header">
        <div>
          <h1 class="title">Ativos</h1>
          <p class="subtitle">Gerenciamento de equipamentos</p>
        </div>
        <button class="primary-btn disabled" title="Em breve">
          <i class="fas fa-plus"></i> Novo Ativo
        </button>
      </div>

      <div class="controls-bar">
        <div class="filters">
          <button
            class="filter-button"
            :class="{ active: sortColumn === 'category' }"
            @click="handleSort('category')"
          >
            Categoria
            <i
              class="fas"
              :class="
                sortColumn === 'category' && sortDirection === 1
                  ? 'fa-chevron-up'
                  : 'fa-chevron-down'
              "
            ></i>
          </button>

          <button
            class="filter-button"
            :class="{ active: sortColumn === 'environment' }"
            @click="handleSort('environment')"
          >
            Ambiente
            <i
              class="fas"
              :class="
                sortColumn === 'environment' && sortDirection === 1
                  ? 'fa-chevron-up'
                  : 'fa-chevron-down'
              "
            ></i>
          </button>

          <button
            class="filter-button"
            :class="{ active: sortColumn === 'name' }"
            @click="handleSort('name')"
          >
            Nome
            <i
              class="fas"
              :class="
                sortColumn === 'name' && sortDirection === 1 ? 'fa-chevron-up' : 'fa-chevron-down'
              "
            ></i>
          </button>
        </div>

        <div class="table-search">
          <i class="fas fa-search"></i>
          <input v-model="searchQuery" type="text" placeholder="Buscar ativos..." />
        </div>
      </div>

      <div class="data-view">
        <div v-if="loading" class="state-message">
          <div class="spinner"></div>
          Carregando ativos...
        </div>
        <div v-if="error" class="state-message error">{{ error }}</div>

        <div v-else class="table-responsive">
          <table class="custom-table">
            <thead>
              <tr>
                <th width="25%" @click="handleSort('name')" class="sortable">Nome</th>
                <th width="15%" @click="handleSort('code')" class="sortable">Código</th>
                <th width="20%" @click="handleSort('category')" class="sortable">Categoria</th>
                <th width="20%" @click="handleSort('environment')" class="sortable">Ambiente</th>
                <th width="10%">QR Code</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="equipment in filteredEquipments" :key="equipment.id">
                <td data-label="Nome">
                  <span class="equip-name">{{ equipment.name }}</span>
                </td>

                <td data-label="Código">
                  <span class="equip-code">{{ equipment.code }}</span>
                </td>

                <td data-label="Categoria" class="hide-mobile">
                  {{ equipment.category_FK?.name || '-' }}
                </td>

                <td data-label="Ambiente" class="hide-mobile">
                  {{ equipment.environment_FK?.name || '-' }}
                </td>

                <td data-label="QR Code">
                  <div v-if="equipment.qr_code_image" class="qr-wrapper">
                    <img :src="equipment.qr_code_image" alt="QR" class="qr-thumb" />
                  </div>
                  <span v-else class="text-muted">-</span>
                </td>
              </tr>
              <tr v-if="filteredEquipments.length === 0">
                <td colspan="5" class="empty-row">Nenhum ativo encontrado.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* --- DESIGN SYSTEM --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-app: #f3f4f6;
  --bg-panel: #ffffff;
  --border: #e5e7eb;
  --text-main: #111827;
  --text-muted: #6b7280;
  --primary: #2563eb;
  --danger: #ef4444;
  --green-btn: #38e07b;
}

* {
  box-sizing: border-box;
}

.app-container {
  background-color: var(--bg-app);
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  color: var(--text-main);
  display: flex;
  flex-direction: column;
}

/* HEADER */
.header {
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  padding: 0 2rem;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 50;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 3rem;
}
.brand-logo {
  font-weight: 800;
  font-size: 1.25rem;
  letter-spacing: -0.5px;
}
.nav-links {
  display: none;
  gap: 1.5rem;
}
.nav-item {
  text-decoration: none;
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: 0.2s;
}
.nav-item:hover,
.nav-item.active {
  color: var(--text-main);
  border-bottom-color: var(--text-main);
}
@media (min-width: 768px) {
  .nav-links {
    display: flex;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-left: 1rem;
  border-left: 1px solid var(--border);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: default;
}
.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
}
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border);
  transition: border-color 0.2s;
}
.user-info:hover .user-avatar {
  border-color: var(--primary);
}
.icon-btn {
  background-color: var(--bg-app);
  color: var(--text-muted);
  border: 0.6px solid;
  text-decoration: none;
  padding: 0.5rem 1.0rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: 0.2s;
  cursor: not-allowed;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--danger);
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.logout-btn:hover {
  opacity: 1;
}

/* MAIN CONTENT */
.main-content {
  flex: 1;
  padding: 2rem;
}
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.title {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
}
.subtitle {
  color: var(--text-muted);
  margin-top: 0.25rem;
  font-size: 0.95rem;
}

.primary-btn {
  background-color: var(--bg-app);
  color: var(--text-muted);
  border: 1px solid var(--border);
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: 0.2s;
  cursor: not-allowed;
}
.primary-btn:hover {
  border-color: var(--text-muted);
  color: var(--text-main);
}

/* TOOLBAR */
.controls-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}
.filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}
.filter-label {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-right: 0.5rem;
}

.filter-button {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-main);
  transition: all 0.2s;
}
/* Estilo para botão ativo/ordenado */
.filter-button.active {
  border-color: var(--primary);
  color: var(--primary);
  background-color: #f0f9ff;
}
.filter-button:hover {
  background-color: #f9fafb;
}

.table-search {
  position: relative;
  width: 300px;
}
.table-search i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 0.8rem;
}
.table-search input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}
.table-search input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

/* TABLE */
.data-view {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.state-message,
.empty-row {
  padding: 4rem 2rem;
  text-align: center;
  color: var(--text-muted);
  font-style: italic;
}
.error {
  color: var(--danger);
}
.spinner {
  border: 3px solid rgba(37, 99, 235, 0.1);
  border-left-color: var(--primary);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: inline-block;
  animation: spin 1s linear infinite;
  vertical-align: middle;
  margin-right: 10px;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
}
.custom-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  text-align: left;
  white-space: nowrap;
}
.custom-table th {
  background: #f9fafb;
  padding: 1rem 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.2s;
}
.custom-table th:hover {
  background: #f3f4f6;
  color: var(--text-main);
}
.custom-table td {
  padding: 1.1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
  color: var(--text-main);
  font-size: 0.9rem;
}
.custom-table tr:last-child td {
  border-bottom: none;
}
.custom-table tr:hover td {
  background: #f9fafb;
}

.equip-name {
  font-weight: 600;
  color: var(--text-main);
}
.equip-code {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 6px;
  color: var(--text-main);
  font-weight: 600;
  font-size: 0.85rem;
  border: 1px solid #e5e7eb;
}
.qr-wrapper {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
}
.qr-thumb {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.text-muted {
  color: var(--text-muted);
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .header-nav,
  .hide-mobile {
    display: none;
  }
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  .controls-bar {
    flex-direction: column;
  }
  .table-search {
    width: 100%;
  }

  .custom-table thead {
    display: none;
  }
  .custom-table,
  .custom-table tbody,
  .custom-table tr,
  .custom-table td {
    display: block;
    width: 100%;
  }
  .custom-table tr {
    margin-bottom: 1rem;
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  .custom-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    text-align: right;
  }
  .custom-table td:last-child {
    border-bottom: none;
  }
  .custom-table td::before {
    content: attr(data-label);
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .hide-mobile {
    display: flex;
  }
}
</style>