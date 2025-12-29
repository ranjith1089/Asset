import React, { useEffect, useState } from 'react';
import { AssignmentWithDetails, AssignmentCreate, AssignmentReturn } from '../types/assignment';
import { assignmentsService } from '../services/assignments';
import { assetsService } from '../services/assets';
import { employeesService } from '../services/employees';
import { Asset } from '../types/asset';
import { Employee } from '../types/employee';
import AssignmentList from '../components/assignments/AssignmentList';
import AssignmentForm from '../components/assignments/AssignmentForm';

const Assignments: React.FC = () => {
  const [assignments, setAssignments] = useState<AssignmentWithDetails[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('');

  useEffect(() => {
    fetchData();
  }, [filterStatus]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filterStatus) params.status = filterStatus;
      const [assignmentsData, assetsData, employeesData] = await Promise.all([
        assignmentsService.getAll(params),
        assetsService.getAll(),
        employeesService.getAll(),
      ]);
      setAssignments(assignmentsData);
      setAssets(assetsData);
      setEmployees(employeesData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setShowForm(true);
  };

  const handleReturn = async (id: string) => {
    if (!window.confirm('Are you sure you want to return this asset?')) return;
    try {
      await assignmentsService.return(id, {});
      fetchData();
    } catch (error) {
      console.error('Error returning assignment:', error);
      alert('Failed to return asset');
    }
  };

  const handleSubmit = async (assignment: AssignmentCreate) => {
    try {
      await assignmentsService.create(assignment);
      setShowForm(false);
      fetchData();
    } catch (error: any) {
      console.error('Error creating assignment:', error);
      alert(error.response?.data?.detail || 'Failed to assign asset');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Assignments</h1>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          + New Assignment
        </button>
      </div>

      {showForm ? (
        <AssignmentForm
          assets={assets}
          employees={employees}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      ) : (
        <>
          <div className="bg-white rounded-lg shadow-md p-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Filter by Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="returned">Returned</option>
              </select>
            </div>
          </div>

          <AssignmentList assignments={assignments} onReturn={handleReturn} loading={loading} />
        </>
      )}
    </div>
  );
};

export default Assignments;

