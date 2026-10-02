import { useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function Webhooks() {
  const [form, setForm] = useState({
    api_id: "",
    event_type: "",
    target_url: "",
    secret: "",
    is_active: true,
  });

  const [apiId, setApiId] = useState("");
  const [webhooks, setWebhooks] = useState([]);
  const [deliveries, setDeliveries] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const createWebhook = async (e) => {
    e.preventDefault();

    try {
      await API.post("/webhooks/", {
        api_id: Number(form.api_id),
        event_type: form.event_type,
        target_url: form.target_url,
        secret: form.secret,
        is_active: form.is_active,
      });

      toast.success("Webhook created successfully");

      setForm({
        api_id: "",
        event_type: "",
        target_url: "",
        secret: "",
        is_active: true,
      });
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to create webhook"
      );
    }
  };

  const loadWebhooks = async (e) => {
    e.preventDefault();

    if (!apiId) {
      toast.error("Enter API ID");
      return;
    }

    try {
      const response = await API.get(
        `/webhooks/api/${apiId}`
      );

      setWebhooks(response.data);

      toast.success("Webhooks loaded successfully");
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load webhooks"
      );
    }
  };

  const updateWebhookStatus = async (
    webhookId,
    isActive
  ) => {
    try {
      await API.patch(
        `/webhooks/${webhookId}/status`,
        null,
        {
          params: {
            is_active: isActive,
          },
        }
      );

      toast.success(
        isActive
          ? "Webhook activated successfully"
          : "Webhook deactivated successfully"
      );

      setWebhooks((currentWebhooks) =>
        currentWebhooks.map((webhook) =>
          webhook.id === webhookId
            ? {
                ...webhook,
                is_active: isActive,
              }
            : webhook
        )
      );
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to update webhook status"
      );
    }
  };

  const testWebhook = async (webhookId) => {
    try {
      await API.post(
        `/webhooks/${webhookId}/test`
      );

      toast.success("Webhook test completed");

      loadDeliveries(webhookId);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Webhook test failed"
      );
    }
  };

  const loadDeliveries = async (webhookId) => {
    try {
      const response = await API.get(
        `/webhooks/${webhookId}/deliveries`
      );

      setDeliveries((currentDeliveries) => ({
        ...currentDeliveries,
        [webhookId]: response.data,
      }));
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to load webhook deliveries"
      );
    }
  };

  const retryDelivery = async (
    webhookId,
    deliveryId
  ) => {
    try {
      await API.post(
        `/webhooks/${webhookId}/retry/${deliveryId}`
      );

      toast.success("Webhook delivery retried successfully");

      loadDeliveries(webhookId);
    } catch (error) {
      toast.error(
        error.response?.data?.detail ||
          "Failed to retry webhook delivery"
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-700">
            Webhooks
          </h1>

          <p className="mt-1 text-sm text-slate-600">
            Create and manage API webhooks
          </p>
        </div>

        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            Create Webhook
          </h2>

          <form
            onSubmit={createWebhook}
            className="space-y-4"
          >
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
                Event Type
              </label>

              <input
                type="text"
                name="event_type"
                value={form.event_type}
                onChange={handleChange}
                required
                placeholder="subscription.created"
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Target URL
              </label>

              <input
                type="url"
                name="target_url"
                value={form.target_url}
                onChange={handleChange}
                required
                placeholder="https://example.com/webhook"
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Secret
              </label>

              <input
                type="password"
                name="secret"
                value={form.secret}
                onChange={handleChange}
                required
                className="w-full rounded-md border border-slate-300 px-3 py-2 outline-none focus:border-blue-600"
              />
            </div>

            <label className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                name="is_active"
                checked={form.is_active}
                onChange={handleChange}
              />

              Active
            </label>

            <button
              type="submit"
              className="rounded-md bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700"
            >
              Create Webhook
            </button>
          </form>
        </div>

        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            API Webhooks
          </h2>

          <form
            onSubmit={loadWebhooks}
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
              Load Webhooks
            </button>
          </form>

          {webhooks.length === 0 ? (
            <p className="text-sm text-slate-500">
              No webhooks found.
            </p>
          ) : (
            <div className="space-y-5">
              {webhooks.map((webhook) => (
                <div
                  key={webhook.id}
                  className="rounded-lg border border-slate-200 p-5"
                >
                  <div className="mb-4 grid gap-2 text-sm text-slate-600">
                    <p>
                      <span className="font-medium">
                        Webhook ID:
                      </span>{" "}
                      {webhook.id}
                    </p>

                    <p>
                      <span className="font-medium">
                        API ID:
                      </span>{" "}
                      {webhook.api_id}
                    </p>

                    <p>
                      <span className="font-medium">
                        Event Type:
                      </span>{" "}
                      {webhook.event_type}
                    </p>

                    <p>
                      <span className="font-medium">
                        Target URL:
                      </span>{" "}
                      {webhook.target_url}
                    </p>

                    <p>
                      <span className="font-medium">
                        Status:
                      </span>{" "}
                      {webhook.is_active
                        ? "Active"
                        : "Inactive"}
                    </p>
                  </div>

                  <div className="mb-5 flex flex-wrap gap-2">
                    <button
                      onClick={() =>
                        updateWebhookStatus(
                          webhook.id,
                          !webhook.is_active
                        )
                      }
                      className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                    >
                      {webhook.is_active
                        ? "Deactivate"
                        : "Activate"}
                    </button>

                    <button
                      onClick={() =>
                        testWebhook(webhook.id)
                      }
                      disabled={!webhook.is_active}
                      className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Test Webhook
                    </button>

                    <button
                      onClick={() =>
                        loadDeliveries(webhook.id)
                      }
                      className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                    >
                      View Deliveries
                    </button>
                  </div>

                  {deliveries[webhook.id] && (
                    <div>
                      <h3 className="mb-3 font-semibold text-slate-800">
                        Deliveries
                      </h3>

                      {deliveries[webhook.id].length === 0 ? (
                        <p className="text-sm text-slate-500">
                          No deliveries found.
                        </p>
                      ) : (
                        <div className="space-y-3">
                          {deliveries[webhook.id].map(
                            (delivery) => (
                              <div
                                key={delivery.id}
                                className="rounded-md border border-slate-200 p-4"
                              >
                                <div className="grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                                  <p>
                                    <span className="font-medium">
                                      Delivery ID:
                                    </span>{" "}
                                    {delivery.id}
                                  </p>

                                  <p>
                                    <span className="font-medium">
                                      Event ID:
                                    </span>{" "}
                                    {delivery.event_id}
                                  </p>

                                  <p>
                                    <span className="font-medium">
                                      Status:
                                    </span>{" "}
                                    {delivery.status}
                                  </p>

                                  <p>
                                    <span className="font-medium">
                                      Response Code:
                                    </span>{" "}
                                    {delivery.response_code ||
                                      "N/A"}
                                  </p>

                                  <p>
                                    <span className="font-medium">
                                      Attempts:
                                    </span>{" "}
                                    {delivery.attempt_count}
                                  </p>

                                  <p>
                                    <span className="font-medium">
                                      Delivered At:
                                    </span>{" "}
                                    {delivery.delivered_at ||
                                      "Not delivered"}
                                  </p>
                                </div>

                                {delivery.status !==
                                  "delivered" && (
                                  <button
                                    onClick={() =>
                                      retryDelivery(
                                        webhook.id,
                                        delivery.id
                                      )
                                    }
                                    className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                                  >
                                    Retry
                                  </button>
                                )}
                              </div>
                            )
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Webhooks;