const en = {
  app: { title: "RAG Agent" },
  nav: { chat: "Chat", knowledge: "Knowledge" },
  lang: { label: "EN", tooltip: "Switch to Chinese" },

  sidebar: {
    search: "Search conversations...",
    new: "New conversation",
    today: "Today",
    yesterday: "Yesterday",
    earlier: "Earlier",
    empty: 'No conversations yet. Click "+" to start.',
    noResults: "No results found.",
    rename: "Rename",
    delete: "Delete",
    untitled: "Untitled",
  },

  chat: {
    placeholder: "Type a message... Enter to send, Shift+Enter for new line",
    send: "Send",
    stop: "Stop",
    assistant: "Assistant",
    error: "Error",
    retry: "Retry",
  },

  empty: {
    title: "RAG Agent",
    desc: "Upload documents to the knowledge base to start asking questions. The Agent can search, query databases, and run calculations.",
    tryAsking: "Try asking:",
    suggestion1: "What documents are available in the knowledge base?",
    suggestion2: "How can I analyze structured data with SQL?",
    suggestion3: "Search for information about a specific topic",
  },

  tool: {
    running: "running...",
    input: "Input:",
    result: "Result:",
    details: "Details:",
  },

  kb: {
    title: "Knowledge Base",
    allDomains: "All domains",
    allLevels: "All levels",
    searchFiles: "Search files...",
    L1: "L1 - Metadata",
    L2: "L2 - Light",
    L3: "L3 - Full",
  },

  upload: {
    drop: "Drop files here or click to upload",
    formats: "PDF / TXT / MD / CSV",
    uploading: "Uploading...",
    success: 'Uploaded "{name}" ({count} chunks)',
    failed: "Upload failed",
    deleteFailed: "Delete failed",
    deleted: "Document deleted",
    loadFailed: "Failed to load data",
  },

  doc: {
    name: "Name",
    domain: "Domain",
    level: "Level",
    status: "Status",
    actions: "Actions",
    empty: "No documents yet. Upload your first file to get started.",
  },

  stats: {
    files: "files",
    domains: "domains",
    lastProcessed: "Last processed:",
  },

  dialog: {
    cancel: "Cancel",
    delete: "Delete",
    deleteTitle: "Delete Document",
    deleteMsg: 'Delete "{name}"? This action cannot be undone.',
    deleteConfirmTitle: "Delete Conversation",
    deleteConfirmMsg: 'Delete conversation "{name}"? This cannot be undone.',
  },
};

export default en;
