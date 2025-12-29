import React from 'react';
import { AssignmentWithDetails } from '../../types/assignment';

interface AssignmentListProps {
  assignments: AssignmentWithDetails[];
  onReturn: (id: string) => void;
  loading?: boolean;
}

const AssignmentList: React.FC<AssignmentListProps> = ({ assignments, onReturn, loading }) => {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500">Loading assignments...</div>
      </div>
    );
  }

  if (assignments.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500">No assignments found.</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Employee</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned Date</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Returned Date</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {assignments.map((assignment) => (
            <tr key={assignment.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{assignment.asset_name}</div>
                <div className="text-sm text-gray-500">{assignment.asset_tag}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{assignment.employee_name}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(assignment.assigned_date).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {assignment.returned_date ? new Date(assignment.returned_date).toLocaleDateString() : '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  assignment.status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {assignment.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                {assignment.status === 'active' && (
                  <button
                    onClick={() => onReturn(assignment.id)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Return
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AssignmentList;

