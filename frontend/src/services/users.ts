import api from './api';
import { User } from '../types/user';

export const usersService = {
  getAll: async (): Promise<User[]> => {
    const response = await api.get('/api/users');
    return response.data;
  },

  getById: async (id: string): Promise<User> => {
    const response = await api.get(`/api/users/${id}`);
    return response.data;
  },

  create: async (user: Partial<User>): Promise<User> => {
    const response = await api.post('/api/users', user);
    return response.data;
  },

  update: async (id: string, user: Partial<User>): Promise<User> => {
    const response = await api.put(`/api/users/${id}`, user);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/users/${id}`);
  },

  changeRole: async (id: string, role: string): Promise<User> => {
    const response = await api.post(`/api/users/${id}/change-role`, null, {
      params: { new_role: role }
    });
    return response.data.user;
  },
};

