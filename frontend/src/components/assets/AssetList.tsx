import React from 'react';
import { Asset } from '../../types/asset';
import AssetCard from './AssetCard';

interface AssetListProps {
  assets: Asset[];
  onEdit: (asset: Asset) => void;
  onDelete: (id: string) => void;
  loading?: boolean;
}

const AssetList: React.FC<AssetListProps> = ({ assets, onEdit, onDelete, loading }) => {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500">Loading assets...</div>
      </div>
    );
  }

  if (assets.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500">No assets found. Create your first asset to get started.</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {assets.map((asset) => (
        <AssetCard key={asset.id} asset={asset} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </div>
  );
};

export default AssetList;

