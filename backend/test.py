import requests
import json

BASE_URL = "http://localhost:8000"

def test_path_generation(user_id=5):
    print(f"🧪 Testing path generation for user ID: {user_id}")
    
    # Test data
    payload = {
        "learner_type": "beginner",
        "time_availability": "part_time",
        "learning_domain": "web_dev",
        "study_weeks": 12,
        "user_id": user_id
    }
    
    try:
        # Step 1: Generate path
        print("1. Generating learning path...")
        response = requests.post(
            f"{BASE_URL}/generate-path/",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Path generation successful!")
            print(f"   Path ID: {result.get('path_id')}")
            print(f"   Message: {result.get('message')}")
            
            path_data = result.get('path_data', {})
            stats = path_data.get('stats', {})
            print(f"   Nodes generated: {stats.get('nodes_completed', 0)}")
            print(f"   Total hours: {stats.get('total_hours_used', 0)}")
            
            # Step 2: Check current path
            print("\n2. Checking current path...")
            current_response = requests.get(
                f"{BASE_URL}/generate-path/user/{user_id}/current-path"
            )
            
            if current_response.status_code == 200:
                current_result = current_response.json()
                if current_result.get('has_path'):
                    current_path = current_result.get('path', {})
                    print("✅ Current path found!")
                    print(f"   Title: {current_path.get('title')}")
                    print(f"   Progress: {current_path.get('progress_percentage')}%")
                else:
                    print("❌ No active path found")
            
            # Step 3: Get all paths
            print("\n3. Getting all paths...")
            all_paths_response = requests.get(
                f"{BASE_URL}/generate-path/user/{user_id}/all-paths"
            )
            
            if all_paths_response.status_code == 200:
                all_paths = all_paths_response.json()
                paths_list = all_paths.get('paths', [])
                print(f"✅ Found {len(paths_list)} total paths")
                for path in paths_list:
                    print(f"   - {path.get('title')} (ID: {path.get('id')})")
            
        else:
            print(f"❌ Path generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure FastAPI is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_path_generation(5)