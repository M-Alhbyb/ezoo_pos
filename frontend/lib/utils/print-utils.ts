/**
 * Printing utilities for POS system.
 */

/**
 * Fetches an invoice PDF and triggers the browser print dialog.
 * 
 * @param saleId The UUID of the sale to print
 */
export async function printInvoice(saleId: string) {
  try {
    const response = await fetch(`/api/sales/${saleId}/invoice`, {
      method: 'GET',
      headers: {
        'Accept': 'application/pdf'
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch invoice for printing');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    
    // Create a hidden iframe for printing
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = url;
    document.body.appendChild(iframe);
    
    iframe.onload = () => {
      // Focus the iframe and trigger print
      if (iframe.contentWindow) {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      }
      
      // Cleanup after a delay (printing is usually async in the browser)
      setTimeout(() => {
        if (document.body.contains(iframe)) {
          document.body.removeChild(iframe);
        }
        window.URL.revokeObjectURL(url);
      }, 5000); 
    };
  } catch (error) {
    console.error('Printing error:', error);
  }
}
