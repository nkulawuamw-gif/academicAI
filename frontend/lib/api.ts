import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type { Attachment } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  },
);

export default api;

export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  googleAuth: (code: string) =>
    api.post('/auth/google', { code }),
  refreshToken: (refresh_token: string) =>
    api.post('/auth/refresh', { refresh_token }),
  forgotPassword: (email: string) =>
    api.post('/auth/forgot-password', { email }),
  resetPassword: (token: string, password: string) =>
    api.post('/auth/reset-password', { token, password }),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data: Record<string, unknown>) =>
    api.put('/auth/profile', data),
};

export const chatApi = {
  getConversations: (page = 1, perPage = 20) =>
    api.get(`/chat/conversations?page=${page}&per_page=${perPage}`),
  createConversation: (data: { title?: string; context?: Record<string, unknown> }) =>
    api.post('/chat/conversations', data),
  getConversation: (id: string) =>
    api.get(`/chat/conversations/${id}`),
  updateConversation: (id: string, data: { title?: string }) =>
    api.put(`/chat/conversations/${id}`, data),
  deleteConversation: (id: string) =>
    api.delete(`/chat/conversations/${id}`),
  getMessages: (conversationId: string) =>
    api.get(`/chat/conversations/${conversationId}/messages`),
  sendMessage: (conversationId: string, data: { content: string; attachments?: Attachment[] }) =>
    api.post(`/chat/conversations/${conversationId}/messages`, data),
  uploadFile: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/chat/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const researchApi = {
  search: (data: { query: string; max_sources?: number; include_summary?: boolean; include_citations?: boolean }) =>
    api.post('/research/search', data),
  literatureReview: (data: { topic: string; sources: string[]; format?: string }) =>
    api.post('/research/literature-review', data),
};

export const writingApi = {
  generate: (data: { prompt: string; type?: string; length?: string; tone?: string; additional_instructions?: string }) =>
    api.post('/writing/generate', data),
  outline: (data: { topic: string; sections?: number; depth?: string }) =>
    api.post('/writing/outline', data),
};

export const paraphraseApi = {
  paraphrase: (data: { text: string; mode?: string; intensity?: string }) =>
    api.post('/paraphrase', data),
};

export const citationApi = {
  generate: (data: { style: string; source_text: string }) =>
    api.post('/citations/generate', data),
  create: (data: Record<string, unknown>) =>
    api.post('/citations', data),
  list: (page = 1, perPage = 20) =>
    api.get(`/citations?page=${page}&per_page=${perPage}`),
};

export const studyApi = {
  generateQuiz: (data: { topic: string; difficulty?: string; question_count?: number }) =>
    api.post('/study/quizzes/generate', data),
  submitQuiz: (quizId: string, answers: Record<string, string>) =>
    api.post(`/study/quizzes/${quizId}/submit`, { answers }),
  getQuiz: (quizId: string) =>
    api.get(`/study/quizzes/${quizId}`),
  generateFlashcards: (data: { topic: string; count?: number }) =>
    api.post('/study/flashcards/generate', data),
  getFlashcardSet: (id: string) =>
    api.get(`/study/flashcards/${id}`),
  summarize: (data: { text: string; format?: string; detail_level?: string }) =>
    api.post('/study/summarize', data),
  generateStudyPlan: (data: { subject: string; start_date: string; end_date: string; hours_per_day?: number; topics?: string[] }) =>
    api.post('/study/study-plans/generate', data),
  getStudyPlan: (id: string) =>
    api.get(`/study/study-plans/${id}`),
};

export const documentApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => api.get('/documents'),
  get: (id: string) => api.get(`/documents/${id}`),
  delete: (id: string) => api.delete(`/documents/${id}`),
  ask: (documentId: string, question: string) => {
    const formData = new FormData();
    formData.append('question', question);
    return api.post(`/documents/${documentId}/ask`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const adminApi = {
  getUsers: (page = 1, perPage = 20) =>
    api.get(`/admin/users?page=${page}&per_page=${perPage}`),
  getAnalytics: () => api.get('/admin/analytics'),
  toggleUserActive: (userId: string) =>
    api.put(`/admin/users/${userId}/toggle-active`),
};
