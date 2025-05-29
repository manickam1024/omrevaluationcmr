import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { onAuthStateChanged, getAuth } from "firebase/auth";
import { additem, removeitem } from "./utils/slice";
import { useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import { useSelector } from "react-redux";
import firebaseConfig from "./utils/firebase";

const Header = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const auth = getAuth();
  const data = useSelector((stor) => stor.authentication.items);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        const { uid, email, displayName, photoURL } = user;
        dispatch(additem({ email, uid, displayName, photoURL }));
        navigate("/browse");
      } else {
        dispatch(removeitem());
        navigate("/");
      }
    });

    // ✅ Clean up the listener
    return () => unsubscribe();
  }, []);

  function handlesignout() {
    signOut(auth)
      .then(() => {})
      .catch((error) => {});
  }
  return (
    <div className="h-16 w-full flex-col absolute z-40">
      <div className="right-0 absolute flex top-4 right-16 ">
        <div className="pr-16 text-white text-xl font-bold relative top-4"></div>

        <div>
          {" "}
          <button
            onClick={handlesignout}
            className="p-2 w-24 bg-gray-300 text-black text-l mt-3 font-bold rounded-md hover:cursor-pointer">
            Sign Out
          </button>
        </div>
        <br />
      </div>
    </div>
  );
};

export default Header;
