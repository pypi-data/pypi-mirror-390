import os
import sys
from dotenv import load_dotenv

def load_api_key():
    paths_checked = []

    # 1. Current working directory
    cwd_env = os.path.join(os.getcwd(), ".env")
    paths_checked.append(cwd_env)
    if os.path.exists(cwd_env):
        print(f"[ENV] Loading from CWD: {cwd_env}")
        load_dotenv(dotenv_path=cwd_env)

    else:
        # 2. Relative to this file
        source_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        paths_checked.append(source_env)
        if os.path.exists(source_env):
            print(f"[ENV] Loading from source root: {source_env}")
            load_dotenv(dotenv_path=source_env)

        else:
            # 3. Inject project root into sys.path
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            print(f"[ENV] No .env found. Checked paths:\n" + "\n".join(paths_checked))

    # 4. Final fallback
    key = os.getenv("GENAI_API_KEY") or os.environ.get("GENAI_API_KEY")
    print(f"[ENV] GENAI_API_KEY loaded: {key}")
    return key
