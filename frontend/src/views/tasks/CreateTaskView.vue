<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';
import type { CustomUser, Equipment } from '../../types/api';

const router = useRouter();

// --- Estado para os dados do formulário ---
const taskData = ref({
  name: '',
  description: '',
  suggested_date: '',
  suggested_time: '',
  urgency_level: 'LOW',
  creator_FK: null,
  equipments_FK: [], // Para select múltiplo
  responsibles_FK: [], // Para select múltiplo
});

// --- Estado para as opções dos menus <select> ---
const users = ref<CustomUser[]>([]);
const equipments = ref<Equipment[]>([]);
const urgencyLevels = [
  { value: 'LOW', text: 'Baixo' },
  { value: 'MEDIUM', text: 'Médio' },
  { value: 'HIGH', text: 'Alto' },
];

// --- Carregar dados para os menus quando o componente é montado ---
onMounted(async () => {
  try {
    const usersResponse = await api.getUsers();
    users.value = usersResponse.data;

    const equipmentsResponse = await api.getEquipments();
    equipments.value = equipmentsResponse.data;
  } catch (error) {
    console.error('Falha ao carregar dados para o formulário:', error);
    alert('Não foi possível carregar as opções de usuários e equipamentos.');
  }
});

// --- Lógica de envio do formulário ---
async function handleSubmit() {
  // Combina data e hora em um formato ISO 8601 que o Django entende
  const suggestedDateTime = taskData.value.suggested_date && taskData.value.suggested_time
    ? `${taskData.value.suggested_date}T${taskData.value.suggested_time}`
    : null;

  // Monta o payload final para a API
  const payload = {
    name: taskData.value.name,
    description: taskData.value.description,
    suggested_date: suggestedDateTime,
    urgency_level: taskData.value.urgency_level,
    creator_FK: taskData.value.creator_FK,
    equipments_FK: taskData.value.equipments_FK,
    responsibles_FK: taskData.value.responsibles_FK,
  };
  
  try {
    await api.createTask(payload);
    alert('Chamado criado com sucesso!');
    router.push('/'); // Redireciona para o dashboard
  } catch (error) {
    console.error('Falha ao criar o chamado:', error);
    alert('Não foi possível criar o chamado. Verifique os campos.');
  }
}
</script>

<template>
  <div class="form-container">
    <h1>Adicionar Task</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="name">Name:</label>
        <input id="name" v-model="taskData.name" type="text" required />
      </div>

      <div class="form-group">
        <label for="description">Description:</label>
        <textarea id="description" v-model="taskData.description"></textarea>
      </div>

      <div class="form-group date-time-group">
        <div class="date-input">
          <label for="suggested_date">Data:</label>
          <input id="suggested_date" v-model="taskData.suggested_date" type="date" />
        </div>
        <div class="time-input">
          <label for="suggested_time">Hora:</label>
          <input id="suggested_time" v-model="taskData.suggested_time" type="time" />
        </div>
      </div>

      <div class="form-group">
        <label for="urgency_level">Urgency level:</label>
        <select id="urgency_level" v-model="taskData.urgency_level">
          <option v-for="level in urgencyLevels" :key="level.value" :value="level.value">
            {{ level.text }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="creator_FK">Creator:</label>
        <select id="creator_FK" v-model="taskData.creator_FK">
          <option :value="null">---------</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.name }} ({{ user.email }})
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="equipments_FK">Equipments:</label>
        <select id="equipments_FK" v-model="taskData.equipments_FK" multiple>
          <option v-for="equipment in equipments" :key="equipment.id" :value="equipment.id">
            {{ equipment.name }}
          </option>
        </select>
        <small>Pressione "Control" ou "Command" para selecionar mais de um.</small>
      </div>

      <div class="form-group">
        <label for="responsibles_FK">Responsibles:</label>
        <select id="responsibles_FK" v-model="taskData.responsibles_FK" multiple>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.name }} ({{ user.email }})
          </option>
        </select>
        <small>Pressione "Control" ou "Command" para selecionar mais de um.</small>
      </div>

      <div class="form-actions">
        <button type="submit" class="submit-button">Salvar Task</button>
        <router-link to="/" class="cancel-button">Cancelar</router-link>
      </div>
    </form>
  </div>
</template>

<style scoped>
/* Estilos que você já tinha, adaptados para todos os campos */
.form-container { max-width: 600px; margin: 2rem auto; padding: 2rem; background: #fff; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.form-group { margin-bottom: 1.5rem; }
label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
input, textarea, select { width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
select[multiple] { height: 120px; }
.date-time-group { display: flex; gap: 1rem; }
.date-time-group > div { flex: 1; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem; }
.submit-button { background: #38e07b; color: #0e1a13; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: bold; }
.cancel-button { background: #ccc; color: #0e1a13; text-decoration: none; padding: 0.75rem 1.5rem; border-radius: 8px; }
small { margin-top: 0.5rem; color: #666; display: block; }
</style>