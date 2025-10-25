import axios from 'axios'
import type {
  Task,
  CustomUser,
  Equipment,
  TaskStatus,
  TaskPayload,
  TaskStatusPayload, // <-- Verifique se este import está aqui
} from '../types/api'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// --- NOVO: Interceptor para adicionar o token de autenticação ---
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
  // --- NOVA FUNÇÃO DE LOGIN ---
  login: (credentials: { email: string; password: string }) => {
    // Djoser usa o endpoint 'token/login' para autenticação baseada em token
    return apiClient.post<{ auth_token: string }>('/auth/token/login/', credentials)
  },

  // --- NOVA FUNÇÃO DE LOGOUT ---
  logout: () => {
    // Djoser usa o endpoint 'token/logout' para invalidar o token no backend
    return apiClient.post('/auth/token/logout/')
  },

  // --- NOVA FUNÇÃO DE REGISTRO ---
  register: (userData: { name: string, email: string, nif: string, password: string }) => {
    // Ele espera 'name', 'email', 'nif', 'password' 
    return apiClient.post<CustomUser>('/auth/users/', userData); 
  },

  // --- NOVA FUNÇÃO PARA BUSCAR DADOS DO USUÁRIO LOGADO ---
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

  // ESTA É A FUNÇÃO QUE O ERRO ESTÁ APONTANDO
  // Garanta que ela esteja dentro do objeto 'export default'
  createTaskStatus: (payload: TaskStatusPayload) => {
    // Etapa 1: Envia o JSON, espera o novo TaskStatus de volta
    return apiClient.post<TaskStatus>('/task-status/', payload)
  },

  // NOVA FUNÇÃO para Etapa 3: Upload da Imagem
  uploadTaskStatusImage: (payload: FormData) => {
    // O Axios é inteligente: quando ele vê um FormData, ele
    // automaticamente usa 'multipart/form-data'.
    // O interceptor de token ainda será aplicado.
    return apiClient.post('/task-status-image/', payload)
  },
}
