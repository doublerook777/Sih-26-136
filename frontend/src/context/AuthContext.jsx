import { createContext, useContext, useState, useEffect } from "react";
import { login as apiLogin, getMe as apiGetMe } from "../api/endpoints";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function restoreSession() {
      const storedToken = localStorage.getItem("token");
      if (storedToken) {
        try {
          const userData = await apiGetMe();
          setUser(userData);
          setToken(storedToken);
          localStorage.setItem("user", JSON.stringify(userData));
        } catch (err) {
          console.error("Failed to restore session:", err);
          // If 401 or invalid session, clear token
          if (err.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            setUser(null);
            setToken(null);
          } else {
            // If offline / network error, attempt to read stored user
            const savedUser = localStorage.getItem("user");
            if (savedUser) {
              try {
                setUser(JSON.parse(savedUser));
              } catch {
                setUser(null);
              }
            }
          }
        }
      }
      setLoading(false);
    }

    restoreSession();
  }, []);

  const login = async (email, password) => {
    setError(null);
    try {
      const result = await apiLogin(email, password);
      setToken(result.token);
      setUser(result.user);
      localStorage.setItem("token", result.token);
      localStorage.setItem("user", JSON.stringify(result.user));
      return result.user;
    } catch (err) {
      setError(err.detail || err.message || "Login failed");
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    setToken(null);
    setError(null);
  };

  const value = {
    user,
    token,
    loading,
    error,
    login,
    logout,
    isAuthenticated: Boolean(user && token),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
