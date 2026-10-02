import { Toaster } from "react-hot-toast";
import AppRoutes from "./routes/AppRoutes";

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: "#2563eb",
            color: "#eff6ff",
            border: "1px solid #1d4ed8",
          },
        }}
      />

      <AppRoutes />
    </>
  );
}

export default App;