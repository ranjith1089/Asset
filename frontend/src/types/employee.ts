export interface Employee {
  id: string;
  name: string;
  email: string;
  department?: string;
  position?: string;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  name: string;
  email: string;
  department?: string;
  position?: string;
}

export interface EmployeeUpdate {
  name?: string;
  email?: string;
  department?: string;
  position?: string;
}

