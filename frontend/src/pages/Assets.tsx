import React, { useEffect, useState } from 'react';
import { Asset, AssetCreate, AssetUpdate } from '../types/asset';
import { assetsService } from '../services/assets';
import AssetList from '../components/assets/AssetList';
import AssetForm from '../components/assets/AssetForm';

const Assets: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | undefined>();
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterCategory, setFilterCategory] = useState<string>('');

  useEffect(() => {
    fetchAssets();
  }, [filterStatus, filterCategory]);

  const fetchAssets = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filterStatus) params.status = filterStatus;
      if (filterCategory) params.category = filterCategory;
      const data = await assetsService.getAll(params);
      setAssets(data);
    } catch (error) {
      console.error('Error fetching assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingAsset(undefined);
    setShowForm(true);
  };

  const handleEdit = (asset: Asset) => {
    setEditingAsset(asset);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this asset?')) return;
    try {
      await assetsService.delete(id);
      fetchAssets();
    } catch (error) {
      console.error('Error deleting asset:', error);
      alert('Failed to delete asset. Make sure it has no active assignments.');
    }
  };

  const handleSubmit = async (asset: AssetCreate | AssetUpdate) => {
    try {
      if (editingAsset) {
        await assetsService.update(editingAsset.id, asset as AssetUpdate);
      } else {
        await assetsService.create(asset as AssetCreate);
      }
      setShowForm(false);
      setEditingAsset(undefined);
      fetchAssets();
    } catch (error: any) {
      console.error('Error saving asset:', error);
      alert(error.response?.data?.detail || 'Failed to save asset');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingAsset(undefined);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Assets</h1>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          + Add Asset
        </button>
      </div>

      {showForm ? (
        <AssetForm asset={editingAsset} onSubmit={handleSubmit} onCancel={handleCancel} />
      ) : (
        <>
          <div className="bg-white rounded-lg shadow-md p-4 mb-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Status</label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Statuses</option>
                  <option value="available">Available</option>
                  <option value="assigned">Assigned</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="retired">Retired</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Category</label>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Categories</option>
                  <option value="laptop">Laptop</option>
                  <option value="headphone">Headphone</option>
                  <option value="monitor">Monitor</option>
                  <option value="keyboard">Keyboard</option>
                  <option value="mouse">Mouse</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <AssetList assets={assets} onEdit={handleEdit} onDelete={handleDelete} loading={loading} />
        </>
      )}
    </div>
  );
};

export default Assets;

