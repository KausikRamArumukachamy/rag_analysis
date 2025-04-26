import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import AnalysisPage from "./pages/AnalysisPage";

function App() {
  return (
    <Router>
      <div className="p-5 max-w-3xl mx-auto">
        {/* Routes */}
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
