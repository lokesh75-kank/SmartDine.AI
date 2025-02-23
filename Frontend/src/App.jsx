import { useState } from 'react'
import LiveKitModal from './components/LiveKitModal'
import './App.css'

function App() {
  const [showSupport, setShowSupport] = useState(false);

  const handleTalkToAgent = () => {
    setShowSupport(true);
  };

  return (
    <div className="ai-container">
      <div className="ai-content">
        <div className="ai-circle">
          <div className="pulse"></div>
          <div className="ai-icon">AI</div>
        </div>
        <h1>SmartDine AI</h1>
        <p style={{ whiteSpace: 'nowrap', textAlign: 'center' }}>Voice-Powered Restaurant Booking.</p>
        <button className="ai-button" onClick={handleTalkToAgent}>
          <div className="button-content">
            <span className="mic-icon">🎙️</span>
            <span>Start Conversation</span>
          </div>
        </button>
      </div>
      {showSupport && <LiveKitModal setShowSupport={setShowSupport} />}
    </div>
  )
}

export default App