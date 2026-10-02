import { Navigate, Outlet } from "react-router-dom";
import Navbar from "./Navbar";

function getRoleFromToken(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.role;
  } catch {
    return null;
  }
}

function ProtectedRoute({ allowedRoles }) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const role = getRoleFromToken(token);

  if (!role) {
    localStorage.removeItem("access_token");
    return <Navigate to="/login" replace />;
  }

  if (
    allowedRoles &&
    !allowedRoles.includes(role)
  ) {
    if (role === "platform_admin") {
      return <Navigate to="/admin/dashboard" replace />;
    }

    if (role === "api_provider") {
      return <Navigate to="/provider/dashboard" replace />;
    }

    if (role === "developer") {
      return <Navigate to="/developer/dashboard" replace />;
    }

    localStorage.removeItem("access_token");
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <Navbar />
      <Outlet />
    </>
  );
}

export default ProtectedRoute;