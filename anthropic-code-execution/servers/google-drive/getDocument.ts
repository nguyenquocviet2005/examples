/**
 * Get a document from Google Drive
 * @param documentId - The ID of the document to retrieve
 * @returns Document content and metadata
 */
export async function getDocument(documentId: string): Promise<object> {
  // Simulated tool for educational purposes
  console.log(`Fetching document with ID: ${documentId}`);
  
  // In a real implementation, this would call Google Drive API
  return {
    id: documentId,
    title: "Sample Document",
    content: "This is the document content",
    createdAt: new Date().toISOString(),
    modifiedAt: new Date().toISOString(),
  };
}
