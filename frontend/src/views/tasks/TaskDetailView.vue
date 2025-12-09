<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'
import type { Task, TaskStatus, TaskStatusValue } from '../../types/api'
import { useAuth } from '../../stores/auth'

const route = useRoute()
const router = useRouter()
const taskId = Number(route.params.id)

const task = ref<Task | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const { user } = useAuth()

// --- Helpers de Formatação ---

const formatStatus = (status: TaskStatusValue | null | undefined): string => {
  if (!status) {
    return 'Status não informado'
  }
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

const getStatusClass = (status: TaskStatusValue | null | undefined): string => {
  if (!status) return 'badge-gray'
  const map: Record<TaskStatusValue, string> = {
    OPEN: 'badge-blue',
    WAITING_RESPONSIBLE: 'badge-orange',
    ONGOING: 'badge-yellow',
    DONE: 'badge-green',
    FINISHED: 'badge-green',
    CANCELLED: 'badge-red',
  }
  return map[status] || 'badge-gray'
}

const creationDateText = computed(() => {
  if (!task.value) return ''
  const date = new Date(task.value.creation_date)
  return `Criado em ${date.toLocaleDateString('pt-BR')} às ${date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })}`
})

const formatTimelineDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// --- Lógica de Dados ---

onMounted(async () => {
  if (!taskId) {
    error.value = 'ID inválido.'
    loading.value = false
    return
  }
  try {
    const response = await api.getTask(taskId)
    task.value = response.data

    if (task.value?.status_history?.length) {
      task.value.status_history.sort(
        (a, b) => new Date(b.status_date).getTime() - new Date(a.status_date).getTime()
      )
    } else if (task.value) {
      task.value.status_history = []
    }
  } catch (err) {
    console.error('Erro:', err)
    error.value = 'Erro ao carregar detalhes.'
  } finally {
    loading.value = false
  }
})

const hasHistory = computed(
  () => task.value && task.value.status_history && task.value.status_history.length > 0
)

const currentStatus = computed<TaskStatus | null>(() => {
  if (hasHistory.value) return task.value!.status_history[0]
  return null
})

const timelineHistory = computed(() => {
  if (!hasHistory.value) return []
  return task.value!.status_history
})

const comments = computed(() => {
  if (!hasHistory.value) return []
  return task.value!.status_history.filter((s) => s.comment && s.comment.trim() !== '')
})

// --- Ações ---

async function handleDelete() {
  if (!task.value) return
  if (window.confirm(`Deseja excluir o chamado #${task.value.id}?`)) {
    try {
      await api.deleteTask(task.value.id)
      alert('Excluído com sucesso!')
      router.push('/')
    } catch (err) {
      if (err.response && err.response.status === 403) {
        alert('Você não tem permissão para excluir este chamado.')
      } else {
        console.error('Erro ao excluir:', err)
        a
        alert('Erro ao excluir.')
      }
    }
  }
}

async function handleLogout() {
  if (window.confirm('Sair do sistema?')) {
    try {
      await api.logout()
    } catch (e) {
      /* ignore */
    }
    router.push({ name: 'login' })
  }
}

// --- UI Helpers ---
const equipmentName = computed(() => task.value?.equipments_FK[0]?.name || '-')
const locationText = computed(() => task.value?.equipments_FK[0]?.environment_FK?.name || '-')
const priorityText = computed(() => task.value?.urgency_level || 'Normal')
const descriptionText = computed(() => task.value?.description || 'Sem descrição.')
</script>

<template>
  <div class="app-container">
    <header class="header">
      <div class="header-left">
        <div class="brand-logo">MANGE_TECH</div>
        <nav class="nav-links">
          <router-link to="/" class="nav-item">Dashboard</router-link>
          <a class="nav-item active">Chamado</a>
          <router-link to="/equipments" class="nav-item">Ativos</router-link>
          <router-link to="/reports" class="nav-item">Relatórios</router-link>
          
        </nav>
      </div>

      <div class="header-right">
        <div class="user-display" v-if="user">
          <span class="user-name">{{ user.name }}</span>
          <img src="../../assets/user.png" alt="Avatar" class="user-avatar" />
        </div>
        <button @click="handleLogout" class="logout-btn" title="Sair">
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
    </header>

    <main class="main-content">
      <div v-if="loading" class="state-msg"><div class="spinner"></div></div>
      <div v-if="error" class="state-msg error">{{ error }}</div>

      <div v-if="task" class="content-wrapper">
        <div class="page-heading">
          <div class="breadcrumb">
            <router-link to="/" class="bc-link">Dashboard</router-link>
            <i class="fas fa-chevron-right bc-sep"></i>
            <span class="bc-current">#{{ task.id }}</span>
          </div>
          <div class="title-wrapper">
            <h1 class="page-title">{{ task.name || `Chamado #${task.id}` }}</h1>
            <span class="meta-date">{{ creationDateText }}</span>
          </div>
        </div>

        <div class="grid-layout">
          <div class="left-column">
            <section class="info-block">
              <h2 class="block-title">Status Atual</h2>
              <div class="status-display-card">
                <div v-if="currentStatus" class="status-content">
                  <div class="status-badge-wrapper">
                    <span class="status-badge-lg" :class="getStatusClass(currentStatus.status)">
                      {{ formatStatus(currentStatus.status) }}
                    </span>
                  </div>
                  <div class="status-meta">
                    <span class="meta-item"
                      ><i class="far fa-clock"></i> Atualizado em
                      {{ formatTimelineDate(currentStatus.status_date) }}</span
                    >
                    <span class="meta-item" v-if="currentStatus.user_detail">
                      <i class="far fa-user"></i> por
                      <strong>{{ currentStatus.user_detail.name }}</strong>
                    </span>
                  </div>
                </div>
                <div v-else class="empty-state">Sem status definido.</div>
              </div>
            </section>

            <section class="info-block">
              <h2 class="block-title">Histórico de Atualizações</h2>

              <div v-if="hasHistory" class="timeline">
                <div v-for="status in timelineHistory" :key="status.id" class="timeline-item">
                  <div class="timeline-connector"></div>
                  <div class="timeline-marker" :class="getStatusClass(status.status)">
                    {{ formatStatus(status.status).charAt(0) }}
                  </div>
                  <div class="timeline-content">
                    <div class="tl-header">
                      <h3 class="tl-title">{{ formatStatus(status.status) }}</h3>
                      <span class="tl-date">{{ formatTimelineDate(status.status_date) }}</span>
                    </div>

                    <p class="tl-author" v-if="status.user_detail">
                      Atualizado por {{ status.user_detail.name }}
                    </p>

                    <div v-if="status.images && status.images.length > 0" class="tl-attachments">
                      <div v-for="img in status.images" :key="img.id" class="image-hover-wrapper">
                        <span class="attachment-link">
                          <i class="fas fa-paperclip"></i> Visualizar anexo
                        </span>
                        <div class="popover-image">
                          <img
                            :src="
                              img.image.startsWith('http')
                                ? img.image
                                : `http://localhost:8000${img.image}`
                            "
                            alt="Evidência"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-text">Nenhum histórico registrado.</div>
            </section>
          </div>

          <div class="right-column">
            <div class="sidebar-card action-card-container">
              <div class="action-buttons">
                <router-link :to="`/task/edit/${task.id}`" class="btn btn-outline-primary">
                  Editar Chamado
                </router-link>
                <button @click="handleDelete" class="btn btn-outline-danger">Excluir</button>
              </div>
            </div>

            <div class="sidebar-card">
              <h3 class="sidebar-title">Detalhes do Chamado</h3>
              <div class="detail-list">
                <div class="detail-row">
                  <span class="dt-label">Equipamento</span>
                  <span class="dt-value">{{ equipmentName }}</span>
                </div>
                <div class="detail-row">
                  <span class="dt-label">Localização</span>
                  <span class="dt-value">{{ locationText }}</span>
                </div>
                <div class="detail-row">
                  <span class="dt-label">Prioridade</span>
                  <span class="dt-value priority-tag">{{ priorityText }}</span>
                </div>
                <div class="detail-row description">
                  <span class="dt-label">Descrição</span>
                  <p class="dt-desc">{{ descriptionText }}</p>
                </div>
              </div>
            </div>

            <div class="sidebar-card">
              <h3 class="sidebar-title">Comentários</h3>
              <div v-if="comments.length > 0" class="comments-list">
                <div v-for="comment in comments" :key="comment.id" class="comment-block">
                  <div class="cb-header">
                    <span class="cb-author">{{ comment.user_detail?.name || 'Usuário' }}</span>
                    <span class="cb-date">{{
                      new Date(comment.status_date).toLocaleDateString()
                    }}</span>
                  </div>
                  <p class="cb-text">{{ comment.comment }}</p>
                </div>
              </div>
              <div v-else class="empty-text-small">Nenhum comentário disponível.</div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
  box-sizing: border-box;
}

/* DEFINIÇÃO DE CORES DENTRO DO CONTAINER PARA GARANTIR APLICAÇÃO */
.app-container {
  --bg-app: #fafbfc;
  --bg-panel: #ffffff;
  --border: #e1e4e8;
  --text-main: #24292e;
  --text-muted: #586069;
  --primary: #0366d6;
  --danger: #cb2431;

  /* Cor de Destaque (Verde/Teal do protótipo) */
  --accent-green: #10b981;

  /* Badge Colors (Fundo e Texto) */
  --badge-blue-bg: #eff6ff;
  --badge-blue-tx: #1d4ed8;
  --badge-green-bg: #ecfdf5;
  --badge-green-tx: #047857;
  --badge-yellow-bg: #fffbeb;
  --badge-yellow-tx: #b45309;
  --badge-orange-bg: #fff7ed;
  --badge-orange-tx: #c2410c;
  --badge-gray-bg: #f3f4f6;
  --badge-gray-tx: #374151;

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
  height: 64px;
  padding: 0 2rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  /* position: sticky removido para não acompanhar o scroll */
  position: relative;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 2.5rem;
}
.brand-logo {
  font-weight: 800;
  font-size: 1.2rem;
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
  transition: 0.2s;
}
.nav-item:hover,
.nav-item.active {
  color: var(--text-main);
  border-bottom: 2px solid var(--text-main);
  padding-bottom: 19px;
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
.user-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.user-name {
  font-weight: 600;
  font-size: 0.9rem;
}
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--border);
}
.logout-btn {
  background: none;
  border: none;
  color: black;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.logout-btn:hover {
  opacity: 1;
}

/* MAIN */
.main-content {
  flex: 1;
  padding: 2rem;
}
.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}
.state-msg {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}
.spinner {
  border: 2px solid #e1e4e8;
  border-top-color: var(--accent-green);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* PAGE HEADING */
.page-heading {
  margin-bottom: 2.5rem;
}
.breadcrumb {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.bc-link {
  color: var(--accent-green);
  text-decoration: none;
}
.bc-link:hover {
  text-decoration: underline;
}
.bc-sep {
  font-size: 0.6rem;
}
.title-wrapper {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  flex-wrap: wrap;
}
.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
}
.meta-date {
  font-size: 0.9rem;
  color: var(--text-muted);
}

/* GRID */
.grid-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
}
@media (min-width: 1024px) {
  .grid-layout {
    grid-template-columns: 2fr 1fr;
  }
}

/* CARDS GERAIS */
.info-block {
  margin-bottom: 3rem;
}
.block-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 1.5rem 0;
}

/* STATUS ATUAL (CARD) */
.status-display-card {
  padding: 0;
}
.status-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.status-badge-lg {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 1rem;
}
.status-meta {
  font-size: 0.9rem;
  color: var(--text-muted);
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

/* TIMELINE */
.timeline {
  position: relative;
  padding-left: 1rem;
  margin-top: 1rem;
}
.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 23px;
  width: 2px;
  background: #e1e4e8;
  z-index: 0;
}
.timeline-item {
  position: relative;
  margin-bottom: 3rem;
  padding-left: 3.5rem;
  z-index: 1;
}
.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: 8px;
  top: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  background: var(--bg-panel);
  border: 2px solid var(--border);
  box-shadow: 0 0 0 4px var(--bg-app);
}

/* Cores dos Badges */
.badge-blue,
.timeline-marker.badge-blue {
  background: var(--badge-blue-bg);
  color: var(--badge-blue-tx);
  border-color: var(--badge-blue-bg);
}
.badge-green,
.timeline-marker.badge-green {
  background: var(--badge-green-bg);
  color: var(--badge-green-tx);
  border-color: var(--badge-green-bg);
}
.badge-yellow,
.timeline-marker.badge-yellow {
  background: var(--badge-yellow-bg);
  color: var(--badge-yellow-tx);
  border-color: var(--badge-yellow-bg);
}
.badge-orange,
.timeline-marker.badge-orange {
  background: var(--badge-orange-bg);
  color: var(--badge-orange-tx);
  border-color: var(--badge-orange-bg);
}
.badge-red,
.timeline-marker.badge-red {
  background: #fee2e2;
  color: #991b1b;
  border-color: #fee2e2;
}
.badge-gray,
.timeline-marker.badge-gray {
  background: var(--badge-gray-bg);
  color: var(--badge-gray-tx);
}

.tl-header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 0.2rem;
}
.tl-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-main);
}
.tl-date {
  font-size: 0.85rem;
  color: var(--accent-green);
}
.tl-author {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0;
}

.tl-attachments {
  margin-top: 0.8rem;
}
.attachment-link {
  font-size: 0.85rem;
  color: var(--text-main);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 500;
}
.attachment-link:hover {
  color: var(--accent-green);
  text-decoration: underline;
}
.popover-image {
  display: none;
  position: absolute;
  bottom: 100%;
  left: 0;
  background: white;
  padding: 0.5rem;
  border: 1px solid var(--border);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 50;
  width: 250px;
  border-radius: 8px;
}
.popover-image img {
  width: 100%;
  display: block;
  border-radius: 4px;
}
.image-hover-wrapper:hover .popover-image {
  display: block;
}

/* --- DIREITA (SIDEBAR) --- */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.sidebar-actions {
  display: flex;
  gap: 1rem;
}
.btn {
  flex: 1;
  padding: 0.7rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-panel);
  font-weight: 600;
  font-size: 0.9rem;
  text-align: center;
  text-decoration: none;
  color: var(--text-main);
  cursor: pointer;
  transition: 0.2s;
}
.btn-outline-primary:hover {
  border-color: var(--text-main);
}
.btn-outline-danger:hover {
  border-color: #ef4444;
  color: #ef4444;
}

/* SIDEBAR SECTIONS */
.sidebar-section {
  margin-bottom: 1rem;
}
.sidebar-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 1.5rem 0;
  color: var(--text-main);
}

/* Cards da Sidebar (Com bordas) */
.sidebar-card {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}
.action-card-container {
  padding: 1rem; /* Padding menor para os botões */
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.detail-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}
.detail-row:last-child {
  border-bottom: none;
}
.detail-row.description {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dt-label {
  color: var(--accent-green);
  font-weight: 500;
  font-size: 0.9rem;
}
.dt-value {
  color: var(--text-main);
  font-weight: 500;
  font-size: 0.95rem;
  text-align: right;
}
.dt-desc {
  text-align: left;
  line-height: 1.6;
  color: var(--text-main);
  font-size: 0.95rem;
}

/* COMENTÁRIOS */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.comment-block {
  position: relative;
}
.cb-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}
.cb-author {
  font-weight: 700;
  color: var(--text-main);
  font-size: 0.95rem;
}
.cb-date {
  color: var(--accent-green);
  font-size: 0.85rem;
}
.cb-text {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-muted);
  margin: 0;
}

.empty-text,
.empty-text-small {
  font-style: italic;
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* RESPONSIVIDADE */
@media (max-width: 768px) {
  .header-nav {
    display: none;
  }
  .grid-layout {
    grid-template-columns: 1fr;
  }
  .timeline-marker {
    left: 5px;
    width: 24px;
    height: 24px;
    font-size: 0.8rem;
  }
  .timeline::before {
    left: 16px;
  }
  .timeline-item {
    padding-left: 3rem;
  }
  .detail-row {
    grid-template-columns: 1fr;
    gap: 0.2rem;
  }
  .dt-value {
    text-align: left;
  }
}
</style>