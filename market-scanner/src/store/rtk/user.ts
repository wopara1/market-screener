import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { TOKEN } from "../Config";

export const userApi = createApi({
  reducerPath: "userApi",
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_BASE_URL,
    prepareHeaders: (header) => {
      header.set("authorization", "Bearer " + localStorage.getItem(TOKEN));
    },
  }),
  endpoints: (builder) => ({
    getUsers: builder.query<
      { data: User[], message: string },
      { type: string; limit?: string; search?: string; page?: string | null }
    >({
      query: ({ type, limit, search, page = 1 }) =>
        search
          ? `/user/all?type=${type}&_limit=${limit ? limit : "0"
          }&_offset=${page}&_populate=category&_searchBy[]=firstName&_searchBy[]=lastName&_searchBy[]=category.name&_searchBy[]=phone&_searchBy[]=email&_keyword=${search}`
          : `/user/all?type=${type}&_limit=${limit ? limit : "0"
          }&_populate=category&_page=${page}`,
    }),
    getUser: builder.query<
      { message: string; data: User },
      string
    >({
      query: (id) => `/user/${id}`,
    }),
  })
})

export const {
  useGetUsersQuery,
  useGetUserQuery
} = userApi;
