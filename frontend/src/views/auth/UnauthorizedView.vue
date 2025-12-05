<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuth } from '@/stores/auth';
import api from '@/services/api';

const router = useRouter();
const { clearToken } = useAuth();

async function handleLogout() {
  try {
    await api.logout();
  } catch (e) {
    console.error(e);
  } finally {
    clearToken();
    router.push({ name: 'login' });
  }
}
</script>

<template>
  <div class="unauthorized-container">
    <div class="card">
      <div class="icon-wrapper">
        <i class="fas fa-mobile-alt"></i>
      </div>
      <h1>Acesso Restrito</h1>
      <p>
        A versão web do <strong>MANGE_TECH</strong> é exclusiva para <strong>Técnicos</strong>.
      </p>
      <p class="sub-text">
        Como colaborador, por favor utilize o nosso aplicativo móvel para abrir e acompanhar seus chamados.
      </p>
      
      <button @click="handleLogout" class="logout-btn">
        Voltar para o Login
      </button>
    </div>
  </div>
</template>

<style scoped>
.unauthorized-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #F3F4F6;
  padding: 1rem;
  font-family: 'Inter', sans-serif;
}

.card {
  background: white;
  padding: 3rem 2rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  text-align: center;
  max-width: 480px;
  width: 100%;
}

.icon-wrapper {
  font-size: 3rem;
  color: #10B981; /* Verde do projeto */
  margin-bottom: 1.5rem;
}

h1 {
  font-size: 1.8rem;
  color: #111827;
  margin-bottom: 1rem;
  font-weight: 700;
}

p {
  color: #4B5563;
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.sub-text {
  color: #6B7280;
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.logout-btn {
  background-color: #10B981;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
}

.logout-btn:hover {
  background-color: #059669;
}
</style>