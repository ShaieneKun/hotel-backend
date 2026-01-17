import axiosInstance from './axiosConfig';

const reservationService = {
    getAllReservations: async () => {
        const response = await axiosInstance.get('/reservations/');
        return response.data;
    },

    getReservationById: async (id) => {
        const response = await axiosInstance.get(`/reservations/${id}/`);
        return response.data;
    },

    createReservation: async (reservationData) => {
        const response = await axiosInstance.post('/reservations/', reservationData);
        return response.data;
    },

    updateReservation: async (id, reservationData) => {
        const response = await axiosInstance.put(`/reservations/${id}/`, reservationData);
        return response.data;
    },

    partialUpdateReservation: async (id, reservationData) => {
        const response = await axiosInstance.patch(`/reservations/${id}/`, reservationData);
        return response.data;
    },

    cancelReservation: async (id, reason = '') => {
        const response = await axiosInstance.post(`/reservations/${id}/cancel/`, { reason });
        return response.data;
    },

    checkInReservation: async (id) => {
        const response = await axiosInstance.post(`/reservations/${id}/check_in/`);
        return response.data;
    },

    checkOutReservation: async (id) => {
        const response = await axiosInstance.post(`/reservations/${id}/check_out/`);
        return response.data;
    },

    getReservationStats: async () => {
        const response = await axiosInstance.get('/reservations/stats/');
        return response.data;
    },
};

export default reservationService;
