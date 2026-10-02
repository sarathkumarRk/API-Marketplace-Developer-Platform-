import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import API from "../../api/axios";

function Login() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const getRoleFromToken = (token) => {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.role;
    } catch {
      return null;
    }
  };

  const onSubmit = async (data) => {
    setLoading(true);

    try {
      const response = await API.post("/auth/login", {
        email: data.email,
        password: data.password,
      });

      const accessToken = response.data.access_token;

      localStorage.setItem("access_token", accessToken);

      const role = getRoleFromToken(accessToken);

      if (role === "platform_admin") {
        localStorage.setItem("role", role);

        toast.success("Platform Admin login successful");

        setTimeout(() => {
          navigate("/admin/dashboard");
        }, 700);

        return;
      }

      if (role === "api_provider") {
        localStorage.setItem("role", role);

        toast.success("API Provider login successful");

        setTimeout(() => {
          navigate("/provider/dashboard");
        }, 700);

        return;
      }

      if (role === "developer") {
        localStorage.setItem("role", role);

        toast.success("Developer login successful");

        setTimeout(() => {
          navigate("/developer/dashboard");
        }, 700);

        return;
      }

      toast.error("Invalid user role");
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Login failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-blue-100 border border-blue-200 rounded-xl shadow-lg p-8">

        <div className="text-center mb-7">
          <div className="w-14 h-14 bg-blue-600 text-blue-50 rounded-xl flex items-center justify-center mx-auto mb-4 text-xl font-bold">
            API
          </div>

          <h1 className="text-2xl font-bold text-blue-900">
            API Marketplace
          </h1>

          <p className="text-blue-700 text-sm mt-2">
            Login to your account
          </p>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-5"
        >
          <div>
            <label className="block text-sm font-medium text-blue-900 mb-2">
              Email
            </label>

            <input
              type="email"
              placeholder="Enter your email"
              {...register("email", {
                required: "Email is required",
              })}
              className="w-full bg-blue-50 border border-blue-300 text-blue-900 placeholder-blue-400 rounded-lg px-4 py-3 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            />

            {errors.email && (
              <p className="text-blue-700 text-sm mt-1">
                {errors.email.message}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-blue-900 mb-2">
              Password
            </label>

            <input
              type="password"
              placeholder="Enter your password"
              {...register("password", {
                required: "Password is required",
              })}
              className="w-full bg-blue-50 border border-blue-300 text-blue-900 placeholder-blue-400 rounded-lg px-4 py-3 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            />

            {errors.password && (
              <p className="text-blue-700 text-sm mt-1">
                {errors.password.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-blue-50 font-semibold py-3 rounded-lg transition"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="text-center mt-6">
          <p className="text-blue-700 text-sm">
            Don't have an account?{" "}
            <button
              type="button"
              onClick={() => navigate("/register")}
              className="text-blue-900 font-semibold hover:underline"
            >
              Register
            </button>
          </p>
        </div>

      </div>
    </div>
  );
}

export default Login;