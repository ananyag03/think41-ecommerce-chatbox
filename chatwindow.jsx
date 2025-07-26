import MessageList from "./MessageList";
import UserInput from "./UserInput";
import HistoryPanel from "./HistoryPanel";

export default function ChatWindow() {
  return (
    <div className="flex h-screen">
      <HistoryPanel />
      <div className="flex flex-col flex-1 p-4">
        <MessageList />
        <UserInput />
      </div>
    </div>
  );
}
