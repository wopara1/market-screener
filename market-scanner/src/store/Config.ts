import axios from "axios";

export const useURL = "http://0.0.0.0:80"

export const SetDefaultHeaders = () => {
  axios.defaults.baseURL = useURL;
};
