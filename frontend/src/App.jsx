import ReactDOM from "react-dom/client";
import { createBrowserRouter, Outlet, RouterProvider } from "react-router-dom";
import Login from "./components/login";
import Header from "./components/header";
import Footer from "./components/footer";
import { Provider } from "react-redux";
import store from "./components/utils/appstore";
import Browse from "./components/browse";
import "./components/main.css"; // Or './main.css' depending on your filename

// App component
const App = () => {
  return (
    <Provider store={store}>
      <Header />
      <Outlet />
    </Provider>
  );
};

// Router setup
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "/",
        element: <Login />,
      },

      {
        path: "/browse",
        element: <Browse />,
      },
    ],
  },
]);

console.log(router);
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<RouterProvider router={router} />);
