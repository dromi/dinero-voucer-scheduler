# Dinero Voucher Scheduler

This repository currently provides a helper script that verifies connectivity
with the Dinero API using the credentials made available in the following
environment variables:

- `DINERO_CLIENT_ID`
- `DINERO_CLIENT_SECRET`
- `DINERO_API_KEY`
- `DINERO_ORG_ID`

## Verifying the Dinero connection

1. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Export the required Dinero credentials:

   ```bash
   export DINERO_CLIENT_ID=...
   export DINERO_CLIENT_SECRET=...
   export DINERO_API_KEY=...
   export DINERO_ORG_ID=...
   ```

3. Run the verification script:

   ```bash
   python connect_dinero.py
   ```

   Alternatively, you can copy the sample `run_connect_dinero.sh` helper,
   replace the placeholder values with your credentials, and execute it to
   export the environment variables and run the script in one step:

   ```bash
   ./run_connect_dinero.sh
   ```

If the credentials are valid you will see a confirmation message printed to
stdout.
