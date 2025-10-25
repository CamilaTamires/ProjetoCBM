<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../services/api';
import axios from 'axios'; // Mantenha a importação do axios

const router = useRouter();
const name = ref('');
const email = ref('');
const nif = ref('');
const password = ref('');
const confirmPassword = ref('');
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);

async function handleRegister() {
  errorMessage.value = null;
  successMessage.value = null;

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'As senhas não coincidem.';
    return;
  }
  if (password.value.length < 8) {
    errorMessage.value = 'A senha deve ter pelo menos 8 caracteres.';
    return;
  }

  try {
    await api.register({
      name: name.value,
      email: email.value,
      nif: nif.value,
      password: password.value
    });

    successMessage.value = 'Cadastro realizado com sucesso! Você já pode fazer o login.';
    name.value = '';
    email.value = '';
    nif.value = '';
    password.value = '';
    confirmPassword.value = '';

    setTimeout(() => {
      router.push({ name: 'login' });
    }, 2000);

  } catch (error: unknown) {
    console.error('Falha no cadastro:', error);

    if (axios.isAxiosError(error) && error.response && error.response.data) {
      // Definimos 'errors' de forma mais genérica para acomodar 'detail'
      const errors = error.response.data as Record<string, string[] | string>;

      if (errors.email && Array.isArray(errors.email)) {
        errorMessage.value = `Erro no Email: ${errors.email[0]}`;
      } else if (errors.password && Array.isArray(errors.password)) {
        errorMessage.value = `Erro na Senha: ${errors.password[0]}`;
      } else if (errors.name && Array.isArray(errors.name)) {
        errorMessage.value = `Erro no Nome: ${errors.name[0]}`;
      // --- CORREÇÃO AQUI para 'detail' ---
      } else if (errors.detail) {
          if(Array.isArray(errors.detail) && errors.detail.length > 0) {
              errorMessage.value = errors.detail[0]; // Pega a primeira mensagem se for array
          } else if (typeof errors.detail === 'string') {
              errorMessage.value = errors.detail; // Usa diretamente se for string
          } else {
               errorMessage.value = 'Ocorreu um erro nos dados fornecidos.'; // Fallback
          }
      } else {
        errorMessage.value = 'Ocorreu um erro desconhecido durante o cadastro.';
      }
    } else if (error instanceof Error) {
      errorMessage.value = `Ocorreu um erro: ${error.message}`;
    } else {
      errorMessage.value = 'Não foi possível conectar ao servidor ou ocorreu um erro inesperado.';
    }
  }
}
</script>

<template>
  <div class="register-container">
    <div class="register-box">
      <h1>Crie sua Conta</h1>
      <p>Preencha os dados abaixo para se cadastrar</p>
      
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="name">Nome Completo</label>
          <input id="name" v-model="name" type="text" placeholder="Seu nome" required />
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" placeholder="seuemail@exemplo.com" required />
        </div>
        <div class="form-group">
          <label for="nif">NIF</label>
          <input id="nif" v-model="nif" type="nif" placeholder="Número de Identificação" required />
        </div>
        <div class="form-group">
          <label for="password">Senha</label>
          <input id="password" v-model="password" type="password" placeholder="Mínimo 8 caracteres" required />
        </div>
        <div class="form-group">
          <label for="confirmPassword">Confirme a Senha</label>
          <input id="confirmPassword" v-model="confirmPassword" type="password" placeholder="Repita a senha" required />
        </div>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success-message">{{ successMessage }}</p>

        <button type="submit" class="register-button">Cadastrar</button>

        <p class="login-link">
          Já tem uma conta? <router-link to="/login">Faça login</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Estilos similares aos do LoginView, mas adaptados */
.register-container { display: flex; align-items: center; justify-content: center; min-height: 100vh; background-color: #f8fbfa; padding: 2rem 0; }
.register-box { background: white; padding: 3rem; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 100%; max-width: 450px; text-align: center; }
h1 { font-size: 1.8rem; font-weight: bold; color: #0e1a13; margin-bottom: 0.5rem; }
p { color: #7f8c8d; margin-bottom: 2rem; }
.form-group { text-align: left; margin-bottom: 1rem; } /* Diminuí a margem */
label { display: block; margin-bottom: 0.5rem; font-weight: 500; font-size: 0.9rem; }
input { width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.error-message { color: #ef4444; margin: 1rem 0; font-size: 0.9rem; }
.success-message { color: #10b981; margin: 1rem 0; font-size: 0.9rem; }
.register-button { width: 100%; background: #38e07b; color: #0e1a13; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 1rem; margin-top: 1rem; }
.login-link { margin-top: 1.5rem; font-size: 0.9rem; color: #7f8c8d; }
.login-link a { color: #3b82f6; text-decoration: none; font-weight: 500; }
.login-link a:hover { text-decoration: underline; }
</style>