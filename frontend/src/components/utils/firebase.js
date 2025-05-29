// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyC9G1zCcX6NJdcziP1biNKE25_W2dGMMlk",
  authDomain: "omrevaluation-bf852.firebaseapp.com",
  projectId: "omrevaluation-bf852",
  storageBucket: "omrevaluation-bf852.firebasestorage.app",
  messagingSenderId: "633701498924",
  appId: "1:633701498924:web:6458ef02b79a1b387c9189",
  measurementId: "G-M185LGZ6B4",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export default firebaseConfig;
