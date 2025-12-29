export interface Asset {
  id: string;
  asset_tag: string;
  name: string;
  category: string;
  brand?: string;
  model?: string;
  serial_number?: string;
  purchase_date?: string;
  purchase_price?: number;
  status: 'available' | 'assigned' | 'maintenance' | 'retired';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface AssetCreate {
  asset_tag: string;
  name: string;
  category: string;
  brand?: string;
  model?: string;
  serial_number?: string;
  purchase_date?: string;
  purchase_price?: number;
  status?: 'available' | 'assigned' | 'maintenance' | 'retired';
  notes?: string;
}

export interface AssetUpdate {
  asset_tag?: string;
  name?: string;
  category?: string;
  brand?: string;
  model?: string;
  serial_number?: string;
  purchase_date?: string;
  purchase_price?: number;
  status?: 'available' | 'assigned' | 'maintenance' | 'retired';
  notes?: string;
}

