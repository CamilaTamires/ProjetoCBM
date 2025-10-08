// DENTRO DO ARQUIVO: src/types/api.ts

export interface Category {
  id: number;
  name: string;
}

export interface Environment {
  id: number;
  name: string;
}

export interface CustomUser {
  id: number;
  name: string;
  email: string;
}

export interface Equipment {
  id: number;
  name: string;
  code: string;
  description: string;
  environment_FK: Environment | null;
  category_FK: Category | null;
}

export type TaskStatus = 'OPEN' | 'WAITING_RESPONSIBLE' | 'ONGOING' | 'DONE' | 'FINISHED' | 'CANCELLED';

export interface Task {
  id: number;
  name: string;
  description: string;
  suggested_date: string | null;
  urgency_level: string;
  creation_date: string;
  current_status: TaskStatus | null;
  creator_FK: CustomUser | null;
  equipments_FK: Equipment[];
  responsibles_FK: CustomUser[];
}

export interface TaskPayload {
  name: string;
  description: string;
  suggested_date: string | null;
  urgency_level: string;
  creator_FK: number | null;
  equipments_FK: number[];
  responsibles_FK: number[];
}

// --- ESTA É A INTERFACE QUE ESTAVA FALTANDO ---
// Descreve o objeto que enviamos para criar um novo registro de status
export interface TaskStatusPayload {
  status: string;
  comment: string | null;
  task_FK: number;
  user_FK: number;
}