import { combineReducers } from "redux";
import { userApi } from "./rtk/user";
import UserSlice from './reducers/userSlice'

const rootReducer = combineReducers({
  user: UserSlice,
  [userApi.reducerPath]: userApi.reducer,
});

export default rootReducer;
