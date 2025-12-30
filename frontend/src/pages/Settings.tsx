import React, { useState, useEffect } from 'react';
import { tenantsService } from '../services/tenants';
import { subscriptionsService, Invoice } from '../services/subscriptions';
import { useAuth } from '../hooks/useAuth';
import { TenantUpdate } from '../types/tenant';

const Settings: React.FC = () => {
  const { tenant, userInfo, refreshUserInfo } = useAuth();
  const [subscription, setSubscription] = useState<any>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'general' | 'subscription' | 'billing'>('general');
  const [formData, setFormData] = useState<TenantUpdate>({
    name: '',
    logo_url: '',
  });

  useEffect(() => {
    fetchData();
  }, [tenant]);

  const fetchData = async () => {
    try {
      setLoading(true);
      if (tenant) {
        setFormData({
          name: tenant.name,
          logo_url: tenant.logo_url || '',
        });
      }
      
      const subData = await subscriptionsService.getCurrent();
      setSubscription(subData);
      
      const invoiceData = await subscriptionsService.getInvoices();
      setInvoices(invoiceData);
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tenant) return;
    
    try {
      await tenantsService.update(tenant.id, formData);
      await refreshUserInfo();
      alert('Settings saved successfully');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save settings');
    }
  };

  const handleUpgrade = async (plan: string) => {
    if (!window.confirm(`Upgrade to ${plan} plan?`)) return;
    try {
      await subscriptionsService.upgrade(plan);
      await fetchData();
      alert('Subscription upgraded successfully');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to upgrade subscription');
    }
  };

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription?')) return;
    try {
      await subscriptionsService.cancel();
      await fetchData();
      alert('Subscription will be cancelled at the end of the current period');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to cancel subscription');
    }
  };

  const canManageSettings = userInfo?.role === 'tenant_admin' || userInfo?.role === 'super_admin';

  if (loading) {
    return <div className="text-center py-8">Loading settings...</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('general')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'general'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              General
            </button>
            <button
              onClick={() => setActiveTab('subscription')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'subscription'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Subscription
            </button>
            <button
              onClick={() => setActiveTab('billing')}
              className={`px-6 py-3 text-sm font-medium border-b-2 ${
                activeTab === 'billing'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Billing
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'general' && (
            <form onSubmit={handleSave} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organization Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  disabled={!canManageSettings}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Logo URL
                </label>
                <input
                  type="url"
                  value={formData.logo_url || ''}
                  onChange={(e) => setFormData({ ...formData, logo_url: e.target.value })}
                  disabled={!canManageSettings}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  placeholder="https://example.com/logo.png"
                />
                {formData.logo_url && (
                  <div className="mt-2">
                    <img
                      src={formData.logo_url}
                      alt="Logo preview"
                      className="h-16 w-auto object-contain"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  </div>
                )}
              </div>

              {canManageSettings && (
                <div>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    Save Changes
                  </button>
                </div>
              )}
            </form>
          )}

          {activeTab === 'subscription' && (
            <div className="space-y-6">
              {subscription && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Current Subscription</h3>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Plan:</span>
                      <span className="font-medium capitalize">{subscription.plan}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <span
                        className={`font-medium ${
                          subscription.status === 'active'
                            ? 'text-green-600'
                            : subscription.status === 'cancelled'
                            ? 'text-yellow-600'
                            : 'text-red-600'
                        }`}
                      >
                        {subscription.status}
                      </span>
                    </div>
                    {subscription.current_period_end && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Renews:</span>
                        <span className="font-medium">
                          {new Date(subscription.current_period_end).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {canManageSettings && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Upgrade Plan</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {['basic', 'premium', 'enterprise'].map((plan) => (
                      <div
                        key={plan}
                        className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 cursor-pointer"
                        onClick={() => handleUpgrade(plan)}
                      >
                        <h4 className="font-semibold capitalize mb-2">{plan}</h4>
                        <p className="text-sm text-gray-600">Upgrade to {plan} plan</p>
                      </div>
                    ))}
                  </div>

                  {subscription?.status === 'active' && !subscription?.cancel_at_period_end && (
                    <div className="mt-6">
                      <button
                        onClick={handleCancel}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                      >
                        Cancel Subscription
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {activeTab === 'billing' && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Invoice History</h3>
              {invoices.length === 0 ? (
                <p className="text-gray-500">No invoices found</p>
              ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Amount
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {invoices.map((invoice) => (
                        <tr key={invoice.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(invoice.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {invoice.currency} {invoice.amount.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 py-1 text-xs rounded-full ${
                                invoice.status === 'paid'
                                  ? 'bg-green-100 text-green-800'
                                  : invoice.status === 'pending'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {invoice.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;

