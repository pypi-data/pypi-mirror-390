T-OCR Library
--------------

This is a Python library that contains methods for easy and fast OCR parsing with various tools. Used to read scanned PDF documents and images with text.

|

Key Features
------------

1. File parsing is done in the AWS cloud, eliminating the need for additional dependencies on your machine.
2. Parsing of each page is done in parallel in AWS, resulting in a significantly faster parsing process.
3. Access to the T-OCR AWS part is required to use the library.
4. Combines the best OCR tools and provides a consistent interface, making it easy to use and switch between tools.

    .. code-block:: python

         # Parsing with Tesseract (Free OCR)
         free_ocr = FreeOCR()
         pages = free_ocr.read_pdf("1.pdf")
         for page in pages:
             print(page.full_text)

    .. code-block:: python

         # Parsing with Textract
         textract = Textract()
         pages = textract.read_pdf("1.pdf")
         for page in pages:
             print(page.full_text)

5. The package contains a large number of powerful methods that will help you save time and read parsed data faster and better.

    .. code-block:: python

         # Get dates etc. from text
         date_matches = get_valid_dates("Text - February 17, 2009, text...")  # 02/17/2009

         # Compare the real text with what the OCR read
         does_strings_match_by_fuzzy("Apple", "Appla", percentage=0.8)  # True
         does_text_contains_string_by_fuzzy("Apple", "Appla watch", percentage=0.8) # True

         text = "Long article about Appla watch"
         find_string_in_text_by_fuzzy("Apple", text, percentage=0.8)  # 19

6. Caching OCR results locally in `t_ocr_cache` folder is supported. Use this during development to avoid blocking parsing time.

    .. code-block:: python

         pdf_file = "file.pdf"
         # First run
         free_ocr.read_pdf("1.pdf", cache_data=True) # Takes 15 seconds
         # Every next run
         free_ocr.read_pdf("1.pdf", cache_data=True) # Takes 0.01 seconds

         # If the state of the file or arguments changes, it will save the cache for this call too
         free_ocr.read_pdf("1.pdf", dpi=500, cache_data=True) # Takes 15 seconds
         free_ocr.read_pdf("1.pdf", dpi=500, cache_data=True) # Takes 0.01 seconds

|

Supported OCR Tools
-------------------

**1. Tesseract (Free OCR)**

    - 🆓 Free
    - ✅ Read text
    - ❌ Read tables, vertical field values
    - ⬛ Simple form design preferred

**2. AWS Textract**

    - 💸 Paid
    - ✅ Read text
    - ✅ Read tables, vertical field values
    - 🌃 Flexible for different file designs
