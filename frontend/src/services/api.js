import axios from "axios";

// Create an axios instance with default settings
const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,  // ✅ Important! This sends cookies with requests
});

// Add a request interceptor to include CSRF token if needed
api.interceptors.request.use(
  (config) => {
    // You can add any request headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized - redirect to login
    if (error.response && error.response.status === 401) {
      // Clear local storage and redirect to login
      localStorage.removeItem("dayflow_user");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export default api;