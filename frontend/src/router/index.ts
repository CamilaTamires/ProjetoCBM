import { createRouter, createWebHistory } from 'vue-router';
import { useAuth } from '@/stores/auth'; // Importe nosso gerenciador de autenticação
import DashboardView from '../views/DashboardView.vue';
import CreateTaskView from '../views/tasks/CreateTaskView.vue';
import LoginView from '../views/auth/LoginView.vue'; // Importe a nova view de login
import RegisterView from '../views/auth/RegisterView.vue';
import ReportsView from '../views/test/ReportsView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true } 
    },
    {
      path: '/login', // Rota para a página de login
      name: 'login',
      component: LoginView
    },
    {
      path: '/register', // Rota para a página de registro
      name: 'register',
      component: RegisterView
    },
    // Rota para detalhes do chamado
    {
      path: '/task/:id', // O ':id' captura o número da URL
      name: 'task-detail',
      // Carrega o componente sob demanda (lazy loading)
      component: () => import('../views/tasks/TaskDetailView.vue'), 
      meta: { requiresAuth: true } // Também protegida por login
    },
    // Rota para criar um novo chamado
    {
      path: '/task/new',
      name: 'task-create',
      component: CreateTaskView,
      meta: { requiresAuth: true } // Protegida por autenticação
    },
    // Rota para editar o chamado
    {
      path: '/task/edit/:id',
      name: 'task-edit',
      component: () => import('../views/tasks/EditTaskView.vue'),
      meta: { requiresAuth: true } // Protegida por autenticação
    },
    
    // Rota para equipamentos
    {
      path: '/equipments',
      name: 'equipments',
      component: () => import('../views/EquipmentsView.vue'),
      meta: { requiresAuth: true } // Protegida por autenticação
    },
    // Rota para página de relatórios
    {
      path: '/reports',
      name: 'reports',
      component: ReportsView,
      meta: { requiresAuth: true } // Protegida por autenticação
    }
  ]
});

// --- GUARDA DE NAVEGAÇÃO GLOBAL ---
// Este código roda ANTES de cada mudança de rota
router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuth();

  // Se a rota requer autenticação, e o usuário não está logado
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    // Redireciona para a página de login
    next({ name: 'login' });
  } 
  // Se o usuário está logado e tenta acessar a página de login
  else if (to.name === 'login' && isAuthenticated.value) {
    // Redireciona para o dashboard
    next({ name: 'dashboard' });
  } 
  else {
    // Permite o acesso à rota
    next();
  }
});

export default router;