import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function ProviderDashboard() {
  const [dashboard, setDashboard] = useState({
    total_apis: 0,
    published_apis: 0,
    active_developers: 0,
    total_requests: 0,
    api_revenue: 0,
    top_endpoints: [],
    error_rate: 0,
    average_response_time_ms: 0,
  });

  const [loading, setLoading] = useState(true);

  const loadDashboard = async () => {
    try {
      const response = await API.get("/dashboards/provider");

      setDashboard(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load provider dashboard"
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
            Provider Dashboard
          </h1>

          <p className="mt-2 text-slate-600">
            API performance and usage overview
          </p>
        </div>

        {/* API Statistics */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            API Statistics
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
                {dashboard.published_apis}
              </p>
            </div>

            <div className="rounded-lg border bg-white p-5 shadow-sm">
              <p className="text-sm text-slate-500">
                Active Developers
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.active_developers}
              </p>
            </div>

          </div>
        </div>

        {/* Usage Statistics */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Usage Statistics
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
                Error Rate
              </p>

              <p className="mt-2 text-3xl font-bold text-blue-600">
                {dashboard.error_rate}%
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

        {/* Revenue */}
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Revenue
          </h2>

          <div className="rounded-lg border bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">
              API Revenue
            </p>

            <p className="mt-2 text-3xl font-bold text-blue-600">
              ₹{dashboard.api_revenue.toFixed(2)}
            </p>
          </div>
        </div>

        {/* Top Endpoints */}
        <div>
          <h2 className="mb-4 text-xl font-semibold text-slate-900">
            Top Endpoints
          </h2>

          <div className="overflow-x-auto rounded-lg border bg-white shadow-sm">

            <table className="w-full text-left">
              <thead className="border-b bg-slate-100">
                <tr>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-700">
                    Endpoint ID
                  </th>

                  <th className="px-4 py-3 text-sm font-semibold text-slate-700">
                    Method
                  </th>

                  <th className="px-4 py-3 text-sm font-semibold text-slate-700">
                    Path
                  </th>

                  <th className="px-4 py-3 text-sm font-semibold text-slate-700">
                    Request Count
                  </th>
                </tr>
              </thead>

              <tbody>
                {dashboard.top_endpoints.length === 0 ? (
                  <tr>
                    <td
                      colSpan="4"
                      className="px-4 py-6 text-center text-slate-500"
                    >
                      No endpoint usage found
                    </td>
                  </tr>
                ) : (
                  dashboard.top_endpoints.map((endpoint) => (
                    <tr
                      key={endpoint.endpoint_id}
                      className="border-b last:border-b-0"
                    >
                      <td className="px-4 py-3 text-slate-700">
                        {endpoint.endpoint_id}
                      </td>

                      <td className="px-4 py-3 text-slate-700">
                        {endpoint.method}
                      </td>

                      <td className="px-4 py-3 text-slate-700">
                        {endpoint.path}
                      </td>

                      <td className="px-4 py-3 font-medium text-blue-600">
                        {endpoint.request_count}
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

export default ProviderDashboard;