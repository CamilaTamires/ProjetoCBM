import axios from 'axios';
import type { 
  Task, 
  CustomUser, 
  Equipment, 
  TaskPayload, 
  TaskStatusPayload // <-- Verifique se este import está aqui
} from '../types/api';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', 
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
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
    return apiClient.post('/task-status/', payload);
  },
};