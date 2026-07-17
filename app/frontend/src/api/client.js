import axios from 'axios';

const apiClient = axios.create({
  baseURL:'http://localhost:8000' ,
  withCredentials: true, // to send cookies in cross-origin requests
});

export default apiClient;