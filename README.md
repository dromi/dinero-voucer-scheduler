# Dinero Voucher Scheduler

This repository currently provides a helper script that verifies connectivity
with the Dinero API using the "personal integration" flow described in the
Dinero documentation. The script expects the following environment variables
to be defined:

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
stdout. The script exchanges the client ID/secret and API key for an access
token using `https://authz.dinero.dk/dineroapi/oauth/token` before listing the
organizations available to your credentials via `GET /v1/organizations`. It
then confirms that the provided `DINERO_ORG_ID` appears in that list, mirroring
the manual validation steps described in the Dinero "Personal integration"
guide.
