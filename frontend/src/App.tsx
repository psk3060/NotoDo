import "@/styles/bootstrap.scss";

import '@fortawesome/fontawesome-svg-core/styles.css'
import { config } from '@fortawesome/fontawesome-svg-core'

import TodoApp from "./TodoApp";

config.autoAddCss = false

function App() {
  return (
    <>
      <TodoApp />
    </>
  )
}

export default App
