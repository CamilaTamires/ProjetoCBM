<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../stores/auth'
import api from '../../services/api'
import type { Task } from '../../types/api'

// --- Estado ---
const loading = ref(true)
const error = ref<string | null>(null)
const tasks = ref<Task[]>([])
const router = useRouter()
const { user, clearToken } = useAuth()

// --- Funções ---
async function fetchData() {
  try {
    const response = await api.getTasks()
    tasks.value = response.data
    // Debug para verificar no console se os status estão vindo corretamente
    console.log('Exemplo de histórico:', tasks.value[0]?.status_history)
  } catch (err) {
    console.error('Erro ao carregar dados:', err)
    error.value = 'Não foi possível carregar os dados do relatório.'
  } finally {
    loading.value = false
  }
}

// --- Função Auxiliar Inteligente ---
// Descobre qual é o status ATUAL baseado no histórico
function getCurrentStatus(task: Task): string {
  // Se não tem histórico, assumimos OPEN por segurança
  if (!task.status_history || task.status_history.length === 0) {
    return 'OPEN';
  }
  
  // Pega o ÚLTIMO item do array (o mais recente adicionado no banco)
  const lastStatusObj = task.status_history[task.status_history.length - 1];
  return lastStatusObj.status;
}

// --- Métricas Reais ---

const totalChamados = computed(() => tasks.value.length)

// Filtra chamados abertos (Tudo que NÃO for finalizado ou cancelado)
const chamadosAbertos = computed(() =>
  tasks.value.filter((t) => {
    const currentStatus = getCurrentStatus(t);
    // Lista de status que consideram o chamado como encerrado
    const closedStatuses = ['DONE', 'FINISHED', 'CANCELLED'];
    return !closedStatuses.includes(currentStatus);
  }).length
)

// Filtra chamados concluídos (DONE ou FINISHED)
const chamadosConcluidos = computed(() =>
  tasks.value.filter((t) => {
    const currentStatus = getCurrentStatus(t);
    return ['DONE', 'FINISHED'].includes(currentStatus);
  }).length
)

// Filtra chamados cancelados (CANCELLED)
const chamadosCancelados = computed(() =>
  tasks.value.filter((t) => {
    const currentStatus = getCurrentStatus(t);
    return currentStatus === 'CANCELLED';
  }).length
)

// Agrupamento por Urgência
const porUrgencia = computed(() => {
  const counts = { HIGH: 0, MEDIUM: 0, LOW: 0 } // Se tiver EXTRA_HIGH no front, adicione aqui
  tasks.value.forEach((t) => {
    // Garante que a urgência venha em uppercase para bater com a chave
    const urgency = (t.urgency_level || 'LOW').toUpperCase() as 'HIGH' | 'MEDIUM' | 'LOW';
    
    if (counts[urgency] !== undefined) {
      counts[urgency]++
    }
  })
  
  return [
    { label: 'Alta', value: counts.HIGH, class: 'high' },
    { label: 'Média', value: counts.MEDIUM, class: 'medium' },
    { label: 'Baixa', value: counts.LOW, class: 'low' },
  ]
})

// Lista de Chamados Recentes
const chamadosRecentes = computed(() => {
  return [...tasks.value]
    .sort((a, b) => new Date(b.creation_date).getTime() - new Date(a.creation_date).getTime())
    .slice(0, 5)
})

// --- Ações ---
async function handleLogout() {
  if (window.confirm('Tem certeza que deseja sair?')) {
    try {
      await api.logout()
    } catch (e) { } 
    finally {
      clearToken()
      router.push({ name: 'login' })
    }
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="app-layout">
    <!-- NOVO HEADER APLICADO -->
    <header class="header">
      <div class="header-left">
        <div class="brand-logo">MANGE_TECH</div>
        <nav class="nav-links">
          <router-link to="/" class="nav-item">Dashboard</router-link>
          <router-link to="/equipments" class="nav-item">Ativos</router-link>
          <router-link to="/reports" class="nav-item active">Relatórios</router-link>
        </nav>
      </div>

      <div class="header-right">
        <div class="user-menu">
          <div class="user-info" v-if="user">
            <span class="user-name">{{ user.name }}</span>
            <img src="../../assets/user.png" alt="Avatar" class="user-avatar" />
          </div>
          <button @click="handleLogout" class="logout-btn" title="Sair">
            <i class="fas fa-sign-out-alt"></i>
          </button>
        </div>
      </div>
    </header>
    <!-- FIM DO NOVO HEADER -->

    <main class="main-content">
      <div class="content-wrapper">
        <div class="page-header">
          <h1 class="title">Relatórios Gerais</h1>
          <p class="subtitle">Resumo consolidado dos chamados registrados no sistema.</p>
        </div>

        <div v-if="loading" class="loading-state">Calculando métricas...</div>
        <div v-else-if="error" class="error-message">{{ error }}</div>

        <div v-else class="reports-grid">
          <!-- KPIs (Indicadores Chave - Dados 100% Reais) -->
          <section class="kpi-row">
            <div class="kpi-card total">
              <span class="kpi-label">Total de Chamados</span>
              <span class="kpi-value">{{ totalChamados }}</span>
            </div>
            <div class="kpi-card open">
              <span class="kpi-label">Em Aberto / Andamento</span>
              <span class="kpi-value">{{ chamadosAbertos }}</span>
            </div>
            <div class="kpi-card done">
              <span class="kpi-label">Concluídos</span>
              <span class="kpi-value">{{ chamadosConcluidos }}</span>
            </div>
            <div class="kpi-card cancelled">
              <span class="kpi-label">Cancelados</span>
              <span class="kpi-value">{{ chamadosCancelados }}</span>
            </div>
          </section>

          <div class="split-section">
            <!-- Tabela de Urgência (Dados Reais Agrupados) -->
            <div class="report-card">
              <h3>Chamados por Prioridade</h3>
              <div class="urgency-list">
                <div v-for="item in porUrgencia" :key="item.label" class="urgency-item">
                  <div class="urgency-info">
                    <span class="urgency-label">{{ item.label }}</span>
                    <span class="urgency-count">{{ item.value }}</span>
                  </div>
                  <!-- Barra de progresso visual simples baseada no total -->
                  <div class="progress-bg">
                    <div
                      class="progress-fill"
                      :class="item.class"
                      :style="{
                        width: totalChamados > 0 ? (item.value / totalChamados) * 100 + '%' : '0%'
                      }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Lista de Recentes (Dados Reais) -->
            <div class="report-card">
              <h3>Últimos Chamados Registrados</h3>
              <div class="recent-list">
                <div v-for="task in chamadosRecentes" :key="task.id" class="recent-item">
                  <div class="recent-header">
                    <span class="recent-id">#{{ task.id }}</span>
                    <span class="recent-date">{{
                      new Date(task.creation_date).toLocaleDateString()
                    }}</span>
                  </div>
                  <p class="recent-title">{{ task.name }}</p>
                  <small class="recent-author"
                    >Solicitado por: {{ task.creator_FK?.name || 'Desconhecido' }}</small
                  >
                </div>
                <div v-if="chamadosRecentes.length === 0" class="empty-text">
                  Nenhum chamado registrado.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

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
  gap: 1rem;
}

/* CORREÇÃO APLICADA AQUI */
.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem; /* Adicionado para alinhar user-info e logout-btn */
}
/* FIM DA CORREÇÃO */

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

/* Estilos do novo header */
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

.icon-btn:hover:not(.disabled) {
  color: var(--text-main);
}
.icon-btn.disabled {
  opacity: 0.5;
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


/* MAIN */
.main-content {
  flex: 1;
  padding: 2rem 4rem;
}
.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 3rem;
}
.title {
  font-size: 1.875rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.5px;
}
.subtitle {
  color: var(--primary);
  margin-top: 0.5rem;
  font-size: 0.95rem;
}

/* KPI ROW */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.kpi-card {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.kpi-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.kpi-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1;
}

.kpi-card.total {
  border-left: 4px solid var(--primary);
}
.kpi-card.open {
  border-left: 4px solid var(--st-wait-tx);
}
.kpi-card.done {
  border-left: 4px solid var(--st-done-tx);
}
.kpi-card.cancelled {
  border-left: 4px solid var(--st-canc-tx);
}

/* SPLIT SECTION */
.split-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.report-card {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 2rem;
  height: 100%;
}

.report-card h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem;
}

/* Urgency List */
.urgency-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.urgency-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.urgency-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  font-weight: 600;
}
.progress-bg {
  width: 100%;
  height: 8px;
  background-color: whitesmoke; /* Usando a variável CSS para o fundo */
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease-in-out; /* Adicionando transição para efeito visual */
  min-width: 1px; /* Garante que a barra seja visível mesmo com porcentagem muito baixa */
}
.progress-fill.high {
  background-color: rgb(229, 27, 27);
}
.progress-fill.medium {
  background-color: rgba(255, 166, 0, 0.928);
}

.progress-fill.low {
  background-color: rgb(255, 230, 0);
}

/* Recent List */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.recent-item {
  padding-bottom: 1rem;
  border-bottom: 1px dashed var(--border);
}
.recent-item:last-child {
  border-bottom: none;
}
.recent-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}
.recent-id {
  font-weight: 700;
  color: var(--primary);
  font-size: 0.9rem;
}
.recent-date {
  font-size: 0.8rem;
  color: var(--text-muted);
}
.recent-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
}
.recent-author {
  color: var(--text-muted);
  font-size: 0.8rem;
  display: block;
  margin-top: 0.25rem;
}

.empty-text {
  font-style: italic;
  color: var(--text-muted);
  text-align: center;
  padding: 2rem;
}

/* RESPONSIVIDADE */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
  .nav-links {
    display: none;
  }
  .kpi-grid {
    grid-template-columns: 1fr 1fr;
  }
  .split-section {
    grid-template-columns: 1fr;
  }
  .header-right {
    gap: 0.5rem;
  }
}
</style>
