<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import type { Ref } from 'vue';

import api from '../services/api';
// Renomeado para TaskStatusValue para evitar conflito com um possível model TaskStatus
import type { Task, TaskStatus } from '../types/api'; 

// --- Estado do Componente ---
const tasks: Ref<Task[]> = ref([]);
const loading: Ref<boolean> = ref(true);
const error: Ref<string | null> = ref(null);
const searchQuery: Ref<string> = ref('');

// --- Funções ---
async function fetchTasks() {
  try {
    const response = await api.getTasks();
    tasks.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar as tarefas:', err);
    error.value = 'Falha ao carregar os chamados. Verifique se o backend está rodando.';
  } finally {
    loading.value = false;
  }
}

onMounted(fetchTasks);

const filteredTasks = computed<Task[]>(() => {
  if (!searchQuery.value) {
    return tasks.value;
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase();
  return tasks.value.filter(task =>
    task.name.toLowerCase().includes(lowerCaseQuery) ||
    task.id.toString().includes(lowerCaseQuery) ||
    task.creator_FK?.name.toLowerCase().includes(lowerCaseQuery)
  );
});

const getStatusClass = (status: TaskStatus | null | undefined): string => {
  if (!status) return '';

  const statusMap: Record<TaskStatus, string> = {
    'OPEN': 'status-aberto',
    'WAITING_RESPONSIBLE': 'status-andamento',
    'ONGOING': 'status-andamento',
    'DONE': 'status-concluido',
    'FINISHED': 'status-concluido',
    'CANCELLED': 'status-cancelado'
  };
  return statusMap[status] || '';
};

const formatStatus = (status: TaskStatus | null | undefined): string => {
  if (!status) {
    return 'Status não informado';
  }
  const statusMap: Record<TaskStatus, string> = {
    'OPEN': 'Aberto',
    'WAITING_RESPONSIBLE': 'Aguardando Responsável',
    'ONGOING': 'Em Andamento',
    'DONE': 'Feito',
    'FINISHED': 'Finalizado',
    'CANCELLED': 'Cancelado'
  };
  return statusMap[status] || status.replace(/_/g, ' ');
};

async function handleDelete(taskId: number) {
  if (window.confirm('Tem certeza que deseja excluir este chamado?')) {
    try {
      await api.deleteTask(taskId);
      tasks.value = tasks.value.filter(task => task.id !== taskId);
    } catch (err) {
      console.error('Falha ao excluir o chamado:', err);
      alert('Não foi possível excluir o chamado.');
    }
  }
}

// DENTRO DO <script setup lang="ts"> de DashboardView.vue

async function handleStatusChange(task: Task, event: Event) {
  // 1. Extrai o novo status a partir do evento
  const target = event.target as HTMLSelectElement;
  const newStatus = target.value;
  
  const comment = prompt(`Por favor, adicione um comentário para a mudança de status para "${formatStatus(newStatus as TaskStatus)}":`);
  
  if (comment === null) {
    fetchTasks();
    return;
  }

  const loggedInUserId = 1;

  try {
    const payload = {
      task_FK: task.id,
      status: newStatus, // 2. Usa o novo status extraído
      comment: comment,
      user_FK: loggedInUserId
    };
    await api.createTaskStatus(payload);
    
    task.current_status = newStatus as TaskStatus;

    alert(`Status do chamado #${task.id} alterado com sucesso!`);
    
  } catch (error) {
    console.error('Falha ao atualizar o status:', error);
    alert('Não foi possível atualizar o status.');
    fetchTasks();
  }
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
        <div class="search-bar">
          <i class="fas fa-search"></i>
          <input type="text" placeholder="Search" />
        </div>
        <i class="far fa-bell"></i>
        <img src="../assets/user.png" alt="User" class="user-profile" />
      </div>
    </header>

    <main class="dashboard-container">
      <div class="dashboard-content">
        <div class="dashboard-header" style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <h1>Dashboard</h1>
            <p>Visão geral dos chamados e ativos</p>
          </div>
          <router-link to="/task/new" class="create-button">
            Novo Chamado
          </router-link>
        </div>

        <div class="filters">
          <div class="filter-item"><span>Data</span><i class="fas fa-chevron-down"></i></div>
          <div class="filter-item"><span>Status</span><i class="fas fa-chevron-down"></i></div>
          <div class="filter-item"><span>Ambiente</span><i class="fas fa-chevron-down"></i></div>
          <div class="filter-item"><span>Ativo</span><i class="fas fa-chevron-down"></i></div>
        </div>

        <div class="table-container">
          <div class="table-search">
            <i class="fas fa-search"></i>
            <input v-model="searchQuery" type="text" placeholder="Buscar por chamado, título ou solicitante..." />
          </div>

          <div v-if="loading">Carregando chamados...</div>
          <div v-if="error" class="error-message">{{ error }}</div>

          <table v-if="!loading && !error">
            <thead>
              <tr>
                <th>Chamado</th>
                <th>Data</th>
                <th>Status</th>
                <th>Ambiente</th>
                <th>Ativo</th>
                <th>Solicitante</th>
                <th>Responsável</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in filteredTasks" :key="task.id">
                <td>#{{ task.id }}</td>
                <td>
                  {{ task.creation_date ? new Date(task.creation_date).toLocaleDateString() : 'Data Inválida' }}
                </td>
                <td>
                  <select 
                    v-model="task.current_status" 
  @change="handleStatusChange(task, $event)" class="status-select"
  :class="getStatusClass(task.current_status)"
>
                    <option v-if="!task.current_status" :value="null">Selecione</option>
                    <option value="OPEN">Aberto</option>
                    <option value="WAITING_RESPONSIBLE">Aguardando Responsável</option>
                    <option value="ONGOING">Em Andamento</option>
                    <option value="DONE">Feito</option>
                    <option value="FINISHED">Finalizado</option>
                    <option value="CANCELLED">Cancelado</option>
                  </select>
                </td>
                <td>{{ task.equipments_FK[0]?.environment_FK?.name || 'N/A' }}</td>
                <td>{{ task.equipments_FK[0]?.name || 'N/A' }}</td>
                <td>{{ task.creator_FK?.name || 'Não definido' }}</td>
                <td>{{ task.responsibles_FK[0]?.name || 'Não atribuído' }}</td>
                <td>
                  <router-link :to="`/task/edit/${task.id}`" class="action-button edit">
                    Editar
                  </router-link>
                  <button @click="handleDelete(task.id)" class="action-button delete">
                    Excluir
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Seu CSS existente ... */
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
body { font-family: 'Poppins', sans-serif; background-color: var(--bg-color); margin: 0; padding: 0; }
.dashboard-container { max-width: 1200px; margin: 0 auto; padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; background-color: var(--card-bg-color); box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-bottom: 1px solid var(--border-color); }
.header-logo { font-weight: 700; font-size: 24px; color: var(--primary-text-color); }
.header-nav { display: flex; gap: 20px; font-weight: 500; color: var(--secondary-text-color); }
.header-nav a { text-decoration: none; color: inherit; }
.header-icons { display: flex; align-items: center; gap: 20px; }
.header-icons .search-bar { position: relative; width: 250px; }
.header-icons .search-bar input { width: 100%; padding: 8px 15px 8px 40px; border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--search-bg-color); }
.header-icons .search-bar .fa-search { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: var(--secondary-text-color); }
.user-profile { width: 35px; height: 35px; border-radius: 50%; object-fit: cover; }
.dashboard-content { padding: 40px 0; }
.dashboard-header { font-size: 36px; font-weight: 700; margin: 0; color: var(--primary-text-color); }
.dashboard-header p { font-size: 16px; color: var(--secondary-text-color); margin-top: 5px; }
.filters { display: flex; align-items: center; gap: 15px; margin: 30px 0; }
.filter-item { position: relative; cursor: pointer; padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--card-bg-color); color: var(--primary-text-color); font-weight: 500; }
.filter-item i { margin-left: 8px; }
.table-container { background-color: var(--card-bg-color); border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); padding: 20px; }
.table-search { position: relative; margin-bottom: 20px; }
.table-search input { width: 100%; padding: 10px 15px 10px 40px; border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--search-bg-color); color: var(--primary-text-color); }
.table-search .fa-search { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: var(--secondary-text-color); }
table { width: 100%; border-collapse: collapse; text-align: left; }
th, td { padding: 15px; border-bottom: 1px solid var(--border-color); color: var(--primary-text-color); }
th { font-weight: 600; color: var(--secondary-text-color); font-size: 14px; }
td { font-weight: 400; font-size: 15px; }
tr:hover { background-color: #f5f5f5; }
.status-badge { display: inline-block; padding: 5px 10px; border-radius: 20px; font-weight: 500; font-size: 13px; }
.status-aberto { background-color: var(--status-aberto); color: #1a7e4b; }
.status-andamento { background-color: var(--status-andamento); color: #d88909; }
.status-concluido { background-color: var(--status-concluido); color: #3b82f6; }
.error-message { color: red; padding: 20px; text-align: center; }
.create-button { background-color: #38e07b; color: #0e1a13; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; }
.action-button { border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; margin-right: 5px; font-size: 14px; text-decoration: none; color: white !important; display: inline-block; }
.action-button.edit { background-color: #3b82f6; }
.action-button.delete { background-color: #ef4444; }

/* NOVO: Estilos para o select de status */
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
</style>