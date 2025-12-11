<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuth } from '@/stores/auth';
import api from '@/services/api';

const router = useRouter();
const { clearToken } = useAuth();

// Ao atualizar, substituir link do apk correto e atualizado.
const APK_DOWNLOAD_URL = 'https://drive.google.com/file/d/1O5XRc7ZleJAwp7WKJBv_BDFlGJRjMulv/view?usp=drive_link'; // <--- SUBSTITUA ESTE LINK
// ====================================================================

// URL para gerar o QR Code (usando uma API pública para demonstração)
// O QR code apontará para o URL definido acima.
const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(APK_DOWNLOAD_URL)}`;

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
        A versão web do <strong>CBM TECH</strong> é exclusiva para <strong>Técnicos</strong>.
      </p>
      <p class="sub-text">
        Como colaborador, por favor utilize o nosso aplicativo móvel para abrir e acompanhar seus chamados.
      </p>

      <div class="qr-code-wrapper">
        <p class="qr-code-text">Baixe o aplicativo para Android:</p>
        <img :src="qrCodeUrl" alt="QR Code para download do APK" class="qr-code-img" />
      </div>
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

/* NOVOS ESTILOS PARA O QR CODE */
.qr-code-wrapper {
  margin-top: 1.5rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #E5E7EB; /* Divisor claro */
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qr-code-text {
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.qr-code-img {
  width: 150px;
  height: 150px;
  border: 5px solid #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  /* Garante que a imagem é tratada como bloco para centralização e dimensões corretas */
  display: block; 
}
/* FIM NOVOS ESTILOS */

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