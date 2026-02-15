import { useNavigate } from 'react-router-dom';
import { useState, SubmitEvent } from 'react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { ROUTES } from '@/shared/constants';

export default function Login() {
  
  let navigate = useNavigate();
  
  const {login} = useAuth();

  const [userId, setUserId] = useState('demo');
  const [password, setPassword] = useState('dummy');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e:SubmitEvent) => {
    e.preventDefault();

    if (!userId || !password) {
      return;
    }

    setIsLoading(true);

    try {
      const success = await login(userId, password);

      if(success) {
        navigate(ROUTES.TODOS);
      }

    }
    finally {
      setIsLoading(false);
    }

  }

  return (
    <div className="container w-25 mt-5 border p-4 rounded">

        <h2>Login Page</h2>

        <form onSubmit={handleSubmit} className='login-form'>
          <fieldset className="form-group">
            <label htmlFor="userId">User Id</label>
            <input 
              className="form-control" 
              type="text" 
              placeholder="userId" 
              name="userId" 
              id="userId" 
              value={userId} 
              onChange={(e) => setUserId(e.target.value)} 
              disabled={isLoading}
              />
          </fieldset>

          <fieldset className="form-group mt-2">
            <label htmlFor="password">Password</label>
            <input 
              className="form-control" 
              type="password" 
              placeholder="password" 
              name="password" 
              id="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              disabled={isLoading}
              />
          </fieldset>

          <div className="text-center mt-2">
            <button 
              className="btn btn-primary" 
              type="submit"
              disabled={isLoading}>
                {isLoading ? 'Loading...' : 'Login'}
              </button>
          </div>
        </form>

    </div>
  )
}