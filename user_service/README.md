Based on the provided code and the discussion, here's the structured approach we have followed and the adjustments made to resolve the issues:

### Structure and Adjustments:

1. **Dependency Management with `get_supabase_client()`**:
   - This function dynamically selects between using a mock Supabase client (`MockSupabaseClient`) or a real Supabase client (`supabase.create_client`) based on the environment variable `USE_MOCK_SUPABASE`.

2. **MockSupabaseClient**:
   - Implements mock functionality for `sign_up`, `sign_in`, `set_access_token`, and `user` methods.
   - Stores user data in an in-memory list (`users`).

3. **Endpoint Definitions**:
   - **`/register`**: Registers a user using the Supabase client (`supabase_client.auth.sign_up`).
   - **`/login`**: Logs in a user and returns an access token.
   - **`/profile`**: Retrieves the user profile using the access token from the Authorization header.
   - **`/mock-users`**: Retrieves the list of mock users stored in `MockSupabaseClient`.

4. **Dependency Injection with `Depends`**:
   - Used `Depends` to inject `supabase_client` into endpoint functions (`register_user`, `login_user`, `get_user_profile`, `get_mock_users`).
   - Ensured proper handling of authorization tokens (`Bearer <token>`) in `get_user_profile`.

5. **Environment Variables**:
   - Defined environment variables (`USE_MOCK_SUPABASE`, `SUPABASE_URL`, `SUPABASE_KEY`) to configure Supabase connection details.

### Resolving Issues:

- **Handling Authentication**:
  - Implemented token extraction and validation in `get_user_profile`.
  - Set access token in `supabase_client` to fetch user profile correctly.

- **Mocking Supabase Client**:
  - Utilized `MockSupabaseClient` for testing and development by setting `USE_MOCK_SUPABASE=true`.

### Next Steps:

- **Testing**:
  - Verify each endpoint using Swagger or testing framework to ensure correct functionality.
  - Check `/profile` endpoint with a valid `Bearer <token>` to retrieve user profile after login.

### Conclusion:

The provided structure and adjustments ensure that your FastAPI application integrates properly with Supabase, supports mock testing, and handles user registration, login, and profile retrieval effectively. Make sure to test thoroughly to validate each endpoint's behavior and integration with Supabase. Adjust configurations (`USE_MOCK_SUPABASE`, Supabase URL, and key) as per your environment setup.