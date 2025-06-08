import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import TestCasePage from './pages/TestCasePage';
import TestSuitePage from './pages/TestSuitePage';
import TestResultPage from './pages/TestResultPage';
import ApiDefinitionPage from './pages/ApiDefinitionPage';
import { Layout, Typography, Flex, Button } from 'antd';
// import './HomePage.css'; // No longer needed for this layout

const { Content } = Layout;
const { Title } = Typography;

function App() {
  return (
    <Router>
      {/* Main Layout - provides basic structure for other routes */} 
      <Layout style={{ minHeight: '100vh' }}>
        {/* Content area for other routes - minimal padding */} 
        <Content style={{ padding: 0 }}>
          <Routes>
            {/* Home Page route: Absolute positioned container for full viewport centering */} 
            <Route 
              path="/"
              element={
                <div style={{
                  position: 'absolute', /* Absolute positioning */
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  textAlign: 'center', /* Center inline content */
                  padding: '20px', /* Add some padding */
                  backgroundColor: '#f0f2f5' /* Optional: Add a background color */
                }}>
                  {/* Centered Platform Name */} 
                  <Title level={1} style={{ marginBottom: '40px' }}>Django Test Platform</Title>
                  
                  {/* Navigation buttons with spacing and styling */} 
                  {/* Flex container for buttons, centered horizontally within the div */} 
                  <Flex vertical gap="middle" align="center" style={{ width: '100%', maxWidth: '400px' }}> 
                    <Button type="primary" size="large" block>
                      <Link to="/test-cases" style={{ color: 'inherit' }}>Test Cases</Link>
                    </Button>
                    <Button type="primary" size="large" block>
                      <Link to="/test-suites" style={{ color: 'inherit' }}>Test Suites</Link>
                    </Button>
                    <Button type="primary" size="large" block>
                      <Link to="/test-results" style={{ color: 'inherit' }}>Test Results</Link>
                    </Button>
                    <Button type="primary" size="large" block>
                      <Link to="/api-definitions" style={{ color: 'inherit' }}>API Definitions</Link>
                    </Button>
                  </Flex>
                </div>
              }
            />

            {/* Routes for other components - they will render within the Content area */} 
            <Route path="/test-cases" element={<TestCasePage />} />
            <Route path="/test-suites" element={<TestSuitePage />} />
            <Route path="/test-results" element={<TestResultPage />} />
            <Route path="/api-definitions" element={<ApiDefinitionPage />} />
          </Routes>
        </Content>
        {/* Optional Footer */}
        {/* <Layout.Footer style={{ textAlign: 'center' }}>Ant Design ©2023 Created by Ant UED</Layout.Footer> */} 
      </Layout>
    </Router>
  );
}

export default App;