import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import { useChat } from './hooks/useChat';

function App() {
  const { messages, isLoading, sendMessage, clearMessages } = useChat();

  return (
    <div className="h-screen flex flex-col">
      <Header />
      <ChatContainer
        messages={messages}
        isLoading={isLoading}
        onSendMessage={sendMessage}
        onClear={clearMessages}
      />
    </div>
  );
}

export default App;
