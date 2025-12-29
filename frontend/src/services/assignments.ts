import api from './api';
import { AssignmentWithDetails, AssignmentCreate, AssignmentReturn } from '../types/assignment';

export const assignmentsService = {
  getAll: async (params?: { status?: string; asset_id?: string; employee_id?: string }) => {
    const response = await api.get<AssignmentWithDetails[]>('/api/assignments', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get<AssignmentWithDetails>(`/api/assignments/${id}`);
    return response.data;
  },

  create: async (assignment: AssignmentCreate) => {
    const response = await api.post<AssignmentWithDetails>('/api/assignments', assignment);
    return response.data;
  },

  return: async (id: string, returnData: AssignmentReturn) => {
    const response = await api.put<AssignmentWithDetails>(`/api/assignments/${id}/return`, returnData);
    return response.data;
  },
};

