<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../../services/api';
// Importamos TaskStatus (o objeto) e TaskStatusValue (o tipo 'OPEN' | 'ONGOING'...)
import type { Task, TaskStatus, TaskStatusValue } from '../../types/api';

const route = useRoute();
const router = useRouter();
const taskId = Number(route.params.id);

const task = ref<Task | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

// Estado para controlar qual status do histórico está sendo exibido
const currentStatusIndex = ref(0);

// Função de formatação (mantida)
const formatStatus = (status: TaskStatusValue | null | undefined): string => {
  if (!status) { return 'Status não informado'; }
  const statusMap: Record<TaskStatusValue, string> = { 'OPEN': 'Aberto', 'WAITING_RESPONSIBLE': 'Aguardando Responsável', 'ONGOING': 'Em Andamento', 'DONE': 'Feito', 'FINISHED': 'Finalizado', 'CANCELLED': 'Cancelado' };
  return statusMap[status] || status.replace(/_/g, ' ');
};

// Função para buscar os dados da tarefa (agora inclui ordenação do histórico)
onMounted(async () => {
  if (!taskId) {
    error.value = 'ID do chamado inválido.';
    loading.value = false;
    return;
  }
  try {
    const response = await api.getTask(taskId);
    task.value = response.data;

    // Ordena o histórico recebido pela data, MAIS RECENTE PRIMEIRO
    if (task.value && task.value.status_history) {
      task.value.status_history.sort((a, b) => new Date(b.status_date).getTime() - new Date(a.status_date).getTime());
      // Define o índice inicial para mostrar o status mais recente (o primeiro da lista ordenada)
      currentStatusIndex.value = 0;
    } else if (task.value) {
      // Garante que status_history seja um array vazio se vier nulo ou indefinido
      task.value.status_history = [];
    }
  } catch (err) {
    console.error('Erro ao buscar detalhes da tarefa:', err);
    error.value = 'Falha ao carregar os detalhes do chamado.';
  } finally {
    loading.value = false;
  }
});

// Computed property para acessar facilmente o objeto TaskStatus atual
const currentStatus = computed<TaskStatus | null>(() => {
  if (task.value && task.value.status_history && task.value.status_history.length > currentStatusIndex.value) {
    return task.value.status_history[currentStatusIndex.value];
  }
  return null;
});

// Funções para navegar pelo histórico
function showPreviousStatus() {
  // Incrementa o índice para ver um status MAIS ANTIGO (já que ordenamos do mais novo pro mais velho)
  if (task.value && currentStatusIndex.value < task.value.status_history.length - 1) {
    currentStatusIndex.value++;
  }
}
function showNextStatus() {
  // Decrementa o índice para ver um status MAIS NOVO
  if (currentStatusIndex.value > 0) {
    currentStatusIndex.value--;
  }
}

// Função para excluir (mantida)
async function handleDelete() {
  if (!task.value) return;
  if (window.confirm(`Tem certeza que deseja excluir o chamado #${task.value.id}?`)) {
    try {
      await api.deleteTask(task.value.id);
      alert('Chamado excluído com sucesso!');
      router.push('/');
    } catch (err) {
      console.error('Falha ao excluir o chamado:', err);
      alert('Não foi possível excluir o chamado.');
    }
  }
}
</script>

<template>
  <div class="detail-container">
    <router-link to="/" class="back-button">&larr; Voltar para o Dashboard</router-link>

    <div v-if="loading">Carregando detalhes...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="task" class="task-details">
      <h1>Detalhes do Chamado #{{ task.id }}</h1>

      <div class="detail-section">
        <h2>Informações Gerais</h2>
        <p><strong>Nome:</strong> {{ task.name }}</p>
        <p><strong>Descrição:</strong> {{ task.description || 'Nenhuma descrição fornecida.' }}</p>
        <p><strong>Data Sugerida:</strong> {{ task.suggested_date ? new Date(task.suggested_date).toLocaleString() : 'Não definida' }}</p>
        <p><strong>Nível de Urgência:</strong> {{ task.urgency_level }}</p>
        <p><strong>Data de Criação:</strong> {{ new Date(task.creation_date).toLocaleString() }}</p>
        </div>

      <div class="detail-section status-history-section">
        <h2>Histórico de Status</h2>
        <div v-if="currentStatus" class="status-display">
          <div class="status-navigation">
            <button @click="showPreviousStatus" :disabled="!task || currentStatusIndex >= task.status_history.length - 1">
              &lt; Mais Antigo
            </button>
            <span>
              {{ currentStatusIndex + 1 }} / {{ task.status_history.length }}
              ({{ new Date(currentStatus.status_date).toLocaleString() }})
            </span>
            <button @click="showNextStatus" :disabled="currentStatusIndex <= 0">
              Mais Novo &gt;
            </button>
          </div>
          <div class="status-info">
            <p><strong>Status:</strong> {{ formatStatus(currentStatus.status) }}</p>
            <p><strong>Comentário:</strong> {{ currentStatus.comment || 'Sem comentário.' }}</p>
            <p><strong>Atualizado por:</strong> {{ currentStatus.user_detail?.name || 'Usuário desconhecido' }}</p>
            <div v-if="currentStatus.images && currentStatus.images.length > 0" class="status-images">
              <strong>Imagens Anexadas:</strong>
              <div v-for="img in currentStatus.images" :key="img.id" class="image-container">
                 <img :src="img.image.startsWith('http') ? img.image : `http://localhost:8000${img.image}`"
                     :alt="`Imagem do status ${formatStatus(currentStatus.status)}`"
                     class="status-image"/>
              </div>
            </div>
            <p v-else>Nenhuma imagem anexada para este status.</p>
          </div>
        </div>
        <p v-else>Nenhum histórico de status encontrado para este chamado.</p>
      </div>

      <div class="detail-section">
        <h2>Pessoas Envolvidas</h2>
        <p><strong>Solicitante:</strong> {{ task.creator_FK?.name || 'Não definido' }} ({{ task.creator_FK?.email || 'N/A' }})</p>
        <p><strong>Responsáveis:</strong></p>
        <ul>
          <li v-if="task.responsibles_FK.length === 0">Nenhum responsável atribuído.</li>
          <li v-for="resp in task.responsibles_FK" :key="resp.id">
            {{ resp.name }} ({{ resp.email }})
          </li>
        </ul>
      </div>

      <div class="detail-section">
        <h2>Equipamentos Associados</h2>
        <ul>
          <li v-if="task.equipments_FK.length === 0">Nenhum equipamento associado.</li>
          <li v-for="equip in task.equipments_FK" :key="equip.id" class="equipment-item">
            <div class="equipment-info">
              <strong>{{ equip.name }}</strong> (Ambiente: {{ equip.environment_FK?.name || 'N/A' }}, Categoria: {{ equip.category_FK?.name || 'N/A' }})
              <br>Código: {{ equip.code || 'N/A' }} | Descrição: {{ equip.description || 'N/A' }}
            </div>
            <div v-if="equip.qr_code_image" class="qr-code-container">
              <img
                :src="equip.qr_code_image.startsWith('http') ? equip.qr_code_image : `http://localhost:8000${equip.qr_code_image}`"
                alt="QR Code"
                class="qr-code-image"
              />
              <small>QR Code</small>
            </div>
            <div v-else class="qr-code-container">
              <small>Sem QR Code</small>
            </div>
          </li>
        </ul>
      </div>

      <div class="detail-actions">
           <router-link :to="`/task/edit/${task.id}`" class="action-button edit">Editar Chamado</router-link>
           <button @click="handleDelete" class="action-button delete">Excluir Chamado</button>
       </div>
    </div>
  </div>
</template>

<style scoped>
.detail-container { max-width: 900px; margin: 2rem auto; padding: 2rem; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); }
.back-button { display: inline-block; margin-bottom: 1.5rem; color: #51946c; text-decoration: none; font-weight: 500; }
.back-button:hover { text-decoration: underline; }
.error-message { color: red; text-align: center; }
.task-details h1 { font-size: 2em; font-weight: bold; color: #0e1a13; margin-bottom: 1.5rem; border-bottom: 1px solid #e0e0e0; padding-bottom: 1rem; }
.detail-section { margin-bottom: 2rem; }
.detail-section h2 { font-size: 1.4em; font-weight: 600; color: #2c3e50; margin-bottom: 1rem; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }
.detail-section p, .detail-section li { color: #2c3e50; line-height: 1.6; margin-bottom: 0.5rem; }
.detail-section strong { font-weight: 600; color: #0e1a13; }
.detail-section ul { list-style: none; padding-left: 0; } /* Removido estilo de lista padrão */

/* Estilos para Histórico de Status */
.status-history-section { background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 1.5rem; }
.status-display { margin-top: 1rem; }
.status-navigation { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px dashed #ccc; }
.status-navigation button { padding: 5px 10px; background-color: #eee; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; }
.status-navigation button:disabled { opacity: 0.5; cursor: not-allowed; }
.status-navigation span { font-size: 0.9em; color: #555; text-align: center; }
.status-info p { margin-bottom: 0.75rem; }
.status-images { margin-top: 1rem; }
.status-images strong { display: block; margin-bottom: 0.5rem; }
.image-container { display: inline-block; margin-right: 10px; margin-bottom: 10px; }
.status-image { max-width: 150px; max-height: 150px; height: auto; border: 1px solid #ccc; border-radius: 4px; display: block; }

/* Estilos para Equipamentos */
.equipment-item { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 1rem; margin-bottom: 1rem; }
.equipment-info { flex-grow: 1; margin-right: 1rem; }
.qr-code-container { flex-shrink: 0; text-align: center; }
.qr-code-image { max-width: 80px; height: auto; display: block; margin-bottom: 0.25rem; }

/* Estilos para Botões de Ação */
.detail-actions { margin-top: 2rem; text-align: right; display: flex; justify-content: flex-end; gap: 1rem; }
.action-button { border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; font-size: 1rem; }
.action-button.edit { background-color: #3b82f6; color: white; }
.action-button.delete { background-color: #ef4444; color: white; }
</style>