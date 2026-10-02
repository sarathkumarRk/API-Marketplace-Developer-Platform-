import { useEffect, useState } from "react";
import API from "../../api/axios";
import toast from "react-hot-toast";

function APIReview() {
  const [apis, setApis] = useState([]);

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

  const reviewAPI = async (apiId) => {
    try {
      await API.post(`/apis/${apiId}/review`);

      toast.success("API moved to admin review");
      loadAPIs();
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to review API"
      );
    }
  };

  const approveAPI = async (apiId) => {
    try {
      await API.post(`/apis/${apiId}/approve`);

      toast.success("API approved successfully");
      loadAPIs();
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to approve API"
      );
    }
  };

  const rejectAPI = async (apiId) => {
    try {
      await API.post(`/apis/${apiId}/reject`);

      toast.success("API rejected");
      loadAPIs();
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to reject API"
      );
    }
  };

  const suspendAPI = async (apiId) => {
    try {
      await API.post(`/apis/${apiId}/suspend`);

      toast.success("API suspended successfully");
      loadAPIs();
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Failed to suspend API"
      );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-blue-700">
            API Review
          </h1>

          <p className="mt-1 text-sm text-slate-600">
            Review and manage submitted APIs
          </p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-5 text-lg font-semibold text-slate-800">
            APIs
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
                      {api.status === "submitted" && (
                        <button
                          onClick={() => reviewAPI(api.id)}
                          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Review
                        </button>
                      )}

                      {api.status === "admin_review" && (
                        <>
                          <button
                            onClick={() => approveAPI(api.id)}
                            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                          >
                            Approve
                          </button>

                          <button
                            onClick={() => rejectAPI(api.id)}
                            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                          >
                            Reject
                          </button>
                        </>
                      )}

                      {api.status === "published" && (
                        <button
                          onClick={() => suspendAPI(api.id)}
                          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                          Suspend
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

export default APIReview;