import slicereducer from "./slice";
import { configureStore } from "@reduxjs/toolkit";

const store = configureStore({
  reducer: {
    authentication: slicereducer,
  },
});

export default store;
