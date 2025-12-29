export interface Assignment {
  id: string;
  asset_id: string;
  employee_id: string;
  assigned_by: string;
  assigned_date: string;
  returned_date?: string;
  notes?: string;
  status: 'active' | 'returned';
  created_at: string;
  updated_at: string;
}

export interface AssignmentWithDetails extends Assignment {
  asset_name?: string;
  asset_tag?: string;
  employee_name?: string;
}

export interface AssignmentCreate {
  asset_id: string;
  employee_id: string;
  assigned_date: string;
  notes?: string;
}

export interface AssignmentReturn {
  returned_date?: string;
  notes?: string;
}

