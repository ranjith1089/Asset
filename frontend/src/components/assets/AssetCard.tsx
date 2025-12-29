import React from 'react';
import { Asset } from '../../types/asset';

interface AssetCardProps {
  asset: Asset;
  onEdit: (asset: Asset) => void;
  onDelete: (id: string) => void;
}

const AssetCard: React.FC<AssetCardProps> = ({ asset, onEdit, onDelete }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'assigned':
        return 'bg-blue-100 text-blue-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      case 'retired':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">{asset.name}</h3>
          <p className="text-sm text-gray-500">{asset.asset_tag}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(asset.status)}`}>
          {asset.status}
        </span>
      </div>

      <div className="space-y-2 text-sm text-gray-600 mb-4">
        <p><span className="font-medium">Category:</span> {asset.category}</p>
        {asset.brand && <p><span className="font-medium">Brand:</span> {asset.brand}</p>}
        {asset.model && <p><span className="font-medium">Model:</span> {asset.model}</p>}
        {asset.serial_number && <p><span className="font-medium">Serial:</span> {asset.serial_number}</p>}
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => onEdit(asset)}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(asset.id)}
          className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
};

export default AssetCard;

