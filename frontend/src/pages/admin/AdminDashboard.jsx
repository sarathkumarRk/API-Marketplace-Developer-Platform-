import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function AdminDashboard() {
  const [dashboard, setDashboard] = useState({
    total_users: 0,
    total_developers: 0,
    total_providers: 0,
    total_apis: 0,
    total_published_apis: 0,
    active_subscriptions: 0,
    platform_revenue: 0,
    total_requests: 0,
    successful_requests: 0,
    failed_requests: 0,
    average_response_time_ms: 0,
  });

  const [loading, setLoading] = useState(true);

  const loadDashboard = async () => {
    try {
      const response = await API.get("/dashboards/admin");

      setDashboard(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load admin dashboard"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 p-6">
        <div className="mx-auto max-w-7xl">
          <p className="text-blue-600">
            Loading dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-7xl">

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">
            Admin Dashboard
          </h1>

          <p className="mt-2 text-slate-600">
            Platform overview and API marketplace statistics
          </p>
        </div>

        {/* User Statistics */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Users
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Total Users
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.total_users}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Developers
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.total_developers}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                API Providers
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.total_providers}
              </p>
            </div>

          </div>
        </div>

        {/* API Statistics */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            APIs
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Total APIs
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.total_apis}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Published APIs
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.total_published_apis}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Active Subscriptions
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.active_subscriptions}
              </p>
            </div>

          </div>
        </div>

        {/* Platform Statistics */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Platform Statistics
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Platform Revenue
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                ₹{dashboard.platform_revenue.toFixed(2)}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Average Response Time
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.average_response_time_ms} ms
              </p>
            </div>

          </div>
        </div>

        {/* Request Statistics */}
        <div>
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            API Requests
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Total Requests
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.total_requests}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Successful Requests
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.successful_requests}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Failed Requests
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.failed_requests}
              </p>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}

export default AdminDashboard;