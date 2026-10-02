import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function Organizations() {
  const [organizations, setOrganizations] = useState([]);

  const [form, setForm] = useState({
    name: "",
    owner_id: "",
  });

  const loadOrganizations = async () => {
    try {
      const response = await API.get("/organizations/");
      setOrganizations(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load organizations"
      );
    }
  };

  useEffect(() => {
    loadOrganizations();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const createOrganization = async (e) => {
    e.preventDefault();

    try {
      await API.post("/organizations/", {
        name: form.name,
        owner_id: Number(form.owner_id),
      });

      toast.success("Organization created successfully");

      setForm({
        name: "",
        owner_id: "",
      });

      loadOrganizations();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to create organization"
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-700">
            Organizations
          </h1>

          <p className="mt-1 text-sm text-slate-600">
            Create and manage organizations
          </p>
        </div>

        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            Create Organization
          </h2>

          <form
            onSubmit={createOrganization}
            className="space-y-4"
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Organization Name
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
                API Provider ID
              </label>

              <input
                type="number"
                name="owner_id"
                value={form.owner_id}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <button
              type="submit"
              className="rounded-md bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700"
            >
              Create Organization
            </button>
          </form>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            Organizations
          </h2>

          {organizations.length === 0 ? (
            <p className="text-sm text-slate-500">
              No organizations found.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[500px] border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-left">
                    <th className="p-3 text-sm font-semibold text-slate-700">
                      ID
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Name
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Owner ID
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Created At
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {organizations.map((organization) => (
                    <tr
                      key={organization.id}
                      className="border-b border-slate-100"
                    >
                      <td className="p-3 text-sm text-slate-600">
                        {organization.id}
                      </td>

                      <td className="p-3 text-sm font-medium text-slate-800">
                        {organization.name}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {organization.owner_id}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {organization.created_at}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Organizations;