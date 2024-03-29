import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Raw from './Pages/Raw/Raw.jsx';
import Label from './Pages/Label/Label.jsx';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Raw />} />
                <Route path="/label" element={<Label />} />
            </Routes>
        </Router>
    );
}

export default App;