import { BrowserRouter, Routes, Route } from "react-router-dom";
import SearchResultsPage from "./pages/SearchResultsPage";
import BusinessProfilePage from "./pages/BusinessProfilePage";
import { ThemeProvider } from "./context/ThemeContext";

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SearchResultsPage />} />
          <Route path="/business/:id" element={<BusinessProfilePage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
