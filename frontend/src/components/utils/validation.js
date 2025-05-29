export const validate = (email, password) => {
  const regexemail = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const regexpassword = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

  if (!regexemail.test(email)) {
    return "Enter a valid email";
  }

  if (!regexpassword.test(password)) {
    return "Password must contain at least 8 characters, one uppercase, one lowercase, and one digit";
  }

  return null;
};
