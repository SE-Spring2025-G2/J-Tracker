import fetch from "./handler";

export const getToken = (params) => {
  // console.log(params)
  return fetch({
    method: "POST",
    url: "/users/login",
    body: params,
  });
};

export const signUp = (params) => {
  return fetch({
    method: "POST",
    url: "/users/signup",
    body: params,
  });
};

export const storeToken = (res) => {
  console.log("Storing Token:", res);

  if (!res.token) {
      console.error("No token received:", res);
      return;
  }

  localStorage.setItem("token", res.token);
  localStorage.setItem("expiry", res.expiry);
  localStorage.setItem("userId", res.userId);
};
