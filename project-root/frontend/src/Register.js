import React from 'react';

function Register({ registerData, setRegisterData, handleRegister }) {
  return (
    <form onSubmit={handleRegister} className="auth-form">
      <h2>Create Account</h2>
      <div className="form-group">
        <input
          type="email"
          placeholder="Email"
          value={registerData.email}
          onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
          required
        />
      </div>
      <div className="form-group">
        <input
          type="password"
          placeholder="Password"
          value={registerData.password}
          onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
          required
        />
      </div>
      <div className="form-group">
        <input
          type="text"
          placeholder="Full Name"
          value={registerData.fullName}
          onChange={(e) => setRegisterData({ ...registerData, fullName: e.target.value })}
        />
      </div>
      <button type="submit" className="submit-btn">Register</button>
    </form>
  );
}

export default Register;
