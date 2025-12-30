import api from './api';
import { Tenant } from '../types/tenant';

export const tenantsService = {
  getCurrent: async (): Promise<Tenant> => {
    const response = await api.get('/api/tenants/current/info');
    return response.data;
  },

  update: async (tenantId: string, updates: Partial<Tenant>): Promise<Tenant> => {
    const response = await api.put(`/api/tenants/${tenantId}`, updates);
    return response.data;
  },
};

