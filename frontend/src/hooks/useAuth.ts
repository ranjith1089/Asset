import { useState, useEffect } from 'react';
import { createClient, SupabaseClient, User } from '@supabase/supabase-js';
import api from '../services/api';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  theme?: Record<string, any>;
  status: string;
  subscription_plan: string;
  subscription_status: string;
}

export interface UserInfo {
  id: string;
  email: string;
  name?: string;
  tenant_id?: string;
  role?: string;
  status?: string;
}

export interface AuthContextType {
  user: User | null;
  userInfo: UserInfo | null;
  tenant: Tenant | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string, organizationName: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  refreshUserInfo: () => Promise<void>;
}

export const useAuth = (): AuthContextType => {
  const [user, setUser] = useState<User | null>(null);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUserInfo = async (_userId: string) => {
    try {
      const response = await api.get('/api/auth/me');
      setUserInfo(response.data);
      
      // Load tenant info if tenant_id exists
      if (response.data.tenant_id) {
        try {
          const tenantResponse = await api.get(`/api/tenants/current/info`);
          setTenant(tenantResponse.data);
        } catch (error) {
          console.error('Failed to load tenant info:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load user info:', error);
    }
  };

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      setUser(session?.user ?? null);
      if (session?.user) {
        await loadUserInfo(session.user.id);
      }
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setUser(session?.user ?? null);
      if (session?.user) {
        await loadUserInfo(session.user.id);
      } else {
        setUserInfo(null);
        setTenant(null);
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    // User info will be loaded by the auth state change listener
  };

  const signUp = async (email: string, password: string, name: string, organizationName: string) => {
    await api.post('/api/auth/signup', {
      email,
      password,
      name,
      organization_name: organizationName
    });
    // User will be created in Supabase auth by the backend
    // Then sign in
    await signIn(email, password);
  };

  const signOut = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    setUserInfo(null);
    setTenant(null);
  };

  const resetPassword = async (email: string) => {
    const redirectUrl = `${window.location.origin}/reset-password`;
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: redirectUrl,
    });
    if (error) throw error;
  };

  const refreshUserInfo = async () => {
    if (user) {
      await loadUserInfo(user.id);
    }
  };

  return { user, userInfo, tenant, loading, signIn, signUp, signOut, resetPassword, refreshUserInfo };
};

