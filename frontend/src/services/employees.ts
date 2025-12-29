import api from './api';
import { Employee, EmployeeCreate, EmployeeUpdate } from '../types/employee';

export const employeesService = {
  getAll: async (params?: { department?: string }) => {
    const response = await api.get<Employee[]>('/api/employees', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get<Employee>(`/api/employees/${id}`);
    return response.data;
  },

  create: async (employee: EmployeeCreate) => {
    const response = await api.post<Employee>('/api/employees', employee);
    return response.data;
  },

  update: async (id: string, employee: EmployeeUpdate) => {
    const response = await api.put<Employee>(`/api/employees/${id}`, employee);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/api/employees/${id}`);
  },
};

