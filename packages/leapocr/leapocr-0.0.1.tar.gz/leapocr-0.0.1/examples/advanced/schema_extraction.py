"""Advanced example: Schema-based structured data extraction with LeapOCR.

This example demonstrates:
- Using custom schemas for structured extraction
- Extracting specific fields from invoices
- Working with nested data structures

Requirements:
- LEAPOCR_API_KEY environment variable
"""

import asyncio
import json
import os

from leapocr import Format, LeapOCR, Model, ProcessOptions


async def main():
    # Get API key from environment
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        print("ERROR: LEAPOCR_API_KEY environment variable is required")
        return

    # Define custom schema for invoice extraction
    invoice_schema = {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "The invoice number",
            },
            "invoice_date": {
                "type": "string",
                "format": "date",
                "description": "The invoice date",
            },
            "due_date": {
                "type": "string",
                "format": "date",
                "description": "The payment due date",
            },
            "vendor_name": {
                "type": "string",
                "description": "The name of the vendor/supplier",
            },
            "vendor_address": {
                "type": "string",
                "description": "The vendor's address",
            },
            "customer_name": {
                "type": "string",
                "description": "The name of the customer",
            },
            "total_amount": {
                "type": "number",
                "description": "The total invoice amount",
            },
            "tax_amount": {
                "type": "number",
                "description": "The tax amount",
            },
            "currency": {
                "type": "string",
                "description": "The currency code (e.g., USD, EUR)",
            },
            "line_items": {
                "type": "array",
                "description": "List of invoice line items",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "total": {"type": "number"},
                    },
                },
            },
        },
        "required": ["invoice_number", "total_amount", "vendor_name"],
    }

    # Example invoice URL (replace with a real invoice)
    invoice_url = os.getenv("INVOICE_URL", "https://example.com/sample-invoice.pdf")

    print("=== Schema-Based Extraction ===\n")
    print(f"Processing invoice: {invoice_url}")
    print("\nSchema fields:")
    for field in invoice_schema["properties"]:
        print(f"  - {field}")

    async with LeapOCR(api_key) as client:
        print("\nStarting extraction with custom schema...")

        try:
            result = await client.ocr.process_and_wait(
                invoice_url,
                options=ProcessOptions(
                    format=Format.STRUCTURED,
                    model=Model.STANDARD_V1,  # Use best model for accuracy
                    schema=invoice_schema,
                    instructions=(
                        "Extract invoice data according to the provided schema. "
                        "Be precise with numbers and dates. "
                        "Ensure all line items are captured accurately."
                    ),
                ),
            )

            print("\n✓ Extraction completed successfully!")
            print(f"  Credits used: {result.credits_used}")
            print(f"  Processing time: {result.processing_time_seconds:.2f}s")
            print(f"  Pages processed: {len(result.pages)}")

            # Parse and display extracted data
            if result.pages:
                # The structured data is in the text field as JSON
                try:
                    extracted_data = json.loads(result.pages[0].text)

                    print("\n" + "=" * 50)
                    print("EXTRACTED INVOICE DATA")
                    print("=" * 50)

                    # Display main fields
                    print(f"Invoice Number: {extracted_data.get('invoice_number', 'N/A')}")
                    print(f"Invoice Date: {extracted_data.get('invoice_date', 'N/A')}")
                    print(f"Due Date: {extracted_data.get('due_date', 'N/A')}")
                    print(f"Vendor: {extracted_data.get('vendor_name', 'N/A')}")
                    print(f"Customer: {extracted_data.get('customer_name', 'N/A')}")
                    print(
                        f"Total Amount: {extracted_data.get('currency', '')} "
                        f"{extracted_data.get('total_amount', 0)}"
                    )

                    # Display line items if present
                    line_items = extracted_data.get("line_items", [])
                    if line_items:
                        print(f"\nLine Items ({len(line_items)}):")
                        for i, item in enumerate(line_items, 1):
                            print(f"  {i}. {item.get('description', 'N/A')}")
                            print(
                                f"     Qty: {item.get('quantity', 0)} × "
                                f"${item.get('unit_price', 0):.2f} = "
                                f"${item.get('total', 0):.2f}"
                            )

                    # Show full JSON
                    print("\nFull extracted data (JSON):")
                    print(json.dumps(extracted_data, indent=2))

                except json.JSONDecodeError:
                    print("\nExtracted text (not JSON):")
                    print(result.pages[0].text[:500])

        except Exception as e:
            print(f"\n✗ Extraction failed: {e}")
            print("\nNote: This example requires a real invoice URL and API access.")


if __name__ == "__main__":
    asyncio.run(main())
