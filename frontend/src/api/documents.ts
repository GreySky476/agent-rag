import { request } from "./client";
import type {
  DocumentResponse,
  DocumentUploadResponse,
  KnowledgeDomain,
  KnowledgeDomainCreate,
} from "../types";

export function uploadDocument(
  file: File,
  importance: string = "L2",
  domainId?: number
): Promise<DocumentUploadResponse> {
  const form = new FormData();
  form.append("file", file);

  let url = `/documents/upload?importance=${importance}`;
  if (domainId) url += `&domain_id=${domainId}`;

  return fetch(`/api/v1${url}`, {
    method: "POST",
    body: form,
  }).then((res) => {
    if (!res.ok) {
      return res.json().then((err) => {
        throw new Error(err?.detail || "Upload failed");
      });
    }
    return res.json();
  });
}

export function listDocuments(statusFilter?: string): Promise<DocumentResponse[]> {
  const path = statusFilter ? `/documents?status=${statusFilter}` : "/documents";
  return request<DocumentResponse[]>(path);
}

export function getDocument(id: number): Promise<DocumentResponse> {
  return request<DocumentResponse>(`/documents/${id}`);
}

export function deleteDocument(id: number): Promise<{ detail: string }> {
  return request<{ detail: string }>(`/documents/${id}`, {
    method: "DELETE",
  });
}

export function createKnowledgeDomain(
  body: KnowledgeDomainCreate
): Promise<KnowledgeDomain> {
  return request<KnowledgeDomain>("/knowledge-domains", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function listKnowledgeDomains(): Promise<KnowledgeDomain[]> {
  return request<KnowledgeDomain[]>("/knowledge-domains");
}
