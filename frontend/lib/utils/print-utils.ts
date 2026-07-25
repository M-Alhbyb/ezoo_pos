/**
 * Printing utilities for POS system.
 */

interface ElectronAPI {
  printPDF: (base64Data: string, printerName?: string) => Promise<{ success: boolean; failureReason?: string; error?: string }>;
}

declare global {
  interface Window {
    api?: ElectronAPI;
  }
}

/**
 * Fetches an invoice PDF and prints it.
 * Uses Electron silent printing when available, falls back to browser print dialog.
 *
 * @param saleId The UUID of the sale to print
 */
export async function printInvoice(saleId: string) {
  try {
    const response = await fetch(`/api/sales/${saleId}/invoice`, {
      method: "GET",
      headers: {
        Accept: "application/pdf",
        Authorization: `Bearer ${localStorage.getItem("ezoo_token") || ""}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch invoice for printing");
    }

    const blob = await response.blob();

    // Electron silent print path
    if (window.api?.printPDF) {
      const arrayBuffer = await blob.arrayBuffer();
      const base64 = btoa(
        new Uint8Array(arrayBuffer).reduce(
          (data, byte) => data + String.fromCharCode(byte),
          ""
        )
      );
      const result = await window.api.printPDF(base64);
      if (!result.success) {
        console.error("Electron print failed:", result.failureReason || result.error);
      }
      return;
    }

    // Browser fallback — iframe-based print
    const url = window.URL.createObjectURL(blob);
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = url;
    document.body.appendChild(iframe);

    iframe.onload = () => {
      if (iframe.contentWindow) {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      }
      setTimeout(() => {
        if (document.body.contains(iframe)) {
          document.body.removeChild(iframe);
        }
        window.URL.revokeObjectURL(url);
      }, 5000);
    };
  } catch (error) {
    console.error("Printing error:", error);
  }
}
