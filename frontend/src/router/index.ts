// 1. Importa as funções necessárias do vue-router
import { createRouter, createWebHistory } from 'vue-router'

// 2. Importa o componente da sua página principal (o Dashboard)
import DashboardView from '../views/DashboardView.vue'
import CreateTaskView from '@/views/CreateTaskView.vue'

// 3. Cria a instância do router
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  
  // 4. Define a lista de rotas (o "mapa" do seu site)
  routes: [
    {
      // Quando o usuário acessar a página inicial ("/")
      path: '/',
      // Damos um nome para a rota, útil para navegação
      name: 'dashboard',
      // O componente que será exibido é o DashboardView
      component: DashboardView
    },
     // 2. ROTA PARA A PÁGINA DE CRIAÇÃO
    {
      path: '/task/new',
      name: 'task-create',
      component: CreateTaskView
    },
    

    {
    path: '/task/edit/:id',
    name: 'task-edit',
    component: () => import('../views/EditTaskView.vue'),
    },
  ]
})

// 5. Exporta o router para ser usado no resto da sua aplicação
export default router