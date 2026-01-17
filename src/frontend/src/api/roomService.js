import axiosInstance from './axiosConfig';

const roomService = {
    getAllRooms: async () => {
        const response = await axiosInstance.get('/rooms/');
        return response.data;
    },

    getRoomById: async (id) => {
        const response = await axiosInstance.get(`/rooms/${id}/`);
        return response.data;
    },

    createRoom: async (roomData) => {
        const response = await axiosInstance.post('/rooms/', roomData);
        return response.data;
    },

    updateRoom: async (id, roomData) => {
        const response = await axiosInstance.put(`/rooms/${id}/`, roomData);
        return response.data;
    },

    partialUpdateRoom: async (id, roomData) => {
        const response = await axiosInstance.patch(`/rooms/${id}/`, roomData);
        return response.data;
    },

    deleteRoom: async (id) => {
        await axiosInstance.delete(`/rooms/${id}/`);
    },

    getAvailableRooms: async (checkIn, checkOut) => {
        const response = await axiosInstance.get('/rooms/available/', {
            params: { check_in: checkIn, check_out: checkOut }
        });
        return response.data;
    },
};

export default roomService;
