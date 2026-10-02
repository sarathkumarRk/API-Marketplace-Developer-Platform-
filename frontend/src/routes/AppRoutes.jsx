import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";

import ProtectedRoute from "../components/ProtectedRoute";

import AdminDashboard from "../pages/admin/AdminDashboard";
import APIReview from "../pages/admin/APIReview";
import Organizations from "../pages/admin/Organizations";
import Users from "../pages/admin/Users";

import ProviderDashboard from "../pages/provider/ProviderDashboard";
import APIs from "../pages/provider/APIs";
import APIVersions from "../pages/provider/APIVersions";
import APIEndpoints from "../pages/provider/APIEndpoints";
import APIPlans from "../pages/provider/APIPlans";
import Webhooks from "../pages/provider/Webhooks";

import DeveloperDashboard from "../pages/developer/DeveloperDashboard";
import APIGateway from "../pages/developer/APIGateway";
import APIKeys from "../pages/developer/APIKeys";
import Subscriptions from "../pages/developer/Subscriptions";
import UsageAnalytics from "../pages/developer/UsageAnalytics";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Admin Routes */}
        <Route
          element={
            <ProtectedRoute allowedRoles={["platform_admin"]} />
          }
        >
          <Route
            path="/admin/dashboard"
            element={<AdminDashboard />}
          />

          <Route
            path="/admin/api-review"
            element={<APIReview />}
          />

          <Route
            path="/admin/organizations"
            element={<Organizations />}
          />

          <Route
            path="/admin/users"
            element={<Users />}
          />
        </Route>

        {/* Provider Routes */}
        <Route
          element={
            <ProtectedRoute allowedRoles={["api_provider"]} />
          }
        >
          <Route
            path="/provider/dashboard"
            element={<ProviderDashboard />}
          />

          <Route
            path="/provider/apis"
            element={<APIs />}
          />

          <Route
            path="/provider/api-versions"
            element={<APIVersions />}
          />

          <Route
            path="/provider/api-endpoints"
            element={<APIEndpoints />}
          />

          <Route
            path="/provider/api-plans"
            element={<APIPlans />}
          />

          <Route
            path="/provider/webhooks"
            element={<Webhooks />}
          />
        </Route>

        {/* Developer Routes */}
        <Route
          element={
            <ProtectedRoute allowedRoles={["developer"]} />
          }
        >
          <Route
            path="/developer/dashboard"
            element={<DeveloperDashboard />}
          />

          <Route
            path="/developer/api-gateway"
            element={<APIGateway />}
          />

          <Route
            path="/developer/api-keys"
            element={<APIKeys />}
          />

          <Route
            path="/developer/subscriptions"
            element={<Subscriptions />}
          />

          <Route
            path="/developer/usage-analytics"
            element={<UsageAnalytics />}
          />
        </Route>

        {/* Default Route */}
        <Route
          path="/"
          element={<Navigate to="/login" replace />}
        />

        {/* Unknown Route */}
        <Route
          path="*"
          element={<Navigate to="/login" replace />}
        />

      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;