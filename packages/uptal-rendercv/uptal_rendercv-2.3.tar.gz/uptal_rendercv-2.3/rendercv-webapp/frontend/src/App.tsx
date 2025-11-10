import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Toaster } from "react-hot-toast";
import { CVProvider } from "./components/CVProvider";
import Header from "./components/Layout/Header";
import SplitView from "./components/Layout/SplitView";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <CVProvider>
        <div className="app">
          <Header />
          <SplitView />
          <Toaster position="top-right" />
        </div>
      </CVProvider>
    </ThemeProvider>
  );
}

export default App;
