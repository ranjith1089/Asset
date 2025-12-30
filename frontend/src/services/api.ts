import axios from 'axios';
import { supabase } from '../hooks/useAuth';

// Ensure API_URL is a full URL with protocol
let API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
if (API_URL && !API_URL.startsWith('http://') && !API_URL.startsWith('https://')) {
  // If URL doesn't have protocol, assume https in production
  API_URL = `https://${API_URL}`;
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Log error details for debugging
    if (error.message === 'Network Error' || !error.response) {
      console.error('Network Error:', {
        message: error.message,
        baseURL: API_URL,
        url: error.config?.url,
        fullURL: error.config?.baseURL + error.config?.url,
      });
    }
    
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      await supabase.auth.signOut();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

