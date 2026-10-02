import { useNavigate } from "react-router-dom";

function getRoleFromToken(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.role;
  } catch {
    return null;
  }
}

function Navbar() {
  const navigate = useNavigate();

  const token = localStorage.getItem("access_token");
  const role = token ? getRoleFromToken(token) : null;

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const goTo = (path) => {
    navigate(path);
  };

  return (
    <nav className="border-b bg-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

        {/* Logo */}
        <div
          className="cursor-pointer text-xl font-bold text-blue-600"
          onClick={() => {
            if (role === "platform_admin") {
              navigate("/admin/dashboard");
            } else if (role === "api_provider") {
              navigate("/provider/dashboard");
            } else if (role === "developer") {
              navigate("/developer/dashboard");
            }
          }}
        >
          API Marketplace
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-2">

          {/* Admin Navigation */}
          {role === "platform_admin" && (
            <>
              <button
                onClick={() => goTo("/admin/dashboard")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Dashboard
              </button>

              <button
                onClick={() => goTo("/admin/api-review")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                API Review
              </button>

              <button
                onClick={() => goTo("/admin/organizations")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Organizations
              </button>

              <button
                onClick={() => goTo("/admin/users")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Users
              </button>
            </>
          )}

          {/* Provider Navigation */}
          {role === "api_provider" && (
            <>
              <button
                onClick={() => goTo("/provider/dashboard")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Dashboard
              </button>

              <button
                onClick={() => goTo("/provider/apis")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                APIs
              </button>

              <button
                onClick={() => goTo("/provider/api-versions")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Versions
              </button>

              <button
                onClick={() => goTo("/provider/api-endpoints")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Endpoints
              </button>

              <button
                onClick={() => goTo("/provider/api-plans")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Plans
              </button>

              <button
                onClick={() => goTo("/provider/webhooks")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Webhooks
              </button>
            </>
          )}

          {/* Developer Navigation */}
          {role === "developer" && (
            <>
              <button
                onClick={() => goTo("/developer/dashboard")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Dashboard
              </button>

              <button
                onClick={() => goTo("/developer/api-gateway")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                API Gateway
              </button>

              <button
                onClick={() => goTo("/developer/api-keys")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                API Keys
              </button>

              <button
                onClick={() => goTo("/developer/subscriptions")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Subscriptions
              </button>

              <button
                onClick={() => goTo("/developer/usage-analytics")}
                className="rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-600"
              >
                Usage
              </button>
            </>
          )}

          {/* Logout */}
          {token && (
            <button
              onClick={handleLogout}
              className="ml-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Logout
            </button>
          )}

        </div>
      </div>
    </nav>
  );
}

export default Navbar;