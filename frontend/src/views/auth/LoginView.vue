<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';
import { clearToken, useAuth } from '../../stores/auth';
import axios from 'axios';

const router = useRouter();
const { setToken, setUser } = useAuth();

const email = ref('');
const password = ref('');
const errorMessage = ref<string | null>(null);
const isLoading = ref(false);

async function handleLogin() {
  errorMessage.value = null;
  isLoading.value = true;

  try {
    const loginResponse = await api.login({ email: email.value, password: password.value });
    const token = loginResponse.data.auth_token;
    setToken(token);

    const userResponse = await api.getMe();
    const userData = userResponse.data;
    setUser(userData);

    router.push('/');

  } catch (error: unknown) {
    console.error('Falha no login:', error);
    clearToken();

    if (axios.isAxiosError(error) && error.response) {
       if (error.response.status === 400 || error.response.status === 401) {
           errorMessage.value = 'Email ou senha inválidos.';
       } else {
           errorMessage.value = 'Erro de conexão ou no servidor.';
       }
    } else {
      errorMessage.value = 'Ocorreu um erro inesperado.';
    }
  } finally {
      isLoading.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      
      <div class="card-header-image">
        <div class="banner-placeholder">
           <svg viewBox="0 0 500 150" preserveAspectRatio="none" style="height: 100%; width: 100%;">
              <path d="M0,100 C150,200 350,0 500,100 L500,00 L0,0 Z" style="stroke: none; fill: #2C5F58;"></path>
              <circle cx="400" cy="30" r="10" fill="#2C5F58" />
              <circle cx="350" cy="50" r="7" fill="#2C5F58" />
           </svg>
           <div class="beige-shape"></div>
        </div>
      </div>

      <div class="card-body">
        <h1 class="title">Bem-vindo de volta</h1>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email" class="sr-only">Email</label>
            <input 
              id="email"
              v-model="email"
              type="email"
              placeholder="Nome de usuário ou email"
              class="input-field"
              required 
            />
          </div>
          
          <div class="form-group">
            <label for="password" class="sr-only">Senha</label>
            <input 
              id="password"
              v-model="password"
              type="password"
              placeholder="Senha"
              class="input-field"
              required 
            />
          </div>

          <div class="form-footer">
            <a href="#" class="forgot-password">Esqueceu a senha?</a>
          </div>

          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

          <button type="submit" class="submit-btn" :disabled="isLoading">
            {{ isLoading ? 'Entrando...' : 'Entrar' }}
          </button>

          <p class="register-text">
            Não tem uma conta? <router-link to="/register" class="register-link">Cadastre-se</router-link>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Variáveis baseadas no protótipo */
:root {
  --primary-green: #34D399; /* Verde vibrante do botão */
  --primary-green-hover: #10B981;
  --bg-input: #EAF4F0; /* Fundo esverdeado claro dos inputs */
  --text-main: #111827;
  --text-muted: #6B7280;
  --link-color: #10B981; /* Verde para links */
}

* { box-sizing: border-box; }

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #FAFAFA; /* Fundo muito claro */
  font-family: 'Inter', sans-serif;
  padding: 2rem;
}

.login-card {
  background: white;
  width: 100%;
  max-width: 480px; /* Largura similar ao protótipo */
  border-radius: 16px; /* Bordas bem arredondadas */
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05); /* Sombra suave */
  overflow: hidden; /* Para cortar a imagem no topo */
}

/* --- HEADER / IMAGEM --- */
.card-header-image {
  height: 160px; /* Altura do banner */
  background-color: #fff;
  position: relative;
  overflow: hidden;
}

.banner-placeholder {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: #fff;
}

/* Simulação das formas da imagem (Você substituirá por <img>) */
.beige-shape {
  position: absolute;
  bottom: -40px;
  right: -20px;
  width: 150px;
  height: 150px;
  background-color: #EADBC8; /* Cor bege */
  border-radius: 50%;
  z-index: 1;
}

/* Se for usar imagem real: */
.card-header-image img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Garante que preencha sem distorcer */
}

/* --- CORPO DO CARD --- */
.card-body {
  padding: 2rem 3rem 3rem 3rem;
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  text-align: center;
  margin-bottom: 2.5rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Esconde labels visualmente mas mantém para leitores de tela */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.input-field {
  width: 100%;
  padding: 1rem 1.25rem;
  border: none; /* Sem borda, apenas fundo */
  border-radius: 8px;
  background-color: #E8F3EE; /* Cor de fundo esverdeada clara do protótipo */
  font-size: 1rem;
  color: #374151;
  transition: outline 0.2s;
}

.input-field::placeholder {
  color: #6B7280;
}

.input-field:focus {
  outline: 2px solid #34D399; /* Foco verde */
  background-color: #fff;
}

.form-footer {
  display: flex;
  justify-content: flex-start; /* Alinha à esquerda como no protótipo? Ou direita? */
  margin-top: -0.5rem;
}

.forgot-password {
  font-size: 0.9rem;
  color: #10B981; /* Verde */
  text-decoration: none;
  font-weight: 500;
}
.forgot-password:hover { text-decoration: underline; }

.submit-btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  background-color: #34D399; /* Verde do botão */
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 1rem;
}

.submit-btn:hover {
  background-color: #10B981;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.register-text {
  text-align: center;
  font-size: 0.9rem;
  color: #6B7280;
  margin-top: 1.5rem;
}

.register-link {
  color: #10B981;
  text-decoration: none;
  font-weight: 600;
}
.register-link:hover { text-decoration: underline; }

.error-message {
  color: #EF4444;
  font-size: 0.9rem;
  text-align: center;
}

/* Responsividade para telas muito pequenas */
@media (max-width: 480px) {
  .card-body {
    padding: 1.5rem 1.5rem 2rem 1.5rem;
  }
  .title {
    font-size: 1.5rem;
  }
}
</style>