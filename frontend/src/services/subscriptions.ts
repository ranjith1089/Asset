import api from './api';

export interface Subscription {
  id: string;
  tenant_id: string;
  plan: 'free' | 'trial' | 'basic' | 'premium' | 'enterprise';
  status: 'active' | 'cancelled' | 'expired';
  current_period_start?: string;
  current_period_end?: string;
  cancel_at_period_end: boolean;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: string;
  tenant_id: string;
  subscription_id?: string;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'failed';
  due_date?: string;
  paid_at?: string;
  created_at: string;
  updated_at: string;
}

export const subscriptionsService = {
  getCurrent: async (): Promise<Subscription> => {
    const response = await api.get('/api/subscription');
    return response.data;
  },

  upgrade: async (plan: string): Promise<Subscription> => {
    const response = await api.post(`/api/subscription/upgrade?plan=${plan}`);
    return response.data.subscription || response.data;
  },

  cancel: async (): Promise<void> => {
    await api.post('/api/subscription/cancel');
  },

  getInvoices: async (): Promise<Invoice[]> => {
    const response = await api.get('/api/subscription/invoices');
    return response.data;
  },
};

