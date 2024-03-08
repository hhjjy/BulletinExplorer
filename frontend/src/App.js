import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Label from './Label';
import Raw from './Raw';

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