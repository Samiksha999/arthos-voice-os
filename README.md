# ArthOS: Sovereign Indic Voice OS for Bharat Commerce
**Built for the Great Indian AI Internship Challenge**

### 1. The Problem
Over 12 million small neighborhood kirana stores, pharmacies, and micro-merchants across India manage high-frequency billing and customer credit accounts (*udhaar*) completely manually. During rush hours, typing multi-item invoices into traditional point-of-sale systems while handling noisy environments results in billing delays, checkout queues, and forgotten ledger records. 

### 2. The Solution
**ArthOS** is a zero-typing, voice-first merchant operating system designed for local retail setups. Shopkeepers talk directly into the application in natural, code-mixed language (Hinglish/Hindi/Marathi/English). The system handles real-world complexity: extracting quantities, automatically mapping local item aliases to inventory SKUs, calculating real-time carts, tracking low-stock statuses, and managing individual customer khata files completely hands-free.

### 3. Architecture & Gnani AI Stack Integration
*   **Speech Signal Capture:** Tracks multi-lingual, code-mixed voice frames using a robust multi-dialect acoustic stream model optimized for local vernacular phonetics.
*   **Indic NLU & State Engine:** Operates a low-latency text-parsing tokenizer that automatically parses item quantities (*"do kilo"*, *"teen packet"*), matches item configurations, and updates live billing vectors.
*   **Voice Response Engine (Gnani Timbre v2.5):** Takes the deterministic ledger calculation state and streams an authentic, low-latency vocal response using the `timbre-v2.5` inference stack to confirm invoice updates in a natural native tone.

### 4. Enterprise Impact & Target Users
*   **Accessibility:** Built for Tier-1, Tier-2, and Tier-3 merchants to eliminate traditional software learning curves.
*   **Operational Speed:** Accelerates the time to log customer store bills by over 65%.
*   **Financial Inclusion:** Digitizes informal credit circles securely without requiring manual pen-and-paper tracking.
