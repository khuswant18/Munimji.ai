// Frontend/utils/auth.ts
const TOKEN_KEY = 'munimji_token';
const USER_KEY = 'munimji_user';

export interface StoredUser {
  id: number;
  phone: string;
  name?: string;
  shop_name?: string;
}

export const setAuthToken = (token: string) => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const setUser = (user: StoredUser) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const getUser = (): StoredUser | null => {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
};

export const login = (token: string, user: { id: number; phone_number: string; name?: string; shop_name?: string }) => {
  setAuthToken(token);
  setUser({
    id: user.id,
    phone: user.phone_number,
    name: user.name,
    shop_name: user.shop_name,
  });
};

export const logout = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};
