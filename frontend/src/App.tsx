import "@/styles/bootstrap.scss";

import '@fortawesome/fontawesome-svg-core/styles.css'
import { config } from '@fortawesome/fontawesome-svg-core'
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Header from "@/shared/components/Header";
import { routes } from "@/config/routes";

config.autoAddCss = false

function App() {
  return (
      <>
        <ToastContainer 
          position="top-center"
          autoClose={3500}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          pauseOnHover
          draggable
        />
        <BrowserRouter>
          <Header />
          <Routes>
            {routes.map((route, index) => (
              <Route key={index} {...route} />
            ))}
          </Routes>
        </BrowserRouter>
      
    </>
  )
}

export default App
