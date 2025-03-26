import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';  // Global styles
import { RouterProvider } from "react-router-dom";
import { router } from "./routes";  // Your routes configuration
import { StoreProvider } from './hooks/useGlobalReducer';  // Global state management
import { BackendURL } from './components/BackendURL';

const Main = () => {
    const backendUrl = import.meta.env.VITE_BACKEND_URL;

    // If the backend URL is missing, render the BackendURL component
    if (!backendUrl || backendUrl === "") {
        return (
            <React.StrictMode>
                <BackendURL />
            </React.StrictMode>
        );
    }

    return (
        <React.StrictMode>
            <StoreProvider>
                <RouterProvider router={router} />
            </StoreProvider>
        </React.StrictMode>
    );
}

ReactDOM.createRoot(document.getElementById('root')).render(<Main />);
