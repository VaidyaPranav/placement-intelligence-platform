// Client-side PDF Text Extraction Service

import * as pdfjsLib from 'pdfjs-dist';

// Configure PDFJS worker path using Unpkg CDN matching package version
pdfjsLib.GlobalWorkerOptions.workerSrc = '//unpkg.com/pdfjs-dist@6.0.227/build/pdf.worker.min.mjs';

/**
 * Extracts raw text content page-by-page from a PDF File object.
 */
export async function extractTextFromPDF(file: File): Promise<string> {
  try {
    const arrayBuffer = await file.arrayBuffer();
    const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
    const pdf = await loadingTask.promise;
    let fullText = '';

    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const textContent = await page.getTextContent();
      const pageText = textContent.items
        .map((item: any) => item.str || '')
        .join(' ');
      fullText += pageText + '\n';
    }

    const trimmedText = fullText.trim();
    if (trimmedText.length < 10) {
      throw new Error("No readable text found in PDF resume. Please verify the document content.");
    }
    return trimmedText;
  } catch (error: any) {
    console.error("[PDF EXTRACTOR] Error parsing PDF:", error);
    throw new Error(error.message || "Failed to parse PDF file. Ensure it is a valid, unencrypted document.");
  }
}
