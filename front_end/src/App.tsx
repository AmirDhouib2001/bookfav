import * as React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import Catalogue from './pages/Catalogue';
import Dashboard from './pages/Dashboard';
import BookDetail from './pages/BookDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import UserProfile from './pages/UserProfile';
import PrivateRoute from './components/PrivateRoute';
import { AuthProvider } from './components/AuthProvider';

const App: React.FC = () => {
  return (
    <AuthProvider>
    <React.Fragment>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route 
          path="/dashboard" 
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } 
        />
        <Route path="/catalogue" element={<Catalogue />} />
        <Route path="/book/:isbn" element={<BookDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route 
          path="/profile" 
          element={
            <PrivateRoute>
              <UserProfile />
            </PrivateRoute>
          } 
        />
      </Routes>
    </React.Fragment>
    </AuthProvider>
  );
};

export default App;
