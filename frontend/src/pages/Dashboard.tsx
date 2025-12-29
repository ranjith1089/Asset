import React, { useEffect, useState } from 'react';
import { assetsService } from '../services/assets';
import { employeesService } from '../services/employees';
import { assignmentsService } from '../services/assignments';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    totalAssets: 0,
    availableAssets: 0,
    assignedAssets: 0,
    totalEmployees: 0,
    activeAssignments: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [assets, employees, assignments] = await Promise.all([
          assetsService.getAll(),
          employeesService.getAll(),
          assignmentsService.getAll({ status: 'active' }),
        ]);

        const available = assets.filter(a => a.status === 'available').length;
        const assigned = assets.filter(a => a.status === 'assigned').length;

        setStats({
          totalAssets: assets.length,
          availableAssets: available,
          assignedAssets: assigned,
          totalEmployees: employees.length,
          activeAssignments: assignments.length,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading dashboard...</div>;
  }

  const statCards = [
    { label: 'Total Assets', value: stats.totalAssets, color: 'bg-blue-500' },
    { label: 'Available Assets', value: stats.availableAssets, color: 'bg-green-500' },
    { label: 'Assigned Assets', value: stats.assignedAssets, color: 'bg-yellow-500' },
    { label: 'Total Employees', value: stats.totalEmployees, color: 'bg-purple-500' },
    { label: 'Active Assignments', value: stats.activeAssignments, color: 'bg-indigo-500' },
  ];

  return (
    <div>
      <div className="mb-6 flex items-center gap-4">
        <img 
          src="/logo.png" 
          alt="Logo" 
          className="h-12 w-auto object-contain"
          onError={(e) => {
            // Fallback if logo doesn't exist
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
        <h1 className="text-3xl font-bold">Dashboard</h1>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {statCards.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow-md p-6">
            <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center text-white text-2xl font-bold mb-4`}>
              {stat.value}
            </div>
            <h3 className="text-sm font-medium text-gray-500">{stat.label}</h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;

