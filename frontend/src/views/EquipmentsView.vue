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

// Chama a função ao montar o componente
onMounted(fetchEquipments)

// Filtra os equipamentos com base na busca
const filteredEquipments = computed<Equipment[]>(() => {
  if (!searchQuery.value) {
    return equipments.value
  }
  const lowerCaseQuery = searchQuery.value.toLowerCase()
  return equipments.value.filter(
    (equip) =>
      equip.name.toLowerCase().includes(lowerCaseQuery) ||
      equip.code.toLowerCase().includes(lowerCaseQuery) ||
      equip.environment_FK?.name.toLowerCase().includes(lowerCaseQuery) ||
      equip.category_FK?.name.toLowerCase().includes(lowerCaseQuery)
  )
})

// Função de Logout (mantida)
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


</script>

<template>
  <div>
    <header class="header">
      <div class="header-logo">MANGE-TECH</div>
      <nav class="header-nav">
        <router-link to="/" class="nav-link">Dashboard</router-link>
        <router-link to="/equipments/" class="nav-link">Ativos</router-link>
        <!-- <router-link to="/relatorios" class="nav-link">Relatórios</router-link> -->
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
            <h1>Ativos</h1>
            <p>Visão geral de todos os equipamentos</p>
          </div>
          </div>

        <div class="table-container">
          <div class="table-search">
            <i class="fas fa-search"></i>
            <input v-model="searchQuery" type="text" placeholder="Buscar por nome, código, ambiente..." />
          </div>

          <table v-if="!loading && !error">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Código</th>
                <th>Categoria</th>
                <th>Ambiente</th>
                <th>QR Code</th>
                </tr>
            </thead>
            <tbody>
              <tr v-for="equipment in filteredEquipments" :key="equipment.id">
                <td>{{ equipment.name }}</td>
                <td>{{ equipment.code }}</td>
                <td>{{ equipment.category_FK?.name || 'N/A' }}</td>
                <td>{{ equipment.environment_FK?.name || 'N/A' }}</td>
                <td>
                  <img v-if="equipment.qr_code_image" 
                       :src="equipment.qr_code_image" 
                       alt="QR Code" 
                       style="width: 40px; height: 40px;" />
                  <span v-else>N/A</span>
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

.error-message {
  color: red;
  padding: 20px;
  text-align: center;
}

/* .create-button {
  background-color: #38e07b;
  color: #0e1a13;
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  font-size: 16px;
} */

/* .action-button {
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 5px;
  font-size: 14px;
  text-decoration: none;
  color: white !important;
  display: inline-block;
} */
</style>