import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function APIKeys() {
  const [apiKeys, setApiKeys] = useState([]);

  const [form, setForm] = useState({
    developer_id: "",
    subscription_id: "",
    expires_at: "",
  });

  const [loading, setLoading] = useState(false);
  const [generatedKey, setGeneratedKey] = useState("");

  const loadApiKeys = async () => {
    try {
      const response = await API.get("/api-keys/my");

      setApiKeys(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load API keys"
      );
    }
  };

  useEffect(() => {
    loadApiKeys();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: value,
    });
  };

  const generateApiKey = async (e) => {
    e.preventDefault();

    setLoading(true);
    setGeneratedKey("");

    try {
      const response = await API.post("/api-keys/", {
        developer_id: Number(form.developer_id),
        subscription_id: Number(form.subscription_id),
        expires_at: form.expires_at
          ? new Date(form.expires_at).toISOString()
          : null,
      });

      if (response.data.full_key) {
        setGeneratedKey(response.data.full_key);
      }

      toast.success("API key generated successfully");

      setForm({
        developer_id: "",
        subscription_id: "",
        expires_at: "",
      });

      loadApiKeys();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to generate API key"
      );
    } finally {
      setLoading(false);
    }
  };

  const revokeApiKey = async (apiKeyId) => {
    try {
      await API.patch(
        `/api-keys/${apiKeyId}/revoke`
      );

      toast.success("API key revoked successfully");

      loadApiKeys();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to revoke API key"
      );
    }
  };

  const regenerateApiKey = async (apiKeyId) => {
    try {
      const response = await API.post(
        `/api-keys/${apiKeyId}/regenerate`
      );

      if (response.data.full_key) {
        setGeneratedKey(response.data.full_key);
      }

      toast.success("API key regenerated successfully");

      loadApiKeys();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to regenerate API key"
      );
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 p-6">
      <div className="mx-auto max-w-6xl">

        <h1 className="mb-2 text-3xl font-bold text-blue-900">
          API Keys
        </h1>

        <p className="mb-6 text-blue-700">
          Generate and manage your API keys.
        </p>

        {generatedKey && (
          <div className="mb-6 rounded-xl border border-blue-300 bg-blue-100 p-6 shadow-md">
            <h2 className="mb-2 text-xl font-semibold text-blue-900">
              Your New API Key
            </h2>

            <p className="mb-4 text-sm text-blue-700">
              Copy this full API key and use it in the API Gateway.
              It will not be available again after this response.
            </p>

            <div className="break-all rounded-lg border border-blue-300 bg-blue-50 p-4 font-mono text-sm font-semibold text-blue-900">
              {generatedKey}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

          <div className="rounded-xl border border-blue-200 bg-blue-100 p-6 shadow-md">

            <h2 className="mb-5 text-xl font-semibold text-blue-900">
              Generate API Key
            </h2>

            <form
              onSubmit={generateApiKey}
              className="space-y-4"
            >

              <div>
                <label className="mb-2 block text-sm font-medium text-blue-900">
                  Developer ID
                </label>

                <input
                  type="number"
                  name="developer_id"
                  value={form.developer_id}
                  onChange={handleChange}
                  placeholder="Enter developer ID"
                  required
                  className="w-full rounded-lg border border-blue-300 bg-blue-50 px-4 py-3 text-blue-900 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-blue-900">
                  Subscription ID
                </label>

                <input
                  type="number"
                  name="subscription_id"
                  value={form.subscription_id}
                  onChange={handleChange}
                  placeholder="Enter subscription ID"
                  required
                  className="w-full rounded-lg border border-blue-300 bg-blue-50 px-4 py-3 text-blue-900 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-blue-900">
                  Expires At
                </label>

                <input
                  type="datetime-local"
                  name="expires_at"
                  value={form.expires_at}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-blue-300 bg-blue-50 px-4 py-3 text-blue-900 outline-none focus:border-blue-600"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-blue-50 hover:bg-blue-700 disabled:bg-blue-400"
              >
                {loading
                  ? "Generating..."
                  : "Generate API Key"}
              </button>

            </form>
          </div>

          <div className="rounded-xl border border-blue-200 bg-blue-100 p-6 shadow-md lg:col-span-2">

            <h2 className="mb-5 text-xl font-semibold text-blue-900">
              My API Keys
            </h2>

            {apiKeys.length === 0 ? (
              <div className="py-10 text-center text-blue-700">
                No API keys found
              </div>
            ) : (
              <div className="space-y-4">

                {apiKeys.map((apiKey) => (
                  <div
                    key={apiKey.id}
                    className="rounded-lg border border-blue-200 bg-blue-50 p-5"
                  >

                    <div className="flex flex-col gap-4">

                      <div>
                        <p className="text-sm text-blue-700">
                          Key Prefix
                        </p>

                        <p className="font-semibold text-blue-900">
                          {apiKey.key_prefix}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-blue-700">
                          Subscription ID
                        </p>

                        <p className="font-semibold text-blue-900">
                          {apiKey.subscription_id}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-blue-700">
                          Status
                        </p>

                        <p className="font-semibold text-blue-900">
                          {apiKey.is_active
                            ? "Active"
                            : "Revoked"}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-blue-700">
                          Created At
                        </p>

                        <p className="font-semibold text-blue-900">
                          {apiKey.created_at
                            ? new Date(
                                apiKey.created_at
                              ).toLocaleString()
                            : "-"}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-blue-700">
                          Expires At
                        </p>

                        <p className="font-semibold text-blue-900">
                          {apiKey.expires_at
                            ? new Date(
                                apiKey.expires_at
                              ).toLocaleString()
                            : "-"}
                        </p>
                      </div>

                      <div className="flex gap-3">

                        {apiKey.is_active && (
                          <>
                            <button
                              type="button"
                              onClick={() =>
                                revokeApiKey(apiKey.id)
                              }
                              className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-blue-50 hover:bg-blue-700"
                            >
                              Revoke
                            </button>

                            <button
                              type="button"
                              onClick={() =>
                                regenerateApiKey(apiKey.id)
                              }
                              className="rounded-lg bg-blue-900 px-4 py-2 font-medium text-blue-50 hover:bg-blue-950"
                            >
                              Regenerate
                            </button>
                          </>
                        )}

                      </div>

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

export default APIKeys;