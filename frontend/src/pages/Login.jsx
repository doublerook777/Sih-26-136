import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [role, setRole] = useState("government");
  const navigate = useNavigate();

  const submit = (e) => {
    e.preventDefault();
    navigate(`/${role}`);
  };

  return (
    <div className="auth-page">
      <div className="auth-orb orb-one"></div>
      <div className="auth-orb orb-two"></div>

      <form className="auth-card" onSubmit={submit}>
        <div className="brand centered">
          <span className="brand-mark">P</span>
          <div>
            <strong>ProcuraAI</strong>
            <small>Prototype access</small>
          </div>
        </div>

        <h1>Welcome back</h1>
        <p className="muted">Choose a role to explore the complete demo.</p>

        <div className="role-selector">
          {["government", "startup", "evaluator"].map((item) => (
            <button
              type="button"
              key={item}
              className={role === item ? "role-option selected" : "role-option"}
              onClick={() => setRole(item)}
            >
              <span>{item === "government" ? "🏛️" : item === "startup" ? "🚀" : "🧾"}</span>
              {item}
            </button>
          ))}
        </div>

        <label>
          Email
          <input type="email" defaultValue={`${role}@demo.in`} />
        </label>

        <label>
          Password
          <input type="password" defaultValue="demopass" />
        </label>

        <button className="btn btn-primary full btn-lg" type="submit">
          Enter dashboard
        </button>

        <p className="demo-note">Demo only — authentication can be connected to Supabase later.</p>
      </form>
    </div>
  );
}
