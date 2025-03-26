import { Link, useNavigate } from "react-router-dom";

export const Navbar = () => {
  const navigate = useNavigate();
  const token = sessionStorage.getItem("token");

  const handleLogout = () => {
    sessionStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-light bg-light">
      <div className="container">
        <Link to="/" className="navbar-brand">Home</Link>
        <div className="ml-auto">
          {token ? (
            <>
              <Link to="/private">
                <button className="btn btn-primary">Private</button>
              </Link>
              <button onClick={handleLogout} className="btn btn-danger ms-2">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login">
                <button className="btn btn-primary">Login</button>
              </Link>
              <Link to="/signup">
                <button className="btn btn-secondary ms-2">Sign Up</button>
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};
