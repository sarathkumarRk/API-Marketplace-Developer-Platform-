import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function APIs() {
  const [apis, setApis] = useState([]);

  const [form, setForm] = useState({
    organization_id: "",
    name: "",
    slug: "",
    description: "",
    category: "",
    status: "draft",
  });

  const loadAPIs = async () => {
    try {
      const response = await API.get("/apis/");
      setApis(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to load APIs"
      );
    }
  };

  useEffect(() => {
    loadAPIs();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const createAPI = async (e) => {
    e.preventDefault();

    try {
      await API.post("/apis/", {
        organization_id: Number(form.organization_id),
        name: form.name,
        slug: form.slug,
        description: form.description,
        category: form.category,
        status: form.status,
      });

      toast.success("API created successfully");

      setForm({
        organization_id: "",
        name: "",
        slug: "",
        description: "",
        category: "",
        status: "draft",
      });

      loadAPIs();
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to create API"
      );
    }
  };

  const submitAPI = async (apiId) => {
    try {
      await API.post(`/apis/${apiId}/submit`);

      toast.success("API submitted successfully");
      loadAPIs();
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to submit API"
      );
    }
  };

  const returnToDraft = async (apiId) => {
    try {
      await API.post(`/apis/${apiId}/return-to-draft`);

      toast.success("API returned to draft");
      loadAPIs();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to return API to draft"
      );
    }
  };

  const publishAPI = async (apiId) => {
    try {
      await API.post(`/apis/${apiId}/publish`);

      toast.success("API published successfully");
      loadAPIs();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to publish API"
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl">

        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-700">
            APIs
          </h1>

          <p className="mt-1 text-sm text-slate-600">
            Create and manage your APIs
          </p>
        </div>

        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            Create API
          </h2>

          <form
            onSubmit={createAPI}
            className="space-y-4"
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Organization ID
              </label>

              <input
                type="number"
                name="organization_id"
                value={form.organization_id}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                API Name
              </label>

              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Slug
              </label>

              <input
                type="text"
                name="slug"
                value={form.slug}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Description
              </label>

              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                required
                rows="3"
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Category
              </label>

              <input
                type="text"
                name="category"
                value={form.category}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Status
              </label>

              <select
                name="status"
                value={form.status}
                onChange={handleChange}
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 outline-none focus:border-blue-600"
              >
                <option value="draft">Draft</option>
                <option value="submitted">Submitted</option>
                <option value="admin_review">
                  Admin Review
                </option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="published">Published</option>
              </select>
            </div>

            <button
              type="submit"
              className="rounded-md bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700"
            >
              Create API
            </button>
          </form>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            My APIs
          </h2>

          {apis.length === 0 ? (
            <p className="text-sm text-slate-500">
              No APIs found.
            </p>
          ) : (
            <div className="space-y-4">

              {apis.map((api) => (
                <div
                  key={api.id}
                  className="rounded-lg border border-slate-200 p-5"
                >
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

                    <div>
                      <h3 className="text-lg font-semibold text-slate-800">
                        {api.name}
                      </h3>

                      <p className="mt-1 text-sm text-slate-600">
                        {api.description}
                      </p>

                      <div className="mt-3 space-y-1 text-sm text-slate-600">

                        <p>
                          <span className="font-medium">
                            ID:
                          </span>{" "}
                          {api.id}
                        </p>

                        <p>
                          <span className="font-medium">
                            Organization ID:
                          </span>{" "}
                          {api.organization_id}
                        </p>

                        <p>
                          <span className="font-medium">
                            Slug:
                          </span>{" "}
                          {api.slug}
                        </p>

                        <p>
                          <span className="font-medium">
                            Category:
                          </span>{" "}
                          {api.category}
                        </p>

                        <p>
                          <span className="font-medium">
                            Status:
                          </span>{" "}
                          {api.status}
                        </p>

                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">

                      {api.status === "draft" && (
                        <button
                          onClick={() => submitAPI(api.id)}
                          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Submit
                        </button>
                      )}

                      {api.status === "rejected" && (
                        <button
                          onClick={() =>
                            returnToDraft(api.id)
                          }
                          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Return to Draft
                        </button>
                      )}

                      {api.status === "approved" && (
                        <button
                          onClick={() =>
                            publishAPI(api.id)
                          }
                          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Publish
                        </button>
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
  );
}

export default APIs;