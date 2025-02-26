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
  
  // Store user preferences
  if (res.profile) {
      localStorage.setItem("userProfile", JSON.stringify({
          skills: res.profile.skills || [],
          job_levels: res.profile.job_levels || [],
          locations: res.profile.locations || [],
          institution: res.profile.institution || '',
          phone_number: res.profile.phone_number || '',
          address: res.profile.address || '',
          email: res.profile.email || '',
          fullName: res.profile.fullName || ''
      }));
  }
};
