<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';
// Importe setUser do seu store de autenticação
import { clearToken, useAuth } from '../../stores/auth';
import axios from 'axios'; // Mantenha a importação do axios para error handling

const router = useRouter();
// Pegue setToken E setUser
const { setToken, setUser } = useAuth();

const email = ref('');
const password = ref('');
const errorMessage = ref<string | null>(null);
const isLoading = ref(false); // Opcional: para feedback visual

async function handleLogin() {
  errorMessage.value = null;
  isLoading.value = true; // Opcional: Inicia loading

  try {
    // 1. Fazer login para obter o token
    const loginResponse = await api.login({ email: email.value, password: password.value });
    const token = loginResponse.data.auth_token;

    // 2. Salvar o token (isso permite que a próxima chamada funcione)
    setToken(token);

    // 3. Buscar os dados do usuário usando o token recém-salvo
    const userResponse = await api.getMe();
    const userData = userResponse.data;

    // 4. Salvar os dados do usuário no store/localStorage
    setUser(userData);

    // 5. Redirecionar para o dashboard
    router.push('/');

  } catch (error: unknown) {
    console.error('Falha no login ou ao buscar dados do usuário:', error);
    // Limpa o token se algo deu errado (ex: getMe falhou)
    clearToken(); // Importe clearToken do useAuth se ainda não o fez

    if (axios.isAxiosError(error) && error.response) {
       if (error.response.status === 400 || error.response.status === 401) {
           errorMessage.value = 'Email ou senha inválidos.';
       } else if (error.request.url?.includes('/me/')) {
           errorMessage.value = 'Erro ao buscar dados do usuário após login.';
       }
        else {
           errorMessage.value = 'Erro de conexão ou no servidor.';
       }
    } else {
      errorMessage.value = 'Ocorreu um erro inesperado.';
    }
  } finally {
      isLoading.value = false; // Opcional: Termina loading
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h1>MANGE-TECH</h1>
      <p>Acesse sua conta para continuar</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="seuemail@exemplo.com"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">Senha</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Sua senha"
            required
          />
        </div>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <button type="submit" class="login-button">Entrar</button>

        <p class="register-link">
          Não tem uma conta? <router-link to="/register">Cadastre-se</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f8fbfa;
}
.login-box {
  background: white;
  padding: 3rem;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}
h1 {
  font-size: 2rem;
  font-weight: bold;
  color: #0e1a13;
  margin-bottom: 0.5rem;
}
p {
  color: #7f8c8d;
  margin-bottom: 2rem;
}
.form-group {
  text-align: left;
  margin-bottom: 1.5rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}
.error-message {
  color: #ef4444;
  margin-top: -1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
.login-button {
  width: 100%;
  background: #38e07b;
  color: #0e1a13;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
}
.register-link {
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: #7f8c8d;
}
.register-link a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}
.register-link a:hover {
  text-decoration: underline;
}
</style>