<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import type { Ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'
import api from '../services/api'
import type { Task, TaskStatus, TaskStatusValue } from '../types/api'

// --- Estado do Componente ---
const tasks: Ref<Task[]> = ref([])
const loading: Ref<boolean> = ref(true)
const error: Ref<string | null> = ref(null)
const searchQuery: Ref<string> = ref('')

// --- Estado de Ordenação / Filtro por coluna ---
const sortColumn = ref<string>('')
const sortDirection = ref<number>(1) // 1 = asc, -1 = desc

// Função para ordenar quando clicar nos botões
function handleSort(column: string) {
  if (sortColumn.value === column) {
    sortDirection.value = -sortDirection.value
  } else {
    sortColumn.value = column
    sortDirection.value = 1
  }
}

const router = useRouter()
const { user, clearToken } = useAuth()

// --- Estado para o Modal de Atualização de Status ---
const showStatusModal = ref(false)
const statusUpdateComment = ref('')
const statusUpdateImage = ref<File | null>(null)
const statusUpdateImageName = ref<string>('')
const taskToUpdate = ref<Task | null>(null)
const newStatusToSet = ref<TaskStatusValue | null>(null)

// --- Funções ---
async function fetchTasks() {
  try {
    // O Backend retorna APENAS o que o usuário pode ver.
    // Se for Técnico -> Retorna tudo.
    // Se for Colaborador -> Retorna só os dele.
    const response = await api.getTasks()
    const fetchedTasks = response.data

    // Organização do Histórico de Status (para pegar o status atual corretamente)
    fetchedTasks.forEach((task) => {
      if (task.status_history && Array.isArray(task.status_history)) {
        task.status_history.sort(
          (a, b) => new Date(b.status_date).getTime() - new Date(a.status_date).getTime()
        )
      } else {
        task.status_history = []
      }
    })

    // Ordenação Visual: Mais recentes no topo (Redundância visual caso backend não ordene)
    fetchedTasks.sort(
      (a, b) => new Date(b.creation_date).getTime() - new Date(a.creation_date).getTime()
    )

    tasks.value = fetchedTasks
  } catch (err) {
    console.error('Erro ao buscar as tarefas:', err)
    error.value = 'Falha ao carregar os chamados. Verifique se o backend está rodando.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchTasks)

// --- Helpers ---
const getLatestStatus = (task: Task): TaskStatusValue | null => {
  return task.status_history && task.status_history.length > 0
    ? task.status_history[0].status
    : null
}

const getLatestStatusDate = (task: Task): string | null => {
  return task.last_status_date || task.creation_date || null
}

const filteredTasks = computed<Task[]>(() => {
  let result = [...tasks.value]

  // Primeiro: filtro de busca
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      (task) =>
        task.name.toLowerCase().includes(q) ||
        task.id.toString().includes(q) ||
        task.creator_FK?.name.toLowerCase().includes(q)
    )
  }

  // Depois: ordenação conforme sortColumn
  if (sortColumn.value) {
    result.sort((a, b) => {
      let vA: any = ''
      let vB: any = ''

      switch (sortColumn.value) {
        case 'date':
          // considera a data mais recente / data de status
          vA = getLatestStatusDate(a) ?? ''
          vB = getLatestStatusDate(b) ?? ''
          break
        case 'environment':
          vA = a.equipments_FK[0]?.environment_FK?.name ?? ''
          vB = b.equipments_FK[0]?.environment_FK?.name ?? ''
          break
        case 'status':
          vA = getLatestStatus(a) ?? ''
          vB = getLatestStatus(b) ?? ''
          break
        case 'asset':
          vA = a.equipments_FK[0]?.name ?? ''
          vB = b.equipments_FK[0]?.name ?? ''
          break
      }

      // se for data, converter para timestamp, senão usar localeCompare
      if (sortColumn.value === 'date') {
        const dA = new Date(vA).getTime()
        const dB = new Date(vB).getTime()
        return (dA - dB) * sortDirection.value
      } else {
        return String(vA).localeCompare(String(vB)) * sortDirection.value
      }
    })
  }

  return result
})

// --- Formatação Visual ---
const getStatusClass = (status: TaskStatusValue | null | undefined): string => {
  if (!status) return 'status-none'
  const statusMap: Record<TaskStatusValue, string> = {
    OPEN: 'status-aberto',
    WAITING_RESPONSIBLE: 'status-andamento',
    ONGOING: 'status-andamento',
    DONE: 'status-concluido',
    FINISHED: 'status-concluido',
    CANCELLED: 'status-cancelado',
  }
  return statusMap[status] || 'status-none'
}

const formatStatus = (status: TaskStatusValue | null | undefined): string => {
  if (!status) return 'Status não informado'
  const statusMap: Record<TaskStatusValue, string> = {
    OPEN: 'Aberto',
    WAITING_RESPONSIBLE: 'Aguardando Responsável',
    ONGOING: 'Em Andamento',
    DONE: 'Feito',
    FINISHED: 'Finalizado',
    CANCELLED: 'Cancelado',
  }
  return statusMap[status] || status.replace(/_/g, ' ')
}

// Função de Logout
async function handleLogout() {
  if (window.confirm('Tem certeza que deseja sair?')) {
    try {
      await api.logout()
    } catch (error) {
      console.error('Erro no logout da API, deslogando localmente:', error)
    } finally {
      clearToken()
      router.push({ name: 'login' })
    }
  }
}

// --- LÓGICA DO MODAL ---
function openStatusUpdateModal(task: Task, event: Event) {
  const target = event.target as HTMLSelectElement
  const newStatus = target.value as TaskStatusValue // --- CORREÇÃO DE TIPO ---

  // Reseta visualmente para o valor antigo (o modal confirmará a troca)
  target.value = getLatestStatus(task) || ''

  taskToUpdate.value = task
  newStatusToSet.value = newStatus
  statusUpdateComment.value = ''
  statusUpdateImage.value = null
  statusUpdateImageName.value = ''
  showStatusModal.value = true
}

function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    statusUpdateImage.value = target.files[0]
    statusUpdateImageName.value = target.files[0].name
  } else {
    statusUpdateImage.value = null
    statusUpdateImageName.value = ''
  }
}

async function handleSubmitStatusUpdate() {
  if (!taskToUpdate.value || !newStatusToSet.value) return

  const loggedInUserId = user.value?.id
  if (!loggedInUserId) {
    alert('Erro: Usuário não identificado. Faça login novamente.')
    return
  }

  try {
    const statusPayload = {
      task_FK: taskToUpdate.value.id,
      status: newStatusToSet.value,
      comment: statusUpdateComment.value,
      user_FK: loggedInUserId,
    }
    const newStatusResponse = await api.createTaskStatus(statusPayload)
    const newStatusId = newStatusResponse.data.id
    if (statusUpdateImage.value) {
      const imagePayload = new FormData()
      imagePayload.append('image', statusUpdateImage.value)
      imagePayload.append('task_status_FK', newStatusId.toString())
      await api.uploadTaskStatusImage(imagePayload)
    }
    alert(`Status do chamado #${taskToUpdate.value.id} alterado com sucesso!`)
    showStatusModal.value = false
    fetchTasks()
  } catch (error) {
    console.error('Falha ao atualizar o status:', error)
    alert('Não foi possível atualizar o status.')
  }
}

function cancelStatusUpdate() {
  showStatusModal.value = false
  fetchTasks()
}
</script>

<template>
  <div class="app-layout">
    <header class="header">
      <div class="header-left">
        <div class="brand-logo">MANGE_TECH</div>
        <nav class="nav-links">
          <router-link to="/" class="nav-item active">Dashboard</router-link>
          <router-link to="/equipments" class="nav-item">Ativos</router-link>
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
            <img src="../assets/user.png" alt="Avatar" class="user-avatar" />
          </div>
          <button @click="handleLogout" class="logout-btn" title="Sair">
            <i class="fas fa-sign-out-alt"></i>
          </button>
        </div>
      </div>
    </header>

    <main class="main-container">
      <div class="content-wrapper">
        <div class="page-header">
          <div class="page-title-group">
            <h1>Dashboard</h1>
            <p>Visão geral dos chamados</p>
          </div>
          <router-link to="/task/new" class="primary-btn">
            <i class="fas fa-plus"></i> Novo Chamado
          </router-link>
        </div>

        <div class="toolbar">
          <div class="filters">
            <button
              class="filter-button"
              :class="{ active: sortColumn === 'date' }"
              @click="handleSort('date')"
            >
              Data
              <i
                class="fas"
                :class="
                  sortColumn === 'date' && sortDirection === 1 ? 'fa-chevron-up' : 'fa-chevron-down'
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
              :class="{ active: sortColumn === 'status' }"
              @click="handleSort('status')"
            >
              Status
              <i
                class="fas"
                :class="
                  sortColumn === 'status' && sortDirection === 1
                    ? 'fa-chevron-up'
                    : 'fa-chevron-down'
                "
              ></i>
            </button>

            <button
              class="filter-button"
              :class="{ active: sortColumn === 'asset' }"
              @click="handleSort('asset')"
            >
              Ativo
              <i
                class="fas"
                :class="
                  sortColumn === 'asset' && sortDirection === 1
                    ? 'fa-chevron-up'
                    : 'fa-chevron-down'
                "
              ></i>
            </button>
          </div>

          <div class="search-group">
            <i class="fas fa-search"></i>
            <input v-model="searchQuery" type="text" placeholder="Filtrar chamados..." />
          </div>
        </div>

        <div class="data-view">
          <div v-if="loading" class="state-message">
            <div class="spinner"></div>
            Carregando chamados...
          </div>
          <div v-else-if="error" class="state-message error">{{ error }}</div>

          <div v-else class="table-responsive">
            <table class="custom-table">
              <thead>
                <tr>
                  <th width="10%">Chamado</th>
                  <th width="15%">Data</th>
                  <th width="15%">Status</th>
                  <th width="15%" class="hide-mobile">Ambiente</th>
                  <th width="15%" class="hide-mobile">Ativo</th>
                  <th width="15%" class="hide-mobile">Responsável</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="task in filteredTasks" :key="task.id">
                  <td data-label="Chamado">
                    <router-link :to="`/task/${task.id}`" class="id-link">
                      #{{ task.id }}
                    </router-link>
                    <div class="mobile-task-name">{{ task.name }}</div>
                  </td>

                  <td data-label="Data">
                    {{ getLatestStatusDate(task) ? new Date(getLatestStatusDate(task)!).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '--/--/--' }}
                  </td>

                  <td data-label="Status">
                    <div class="select-wrapper">
                      <select
                        :value="getLatestStatus(task)"
                        @change="openStatusUpdateModal(task, $event)"
                        class="status-badge-select"
                        :class="getStatusClass(getLatestStatus(task))"
                      >
                        <option :value="null" disabled>Selecione</option>
                        <option value="OPEN">Aberto</option>
                        <option value="WAITING_RESPONSIBLE">Aguardando</option>
                        <option value="ONGOING">Em Andamento</option>
                        <option value="DONE">Feito</option>
                        <option value="FINISHED">Finalizado</option>
                        <option value="CANCELLED">Cancelado</option>
                      </select>
                    </div>
                  </td>

                  <td class="hide-mobile">
                    {{ task.equipments_FK[0]?.environment_FK?.name || '-' }}
                  </td>
                  <td class="hide-mobile">{{ task.equipments_FK[0]?.name || '-' }}</td>
                  <td class="hide-mobile">
                    <div class="avatar-group">
                      <div class="avatar-circle">
                        {{ task.responsibles_FK[0]?.name?.charAt(0) || '?' }}
                      </div>
                      <span>{{ task.responsibles_FK[0]?.name || 'Não atribuído' }}</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>

    <Transition name="fade">
      <div v-if="showStatusModal" class="modal-backdrop" @click.self="cancelStatusUpdate">
        <div class="modal-panel">
          <div class="modal-header">
            <h3>Atualizar Status #{{ taskToUpdate?.id }}</h3>
            <button @click="cancelStatusUpdate" class="close-btn">&times;</button>
          </div>

          <div class="modal-body">
            <p class="status-target">
              Novo Status:
              <span :class="getStatusClass(newStatusToSet)" class="status-pill">{{
                formatStatus(newStatusToSet)
              }}</span>
            </p>

            <form @submit.prevent="handleSubmitStatusUpdate">
              <div class="input-group">
                <label>Comentário (Obrigatório)</label>
                <textarea
                  v-model="statusUpdateComment"
                  rows="4"
                  placeholder="Descreva o motivo da alteração..."
                  required
                ></textarea>
              </div>

              <div class="input-group">
                <label>Evidência (Opcional)</label>
                <div class="file-upload">
                  <input type="file" id="file" @change="onFileSelected" accept="image/*" />
                  <label for="file" class="file-label">
                    <i class="fas fa-cloud-upload-alt"></i>
                    <span>{{ statusUpdateImageName || 'Escolher imagem...' }}</span>
                  </label>
                </div>
              </div>

              <div class="modal-footer">
                <button type="button" @click="cancelStatusUpdate" class="btn-secondary">
                  Cancelar
                </button>
                <button type="submit" class="btn-primary">Salvar</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* --- DESIGN SYSTEM & RESET --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  /* Cores Neutras */
  --bg-app: #f3f4f6; /* Cinza muito claro para fundo */
  --bg-panel: #ffffff; /* Branco para cards */
  --border: #e5e7eb; /* Cinza claro para bordas */
  --text-main: #111827; /* Quase preto */
  --text-muted: #6b7280; /* Cinza médio */

  /* Cores de Ação */
  --primary: #2563eb; /* Azul vibrante */
  --primary-hover: #1d4ed8;
  --danger: #ef4444;

  /* Cores de Status (Badges) */
  --st-open-bg: #dbeafe;
  --st-open-tx: #1e40af;
  --st-wait-bg: #fef3c7;
  --st-wait-tx: #92400e;
  --st-prog-bg: #fef9c3;
  --st-prog-tx: #854d0e; /* Amarelo mais suave */
  --st-done-bg: #d1fae5;
  --st-done-tx: #065f46;
  --st-canc-bg: #f3f4f6;
  --st-canc-tx: #4b5563;
}

* {
  box-sizing: border-box;
}

.app-layout {
  background-color: var(--bg-app);
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  color: var(--text-main);
  display: flex;
  flex-direction: column;
}

/* --- HEADER --- */
.header {
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  padding: 0 2rem;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  display: flex;
  gap: 1.5rem;
}
.nav-item {
  text-decoration: none;
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.9rem;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.nav-item:hover,
.nav-item.router-link-active {
  color: var(--text-main);
  border-bottom-color: var(--text-main);
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
  border-left: 1px solid var(--border);
  padding-left: 1rem;
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

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  display: none;
}
@media (min-width: 768px) {
  .user-name {
    display: block;
  }
}
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border);
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

/* --- MAIN CONTENT --- */
.main-container {
  flex: 1;
  padding: 2rem;
}
.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

/* Headers & Titles */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}
@media (min-width: 640px) {
  .page-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.page-title-group h1 {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
}
.page-title-group p {
  color: var(--text-muted);
  margin: 0.25rem 0 0 0;
  font-size: 0.95rem;
}

.primary-btn {
  background-color: #38e07b;
  color: #0e1a13;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
}
.primary-btn:hover {
  background: var(--primary-hover);
}

/* TOOLBAR */
.toolbar {
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

@media (min-width: 768px) {
  .toolbar {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.filter-button {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: 0.2s;
}
.filter-button.active {
  border-color: var(--primary);
  color: var(--primary);
  background-color: #f0f9ff;
}

.search-group {
  position: relative;
  width: 100%;
}
@media (min-width: 768px) {
  .search-group {
    width: 300px;
  }
}
.search-group i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}
.search-group input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border 0.2s;
}
.search-group input:focus {
  outline: none;
  border-color: var(--primary);
}

/* --- DATA VIEW (Table/Cards) --- */
.data-view {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden; /* Arredonda cantos da tabela */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.state-message {
  padding: 3rem;
  text-align: center;
  color: var(--text-muted);
}
.spinner {
  /* Spinner simples CSS */
  border: 3px solid rgba(0, 0, 0, 0.1);
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

/* Tabela Responsiva */
.table-responsive {
  width: 100%;
  overflow-x: auto;
}
.custom-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  white-space: nowrap;
}

.custom-table th {
  background: #f9fafb;
  padding: 1rem 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border);
}

.custom-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
  color: var(--text-main);
  font-size: 0.9rem;
}
.custom-table tr:last-child td {
  border-bottom: none;
}
.custom-table tr:hover {
  background: #f9fafb;
}

/* Links e Texto */
.id-link {
  font-weight: 600;
  color: var(--text-main);
  text-decoration: none;
}
.id-link:hover {
  color: var(--primary);
  text-decoration: underline;
}
.mobile-task-name {
  display: none;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Avatar Group */
.avatar-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.avatar-circle {
  width: 28px;
  height: 28px;
  background: #e0e7ff;
  color: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.8rem;
}

/* Status Select (Styled as Badge) */
.select-wrapper {
  position: relative;
  display: inline-block;
}
.status-badge-select {
  appearance: none;
  border: none;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 99px;
  cursor: pointer;
  text-align: center;
  width: 100%;
  min-width: 110px;
  transition: opacity 0.2s;
}
.status-badge-select:hover {
  opacity: 0.9;
}
.status-badge-select:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

/* Cores dos Status */
.status-aberto {
  background: var(--st-open-bg);
  color: var(--st-open-tx);
}
.status-andamento {
  background: var(--st-prog-bg);
  color: var(--st-prog-tx);
}
.status-concluido {
  background: var(--st-done-bg);
  color: var(--st-done-tx);
}
.status-cancelado,
.status-none {
  background: var(--st-canc-bg);
  color: var(--st-canc-tx);
}

/* --- RESPONSIVIDADE AVANÇADA (MOBILE VIEW) --- */
@media (max-width: 768px) {
  .header {
    padding: 0 1rem;
  }
  .nav-links {
    display: none;
  } /* Menu hamburger seria ideal aqui futuramente */

  .hide-mobile {
    display: none;
  }

  /* Ajustes na tabela para mobile */
  .mobile-task-name {
    display: block; /* Mostra nome embaixo do ID */
  }
  .custom-table th {
    display: none; /* Esconde cabeçalho em mobile */
  }

  .custom-table tr {
    display: grid;
    grid-template-columns: 1fr auto; /* Duas colunas: ID+Nome | Status */
    gap: 0.5rem;
    padding: 1rem;
    border-bottom: 1px solid var(--border);
    align-items: center;
  }

  .custom-table td {
    border: none;
    padding: 0;
    display: block;
  }

  /* Célula do Status vai para a direita */
  .custom-table td[data-label='Status'] {
    grid-column: 2;
    grid-row: 1 / span 2; /* Ocupa altura */
    text-align: right;
  }

  /* Célula da Data */
  .custom-table td[data-label='Data'] {
    grid-column: 1;
    font-size: 0.8rem;
    color: var(--text-muted);
  }
}

/* --- MODAL --- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-panel {
  background: white;
  width: 100%;
  max-width: 480px;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}
@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-muted);
}

.modal-body {
  padding: 1.5rem;
}
.status-target {
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  color: var(--text-muted);
}
.status-pill {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.85rem;
  margin-left: 0.5rem;
}

.input-group {
  margin-bottom: 1.25rem;
}
.input-group label {
  display: block;
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}
.input-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-family: inherit;
  resize: vertical;
}
.input-group textarea:focus {
  outline: 2px solid var(--primary);
  border-color: transparent;
}

.file-upload input {
  display: none;
}
.file-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px dashed var(--border);
  border-radius: 8px;
  cursor: pointer;
  color: var(--primary);
  font-weight: 500;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.file-label:hover {
  background: #f0f9ff;
  border-color: var(--primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
}
.btn-secondary {
  background: white;
  border: 1px solid var(--border);
  padding: 0.6rem 1.25rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  color: var(--text-main);
}
.btn-secondary:hover {
  background: var(--bg-app);
}
.btn-primary {
  background: #38e07b;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  color: white;
}
.btn-primary:hover {
  background: var(--primary-hover);
}
</style>