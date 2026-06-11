'use client';

import { useState, useEffect, useRef } from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useChatStore } from '@/store/chatStore';
import { chatApi } from '@/lib/api';
import { toast } from 'sonner';
import { Spinner } from '@/components/ui/spinner';
import { Send, Plus, Trash2, MessageSquare, Bot, User, ChevronLeft, Paperclip, X, FileText, Image, File } from 'lucide-react';
import type { Attachment } from '@/types';

const IMAGE_TYPES = new Set(['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg']);
const FILE_ICONS: Record<string, typeof FileText> = {
  pdf: FileText, docx: FileText, txt: FileText,
  py: FileText, js: FileText, ts: FileText, tsx: FileText,
};

function FilePreview({ file, onRemove }: { file: { name: string; type: string; url?: string; size?: number }; onRemove?: () => void }) {
  const ext = file.name.split('.').pop()?.toLowerCase() || '';
  const isImage = IMAGE_TYPES.has(ext) || file.type.startsWith('image/');
  const Icon = FILE_ICONS[ext] || File;

  return (
    <div className="relative flex items-center gap-2 bg-gray-50 rounded-lg p-2 pr-8 border text-sm max-w-[200px]">
      {isImage && file.url ? (
        <img src={file.url} alt={file.name} className="w-10 h-10 rounded object-cover" />
      ) : (
        <Icon className="w-8 h-8 text-gray-400 shrink-0" />
      )}
      <span className="truncate text-xs">{file.name}</span>
      {onRemove && (
        <button onClick={onRemove} className="absolute top-1 right-1 p-0.5 rounded-full hover:bg-gray-200">
          <X className="w-3 h-3" />
        </button>
      )}
    </div>
  );
}

function AttachmentDisplay({ attachments }: { attachments: Attachment[] }) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return (
    <div className="flex flex-wrap gap-2 mt-2">
      {attachments.map((att, i) => {
        const ext = att.file_name.split('.').pop()?.toLowerCase() || '';
        const isImage = IMAGE_TYPES.has(ext) || IMAGE_TYPES.has(att.file_type);
        const url = `${API_URL}${att.file_url}`;
        return isImage ? (
          <a key={i} href={url} target="_blank" rel="noopener noreferrer">
            <img src={url} alt={att.file_name} className="max-w-[200px] max-h-[200px] rounded-lg border object-cover hover:opacity-80 transition" />
          </a>
        ) : (
          <a key={i} href={url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 bg-gray-100 rounded-lg p-2 text-xs hover:bg-gray-200 transition">
            <File className="w-4 h-4 shrink-0" />
            <span className="truncate max-w-[120px]">{att.file_name}</span>
          </a>
        );
      })}
    </div>
  );
}

export default function ChatPage() {
  const {
    conversations, currentConversation, messages, isLoading, isStreaming,
    setConversations, setCurrentConversation, addConversation,
    removeConversation, setMessages, addMessage, setIsLoading, setIsStreaming,
  } = useChatStore();

  const [input, setInput] = useState('');
  const [showSidebar, setShowSidebar] = useState(true);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConversations = async () => {
    try {
      const res = await chatApi.getConversations();
      setConversations(res.data.conversations);
    } catch {
      // silent
    }
  };

  const loadMessages = async (conversationId: string) => {
    try {
      const res = await chatApi.getMessages(conversationId);
      setMessages(res.data);
    } catch {
      toast.error('Failed to load messages');
    }
  };

  const handleNewChat = async () => {
    try {
      const res = await chatApi.createConversation({ title: 'New Chat' });
      addConversation(res.data);
      setCurrentConversation(res.data);
      setMessages([]);
      setShowSidebar(false);
    } catch {
      toast.error('Failed to create conversation');
    }
  };

  const handleSelectConversation = async (conv: any) => {
    setCurrentConversation(conv);
    await loadMessages(conv.id);
    setShowSidebar(false);
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await chatApi.deleteConversation(id);
      removeConversation(id);
      if (currentConversation?.id === id) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch {
      toast.error('Failed to delete');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setPendingFiles((prev) => [...prev, ...files]);
    e.target.value = '';
  };

  const removePendingFile = (index: number) => {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSend = async () => {
    if ((!input.trim() && pendingFiles.length === 0) || isStreaming) return;

    let conv = currentConversation;
    if (!conv) {
      try {
        const title = input.slice(0, 100) || 'New Chat';
        const res = await chatApi.createConversation({ title });
        addConversation(res.data);
        setCurrentConversation(res.data);
        conv = res.data;
      } catch {
        toast.error('Failed to create conversation');
        return;
      }
    }

    if (!conv) return;

    setIsLoading(true);

    let attachments: Attachment[] = [];
    if (pendingFiles.length > 0) {
      try {
        const results = await Promise.all(pendingFiles.map((f) => chatApi.uploadFile(f)));
        attachments = results.map((r) => r.data);
      } catch {
        toast.error('Failed to upload files');
        setIsLoading(false);
        return;
      }
    }

    const userMessage = {
      id: Date.now().toString(),
      conversation_id: conv.id,
      role: 'user' as const,
      content: input,
      attachments,
      created_at: new Date().toISOString(),
    };
    addMessage(userMessage);
    setInput('');
    setPendingFiles([]);
    setIsLoading(true);

    try {
      const res = await chatApi.sendMessage(conv.id, { content: userMessage.content, attachments });
      addMessage({ ...res.data.assistant_message, role: 'assistant' });
    } catch {
      toast.error('Failed to get response');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="flex h-[calc(100vh-8rem)] gap-4">
        <div className={`${showSidebar ? 'w-72' : 'w-0'} transition-all overflow-hidden`}>
          <div className="w-72 space-y-2">
            <Button onClick={handleNewChat} className="w-full gap-2">
              <Plus className="h-4 w-4" /> New Chat
            </Button>
            <div className="space-y-1 overflow-y-auto max-h-[calc(100vh-12rem)]">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv)}
                  className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer text-sm ${
                    currentConversation?.id === conv.id ? 'bg-primary-50 text-primary-700' : 'hover:bg-gray-100'
                  }`}
                >
                  <MessageSquare className="h-4 w-4 shrink-0" />
                  <span className="truncate flex-1">{conv.title}</span>
                  <button onClick={(e) => handleDeleteConversation(e, conv.id)} className="opacity-0 hover:opacity-100">
                    <Trash2 className="h-3 w-3 text-gray-400 hover:text-red-500" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex-1 flex flex-col">
          <Button variant="ghost" size="sm" className="w-fit mb-2" onClick={() => setShowSidebar(!showSidebar)}>
            <ChevronLeft className={`h-4 w-4 mr-1 transition-transform ${showSidebar ? '' : 'rotate-180'}`} />
            {showSidebar ? 'Hide' : 'Show'} sidebar
          </Button>

          <Card className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && !isLoading && (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <Bot className="h-12 w-12 mb-4" />
                  <p className="text-lg font-medium">Start a conversation</p>
                  <p className="text-sm">Ask me anything about your studies</p>
                </div>
              )}

              {messages.map((msg) => (
                <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
                      <Bot className="h-4 w-4 text-primary-600" />
                    </div>
                  )}
                  <div className={`max-w-[70%] rounded-2xl p-4 ${
                    msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100'
                  }`}>
                    {msg.content && <p className="text-sm whitespace-pre-wrap">{msg.content}</p>}
                    {msg.attachments && msg.attachments.length > 0 && (
                      <AttachmentDisplay attachments={msg.attachments} />
                    )}
                    <p className="text-xs opacity-50 mt-1">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center shrink-0">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary-600" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl p-4">
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm text-gray-500">Thinking</span>
                      <span className="flex gap-0.5">
                        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="border-t p-4 space-y-2">
              {pendingFiles.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {pendingFiles.map((f, i) => (
                    <FilePreview key={i} file={{ name: f.name, type: f.type, size: f.size }} onRemove={() => removePendingFile(i)} />
                  ))}
                </div>
              )}
              <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
                <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileSelect} accept=".png,.jpg,.jpeg,.gif,.webp,.svg,.pdf,.docx,.txt,.csv,.md" />
                <Button type="button" variant="ghost" size="icon" onClick={() => fileInputRef.current?.click()} disabled={isStreaming}>
                  <Paperclip className="h-4 w-4" />
                </Button>
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a question..."
                  disabled={isStreaming}
                />
                <Button type="submit" disabled={(!input.trim() && pendingFiles.length === 0) || isStreaming}>
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
