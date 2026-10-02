import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function DeveloperDashboard() {
  const [dashboard, setDashboard] = useState({
    total_subscriptions: 0,
    active_subscriptions: 0,
    active_apis: 0,
    api_requests_today: 0,
    monthly_usage: 0,
    total_requests: 0,
    successful_requests: 0,
    failed_requests: 0,
    rate_limits: [],
    average_response_time_ms: 0,
  });

  const [loading, setLoading] = useState(true);

  const loadDashboard = async () => {
    try {
      const response = await API.get("/dashboards/developer");

      setDashboard(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load developer dashboard"
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
            Developer Dashboard
          </h1>

          <p className="mt-2 text-slate-600">
            Your API subscriptions and usage overview
          </p>
        </div>

        {/* Subscription Statistics */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Subscriptions
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Total Subscriptions
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.total_subscriptions}
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

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Active APIs
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.active_apis}
              </p>
            </div>

          </div>
        </div>

        {/* Usage Statistics */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Usage Statistics
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Requests Today
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.api_requests_today}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Monthly Usage
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.monthly_usage}
              </p>
            </div>

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
                Average Response Time
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.average_response_time_ms} ms
              </p>
            </div>

          </div>
        </div>

        {/* Request Results */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Request Results
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">

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

        {/* Rate Limits */}
        <div>
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Rate Limits
          </h2>

          <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">

            <table className="w-full text-left">
              <thead className="border-b bg-slate-100">
                <tr>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-700">
                    API ID
                  </th>

                  <th className="px-4 py-3 text-sm font-semibold text-slate-700">
                    Plan Name
                  </th>

                  <th className="px-4 py-3 text-sm font-semibold text-slate-700">
                    Requests / Minute
                  </th>

                  <th className="px-4 py-3 text-sm font-semibold text-slate-700">
                    Requests / Month
                  </th>
                </tr>
              </thead>

              <tbody>
                {dashboard.rate_limits.length === 0 ? (
                  <tr>
                    <td
                      colSpan="4"
                      className="px-4 py-6 text-center text-slate-500"
                    >
                      No active API plans found
                    </td>
                  </tr>
                ) : (
                  dashboard.rate_limits.map((plan, index) => (
                    <tr
                      key={`${plan.api_id}-${plan.plan_name}-${index}`}
                      className="border-b last:border-b-0"
                    >
                      <td className="px-4 py-3 text-slate-700">
                        {plan.api_id}
                      </td>

                      <td className="px-4 py-3 text-slate-700">
                        {plan.plan_name}
                      </td>

                      <td className="px-4 py-3 text-slate-700">
                        {plan.requests_per_minute}
                      </td>

                      <td className="px-4 py-3 text-slate-700">
                        {plan.requests_per_month}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>

          </div>
        </div>

      </div>
    </div>
  );
}

export default DeveloperDashboard;