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
  qr_code_image: string | null;
}

// Tipo para os *valores* de status
export type TaskStatusValue = 'OPEN' | 'WAITING_RESPONSIBLE' | 'ONGOING' | 'DONE' | 'FINISHED' | 'CANCELLED';

export interface Task {
  id: number;
  name: string;
  description: string;
  suggested_date: string | null;
  urgency_level: string;
  creation_date: string;
  creator_FK: CustomUser | null;
  equipments_FK: Equipment[];
  responsibles_FK: CustomUser[];
  status_history: TaskStatus[];
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

export interface TaskStatusPayload {
  status: string;
  comment: string | null;
  task_FK: number;
  user_FK: number;
}

// Para a funcionalidade de upload de imagem
// Descreve a resposta da API para uma imagem de status
export interface TaskStatusImage {
  id: number;
  image: string; // O backend envia a URL da imagem
  task_status_FK: number;
}

// Descreve a resposta da API para um objeto TaskStatus
export interface TaskStatus {
  id: number;
  status: TaskStatusValue;
  status_date: string;
  comment: string | null;
  task_FK: number;
  // user_FK: CustomUser | null;
  user_detail: CustomUser | null;
  images: TaskStatusImage[]; // O campo 'images' que definimos no serializer
}