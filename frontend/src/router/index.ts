import { createRouter, createWebHistory } from 'vue-router';
import { useAuth } from '../stores/auth';
import DashboardView from '../views/DashboardView.vue';
import CreateTaskView from '../views/tasks/CreateTaskView.vue';
import LoginView from '../views/auth/LoginView.vue';
import RegisterView from '../views/auth/RegisterView.vue';
import ReportsView from '../views/reports/ReportsView.vue';
import UnauthorizedView from '.././views/auth/UnauthorizedView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true, requiresTechnician: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/unauthorized',
      name: 'unauthorized',
      component: UnauthorizedView,
    },
    {
      path: '/task/:id',
      name: 'task-detail',
      component: () => import('../views/tasks/TaskDetailView.vue'), 
      meta: { requiresAuth: true, requiresTechnician: true }
    },
    {
      path: '/task/new',
      name: 'task-create',
      component: CreateTaskView,
      meta: { requiresAuth: true, requiresTechnician: true }
    },
    {
      path: '/task/edit/:id',
      name: 'task-edit',
      component: () => import('../views/tasks/EditTaskView.vue'),
      meta: { requiresAuth: true, requiresTechnician: true }
    },
    {
      path: '/equipments',
      name: 'equipments',
      component: () => import('../views/EquipmentsView.vue'), 
      meta: { requiresAuth: true, requiresTechnician: true }
    },
    {
      path: '/reports',
      name: 'reports',
      component: ReportsView,
      meta: { requiresAuth: true, requiresTechnician: true }
    }
  ]
});

// --- LÓGICA DE PROTEÇÃO ---
router.beforeEach((to, from, next) => {
  const { isAuthenticated, user } = useAuth();

  // Função robusta inspirada no filtro do seu task.py
  const isTechnician = () => {
    // 1. Garante que o usuário e os grupos existem
    if (!user.value || !user.value.groups) {
      console.warn('Auth check: Usuário ou grupos não carregados corretamente.');
      return false;
    }

    const userGroups = user.value.groups;
    
    // Lista EXATA do seu backend (task.py) + Admin
    const allowedGroups = ['Técnico', 'Tecnico', 'Técnico(a)', 'Admin'];

    // 2. Validação Híbrida: Funciona se o backend mandar Strings OU Objetos
    return userGroups.some((g: any) => {
      // Se 'g' for string (ex: "Técnico"), usa ela. 
      // Se 'g' for objeto (ex: {name: "Técnico"}), usa g.name
      const groupName = (typeof g === 'string') ? g : g.name;
      
      return allowedGroups.includes(groupName);
    });
  };

  // 1. Rota requer Autenticação?
  if (to.meta.requiresAuth) {
    if (!isAuthenticated.value) {
      return next({ name: 'login' });
    }
    
    // 2. Rota requer ser Técnico?
    if (to.meta.requiresTechnician) {
      if (!isTechnician()) {
        // Debug para você ver no console do navegador o que está falhando
        console.log('Bloqueio de rota. Grupos do usuário:', user.value?.groups);
        return next({ name: 'unauthorized' });
      }
    }
  }

  // 3. Redirecionamento de Login/Register se já estiver logado
  if ((to.name === 'login' || to.name === 'register') && isAuthenticated.value) {
    if (isTechnician()) {
      return next({ name: 'dashboard' });
    } else {
      // Se for colaborador comum tentando ir pro login, vai pro unauthorized ou dashboard dele
      // Mantendo sua lógica original de unauthorized:
      return next({ name: 'unauthorized' });
    }
  }

  // Permite a navegação
  next();
});

export default router;