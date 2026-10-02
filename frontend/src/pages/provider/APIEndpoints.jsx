import { useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function APIEndpoints() {
  const [form, setForm] = useState({
    api_version_id: "",
    method: "",
    path: "",
    description: "",
    authentication_required: true,
  });

  const [apiVersionId, setApiVersionId] = useState("");
  const [endpoints, setEndpoints] = useState([]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const createEndpoint = async (e) => {
    e.preventDefault();

    try {
      const response = await API.post("/api-endpoints/", {
        api_version_id: Number(form.api_version_id),
        method: form.method,
        path: form.path,
        description: form.description,
        authentication_required: form.authentication_required,
      });

      toast.success("API endpoint created successfully");

      setForm({
        api_version_id: "",
        method: "",
        path: "",
        description: "",
        authentication_required: true,
      });

      if (apiVersionId) {
        const result = await API.get(
          `/api-endpoints/version/${apiVersionId}`
        );

        setEndpoints(result.data);
      }

      return response;
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to create API endpoint"
      );
    }
  };

  const getEndpoints = async () => {
    if (!apiVersionId) {
      toast.error("API Version ID is required");
      return;
    }

    try {
      const response = await API.get(
        `/api-endpoints/version/${apiVersionId}`
      );

      setEndpoints(response.data);

      toast.success("API endpoints loaded successfully");
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load API endpoints"
      );
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 p-6">
      <div className="max-w-6xl mx-auto">

        <h1 className="text-3xl font-bold text-blue-900 mb-2">
          API Endpoints
        </h1>

        <p className="text-blue-700 mb-6">
          Create and view API endpoints.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <div className="bg-blue-100 border border-blue-200 rounded-xl p-6 shadow-md">

            <h2 className="text-xl font-semibold text-blue-900 mb-5">
              Create API Endpoint
            </h2>

            <form
              onSubmit={createEndpoint}
              className="space-y-4"
            >

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  API Version ID
                </label>

                <input
                  type="number"
                  name="api_version_id"
                  value={form.api_version_id}
                  onChange={handleChange}
                  placeholder="Enter API version ID"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Method
                </label>

                <input
                  type="text"
                  name="method"
                  value={form.method}
                  onChange={handleChange}
                  placeholder="GET"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Path
                </label>

                <input
                  type="text"
                  name="path"
                  value={form.path}
                  onChange={handleChange}
                  placeholder="/users"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Description
                </label>

                <textarea
                  name="description"
                  value={form.description}
                  onChange={handleChange}
                  placeholder="Enter description"
                  rows="3"
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <label className="flex items-center gap-3 text-blue-900">
                <input
                  type="checkbox"
                  name="authentication_required"
                  checked={form.authentication_required}
                  onChange={handleChange}
                  className="accent-blue-600"
                />

                <span className="text-sm font-medium">
                  Authentication Required
                </span>
              </label>

              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-blue-50 font-semibold py-3 rounded-lg"
              >
                Create Endpoint
              </button>

            </form>
          </div>

          <div className="bg-blue-100 border border-blue-200 rounded-xl p-6 shadow-md">

            <h2 className="text-xl font-semibold text-blue-900 mb-5">
              API Endpoints
            </h2>

            <div className="flex gap-3 mb-6">

              <input
                type="number"
                value={apiVersionId}
                onChange={(e) =>
                  setApiVersionId(e.target.value)
                }
                placeholder="API Version ID"
                className="flex-1 bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
              />

              <button
                type="button"
                onClick={getEndpoints}
                className="bg-blue-600 hover:bg-blue-700 text-blue-50 font-semibold px-5 rounded-lg"
              >
                Load
              </button>

            </div>

            {endpoints.length === 0 ? (
              <p className="text-blue-700 text-center py-8">
                No endpoints found
              </p>
            ) : (
              <div className="space-y-4">

                {endpoints.map((endpoint) => (
                  <div
                    key={endpoint.id}
                    className="bg-blue-50 border border-blue-200 rounded-lg p-4"
                  >
                    <h3 className="text-blue-900 font-semibold">
                      {endpoint.method} {endpoint.path}
                    </h3>

                    <p className="text-blue-700 text-sm mt-2">
                      {endpoint.description}
                    </p>

                    <p className="text-blue-700 text-sm mt-2">
                      Authentication:{" "}
                      {endpoint.authentication_required
                        ? "Required"
                        : "Not Required"}
                    </p>
                  </div>
                ))}

              </div>
            )}

          </div>

        </div>
      </div>
    </div>
  );
}

export default APIEndpoints;