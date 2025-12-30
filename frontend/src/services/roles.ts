import api from './api';
import { Role, RoleCreate, RoleUpdate } from '../types/role';

export const rolesService = {
  getAll: async (): Promise<Role[]> => {
    const response = await api.get('/api/roles');
    return response.data;
  },

  getById: async (id: string): Promise<Role> => {
    const response = await api.get(`/api/roles/${id}`);
    return response.data;
  },

  create: async (role: RoleCreate): Promise<Role> => {
    const response = await api.post('/api/roles', role);
    return response.data;
  },

  update: async (id: string, role: RoleUpdate): Promise<Role> => {
    const response = await api.put(`/api/roles/${id}`, role);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/roles/${id}`);
  },
};

