<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../../services/api';
import type { CustomUser, Equipment } from '../../types/api';

const router = useRouter();
const route = useRoute();
const taskId = Number(route.params.id);

// --- INTERFACE PARA OS DADOS DO FORMULÁRIO ---
interface TaskFormData {
  name: string;
  description: string;
  suggested_date: string;
  suggested_time: string;
  urgency_level: string;
  creator_FK: number | null; 
  equipments_FK: number[];     
  responsibles_FK: number[];  
}

const taskData = ref<TaskFormData>({
  name: '',
  description: '',
  suggested_date: '',
  suggested_time: '',
  urgency_level: 'LOW',
  creator_FK: null,
  equipments_FK: [],
  responsibles_FK: [],
});

const users = ref<CustomUser[]>([]);
const equipments = ref<Equipment[]>([]);
const urgencyLevels = [
  { value: 'LOW', text: 'Baixo' },
  { value: 'MEDIUM', text: 'Médio' },
  { value: 'HIGH', text: 'Alto' },
];

onMounted(async () => {
  if (!taskId) {
    alert('ID da tarefa não encontrado.');
    router.push('/');
    return;
  }
  
  try {
    const [taskResponse, usersResponse, equipmentsResponse] = await Promise.all([
      api.getTask(taskId),
      api.getUsers(),
      api.getEquipments()
    ]);

    users.value = usersResponse.data;
    equipments.value = equipmentsResponse.data;

    const fetchedTask = taskResponse.data;
    const suggestedDateTime = fetchedTask.suggested_date ? new Date(fetchedTask.suggested_date) : null;

    taskData.value = {
      name: fetchedTask.name,
      description: fetchedTask.description,
      suggested_date: suggestedDateTime ? suggestedDateTime.toISOString().split('T')[0] : '',
      suggested_time: suggestedDateTime ? suggestedDateTime.toTimeString().split(' ')[0].substring(0, 5) : '',
      urgency_level: fetchedTask.urgency_level,
      creator_FK: fetchedTask.creator_FK?.id || null,
      equipments_FK: fetchedTask.equipments_FK.map(e => e.id),
      responsibles_FK: fetchedTask.responsibles_FK.map(r => r.id),
    };

  } catch (error) {
    console.error('Falha ao carregar dados para edição:', error);
    alert('Não foi possível carregar os dados da tarefa.');
  }
});

// --- Lógica para filtrar apenas Técnicos e Admins ---
const technicians = computed(() => {
  return users.value.filter(u => 
    u.groups && u.groups.some(g => ['Técnico', 'Tecnico', 'Técnico(a)', 'Admin'].includes(g))
  );
});

async function handleSubmit() {
  const suggestedDateTime = taskData.value.suggested_date && taskData.value.suggested_time
    ? `${taskData.value.suggested_date}T${taskData.value.suggested_time}`
    : null;

  const payload = {
    ...taskData.value,
    suggested_date: suggestedDateTime,
  };
  
  try {
    await api.updateTask(taskId, payload);
    alert('Chamado atualizado com sucesso!');
    router.push(`/task/${taskId}`); // Redireciona para os detalhes
  } catch (error: any) {
    if (error.response && error.response.status === 403) {
      alert('Você não tem permissão para editar este chamado. Contate um técnico.');
    } else {
      console.error('Erro ao atualizar o chamado:', error);
      alert('Erro ao atualizar o chamado. Tente novamente mais tarde.');
    }
  }
}
</script>

<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">Editar Chamado #{{ taskId }}</h1>
        <p class="page-subtitle">Atualize as informações do chamado abaixo</p>
      </div>
    </header>

    <main class="main-content">
      <div class="form-card">
        <form @submit.prevent="handleSubmit">
          
          <div class="form-section">
            <div class="form-group">
              <label for="name">Título do Chamado</label>
              <input id="name" v-model="taskData.name" type="text" placeholder="Ex: Manutenção de Impressora" required />
            </div>
            
            <div class="form-group">
              <label for="description">Descrição</label>
              <textarea id="description" v-model="taskData.description" rows="4" placeholder="Descreva o problema detalhadamente..."></textarea>
            </div>
          </div>

          <div class="form-row three-cols">
            <div class="form-group">
              <label for="suggested_date">Data Sugerida</label>
              <input id="suggested_date" v-model="taskData.suggested_date" type="date" />
            </div>
            <div class="form-group">
              <label for="suggested_time">Hora</label>
              <input id="suggested_time" v-model="taskData.suggested_time" type="time" />
            </div>
            <div class="form-group">
              <label for="urgency_level">Urgência</label>
              <select id="urgency_level" v-model="taskData.urgency_level">
                <option v-for="level in urgencyLevels" :key="level.value" :value="level.value">
                  {{ level.text }}
                </option>
              </select>
            </div>
          </div>

          <hr class="divider" />

          <div class="form-section">
            <div class="form-group">
              <label for="creator_FK">Solicitante (Criador)</label>
              <!-- Aqui mantemos 'users' para que qualquer pessoa possa ser o solicitante -->
              <select id="creator_FK" v-model="taskData.creator_FK">
                <option :value="null">Selecione um usuário...</option>
                <option v-for="user in users" :key="user.id" :value="user.id">
                  {{ user.name }} ({{ user.email }})
                </option>
              </select>
            </div>

            <div class="form-row two-cols">
              <div class="form-group">
                <label for="equipments_FK">Equipamentos Envolvidos</label>
                <select id="equipments_FK" v-model="taskData.equipments_FK" multiple class="multi-select">
                  <option v-for="equipment in equipments" :key="equipment.id" :value="equipment.id">
                    {{ equipment.name }}
                  </option>
                </select>
                <small class="hint">Segure Ctrl (ou Cmd) para selecionar múltiplos.</small>
              </div>

              <div class="form-group">
                <label for="responsibles_FK">Responsáveis Técnicos</label>
                <!-- Aqui alteramos para usar a computed property 'technicians' -->
                <select id="responsibles_FK" v-model="taskData.responsibles_FK" multiple class="multi-select">
                  <option v-for="user in technicians" :key="user.id" :value="user.id">
                    {{ user.name }}
                  </option>
                </select>
                <small class="hint">Segure Ctrl (ou Cmd) para selecionar múltiplos.</small>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <router-link :to="`/task/${taskId}`" class="btn btn-cancel">Cancelar</router-link>
            <button type="submit" class="btn btn-save">Salvar Alterações</button>
          </div>

        </form>
      </div>
    </main>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-page: #F9FAFB;
  --bg-card: #FFFFFF;
  --text-main: #111827;
  --text-muted: #6B7280;
  --border: #E5E7EB;
  --primary: #2563EB;
  --primary-hover: #1D4ED8;
  --success: #10B981;
  --bg-input: #F3F4F6;
}

* { box-sizing: border-box; }

.page-container {
  background-color: var(--bg-page);
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  color: var(--text-main);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 4rem;
}

.page-header {
  width: 100%;
  max-width: 800px;
  padding: 3rem 1rem 2rem 1rem;
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
  color: var(--text-main);
  letter-spacing: -0.025em;
}

.page-subtitle {
  margin-top: 0.5rem;
  color: var(--text-muted);
  font-size: 1rem;
}

.main-content {
  width: 100%;
  max-width: 800px;
  padding: 0 1rem;
}

.form-card {
  background: var(--bg-card);
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  padding: 2.5rem;
  border: 1px solid var(--border);
}

/* Layout do Formulário */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.two-cols { grid-template-columns: 1fr 1fr; }
.three-cols { grid-template-columns: 1fr 1fr 1fr; }

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-main);
}

/* Inputs e Selects */
input, textarea, select {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background-color: var(--bg-input);
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
  color: var(--text-main);
  transition: all 0.2s;
  width: 100%;
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--primary);
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

textarea {
  resize: vertical;
  min-height: 100px;
}

select.multi-select {
  height: 140px;
  padding: 0.5rem;
}

option {
  padding: 0.5rem;
}

.hint {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.divider {
  border: 0;
  border-top: 1px solid var(--border);
  margin: 2.5rem 0;
}

/* Ações */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-cancel {
  background-color: #fff;
  border: 1px solid var(--border);
  color: var(--text-main);
}

.btn-cancel:hover {
  background-color: var(--bg-input);
  border-color: #D1D5DB;
}

.btn-save {
  background-color: #2563EB; /* Usa a variável azul definida no :root */
  border: none;
  color: white; /* Texto branco para contraste */
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2); /* Sombra sutil para destacar */
}

.btn-save:hover {
  background-color: var(--primary-hover); /* Azul mais escuro no hover */
  transform: translateY(-1px); /* Efeito leve de clique */
}

/* Responsividade */
@media (max-width: 768px) {
  .form-card {
    padding: 1.5rem;
  }
  
  .two-cols, .three-cols {
    grid-template-columns: 1fr; /* Empilha tudo em mobile */
    gap: 1rem;
  }
  
  .form-actions {
    flex-direction: column-reverse; /* Salvar em cima, Cancelar embaixo */
  }
  
  .btn {
    width: 100%;
  }
}
</style>