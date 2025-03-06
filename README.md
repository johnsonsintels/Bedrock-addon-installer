### How It Works

#### **Key Features**
1. **User-Friendly Upload Process:**
   - Users upload `.mcpack` files to `/home/container/addons/uploads` via the Pterodactyl file manager.
   - No additional steps are required from the user beyond uploading the file.

2. **Automatic Installation:**
   - The script extracts each `.mcpack` file (a ZIP archive) and reads its `manifest.json` to determine:
     - **Pack Type:** Behavior ("data") or Resource ("resources") based on the `modules` section.
     - **UUID and Version:** Extracted from the `header` section for unique identification and versioning.
   - Files are copied to `/home/container/behavior_packs/<uuid>` or `/home/container/resource_packs/<uuid>`.
   - The default world's `world_behavior_packs.json` or `world_resource_packs.json` is updated to include the new pack.

3. **World Detection:**
   - The script reads `server.properties` to find the `level-name`, ensuring addons are applied to the correct world (defaults to "world" if not found).

4. **Robust Error Handling:**
   - Checks for missing `manifest.json`, invalid pack types, and JSON errors, logging issues for debugging.
   - Uses temporary directories to avoid cluttering the server with extraction artifacts.

5. **Logging:**
   - All actions and errors are logged to `/home/container/addons/install_log.txt`, allowing users and admins to verify installations.

6. **File Management:**
   - Processed `.mcpack` files are moved to `/home/container/addons/installed` to prevent reprocessing and keep the upload directory clean.

#### **Execution Timing**
- The script runs before the server starts, processing any `.mcpack` files present in the upload directory. This ensures addons are installed during server startup, aligning with Pterodactyl's workflow.

---

### Integration with Pterodactyl and Blueprints

To deploy this script on your servers using Pterodactyl and Blueprints, follow these steps:

1. **Place the Script:**
   - Upload `addon_installer.py` to `/home/container/scripts/addon_installer.py` within the server's file system.
   - You can do this via the Pterodactyl file manager or by including it in your Blueprint configuration.

2. **Ensure Python is Available:**
   - Verify that Python 3 is installed in the Pterodactyl Docker container. Most Bedrock Dedicated Server eggs include Python, but if not:
     - Modify your Pterodactyl egg (e.g., `egg-bedrock-server.json`) to include Python by adding it to the Docker image or installation script:
       ```json
       "install": [
           "apt-get update",
           "apt-get install -y python3",
           ...
       ]
       ```
     - Alternatively, update your Blueprint to ensure the container has Python 3.

3. **Modify the Startup Command:**
   - In the Pterodactyl panel, under the server's **Startup** settings, prepend the script execution to the existing startup command.
   - Original startup command (example): `/bedrock_server`
   - New startup command:
     ```
     python3 /home/container/scripts/addon_installer.py && /bedrock_server
     ```
   - This runs the script before launching the Bedrock Dedicated Server.

4. **Directory Structure:**
   - The script automatically creates the following directories if they don’t exist:
     - `/home/container/addons/uploads`
     - `/home/container/addons/installed`
     - `/home/container/behavior_packs`
     - `/home/container/resource_packs`
   - Ensure these paths are accessible within the container (they should be by default in Pterodactyl).

5. **User Instructions:**
   - Inform your users to:
     - Upload `.mcpack` files to the `/addons/uploads` directory using the Pterodactyl file manager.
     - Restart their server to trigger the installation (addons are applied during startup).
   - Provide a note that they can check `/addons/install_log.txt` for installation details.

6. **Blueprints Integration:**
   - If using Blueprints to manage server configurations, include the script and directory setup in your Blueprint template:
     - Add `addon_installer.py` to the `scripts` folder in the Blueprint.
     - Update the Blueprint’s startup command to include the script execution as shown above.
   - This ensures consistency across all servers deployed via Blueprints.

---

### Example Usage

1. **User Action:**
   - A user uploads `CoolAddon.mcpack` to `/home/container/addons/uploads` via the Pterodactyl file manager.

2. **Server Restart:**
   - The user restarts the server through the Pterodactyl panel.

3. **Script Execution:**
   - Before the server starts, `addon_installer.py` runs:
     - Extracts `CoolAddon.mcpack` to a temporary directory.
     - Reads `manifest.json`, finding:
       - `uuid`: `abcd1234-5678-90ab-cdef-1234567890ab`
       - `version`: `[1, 0, 0]`
       - `type`: `"resources"`
     - Copies files to `/home/container/resource_packs/abcd1234-5678-90ab-cdef-1234567890ab`.
     - Updates `/home/container/worlds/<default_world>/world_resource_packs.json` with:
       ```json
       [
           {"pack_id": "abcd1234-5678-90ab-cdef-1234567890ab", "version": [1, 0, 0]}
       ]
       ```
     - Moves `CoolAddon.mcpack` to `/home/container/addons/installed`.

4. **Log Output:**
   - In `/home/container/addons/install_log.txt`:
     ```
     2023-10-15 14:30:00 - Starting addon installation process...
     2023-10-15 14:30:01 - Successfully installed resource pack: CoolAddon (abcd1234-5678-90ab-cdef-1234567890ab)
     2023-10-15 14:30:01 - Moved CoolAddon.mcpack to installed directory.
     2023-10-15 14:30:01 - Addon installation process completed.
     ```

5. **Result:**
   - The addon is installed and active when the server starts, enhancing the user’s Minecraft Bedrock experience.

---

- **Seamless User Experience:** Users only need to upload files—no technical knowledge required.
- **Reliability:** Robust error handling and logging ensure issues are caught and reported.
- **Scalability:** Works with any number of .mcpack files and avoids conflicts using UUIDs.
- **Pterodactyl Compatibility:** Integrates smoothly with Pterodactyl’s file system and startup process.
- **Blueprints Support:** Easily incorporated into your Blueprint templates for consistent deployment.

This script delivers a fully automatic, user-friendly addon installation system tailored to your Pterodactyl and Blueprints setup
