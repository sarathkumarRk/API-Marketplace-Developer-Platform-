import { useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function APIGateway() {
  const [form, setForm] = useState({
    api_slug: "",
    path: "",
    method: "GET",
    api_key: "",
    api_version: "",
    body: "",
  });

  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const sendRequest = async (e) => {
    e.preventDefault();

    setLoading(true);
    setResponse(null);

    try {
      let requestBody = undefined;

      if (
        form.method === "POST" ||
        form.method === "PUT" ||
        form.method === "PATCH"
      ) {
        if (form.body.trim()) {
          requestBody = JSON.parse(form.body);
        }
      }

      const config = {
        headers: {
          "X-API-Key": form.api_key,
          "X-API-Version": form.api_version,
        },
      };

      let result;

      if (form.method === "GET") {
        result = await API.get(
          `/api-gateway/${form.api_slug}/${form.path}`,
          config
        );
      }

      if (form.method === "POST") {
        result = await API.post(
          `/api-gateway/${form.api_slug}/${form.path}`,
          requestBody,
          config
        );
      }

      if (form.method === "PUT") {
        result = await API.put(
          `/api-gateway/${form.api_slug}/${form.path}`,
          requestBody,
          config
        );
      }

      if (form.method === "PATCH") {
        result = await API.patch(
          `/api-gateway/${form.api_slug}/${form.path}`,
          requestBody,
          config
        );
      }

      if (form.method === "DELETE") {
        result = await API.delete(
          `/api-gateway/${form.api_slug}/${form.path}`,
          config
        );
      }

      setResponse({
        status: result.status,
        headers: result.headers,
        data: result.data,
      });

      toast.success("API request successful");
    } catch (error) {
      setResponse({
        status: error.response?.status || "Error",
        headers: error.response?.headers || {},
        data:
          error.response?.data ||
          error.message ||
          "Request failed",
      });

      toast.error(
        error.response?.data?.detail || "API request failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-700">
            API Gateway
          </h1>

          <p className="mt-1 text-sm text-slate-600">
            Send requests through the API Gateway
          </p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <form onSubmit={sendRequest} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                API Slug
              </label>

              <input
                type="text"
                name="api_slug"
                value={form.api_slug}
                onChange={handleChange}
                required
                placeholder="example-api"
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Path
              </label>

              <input
                type="text"
                name="path"
                value={form.path}
                onChange={handleChange}
                required
                placeholder="users"
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Method
              </label>

              <input
                type="text"
                name="method"
                value={form.method}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 uppercase outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                API Key
              </label>

              <input
                type="password"
                name="api_key"
                value={form.api_key}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                API Version
              </label>

              <input
                type="text"
                name="api_version"
                value={form.api_version}
                onChange={handleChange}
                required
                placeholder="v1"
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            {(form.method === "POST" ||
              form.method === "PUT" ||
              form.method === "PATCH") && (
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  Request Body
                </label>

                <textarea
                  name="body"
                  value={form.body}
                  onChange={handleChange}
                  rows="6"
                  placeholder='{"name":"John"}'
                  className="w-full rounded-md border border-slate-300 px-3 py-2 font-mono outline-none focus:border-blue-600"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="rounded-md bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Sending..." : "Send Request"}
            </button>
          </form>
        </div>

        {response && (
          <div className="mt-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-slate-800">
              Response
            </h2>

            <div className="mb-4">
              <span className="font-medium text-slate-700">
                Status:
              </span>{" "}
              <span className="text-blue-700">
                {response.status}
              </span>
            </div>

            <div className="mb-4">
              <h3 className="mb-2 font-medium text-slate-700">
                Response Headers
              </h3>

              <pre className="overflow-auto rounded-md bg-slate-100 p-4 text-sm">
                {JSON.stringify(response.headers, null, 2)}
              </pre>
            </div>

            <div>
              <h3 className="mb-2 font-medium text-slate-700">
                Response Body
              </h3>

              <pre className="overflow-auto rounded-md bg-slate-100 p-4 text-sm">
                {typeof response.data === "string"
                  ? response.data
                  : JSON.stringify(response.data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default APIGateway;