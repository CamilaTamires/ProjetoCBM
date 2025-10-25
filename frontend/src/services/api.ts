import axios from 'axios'
import type {
  Task,
  CustomUser,
  Equipment,
  TaskStatus,
  TaskPayload,
  TaskStatusPayload,
} from '../types/api'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// --- Interceptor para adicionar o token de autenticação ---
// Esta função "intercepta" todas as requisições antes de serem enviadas
// e adiciona o token de autenticação no cabeçalho.
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

export default {
  // --- FUNÇÃO DE LOGIN ---
  login: (credentials: { email: string; password: string }) => {
    // Djoser usa o endpoint 'token/login' para autenticação baseada em token
    return apiClient.post<{ auth_token: string }>('/auth/token/login/', credentials)
  },

  // --- FUNÇÃO DE LOGOUT ---
  logout: () => {
    // Djoser usa o endpoint 'token/logout' para invalidar o token no backend
    return apiClient.post('/auth/token/logout/')
  },

  // --- FUNÇÃO DE REGISTRO ---
  register: (userData: { name: string, email: string, nif: string, password: string }) => {
    // Ele espera 'name', 'email', 'nif', 'password' 
    return apiClient.post<CustomUser>('/auth/users/', userData); 
  },

  // --- FUNÇÃO PARA BUSCAR DADOS DO USUÁRIO LOGADO ---
  getMe: () => {
    // O interceptor adicionará o token automaticamente a esta requisição GET
    return apiClient.get<CustomUser>('/auth/users/me/');
  },

  // Funções de Task (CRUD)
  getTasks: () => apiClient.get<Task[]>('/task/'),
  getTask: (id: number) => apiClient.get<Task>(`/task/${id}/`),
  createTask: (taskData: TaskPayload) => apiClient.post<Task>('/task/', taskData),
  updateTask: (id: number, taskData: TaskPayload) => apiClient.put<Task>(`/task/${id}/`, taskData),
  deleteTask: (id: number) => apiClient.delete(`/task/${id}/`),

  // Funções para preencher formulários
  getUsers: () => apiClient.get<CustomUser[]>('/custom-user/'),
  getEquipments: () => apiClient.get<Equipment[]>('/equipment/'),

  // Função para criar TaskStatus com fluxo de upload de imagem em duas etapas
  createTaskStatus: (payload: TaskStatusPayload) => {
    // Etapa 1: Envia o JSON, espera o novo TaskStatus de volta
    return apiClient.post<TaskStatus>('/task-status/', payload)
  },

  // Upload da Imagem
  uploadTaskStatusImage: (payload: FormData) => {
    // Etapa 2: Envia a imagem associada ao TaskStatus criado
    return apiClient.post('/task-status-image/', payload)
  },
}
