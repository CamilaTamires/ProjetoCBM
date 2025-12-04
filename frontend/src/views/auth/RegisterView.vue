<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';
import axios from 'axios';

const router = useRouter();
const name = ref('');
const email = ref('');
// NIF não é mais um 'ref' ligado a input, será gerado no envio
const password = ref('');
const confirmPassword = ref('');
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);
const isLoading = ref(false);

// --- Função para gerar NIF Aleatório ---
function generateRandomNIF(): string {
  // Gera um número aleatório de 9 dígitos
  return Math.floor(100000000 + Math.random() * 900000000).toString();
}

async function handleRegister() {
  errorMessage.value = null;
  successMessage.value = null;
  isLoading.value = true;

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'As senhas não coincidem.';
    isLoading.value = false;
    return;
  }
  if (password.value.length < 8) {
    errorMessage.value = 'A senha deve ter pelo menos 8 caracteres.';
    isLoading.value = false;
    return;
  }

  // Gera o NIF automaticamente aqui, invisível para o usuário
  const randomNIF = generateRandomNIF();

  try {
    await api.register({
      name: name.value,
      email: email.value,
      nif: randomNIF,
      password: password.value
    });

    successMessage.value = 'Cadastro realizado com sucesso! Redirecionando...';
    // Limpa campos
    name.value = '';
    email.value = '';
    password.value = '';
    confirmPassword.value = '';

    setTimeout(() => {
      router.push({ name: 'login' });
    }, 2000);

  } catch (error: unknown) {
    console.error('Falha no cadastro:', error);

    if (axios.isAxiosError(error) && error.response && error.response.data) {
      const errors = error.response.data as Record<string, string[] | string>;

      if (errors.email && Array.isArray(errors.email)) {
        errorMessage.value = `Erro no Email: ${errors.email[0]}`;
      } else if (errors.password && Array.isArray(errors.password)) {
        errorMessage.value = `Erro na Senha: ${errors.password[0]}`;
      } else if (errors.name && Array.isArray(errors.name)) {
        errorMessage.value = `Erro no Nome: ${errors.name[0]}`;
      } else if (errors.detail) {
          if(Array.isArray(errors.detail) && errors.detail.length > 0) {
              errorMessage.value = errors.detail[0];
          } else if (typeof errors.detail === 'string') {
              errorMessage.value = errors.detail;
          } else {
               errorMessage.value = 'Ocorreu um erro nos dados fornecidos.';
          }
      } else {
        errorMessage.value = 'Ocorreu um erro desconhecido durante o cadastro.';
      }
    } else if (error instanceof Error) {
      errorMessage.value = `Ocorreu um erro: ${error.message}`;
    } else {
      errorMessage.value = 'Não foi possível conectar ao servidor.';
    }
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      
      <div class="card-header">
        <div class="header-bg">
           <svg viewBox="0 5  500 150" preserveAspectRatio="none" style="height: 100%; width: 100%;">
              <path d="M0,90 C400,230 300,0 550,130 L500,00 L0,0 Z" style="stroke: none; fill: #2C5F58;"></path>
              </svg>
        </div>
        <h1 class="header-title">Crie sua Conta</h1>
      </div>

      <div class="card-body">
        <p class="subtitle">Preencha os dados abaixo para começar</p>
        
        <form @submit.prevent="handleRegister" class="register-form">
          
          <div class="form-group">
            <input 
              id="name" 
              v-model="name" 
              type="text" 
              placeholder="Nome Completo" 
              class="input-field" 
              required 
            />
          </div>

          <div class="form-group">
            <input 
              id="email" 
              v-model="email" 
              type="email" 
              placeholder="Email" 
              class="input-field" 
              required 
            />
          </div>

          <div class="form-row">
            <div class="form-group half">
              <input 
                id="password" 
                v-model="password" 
                type="password" 
                placeholder="Senha" 
                class="input-field" 
                required 
              />
            </div>
            <div class="form-group half">
              <input 
                id="confirmPassword" 
                v-model="confirmPassword" 
                type="password" 
                placeholder="Confirmar Senha" 
                class="input-field" 
                required 
              />
            </div>
          </div>

          <div v-if="errorMessage" class="message-box error">
            {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="message-box success">
            {{ successMessage }}
          </div>

          <button type="submit" class="register-button" :disabled="isLoading">
            {{ isLoading ? 'Cadastrando...' : 'Cadastrar' }}
          </button>

          <p class="login-text">
            Já tem uma conta? <router-link to="/login" class="login-link">Faça login</router-link>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Definindo variáveis no escopo do componente para garantir aplicação */
.register-page {
  /* Cores idênticas ao Login */
  --primary-green: #34D399;       /* Verde do botão */
  --primary-green-hover: #10B981; /* Verde hover */
  --bg-input: #E8F3EE;            /* Fundo dos inputs */
  --text-main: #111827;
  --text-muted: #6B7280;
  --link-color: #10B981;
  --error-color: #EF4444;
  --success-color: #10B981;

  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #FAFAFA; /* Fundo da página */
  font-family: 'Inter', sans-serif;
  padding: 2rem;
}

* { box-sizing: border-box; }

.register-card {
  background: white;
  width: 100%;
  max-width: 550px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  overflow: hidden; /* Importante para cortar o SVG no topo */
}

/* --- HEADER ESTILIZADO --- */
.card-header {
  height: 160px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fff;
}

.header-bg {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  z-index: 0;
}

.header-title {
  position: relative;
  z-index: 1;
  color: white;
  font-size: 2rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px; /* Ajuste para centralizar visualmente na parte verde */
}

/* --- CORPO --- */
.card-body {
  padding: 2rem 3rem 3rem 3rem;
}

.subtitle {
  text-align: center;
  color: var(--text-muted);
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group {
  flex: 1;
}

/* --- INPUTS --- */
.input-field {
  width: 100%;
  padding: 1rem 1.25rem;
  border: none;
  border-radius: 8px;
  background-color: var(--bg-input);
  font-size: 0.95rem;
  color: var(--text-main);
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}

.input-field::placeholder { color: #9CA3AF; }

.input-field:focus {
  outline: 2px solid var(--primary-green);
  background-color: #fff;
  box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.1);
}

/* --- FEEDBACK --- */
.message-box {
  padding: 0.8rem;
  border-radius: 8px;
  font-size: 0.9rem;
  text-align: center;
  font-weight: 500;
}

.message-box.error {
  background-color: #FEE2E2;
  color: #B91C1C;
  border: 1px solid #FECACA;
}

.message-box.success {
  background-color: #D1FAE5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

/* --- BOTÃO --- */
.register-button {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  background-color: var(--primary-green);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
  margin-top: 1rem;
}

.register-button:hover {
  background-color: var(--primary-green-hover);
}

.register-button:active { transform: scale(0.98); }
.register-button:disabled { opacity: 0.7; cursor: not-allowed; }

/* --- FOOTER --- */
.login-text {
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 1.5rem;
}

.login-link {
  color: var(--link-color);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}
.login-link:hover { color: var(--primary-green-hover); text-decoration: underline; }

/* RESPONSIVIDADE */
@media (max-width: 600px) {
  .register-card { border-radius: 0; height: 100vh; display: flex; flex-direction: column; }
  .card-header { height: 140px; flex-shrink: 0; }
  .card-body { padding: 1.5rem; flex-grow: 1; }
  .form-row { flex-direction: column; gap: 1rem; }
}
</style>