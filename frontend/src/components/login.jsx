import { useState } from "react";
import { validate } from "./utils/validation";
import { useRef } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";
import firebaseConfig from "./utils/firebase";
import { getAuth, updateProfile } from "firebase/auth";

const Login = () => {
  const [signin, setsignin] = useState(true);

  const [msg, setMsg] = useState();

  const email = useRef(null);
  const password = useRef(null);
  const username = useRef(null);
  const reenterpassword = useRef(null);
  const auth = getAuth();

  function handleclick() {
    const result = validate(email.current.value, password.current.value);

    setMsg(result);

    //firebase method for signin
    {
      signin &&
        signInWithEmailAndPassword(
          auth,
          email.current.value,
          password.current.value,
        )
          .then((userCredential) => {
            const user = userCredential.user;
          })
          .catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;

            setMsg("wrong username or password");
          });
    }

    //sign up evaluation
    if (!signin && password.current.value != reenterpassword.current.value) {
      setMsg("password does not match");
    }
    //firebase signup evaluation
    {
      !signin &&
        createUserWithEmailAndPassword(
          auth,
          email.current.value,
          password.current.value,
        )
          .then((userCredential) => {
            // Signed up
            const user = userCredential.user;
            updateProfile(user, {
              displayName: username.current.value,
              photoURL: "https://example.com/jane-q-user/profile.jpg",
            });

            window.alert("user succesfully signed up");
            // ...
          })
          .catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            // ..
          });
    }
  }

  return (
    <div>
      {" "}
      {/* here i provided z-index so that my header  element goes back of my div */}
      <div className="absolute overflow-hidden z-50 ">
        {" "}
        <img
          className="overflow-hidden h-screen w-screen"
          src="https://www.webdesign.org/img_articles/20925/step01.gif"
          alt=""
        />
      </div>
      <div
        id="loginform"
        style={{ height: "max-content ", width: "900px" }}
        className=" bg-black absolute left-0 right-0 top-0 bottom-0 my-auto mx-auto rounded-4xl bg-opacity-80 pb-8 z-50 opacity-80">
        <h1
          className="text-white text-3xl p-12 pl-12 font-bold "
          style={{
            left: "300px",
            position: "relative",
          }}>
          {" "}
          {signin ? " Admin Login" : "Admin Signup"}
        </h1>
        <form className="p-5 pl-12  relative " style={{ left: "100px" }}>
          {" "}
          <input
            ref={email}
            type="text"
            name="email"
            id="email"
            className=" p-2 w-72 mb-8 rounded-sm bg-transparent border-gray-500 border-2 text-gray-400"
            style={{ width: "600px" }}
            placeholder="email"
            required
          />{" "}
          <br />
          <input
            ref={password}
            type="password"
            name="password"
            style={{ width: "600px" }}
            placeholder="password"
            className=" p-2 w-72 mb-8 rounded-sm bg-transparent  border-gray-500 border-2  text-gray-400"
            required
          />
          {!signin && (
            <input
              ref={reenterpassword}
              type="password"
              style={{ width: "600px" }}
              name="reenterpassword"
              placeholder="Re-enter password"
              className=" p-2 w-72 mb-6 rounded-sm bg-transparent  border-gray-500 border-2  text-gray-400"
              required
            />
          )}
          {!signin && (
            <input
              ref={username}
              type="text"
              style={{ width: "600px" }}
              name="name"
              placeholder="ENTER FULL NAME"
              className=" p-2 w-72 mb-6 rounded-sm bg-transparent  border-gray-500 border-2  text-gray-400"
              required
            />
          )}
          <p className="text-red-600 pb-9">{msg}</p>
          <button
            className="bg-gray-300 w-72 p-2 rounded-xl text-black font-bold hover:cursor-pointer"
            style={{ width: "600px" }}
            onClick={function (event) {
              event.preventDefault();
              handleclick();
            }}>
            {signin ? " login" : "signup"}
          </button>
          <button
            className="  text-white font-bold mt-5 hover:cursor-pointer"
            style={{ width: "600px" }}
            onClick={function (event) {
              event.preventDefault(); // stops default reloading of page because its in form
              setsignin(!signin);
            }}>
            {signin ? "New user ? just sign up" : "Existing user? sign in "}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
