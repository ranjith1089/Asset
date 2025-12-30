import React, { useState } from 'react';
import { AssignmentCreate } from '../../types/assignment';
import { Asset } from '../../types/asset';
import { Employee } from '../../types/employee';

interface AssignmentFormProps {
  assets: Asset[];
  employees: Employee[];
  onSubmit: (assignment: AssignmentCreate) => Promise<void>;
  onCancel: () => void;
}

const AssignmentForm: React.FC<AssignmentFormProps> = ({ assets, employees, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    asset_id: '',
    employee_id: '',
    assigned_date: new Date().toISOString().split('T')[0],
    notes: '',
  });

  const [loading, setLoading] = useState(false);

  // Filter available assets
  const availableAssets = assets.filter(asset => asset.status === 'available');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(formData as AssignmentCreate);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-4">
      <h2 className="text-2xl font-bold mb-4">Assign Asset</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Asset *</label>
          <select
            value={formData.asset_id}
            onChange={(e) => setFormData({ ...formData, asset_id: e.target.value })}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select an asset</option>
            {availableAssets.map((asset) => (
              <option key={asset.id} value={asset.id}>
                {asset.name} ({asset.asset_tag})
              </option>
            ))}
          </select>
          {availableAssets.length === 0 && (
            <p className="mt-1 text-sm text-red-600">No available assets to assign</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Employee *</label>
          <select
            value={formData.employee_id}
            onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select an employee</option>
            {employees.map((employee) => (
              <option key={employee.id} value={employee.id}>
                {employee.name} ({employee.email})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Assigned Date *</label>
          <input
            type="date"
            value={formData.assigned_date}
            onChange={(e) => setFormData({ ...formData, assigned_date: e.target.value })}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={loading || availableAssets.length === 0}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
        >
          {loading ? 'Assigning...' : 'Assign Asset'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default AssignmentForm;

