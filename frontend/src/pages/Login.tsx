import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem("userData");
    if (storedUser) {
      const userData = JSON.parse(storedUser);
      if (userData && userData.id) {
        navigate("/");
      }
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(false);

    try {
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, password }), // ✅ send name + password
      });

      const data = await response.json();

      if (data.success && data.user) {
        localStorage.setItem("userData", JSON.stringify(data.user));
        navigate("/");
      } else {
        setError(true);
      }
    } catch (err) {
      console.error("Login error:", err);
      setError(true);
    }
  };

  return (
    <div className="bg-gray-50 flex items-center justify-center min-h-screen">
      <div className="bg-white shadow-md rounded-xl p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          Login to LearnPath
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 mb-1" htmlFor="name">
              Name
            </label>
            <input
              type="text"
              id="name"
              placeholder="Enter your name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-gray-700 mb-1" htmlFor="password">
              Password
            </label>
            <input
              type="password"
              id="password"
              placeholder="Enter your password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm">
              Invalid name or password. Please try again.
            </p>
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition duration-200"
          >
            Login
          </button>
        </form>

        <p className="mt-4 text-center text-gray-600 text-sm">
          Don't have an account?{" "}
          <a
            href="/onboarding"
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Register
          </a>
        </p>
      </div>
    </div>
  );
};

export default Login;