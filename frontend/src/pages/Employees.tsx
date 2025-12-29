import React, { useEffect, useState } from 'react';
import { Employee, EmployeeCreate, EmployeeUpdate } from '../types/employee';
import { employeesService } from '../services/employees';
import EmployeeList from '../components/employees/EmployeeList';
import EmployeeForm from '../components/employees/EmployeeForm';

const Employees: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | undefined>();

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const data = await employeesService.getAll();
      setEmployees(data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingEmployee(undefined);
    setShowForm(true);
  };

  const handleEdit = (employee: Employee) => {
    setEditingEmployee(employee);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this employee?')) return;
    try {
      await employeesService.delete(id);
      fetchEmployees();
    } catch (error) {
      console.error('Error deleting employee:', error);
      alert('Failed to delete employee. Make sure they have no active assignments.');
    }
  };

  const handleSubmit = async (employee: EmployeeCreate | EmployeeUpdate) => {
    try {
      if (editingEmployee) {
        await employeesService.update(editingEmployee.id, employee as EmployeeUpdate);
      } else {
        await employeesService.create(employee as EmployeeCreate);
      }
      setShowForm(false);
      setEditingEmployee(undefined);
      fetchEmployees();
    } catch (error: any) {
      console.error('Error saving employee:', error);
      alert(error.response?.data?.detail || 'Failed to save employee');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingEmployee(undefined);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Employees</h1>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          + Add Employee
        </button>
      </div>

      {showForm ? (
        <EmployeeForm employee={editingEmployee} onSubmit={handleSubmit} onCancel={handleCancel} />
      ) : (
        <EmployeeList employees={employees} onEdit={handleEdit} onDelete={handleDelete} loading={loading} />
      )}
    </div>
  );
};

export default Employees;

