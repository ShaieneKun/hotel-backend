import axiosInstance from './axiosConfig';

const authService = {
    register: async (userData) => {
        const response = await axiosInstance.post('/auth/register/', userData);
        return response.data;
    },

    login: async (username, password) => {
        const response = await axiosInstance.post('/auth/token/', {
            username,
            password,
        });

        if (response.data.access) {
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);

            // Decode JWT to get user info
            const decodedToken = JSON.parse(atob(response.data.access.split('.')[1]));
            localStorage.setItem('user', JSON.stringify({
                username: decodedToken.username,
                email: decodedToken.email,
                role: decodedToken.role,
            }));
        }

        return response.data;
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },

    getCurrentUser: () => {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isAuthenticated: () => {
        return !!localStorage.getItem('access_token');
    },

    getRole: () => {
        const user = authService.getCurrentUser();
        return user?.role || null;
    },
};

export default authService;
