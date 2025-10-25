<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import type { Ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth' // Presumo que este caminho esteja correto
import api from '../services/api' // Presumo que este caminho esteja correto
// Importamos TaskStatus (o objeto que vem no histórico) e TaskStatusValue (o tipo 'OPEN' | 'ONGOING'...)
import type { Task, TaskStatus, TaskStatusValue } from '../types/api' // Presumo que este caminho esteja correto

// --- Estado do Componente ---
const tasks: Ref<Task[]> = ref([])
const loading: Ref<boolean> = ref(true)
const error: Ref<string | null> = ref(null)
const searchQuery: Ref<string> = ref('')
const router = useRouter()
const { user, clearToken } = useAuth()

// --- NOVO: Estado para o Modal de Atualização de Status ---
const showStatusModal = ref(false)
const statusUpdateComment = ref('')
const statusUpdateImage = ref<File | null>(null)
const statusUpdateImageName = ref<string>('') // Para mostrar o nome do arquivo selecionado
const taskToUpdate = ref<Task | null>(null)
const newStatusToSet = ref<TaskStatusValue | null>(null)

// --- Funções ---
async function fetchTasks() {
  try {
    const response = await api.getTasks()
    const fetchedTasks = response.data
    // --- CORREÇÃO AQUI: Ordena o histórico de cada tarefa ---
    fetchedTasks.forEach((task) => {
      if (task.status_history && Array.isArray(task.status_history)) {
        // Ordena do mais recente para o mais antigo
        task.status_history.sort(
          (a, b) => new Date(b.status_date).getTime() - new Date(a.status_date).getTime()
        )
      } else {
        task.status_history = [] // Garante array vazio se não vier
      }
    })
    tasks.value = fetchedTasks
  } catch (err) {
    console.error('Erro ao buscar as tarefas:', err)
    error.value = 'Falha ao carregar os chamados. Verifique se o backend está rodando.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchTasks)

// --- NOVA FUNÇÃO HELPER ---
// Computed property para pegar o status mais recente do histórico
const getLatestStatus = (task: Task): TaskStatusValue | null => {
  return task.status_history && task.status_history.length > 0
    ? task.status_history[0].status // Pega o status do primeiro item (mais recente)
    : null
}

const filteredTasks = computed<Task[]>(() => {
  if (!searchQuery.value) {
    return tasks.value
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase()
  return tasks.value.filter(
    (task) =>
      task.name.toLowerCase().includes(lowerCaseQuery) ||
      task.id.toString().includes(lowerCaseQuery) ||
      task.creator_FK?.name.toLowerCase().includes(lowerCaseQuery)
  )
})

const getStatusClass = (status: TaskStatusValue | null | undefined): string => {
  if (!status) return ''
  const statusMap: Record<TaskStatusValue, string> = {
    OPEN: 'status-aberto',
    WAITING_RESPONSIBLE: 'status-andamento',
    ONGOING: 'status-andamento',
    DONE: 'status-concluido',
    FINISHED: 'status-concluido',
    CANCELLED: 'status-cancelado',
  }
  return statusMap[status] || ''
}

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

// 1. Esta função agora apenas ABRE o modal
function openStatusUpdateModal(task: Task, event: Event) {
  const target = event.target as HTMLSelectElement
  const newStatus = target.value as TaskStatusValue

  taskToUpdate.value = task
  newStatusToSet.value = newStatus
  statusUpdateComment.value = '' // Limpa campos de um uso anterior
  statusUpdateImage.value = null
  statusUpdateImageName.value = ''
  showStatusModal.value = true // Abre o modal
}

// 2. Esta função captura o arquivo selecionado pelo usuário
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

// 3. Esta função é chamada ao ENVIAR o formulário do modal
async function handleSubmitStatusUpdate() {
  if (!taskToUpdate.value || !newStatusToSet.value) return

  const { user } = useAuth();
  const loggedInUserId = user.value?.id // Pega o ID 

  // Adicione uma verificação para garantir que temos um ID
  if (!loggedInUserId) {
    alert('Erro: Usuário não identificado. Faça login novamente.')
    return // Interrompe a função se não encontrar o ID
  }

  try {
    // ETAPA 1: Envia os dados de texto (JSON) para criar o TaskStatus
    const statusPayload = {
      task_FK: taskToUpdate.value.id,
      status: newStatusToSet.value,
      comment: statusUpdateComment.value,
      user_FK: loggedInUserId,
    }

    const newStatusResponse = await api.createTaskStatus(statusPayload)
    const newStatusId = newStatusResponse.data.id

    // ETAPA 2: Se uma imagem foi selecionada, envia os dados do arquivo (FormData)
    if (statusUpdateImage.value) {
      const imagePayload = new FormData()
      imagePayload.append('image', statusUpdateImage.value)
      imagePayload.append('task_status_FK', newStatusId.toString())

      await api.uploadTaskStatusImage(imagePayload)
    }

    alert(`Status do chamado #${taskToUpdate.value.id} alterado com sucesso!`)

    showStatusModal.value = false // Fecha o modal
    fetchTasks() // Recarrega a lista para mostrar os dados atualizados
  } catch (error) {
    console.error('Falha ao atualizar o status:', error)
    alert('Não foi possível atualizar o status.')
  }
}

// Esta função CANCELA a operação
function cancelStatusUpdate() {
  showStatusModal.value = false
  // Recarrega os dados para que o <select> na tabela volte ao seu valor original
  fetchTasks()
}
</script>

<template>
  <div>
    <header class="header">
      <div class="header-logo">MANGE-TECH</div>
      <nav class="header-nav">
        <a href="#">Dashboard</a>
        <a href="#">Chamados</a>
        <a href="#">Ativos</a>
        <a href="#">Relatórios</a>
      </nav>
      <div class="header-icons">
        <span v-if="user" class="user-name">{{ user.name }}</span>
        <img src="../assets/user.jpg" alt="User" class="user-profile" />
        <button @click="handleLogout" class="logout-button">Sair</button>
      </div>
    </header>

    <main class="dashboard-container">
      <div class="dashboard-content">
        <div
          class="dashboard-header"
          style="display: flex; justify-content: space-between; align-items: center"
        >
          <div>
            <h1>Dashboard</h1>
            <p>Visão geral dos chamados e ativos</p>
          </div>
          <router-link to="/task/new" class="create-button"> Novo Chamado </router-link>
        </div>

        <div class="table-container">
          <table v-if="!loading && !error">
            <thead>
              <tr>
                <th>Chamado</th>
                <th>Nome</th>
                <th>Ativo Principal</th>
                <th>Status</th>
                <th>Ambiente Principal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in filteredTasks" :key="task.id">
                <td>
                  <router-link :to="`/task/${task.id}`" class="task-id-link">
                    #{{ task.id }}
                  </router-link>
                </td>
                <td>{{ task.name }}</td>
                <td>{{ task.equipments_FK[0]?.name || 'N/A' }}</td>
                <td>
                  <select
                    :value="getLatestStatus(task)"
                    @change="openStatusUpdateModal(task, $event)"
                    class="status-select"
                    :class="getStatusClass(getLatestStatus(task))"
                  >
                    <option :value="null" disabled>Selecione</option>
                    <option value="OPEN">Aberto</option>
                    <option value="WAITING_RESPONSIBLE">Aguardando Responsável</option>
                    <option value="ONGOING">Em Andamento</option>
                    <option value="DONE">Feito</option>
                    <option value="FINISHED">Finalizado</option>
                    <option value="CANCELLED">Cancelado</option>
                  </select>
                </td>
                <td>{{ task.equipments_FK[0]?.environment_FK?.name || 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Modal para Atualização de Status -->
    <div v-if="showStatusModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Atualizar Status do Chamado #{{ taskToUpdate?.id }}</h3>
        <p>
          Novo Status: <strong>{{ formatStatus(newStatusToSet) }}</strong>
        </p>

        <form @submit.prevent="handleSubmitStatusUpdate">
          <div class="form-group">
            <label for="comment">Comentário:</label>
            <textarea id="comment" v-model="statusUpdateComment" rows="3" required></textarea>
          </div>

          <div class="form-group">
            <label for="image">Anexar Imagem (Opcional):</label>
            <input id="image" type="file" @change="onFileSelected" accept="image/*" />
            <span v-if="statusUpdateImageName" class="file-name">{{ statusUpdateImageName }}</span>
          </div>

          <div class="modal-actions">
            <button type="button" @click="cancelStatusUpdate" class="cancel-button">
              Cancelar
            </button>
            <button type="submit" class="submit-button">Salvar Atualização</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
:root {
  --bg-color: #f8f8f8;

  --primary-text-color: #2c3e50;

  --secondary-text-color: #7f8c8d;

  --card-bg-color: #ffffff;

  --border-color: #e0e0e0;

  --search-bg-color: #f0f2f5;

  --status-aberto: #d4f3e6;

  --status-andamento: #fbf0d8;

  --status-concluido: #d3eafc;
}

body {
  font-family: 'Poppins', sans-serif;
  background-color: var(--bg-color);
  margin: 0;
  padding: 0;
}

.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background-color: var(--card-bg-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid var(--border-color);
}

.header-logo {
  font-weight: 700;
  font-size: 24px;
  color: var(--primary-text-color);
}

.header-nav {
  display: flex;
  gap: 20px;
  font-weight: 500;
  color: var(--secondary-text-color);
}

.header-nav a {
  text-decoration: none;
  color: inherit;
}

.header-icons {
  display: flex;
  align-items: center;
  gap: 15px; 
}

.user-name {
  font-weight: 500;
  color: var(--primary-text-color);
  margin-right: 7px; 
}

.user-profile {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  object-fit: cover;
}

.dashboard-content {
  padding: 40px 0;
}

.dashboard-header {
  font-size: 36px;
  font-weight: 700;
  margin: 0;
  color: var(--primary-text-color);
}

.dashboard-header p {
  font-size: 16px;
  color: var(--secondary-text-color);
  margin-top: 5px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 30px 0;
}

.filter-item {
  position: relative;
  cursor: pointer;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--card-bg-color);
  color: var(--primary-text-color);
  font-weight: 500;
}

.filter-item i {
  margin-left: 8px;
}

.table-container {
  background-color: var(--card-bg-color);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.table-search {
  position: relative;
  margin-bottom: 20px;
}

.table-search input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--search-bg-color);
  color: var(--primary-text-color);
}

.table-search .fa-search {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--secondary-text-color);
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th,
td {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  color: var(--primary-text-color);
}

th {
  font-weight: 600;
  color: var(--secondary-text-color);
  font-size: 14px;
}

td {
  font-weight: 400;
  font-size: 15px;
}

tr:hover {
  background-color: #f5f5f5;
}

.task-id-link {
  color: #3b82f6; 
  font-weight: 500;
  text-decoration: none;
}
.task-id-link:hover {
  text-decoration: underline;
}

.status-badge {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 13px;
}

.status-aberto {
  background-color: var(--status-aberto);
  color: #1a7e4b;
}

.status-andamento {
  background-color: var(--status-andamento);
  color: #d88909;
}

.status-concluido {
  background-color: var(--status-concluido);
  color: #3b82f6;
}

.error-message {
  color: red;
  padding: 20px;
  text-align: center;
}

.create-button {
  background-color: #38e07b;
  color: #0e1a13;
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  font-size: 16px;
}

.action-button {
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 5px;
  font-size: 14px;
  text-decoration: none;
  color: white !important;
  display: inline-block;
}

.action-button.edit {
  background-color: #3b82f6;
}

.action-button.delete {
  background-color: #ef4444;
}

.status-select {
  border: none;

  border-radius: 20px;

  padding: 5px 10px;

  font-weight: 500;

  font-size: 13px;

  -webkit-appearance: none;

  -moz-appearance: none;

  appearance: none;

  background-color: transparent;

  cursor: pointer;
}

.status-select:focus {
  outline: none;

  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}
.modal-content h3 {
  margin-top: 0;
}
.modal-content .form-group {
  margin-bottom: 1rem;
}
.modal-content label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
.modal-content input,
.modal-content textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.file-name {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.5rem;
  display: block;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}
.modal-actions .submit-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}
.modal-actions .cancel-button {
  background-color: #ccc;
  color: #0e1a13;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
}
</style>