import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function UsageAnalytics() {
  const [usage, setUsage] = useState([]);
  const [analytics, setAnalytics] = useState({
    total_requests: 0,
    successful_requests: 0,
    failed_requests: 0,
    average_response_time_ms: 0,
    error_rate: 0,
  });

  const [apiId, setApiId] = useState("");
  const [apiUsage, setApiUsage] = useState([]);

  const loadMyUsage = async () => {
    try {
      const response = await API.get("/usage/my");
      setUsage(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load usage"
      );
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await API.get("/usage/analytics");
      setAnalytics(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load analytics"
      );
    }
  };

  const loadAPIUsage = async (e) => {
    e.preventDefault();

    if (!apiId) {
      toast.error("Enter API ID");
      return;
    }

    try {
      const response = await API.get(
        `/usage/api/${apiId}`
      );

      setApiUsage(response.data);

      toast.success("API usage loaded successfully");
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load API usage"
      );
    }
  };

  useEffect(() => {
    loadMyUsage();
    loadAnalytics();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-700">
            Usage Analytics
          </h1>

          <p className="mt-1 text-sm text-slate-600">
            View your API usage and request analytics
          </p>
        </div>

        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">
              Total Requests
            </p>

            <p className="mt-2 text-2xl font-bold text-blue-700">
              {analytics.total_requests}
            </p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">
              Successful Requests
            </p>

            <p className="mt-2 text-2xl font-bold text-blue-700">
              {analytics.successful_requests}
            </p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">
              Failed Requests
            </p>

            <p className="mt-2 text-2xl font-bold text-blue-700">
              {analytics.failed_requests}
            </p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">
              Avg Response Time
            </p>

            <p className="mt-2 text-2xl font-bold text-blue-700">
              {analytics.average_response_time_ms} ms
            </p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">
              Error Rate
            </p>

            <p className="mt-2 text-2xl font-bold text-blue-700">
              {analytics.error_rate}%
            </p>
          </div>
        </div>

        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            API Usage
          </h2>

          <form
            onSubmit={loadAPIUsage}
            className="mb-5 flex flex-col gap-3 sm:flex-row"
          >
            <input
              type="number"
              value={apiId}
              onChange={(e) => setApiId(e.target.value)}
              placeholder="Enter API ID"
              className="flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
            />

            <button
              type="submit"
              className="rounded-md bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700"
            >
              Load API Usage
            </button>
          </form>

          {apiUsage.length === 0 ? (
            <p className="text-sm text-slate-500">
              No API usage found.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[700px] border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-left">
                    <th className="p-3 text-sm font-semibold text-slate-700">
                      ID
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Developer ID
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      API ID
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Period Start
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Period End
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Total Requests
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Successful
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Failed
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {apiUsage.map((item) => (
                    <tr
                      key={item.id}
                      className="border-b border-slate-100"
                    >
                      <td className="p-3 text-sm text-slate-600">
                        {item.id}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {item.developer_id}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {item.api_id}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {item.period_start}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {item.period_end}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {item.total_requests}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {item.successful_requests}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {item.failed_requests}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            My Usage
          </h2>

          {usage.length === 0 ? (
            <p className="text-sm text-slate-500">
              No usage records found.
            </p>
          ) : (
            <div className="space-y-3">
              {usage.map((item) => (
                <div
                  key={item.id}
                  className="rounded-md border border-slate-200 p-4"
                >
                  <div className="grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                    <p>
                      <span className="font-medium">
                        API ID:
                      </span>{" "}
                      {item.api_id}
                    </p>

                    <p>
                      <span className="font-medium">
                        Total Requests:
                      </span>{" "}
                      {item.total_requests}
                    </p>

                    <p>
                      <span className="font-medium">
                        Successful:
                      </span>{" "}
                      {item.successful_requests}
                    </p>

                    <p>
                      <span className="font-medium">
                        Failed:
                      </span>{" "}
                      {item.failed_requests}
                    </p>

                    <p>
                      <span className="font-medium">
                        Period Start:
                      </span>{" "}
                      {item.period_start}
                    </p>

                    <p>
                      <span className="font-medium">
                        Period End:
                      </span>{" "}
                      {item.period_end}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default UsageAnalytics;