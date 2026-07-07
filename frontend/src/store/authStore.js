import { create } from "zustand";
import { persist } from "zustand/middleware";
import { login as apiLogin, register as apiRegister, logout as apiLogout, getMe } from "../api/auth";

export const useAuthStore = create(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,

      isAuthenticated: () => Boolean(get().accessToken),

      login: async (username, password) => {
        const { access, refresh } = await apiLogin(username, password);
        set({ accessToken: access, refreshToken: refresh });
        const user = await getMe(access);
        set({ user });
        return user;
      },

      register: async (username, email, password, role) => {
        await apiRegister(username, email, password, role);
        return get().login(username, password);
      },

      logout: async () => {
        const { accessToken, refreshToken } = get();
        if (refreshToken) {
          await apiLogout(accessToken, refreshToken).catch(() => {
            /* token may already be expired — clear local state regardless */
          });
        }
        set({ accessToken: null, refreshToken: null, user: null });
      },
    }),
    { name: "nearme-auth" }
  )
);
