import React from 'react';

function Login({ loginData, setLoginData, handleLogin }) {
  return (
    <form onSubmit={handleLogin} className="auth-form">
      <h2>Welcome Back</h2>
      <div className="form-group">
        <input
          type="email"
          placeholder="Email"
          value={loginData.email}
          onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
          required
        />
      </div>
      <div className="form-group">
        <input
          type="password"
          placeholder="Password"
          value={loginData.password}
          onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
          required
        />
      </div>
      
      <button type="submit" className="submit-btn">Login</button>
    </form>
  );
}

export default Login;
