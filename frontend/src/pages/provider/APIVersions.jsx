import { useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function APIVersions() {
  const [versions, setVersions] = useState([]);
  const [apiId, setApiId] = useState("");

  const [form, setForm] = useState({
    api_id: "",
    version: "",
    base_url: "",
    status: "active",
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: value,
    });
  };

  const createVersion = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      await API.post("/api-versions/", {
        api_id: Number(form.api_id),
        version: form.version,
        base_url: form.base_url,
        status: form.status,
      });

      toast.success("API version created successfully");

      setForm({
        api_id: "",
        version: "",
        base_url: "",
        status: "active",
      });

      if (apiId) {
        const response = await API.get(
          `/api-versions/api/${apiId}`
        );

        setVersions(response.data);
      }
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to create API version"
      );
    } finally {
      setLoading(false);
    }
  };

  const getVersions = async () => {
    if (!apiId) {
      toast.error("API ID is required");
      return;
    }

    try {
      const response = await API.get(
        `/api-versions/api/${apiId}`
      );

      setVersions(response.data);

      toast.success("API versions loaded successfully");
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load API versions"
      );
    }
  };

  const updateVersionStatus = async (
    versionId,
    newStatus
  ) => {
    try {
      await API.patch(
        `/api-versions/${versionId}/status`,
        null,
        {
          params: {
            new_status: newStatus,
          },
        }
      );

      toast.success("API version status updated successfully");

      getVersions();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to update API version status"
      );
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 p-6">
      <div className="max-w-6xl mx-auto">

        <h1 className="text-3xl font-bold text-blue-900 mb-2">
          API Versions
        </h1>

        <p className="text-blue-700 mb-6">
          Create and manage API versions.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <div className="bg-blue-100 border border-blue-200 rounded-xl p-6 shadow-md">

            <h2 className="text-xl font-semibold text-blue-900 mb-5">
              Create API Version
            </h2>

            <form
              onSubmit={createVersion}
              className="space-y-4"
            >

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  API ID
                </label>

                <input
                  type="number"
                  name="api_id"
                  value={form.api_id}
                  onChange={handleChange}
                  placeholder="Enter API ID"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Version
                </label>

                <input
                  type="text"
                  name="version"
                  value={form.version}
                  onChange={handleChange}
                  placeholder="v1"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Base URL
                </label>

                <input
                  type="text"
                  name="base_url"
                  value={form.base_url}
                  onChange={handleChange}
                  placeholder="https://api.example.com"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Status
                </label>

                <input
                  type="text"
                  name="status"
                  value={form.status}
                  onChange={handleChange}
                  placeholder="active"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-blue-50 font-semibold py-3 rounded-lg"
              >
                {loading
                  ? "Creating..."
                  : "Create Version"}
              </button>

            </form>
          </div>

          <div className="bg-blue-100 border border-blue-200 rounded-xl p-6 shadow-md">

            <h2 className="text-xl font-semibold text-blue-900 mb-5">
              API Versions
            </h2>

            <div className="flex gap-3 mb-6">

              <input
                type="number"
                value={apiId}
                onChange={(e) =>
                  setApiId(e.target.value)
                }
                placeholder="API ID"
                className="flex-1 bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
              />

              <button
                type="button"
                onClick={getVersions}
                className="bg-blue-600 hover:bg-blue-700 text-blue-50 font-semibold px-5 rounded-lg"
              >
                Load
              </button>

            </div>

            {versions.length === 0 ? (
              <p className="text-blue-700 text-center py-8">
                No API versions found
              </p>
            ) : (
              <div className="space-y-4">

                {versions.map((version) => (
                  <div
                    key={version.id}
                    className="bg-blue-50 border border-blue-200 rounded-lg p-5"
                  >

                    <h3 className="text-lg font-semibold text-blue-900">
                      {version.version}
                    </h3>

                    <p className="text-blue-700 mt-2">
                      Base URL: {version.base_url}
                    </p>

                    <p className="text-blue-700 mt-1">
                      Status: {version.status}
                    </p>

                    <div className="flex gap-2 mt-4">

                      <button
                        type="button"
                        onClick={() =>
                          updateVersionStatus(
                            version.id,
                            "active"
                          )
                        }
                        className="bg-blue-600 hover:bg-blue-700 text-blue-50 px-4 py-2 rounded-lg"
                      >
                        Active
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          updateVersionStatus(
                            version.id,
                            "deprecated"
                          )
                        }
                        className="bg-blue-700 hover:bg-blue-800 text-blue-50 px-4 py-2 rounded-lg"
                      >
                        Deprecated
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          updateVersionStatus(
                            version.id,
                            "retired"
                          )
                        }
                        className="bg-blue-900 hover:bg-blue-950 text-blue-50 px-4 py-2 rounded-lg"
                      >
                        Retired
                      </button>

                    </div>

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

export default APIVersions;