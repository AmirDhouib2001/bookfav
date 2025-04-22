import * as React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import Catalogue from './pages/Catalogue';
import Dashboard from './pages/Dashboard';

const App: React.FC = () => {
  return (
    <React.Fragment>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/catalogue" element={<Catalogue />} />
      </Routes>
    </React.Fragment>
  );
};

export default App;
