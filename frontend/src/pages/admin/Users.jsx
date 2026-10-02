import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function Users() {
  const [users, setUsers] = useState([]);

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "developer",
  });

  const loadUsers = async () => {
    try {
      const response = await API.get("/users/");
      setUsers(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load users"
      );
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const createUser = async (e) => {
    e.preventDefault();

    try {
      await API.post("/users/", null, {
        params: {
          name: form.name,
          email: form.email,
          password: form.password,
          role: form.role,
        },
      });

      toast.success("User created successfully");

      setForm({
        name: "",
        email: "",
        password: "",
        role: "developer",
      });

      loadUsers();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to create user"
      );
    }
  };

  const updateStatus = async (userId, isActive) => {
    try {
      await API.patch(
        `/users/${userId}/status`,
        null,
        {
          params: {
            is_active: isActive,
          },
        }
      );

      toast.success(
        isActive
          ? "User activated successfully"
          : "User deactivated successfully"
      );

      loadUsers();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to update user status"
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-700">
            Users
          </h1>

          <p className="mt-1 text-sm text-slate-600">
            Create and manage API providers and developers
          </p>
        </div>

        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            Create User
          </h2>

          <form
            onSubmit={createUser}
            className="space-y-4"
          >
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Name
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
                Email
              </label>

              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Password
              </label>

              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Role
              </label>

              <select
                name="role"
                value={form.role}
                onChange={handleChange}
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 outline-none focus:border-blue-600"
              >
                <option value="developer">
                  Developer
                </option>

                <option value="api_provider">
                  API Provider
                </option>
              </select>
            </div>

            <button
              type="submit"
              className="rounded-md bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700"
            >
              Create User
            </button>
          </form>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            Users
          </h2>

          {users.length === 0 ? (
            <p className="text-sm text-slate-500">
              No users found.
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
                      Name
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Email
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Role
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Status
                    </th>

                    <th className="p-3 text-sm font-semibold text-slate-700">
                      Action
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {users.map((user) => (
                    <tr
                      key={user.id}
                      className="border-b border-slate-100"
                    >
                      <td className="p-3 text-sm text-slate-600">
                        {user.id}
                      </td>

                      <td className="p-3 text-sm font-medium text-slate-800">
                        {user.name}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {user.email}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {user.role}
                      </td>

                      <td className="p-3 text-sm text-slate-600">
                        {user.is_active
                          ? "Active"
                          : "Inactive"}
                      </td>

                      <td className="p-3">
                        {user.is_active ? (
                          <button
                            onClick={() =>
                              updateStatus(
                                user.id,
                                false
                              )
                            }
                            className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
                          >
                            Deactivate
                          </button>
                        ) : (
                          <button
                            onClick={() =>
                              updateStatus(
                                user.id,
                                true
                              )
                            }
                            className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
                          >
                            Activate
                          </button>
                        )}
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

export default Users;