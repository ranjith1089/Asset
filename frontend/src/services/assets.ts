import api from './api';
import { Asset, AssetCreate, AssetUpdate } from '../types/asset';

export const assetsService = {
  getAll: async (params?: { status?: string; category?: string }) => {
    const response = await api.get<Asset[]>('/api/assets', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get<Asset>(`/api/assets/${id}`);
    return response.data;
  },

  create: async (asset: AssetCreate) => {
    const response = await api.post<Asset>('/api/assets', asset);
    return response.data;
  },

  update: async (id: string, asset: AssetUpdate) => {
    const response = await api.put<Asset>(`/api/assets/${id}`, asset);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/api/assets/${id}`);
  },
};

