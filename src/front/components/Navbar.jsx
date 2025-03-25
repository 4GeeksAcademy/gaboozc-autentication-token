import { Link, useNavigate } from "react-router-dom";

export const Navbar = () => {
    const navigate = useNavigate();

    // Check if the user is authenticated (JWT token exists)
    const isAuthenticated = !!sessionStorage.getItem("token");

    const handleLogout = () => {
        sessionStorage.removeItem("token");  // Clear the token
        navigate("/login");  // Redirect to login page
    };

    return (
        <nav className="navbar navbar-light bg-light">
            <div className="container">
                {/* Home button */}
                <Link to="/">
                    <span className="navbar-brand mb-0 h1">Home</span>
                </Link>

                <div className="ml-auto d-flex gap-2">
                    {/* Conditional rendering based on authentication */}
                    {!isAuthenticated ? (
                        <>
                            <Link to="/signup">
                                <button className="btn btn-outline-primary">Signup</button>
                            </Link>
                            <Link to="/login">
                                <button className="btn btn-primary">Login</button>
                            </Link>
                        </>
                    ) : (
                        <>
                            <Link to="/private">
                                <button className="btn btn-success">Private</button>
                            </Link>
                            <button 
                                onClick={handleLogout} 
                                className="btn btn-danger"
                            >
                                Logout
                            </button>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};
