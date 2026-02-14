import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from './useAuth';


export default function Login() {

  const authContext = useAuth();

  let navigate = useNavigate();
  
  const [userId, setUserId] = useState('demo');
  const [password, setPassword] = useState('dummy');

  async function handleLogin() {
    // Handle login logic here
    if ( await authContext.login(userId, password) ) {
      navigate(`/todos`);
    }
  }

  return (
    <div className="container w-25 mt-5 border p-4 rounded">

        <h2>Login Page</h2>

        <div className='login-form'>
          <fieldset className="form-group">
            <label htmlFor="userId">User Id</label>
            <input className="form-control" type="text" placeholder="userId" name="userId" id="userId" value={userId} onChange={(e) => setUserId(e.target.value)} />
          </fieldset>

          <fieldset className="form-group mt-2">
            <label htmlFor="password">Password</label>
            <input className="form-control" type="password" placeholder="password" name="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </fieldset>
          
          <div className="text-center mt-2">
            <button className="btn btn-primary" onClick={handleLogin}>Login</button>
          </div>
        </div>
    </div>
  )
}