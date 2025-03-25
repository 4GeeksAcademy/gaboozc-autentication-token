import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Private = () => {
    const [userData, setUserData] = useState(null);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const token = sessionStorage.getItem("token");

        if (!token) {
            navigate("/login");  // Redirect if not authenticated
            return;
        }

        const fetchData = async () => {
            const response = await fetch("http://127.0.0.1:5000/api/private", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUserData(data.user);
            } else {
                setError("Failed to fetch private data");
                navigate("/login");
            }
        };

        fetchData();
    }, [navigate]);

    return (
        <div>
            <h2>Private Page</h2>
            {error && <p style={{ color: "red" }}>{error}</p>}
            {userData ? (
                <div>
                    <p>Email: {userData.email}</p>
                    <button onClick={() => {
                        sessionStorage.removeItem("token");
                        navigate("/login");  // Logout and redirect
                    }}>Logout</button>
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};

export default Private;
