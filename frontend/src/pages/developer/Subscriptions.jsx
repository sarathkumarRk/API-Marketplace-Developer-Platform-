import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([]);

  const [form, setForm] = useState({
    developer_id: "",
    api_id: "",
    plan_id: "",
  });

  const [priceIds, setPriceIds] = useState({});

  const loadSubscriptions = async () => {
    try {
      const response = await API.get("/subscriptions/my");
      setSubscriptions(response.data);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load subscriptions"
      );
    }
  };

  useEffect(() => {
    loadSubscriptions();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const createSubscription = async (e) => {
    e.preventDefault();

    try {
      await API.post("/subscriptions/", {
        developer_id: Number(form.developer_id),
        api_id: Number(form.api_id),
        plan_id: Number(form.plan_id),
      });

      toast.success("Subscription created successfully");

      setForm({
        developer_id: "",
        api_id: "",
        plan_id: "",
      });

      loadSubscriptions();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to create subscription"
      );
    }
  };

  const checkout = async (subscriptionId) => {
    try {
      const response = await API.post(
        `/subscriptions/${subscriptionId}/checkout`
      );

      toast.success("Stripe checkout created");

      window.location.href = response.data.checkout_url;
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to create checkout"
      );
    }
  };

  const cancelSubscription = async (subscriptionId) => {
    try {
      await API.post(
        `/subscriptions/${subscriptionId}/cancel`
      );

      toast.success("Subscription cancelled");
      loadSubscriptions();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to cancel subscription"
      );
    }
  };

  const upgradeSubscription = async (subscriptionId) => {
    const priceId = priceIds[subscriptionId];

    if (!priceId) {
      toast.error("Enter Stripe price ID");
      return;
    }

    try {
      await API.post(
        `/subscriptions/${subscriptionId}/upgrade`,
        null,
        {
          params: {
            price_id: priceId,
          },
        }
      );

      toast.success("Subscription upgraded");
      loadSubscriptions();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to upgrade subscription"
      );
    }
  };

  const downgradeSubscription = async (subscriptionId) => {
    const priceId = priceIds[subscriptionId];

    if (!priceId) {
      toast.error("Enter Stripe price ID");
      return;
    }

    try {
      await API.post(
        `/subscriptions/${subscriptionId}/downgrade`,
        null,
        {
          params: {
            price_id: priceId,
          },
        }
      );

      toast.success("Subscription downgraded");
      loadSubscriptions();
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to downgrade subscription"
      );
    }
  };

  const handlePriceIdChange = (subscriptionId, value) => {
    setPriceIds({
      ...priceIds,
      [subscriptionId]: value,
    });
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-700">
            Subscriptions
          </h1>

          <p className="mt-1 text-sm text-slate-600">
            Manage your API subscriptions
          </p>
        </div>

        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            Create Subscription
          </h2>

          <form onSubmit={createSubscription} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Developer ID
              </label>

              <input
                type="number"
                name="developer_id"
                value={form.developer_id}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                API ID
              </label>

              <input
                type="number"
                name="api_id"
                value={form.api_id}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Plan ID
              </label>

              <input
                type="number"
                name="plan_id"
                value={form.plan_id}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <button
              type="submit"
              className="rounded-md bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700"
            >
              Create Subscription
            </button>
          </form>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            My Subscriptions
          </h2>

          {subscriptions.length === 0 ? (
            <p className="text-sm text-slate-500">
              No subscriptions found.
            </p>
          ) : (
            <div className="space-y-4">
              {subscriptions.map((subscription) => (
                <div
                  key={subscription.id}
                  className="rounded-lg border border-slate-200 p-5"
                >
                  <div className="mb-4 grid gap-2 text-sm text-slate-600">
                    <p>
                      <span className="font-medium">
                        Subscription ID:
                      </span>{" "}
                      {subscription.id}
                    </p>

                    <p>
                      <span className="font-medium">
                        Developer ID:
                      </span>{" "}
                      {subscription.developer_id}
                    </p>

                    <p>
                      <span className="font-medium">
                        API ID:
                      </span>{" "}
                      {subscription.api_id}
                    </p>

                    <p>
                      <span className="font-medium">
                        Plan ID:
                      </span>{" "}
                      {subscription.plan_id}
                    </p>

                    <p>
                      <span className="font-medium">
                        Status:
                      </span>{" "}
                      {subscription.status}
                    </p>

                    <p>
                      <span className="font-medium">
                        Stripe Subscription ID:
                      </span>{" "}
                      {subscription.stripe_subscription_id ||
                        "Not available"}
                    </p>

                    <p>
                      <span className="font-medium">
                        Started At:
                      </span>{" "}
                      {subscription.started_at || "Not started"}
                    </p>

                    <p>
                      <span className="font-medium">
                        Expires At:
                      </span>{" "}
                      {subscription.expires_at || "Not available"}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {(subscription.status === "pending" ||
                      subscription.status === "payment_failed") && (
                      <button
                        onClick={() =>
                          checkout(subscription.id)
                        }
                        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                      >
                        Checkout
                      </button>
                    )}

                    {subscription.status === "active" && (
                      <>
                        <button
                          onClick={() =>
                            cancelSubscription(subscription.id)
                          }
                          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Cancel
                        </button>

                        <input
                          type="text"
                          placeholder="Stripe Price ID"
                          value={priceIds[subscription.id] || ""}
                          onChange={(e) =>
                            handlePriceIdChange(
                              subscription.id,
                              e.target.value
                            )
                          }
                          className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-600"
                        />

                        <button
                          onClick={() =>
                            upgradeSubscription(subscription.id)
                          }
                          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Upgrade
                        </button>

                        <button
                          onClick={() =>
                            downgradeSubscription(subscription.id)
                          }
                          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Downgrade
                        </button>
                      </>
                    )}
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

export default Subscriptions;