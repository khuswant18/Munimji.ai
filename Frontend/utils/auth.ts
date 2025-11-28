export const login = (phone: string) => {
  localStorage.setItem('munimji_user', JSON.stringify({ phone, isLoggedIn: true }));
};

export const logout = () => {
  localStorage.removeItem('munimji_user');
};

export const isAuthenticated = () => {
  const user = localStorage.getItem('munimji_user');
  return !!user;
};

export const getUser = () => {
  const user = localStorage.getItem('munimji_user');
  return user ? JSON.parse(user) : null;
};