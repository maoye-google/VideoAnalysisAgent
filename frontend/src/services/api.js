import axios from 'axios';

const api = axios.create({
    baseURL: '/api', // Base URL for all API requests, proxied in setupProxy.js for dev
});

export default api;