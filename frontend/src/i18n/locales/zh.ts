const zh = {
  app: { title: "RAG Agent" },
  nav: { chat: "对话", knowledge: "知识库" },
  lang: { label: "中", tooltip: "切换到英文" },

  sidebar: {
    search: "搜索对话...",
    new: "新对话",
    today: "今天",
    yesterday: "昨天",
    earlier: "更早",
    empty: "暂无对话，点击 + 开始",
    noResults: "无搜索结果",
    rename: "重命名",
    delete: "删除",
    untitled: "未命名",
  },

  chat: {
    placeholder: "输入问题，Enter 发送，Shift+Enter 换行",
    send: "发送",
    stop: "停止",
    assistant: "助手",
    error: "错误",
    retry: "重试",
  },

  empty: {
    title: "RAG Agent",
    desc: "上传知识库文档后开始提问。Agent 可以搜索知识图谱、查询结构化数据并执行计算。",
    tryAsking: "试试问：",
    suggestion1: "知识库中有哪些文档？",
    suggestion2: "如何用 SQL 分析结构化数据？",
    suggestion3: "搜索特定主题的信息",
  },

  tool: {
    running: "执行中...",
    input: "输入：",
    result: "结果：",
    details: "详情：",
  },

  kb: {
    title: "知识库管理",
    allDomains: "全部领域",
    allLevels: "全部级别",
    searchFiles: "搜索文件名...",
    L1: "L1 - 元数据",
    L2: "L2 - 轻提取",
    L3: "L3 - 全图谱",
  },

  upload: {
    drop: "拖拽文件到此处或点击上传",
    formats: "支持 PDF / TXT / MD / CSV",
    uploading: "上传中...",
    success: "已上传 \"{name}\"（{count} 个块）",
    failed: "上传失败",
    deleteFailed: "删除失败",
    deleted: "文档已删除",
    loadFailed: "加载数据失败",
  },

  doc: {
    name: "名称",
    domain: "领域",
    level: "级别",
    status: "状态",
    actions: "操作",
    empty: "暂无文档，上传第一个文件开始",
  },

  stats: {
    files: "个文件",
    domains: "个领域",
    lastProcessed: "最近处理：",
  },

  dialog: {
    cancel: "取消",
    delete: "删除",
    deleteTitle: "删除文档",
    deleteMsg: "确认删除 \"{name}\"？此操作不可撤销。",
    deleteConfirmTitle: "删除对话",
    deleteConfirmMsg: "确认删除对话 \"{name}\"？此操作不可撤销。",
  },
};

export default zh;
