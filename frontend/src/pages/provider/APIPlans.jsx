import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function APIPlans() {
  const [plans, setPlans] = useState([]);
  const [apiId, setApiId] = useState("");
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    api_id: "",
    name: "",
    price: "",
    requests_per_month: "",
    requests_per_minute: "",
    is_active: true,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const createPlan = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      await API.post("/api-plans/", {
        api_id: Number(form.api_id),
        name: form.name,
        price: Number(form.price),
        requests_per_month: Number(form.requests_per_month),
        requests_per_minute: Number(form.requests_per_minute),
        is_active: form.is_active,
      });

      toast.success("API plan created successfully");

      setForm({
        api_id: "",
        name: "",
        price: "",
        requests_per_month: "",
        requests_per_minute: "",
        is_active: true,
      });

      if (apiId) {
        const response = await API.get(
          `/api-plans/api/${apiId}`
        );

        setPlans(response.data);
      }
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to create API plan"
      );
    } finally {
      setLoading(false);
    }
  };

  const getPlans = async () => {
    if (!apiId) {
      toast.error("API ID is required");
      return;
    }

    try {
      const response = await API.get(
        `/api-plans/api/${apiId}`
      );

      setPlans(response.data);

      toast.success("API plans loaded successfully");
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load API plans"
      );
    }
  };

  const updatePlanStatus = async (planId, isActive) => {
    try {
      await API.patch(
        `/api-plans/${planId}/status`,
        null,
        {
          params: {
            is_active: isActive,
          },
        }
      );

      toast.success("API plan status updated successfully");

      getPlans();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to update plan status"
      );
    }
  };

  useEffect(() => {
    if (!apiId) {
      return;
    }
  }, [apiId]);

  return (
    <div className="min-h-screen bg-blue-50 p-6">
      <div className="max-w-6xl mx-auto">

        <h1 className="text-3xl font-bold text-blue-900 mb-2">
          API Plans
        </h1>

        <p className="text-blue-700 mb-6">
          Create and manage API plans.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <div className="bg-blue-100 border border-blue-200 rounded-xl p-6 shadow-md">

            <h2 className="text-xl font-semibold text-blue-900 mb-5">
              Create API Plan
            </h2>

            <form
              onSubmit={createPlan}
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
                  Plan Name
                </label>

                <input
                  type="text"
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Enter plan name"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Price
                </label>

                <input
                  type="number"
                  step="0.01"
                  name="price"
                  value={form.price}
                  onChange={handleChange}
                  placeholder="Enter price"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Requests Per Month
                </label>

                <input
                  type="number"
                  name="requests_per_month"
                  value={form.requests_per_month}
                  onChange={handleChange}
                  placeholder="Enter monthly limit"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-blue-900 mb-2">
                  Requests Per Minute
                </label>

                <input
                  type="number"
                  name="requests_per_minute"
                  value={form.requests_per_minute}
                  onChange={handleChange}
                  placeholder="Enter per minute limit"
                  required
                  className="w-full bg-blue-50 border border-blue-300 rounded-lg px-4 py-3 text-blue-900 placeholder-blue-400 outline-none focus:border-blue-600"
                />
              </div>

              <label className="flex items-center gap-3 text-blue-900">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={form.is_active}
                  onChange={handleChange}
                  className="accent-blue-600"
                />

                <span className="text-sm font-medium">
                  Active
                </span>
              </label>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-blue-50 font-semibold py-3 rounded-lg"
              >
                {loading ? "Creating..." : "Create Plan"}
              </button>

            </form>
          </div>

          <div className="bg-blue-100 border border-blue-200 rounded-xl p-6 shadow-md">

            <h2 className="text-xl font-semibold text-blue-900 mb-5">
              API Plans
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
                onClick={getPlans}
                className="bg-blue-600 hover:bg-blue-700 text-blue-50 font-semibold px-5 rounded-lg"
              >
                Load
              </button>

            </div>

            {plans.length === 0 ? (
              <p className="text-blue-700 text-center py-8">
                No API plans found
              </p>
            ) : (
              <div className="space-y-4">

                {plans.map((plan) => (
                  <div
                    key={plan.id}
                    className="bg-blue-50 border border-blue-200 rounded-lg p-5"
                  >

                    <h3 className="text-lg font-semibold text-blue-900">
                      {plan.name}
                    </h3>

                    <p className="text-blue-700 mt-2">
                      Price: ₹{plan.price}
                    </p>

                    <p className="text-blue-700">
                      Requests / Month:{" "}
                      {plan.requests_per_month}
                    </p>

                    <p className="text-blue-700">
                      Requests / Minute:{" "}
                      {plan.requests_per_minute}
                    </p>

                    <p className="text-blue-700 mt-2">
                      Status:{" "}
                      {plan.is_active
                        ? "Active"
                        : "Inactive"}
                    </p>

                    <button
                      type="button"
                      onClick={() =>
                        updatePlanStatus(
                          plan.id,
                          !plan.is_active
                        )
                      }
                      className="mt-4 bg-blue-600 hover:bg-blue-700 text-blue-50 font-medium px-4 py-2 rounded-lg"
                    >
                      {plan.is_active
                        ? "Deactivate"
                        : "Activate"}
                    </button>

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

export default APIPlans;